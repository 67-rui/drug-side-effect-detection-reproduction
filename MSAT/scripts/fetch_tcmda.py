#!/usr/bin/env python3
"""Login to TCMDA and query herb adverse phenotypes for Table 5 cache fill.

Credentials via env (never commit):
  export TCMDA_USER=...
  export TCMDA_PASS=...

Usage:
  python scripts/fetch_tcmda.py --dry-run
  python scripts/fetch_tcmda.py --write-cache
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin

import requests

MSAT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MSAT_ROOT))

BASE = 'https://organchem.csdb.cn/scdb/main/'
TCM_MULTI = 'https://organchem.csdb.cn/scdb/Tcm_Multi/'

# Paper Table 5 herbs (Chinese names for TCMDA search)
TABLE5_HERBS = [
    {'pinyin': 'Huzhang', 'chinese': '虎杖', 'latin': 'Polygonum cuspidatum', 'adr_pt': 'Vomiting'},
    {'pinyin': 'Changshan', 'chinese': '常山', 'latin': 'Dichroa febrifuga', 'adr_pt': 'Vomiting'},
    {'pinyin': 'Hongjingtian', 'chinese': '红景天', 'latin': 'Rhodiola crenulata', 'adr_pt': 'Palpitations'},
    {'pinyin': 'Muzei', 'chinese': '木贼', 'latin': 'Equisetum hyemale', 'adr_pt': 'Vomiting'},
    {'pinyin': 'Luole', 'chinese': '罗勒', 'latin': 'Ocimum basilicum', 'adr_pt': 'Acute pulmonary oedema'},
    {'pinyin': 'Aiye', 'chinese': '艾叶', 'latin': 'Artemisia argyi', 'adr_pt': 'Drug-induced liver injury'},
    {'pinyin': 'Ezhu', 'chinese': '莪术', 'latin': 'Curcuma phaeocaulis', 'adr_pt': 'Dermatitis'},
    {'pinyin': 'Niubanggen', 'chinese': '牛蒡根', 'latin': 'Arctium lappa', 'adr_pt': 'Acute pulmonary oedema'},
    {'pinyin': 'Shanglu', 'chinese': '商陆', 'latin': 'Phytolacca acinosa', 'adr_pt': 'Gastric haemorrhage'},
    {'pinyin': 'Bajiao Huixiang', 'chinese': '八角茴香', 'latin': 'Illicium verum', 'adr_pt': 'Pulmonary embolism'},
    {'pinyin': 'Yuanhua', 'chinese': '芫花', 'latin': 'Daphne genkwa', 'adr_pt': 'Small intestinal haemorrhage'},
    {'pinyin': 'Ciwujia', 'chinese': '刺五加', 'latin': 'Eleutherococcus senticosus', 'adr_pt': 'Tinnitus'},
    {'pinyin': 'Hei Shengma', 'chinese': '黑升麻', 'latin': 'Cimicifuga racemosa', 'adr_pt': 'Dizziness'},
    {'pinyin': 'Liangmianzhen', 'chinese': '两面针', 'latin': 'Zanthoxylum nitidum', 'adr_pt': 'Hepatitis'},
    {'pinyin': 'Xishu', 'chinese': '喜树', 'latin': 'Camptotheca acuminata', 'adr_pt': 'Tremor'},
]


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({
        'User-Agent': (
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ),
    })
    return s


def login(sess: requests.Session, user: str, pwd: str) -> bool:
    r = sess.get(BASE + 'tcm_introduce.asp', timeout=30)
    r.encoding = 'gb2312'
    m = re.search(r'name=Todayword value="([^"]+)"', r.text)
    if not m:
        print('[ERR] Todayword not found on intro page')
        return False
    today = m.group(1)
    resp = sess.post(
        BASE + 'slogin.asp',
        data={
            'Username': user,
            'Password': pwd,
            'Todayword': today,
            'login': '登录',
        },
        headers={'Referer': BASE + 'tcm_introduce.asp'},
        timeout=30,
        allow_redirects=True,
    )
    resp.encoding = 'gb2312'
    ok = 'ToxUser' in resp.text or (
        '您好' in resp.text and 'name=Username' not in resp.text
    )
    if ok:
        m2 = re.search(r'class="l5">([^<]+)', resp.text)
        print('[OK] login:', (m2.group(1).strip() if m2 else 'authenticated'))
    else:
        print('[FAIL] login rejected (still shows login form)')
    return ok


def fetch_page(sess: requests.Session, path: str) -> str:
    url = urljoin(TCM_MULTI, path)
    r = sess.get(url, headers={'Referer': BASE + 'slogin_up.asp'}, timeout=30)
    r.encoding = 'gb2312'
    return r.text


def search_herb_tcd(sess: requests.Session, chinese: str) -> str:
    """Query 中药药材检索 (q_tcd.asp) by herb name."""
    r = sess.get(TCM_MULTI + 'q_tcd.asp', headers={'Referer': BASE + 'slogin_up.asp'}, timeout=30)
    r.encoding = 'gb2312'
    if '不能通过这种方式访问' in r.text or '404 Error' in r.text:
        return r.text[:200]
    # discover form field names
    forms = re.findall(r'<form[^>]*action="([^"]*)"[^>]*>(.*?)</form>', r.text, re.I | re.S)
    if not forms:
        return r.text[:500]
    action, body = forms[0]
    fields: dict[str, str] = {}
    for inp in re.finditer(r'<input[^>]+>', body, re.I):
        tag = inp.group(0)
        nm = re.search(r'name="([^"]+)"', tag, re.I)
        if not nm:
            continue
        name = nm.group(1)
        typ = re.search(r'type="([^"]+)"', tag, re.I)
        val = re.search(r'value="([^"]*)"', tag, re.I)
        if typ and typ.group(1).lower() == 'hidden':
            fields[name] = val.group(1) if val else ''
    # guess herb name field
    for key in list(fields):
        if re.search(r'tcd|herb|name|yao|cn', key, re.I):
            fields[key] = chinese
            break
    else:
        # common legacy ASP names
        for guess in ('tcdname', 'TCDName', 'herbname', 'HerbName', 'name', 'keyword'):
            fields[guess] = chinese
    post_url = urljoin(TCM_MULTI, action)
    r2 = sess.post(post_url, data=fields, headers={'Referer': TCM_MULTI + 'q_tcd.asp'}, timeout=30)
    r2.encoding = 'gb2312'
    return r2.text


def search_tox(sess: requests.Session, chinese: str) -> str:
    """Query 中药成分毒副作用数据库."""
    for path in ('Tox_eff_query2.asp', 'Tox_eff_query.asp', 'tox_eff_query2.asp'):
        html = fetch_page(sess, path)
        if '不能通过这种方式访问' in html or '404 Error' in html:
            continue
        forms = re.findall(r'<form[^>]*action="([^"]*)"[^>]*>(.*?)</form>', html, re.I | re.S)
        if not forms:
            return html[:800]
        action, body = forms[0]
        fields: dict[str, str] = {}
        for inp in re.finditer(r'<input[^>]+>', body, re.I):
            tag = inp.group(0)
            nm = re.search(r'name="([^"]+)"', tag, re.I)
            if not nm:
                continue
            name = nm.group(1)
            typ = re.search(r'type="([^"]+)"', tag, re.I)
            val = re.search(r'value="([^"]*)"', tag, re.I)
            if typ and typ.group(1).lower() in ('hidden', 'text'):
                fields[name] = val.group(1) if val else ''
        for key in list(fields):
            if fields[key] == '' or re.search(r'tcd|herb|name|yao|cn|key', key, re.I):
                fields[key] = chinese
        post_url = urljoin(TCM_MULTI, action)
        r2 = sess.post(post_url, data=fields, headers={'Referer': urljoin(TCM_MULTI, path)}, timeout=30)
        r2.encoding = 'gb2312'
        return r2.text
    return ''


def extract_phenotypes(html: str) -> list[str]:
    """Heuristic extraction of adverse phenotype strings from result HTML."""
    phenotypes: list[str] = []
    # table cells often contain toxicity terms
    for cell in re.findall(r'<td[^>]*>([^<]{2,80})</td>', html, re.I):
        t = re.sub(r'\s+', ' ', cell).strip()
        if not t or t.isdigit():
            continue
        if any(k in t for k in ('毒', '不良', '反应', '副', '呕吐', '晕', '损伤', '出血', '水肿', 'tox', 'adverse')):
            if t not in phenotypes:
                phenotypes.append(t)
    return phenotypes[:20]


def build_cache_entries(sess: requests.Session, herbs: list[dict]) -> list[dict]:
    entries = []
    for h in herbs:
        cn = h['chinese']
        print(f'[QUERY] {cn} ({h["pinyin"]}) target ADR: {h["adr_pt"]}')
        html = search_tox(sess, cn) or search_herb_tcd(sess, cn)
        phenotypes = extract_phenotypes(html)
        aliases = [cn, h['pinyin'], h['latin']]
        entries.append({
            'herb_query': cn,
            'herb_aliases': aliases,
            'adverse_phenotypes': phenotypes,
            'predicted_adr_pt': h['adr_pt'],
            'source_url': TCM_MULTI + 'Tox_eff_query2.asp',
            'notes': f"Auto-fetched {datetime.now().date()}",
            'verified_at': datetime.now().strftime('%Y-%m-%d'),
            'verified_by': 'fetch_tcmda.py',
            'raw_html_len': len(html),
        })
        print(f'  -> {len(phenotypes)} phenotype hits: {phenotypes[:5]}')
    return entries


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--user', default=os.environ.get('TCMDA_USER', ''))
    parser.add_argument('--password', default=os.environ.get('TCMDA_PASS', ''))
    parser.add_argument('--write-cache', action='store_true')
    parser.add_argument('--out', type=Path, default=MSAT_ROOT / 'data' / 'tcmda_cache.json')
    parser.add_argument('--dry-run', action='store_true', help='Login only, probe module pages')
    args = parser.parse_args()

    if not args.user or not args.password:
        print('Set TCMDA_USER and TCMDA_PASS env vars (or --user/--password)')
        sys.exit(1)

    sess = _session()
    if not login(sess, args.user, args.password):
        sys.exit(2)

    if args.dry_run:
        for path in ('Tox_eff_query2.asp', 'q_tcd.asp', 'q_comp.asp'):
            html = fetch_page(sess, path)
            print(f'[{path}] len={len(html)} blocked={"不能" in html or "404" in html}')
        return

    entries = build_cache_entries(sess, TABLE5_HERBS)
    payload = {
        'updated_at': datetime.now().isoformat(),
        'source': 'https://organchem.csdb.cn/',
        'entries': entries,
    }
    if args.write_cache:
        args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f'[SAVED] {args.out}')
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False)[:2000])


if __name__ == '__main__':
    main()
