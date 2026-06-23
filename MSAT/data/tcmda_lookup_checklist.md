# TCMDA 查库清单（论文 Table 5 · 15 味 CMM）

登录：https://organchem.csdb.cn/scdb/main/tcm_introduce.asp  
模块：**中药成分毒副作用数据库** 或 **中药药材检索**

| # | 中文名 | 拼音 | 目标 ADR (MedDRA PT) | 论文 database_verified |
|---|--------|------|----------------------|------------------------|
| 1 | 虎杖 | Huzhang | Vomiting | ✓ |
| 2 | 常山 | Changshan | Vomiting | ✗ |
| 3 | 红景天 | Hongjingtian | Palpitations | ✗ |
| 4 | 木贼 | Muzei | Vomiting | ✓ |
| 5 | 罗勒 | Luole | Acute pulmonary oedema | ✓ |
| 6 | 艾叶 | Aiye | Drug-induced liver injury | ✓ |
| 7 | 莪术 | Ezhu | Dermatitis | ✓ |
| 8 | 牛蒡根 | Niubanggen | Acute pulmonary oedema | ✓ |
| 9 | 商陆 | Shanglu | Gastric haemorrhage | ✓ |
| 10 | 八角茴香 | Bajiao Huixiang | Pulmonary embolism | ✓ |
| 11 | 芫花 | Yuanhua | Small intestinal haemorrhage | ✓ |
| 12 | 刺五加 | Ciwujia | Tinnitus | ✓ |
| 13 | 黑升麻 | Hei Shengma | Dizziness | ✗ |
| 14 | 两面针 | Liangmianzhen | Hepatitis | ✗ |
| 15 | 喜树 | Xishu | Tremor | ✓ |

账号可用后：

```bash
export TCMDA_USER='你的用户名'
export TCMDA_PASS='你的密码'
python scripts/fetch_tcmda.py --write-cache
python scripts/run_table5_validation.py --tcmda-cache data/tcmda_cache.json
```
