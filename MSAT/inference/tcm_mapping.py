"""MedDRA PT -> TCM functional system mapping (paper §3.4.2, Table 6)."""

from __future__ import annotations

from inference.paper_tables import paper_table6_mapping

# Fallback rules only when PT is not in paper Table 6 reference.
PT_RULES: list[tuple[str, str]] = [
    ('vomiting', 'Stomach'),
    ('persistent vomiting', 'Stomach'),
    ('palpitation', 'Heart'),
    ('pulmonary oedema', 'Lung+Qi-Blood-Fluid'),
    ('pulmonary embolism', 'Lung+Qi-Blood-Fluid'),
    ('liver injury', 'Liver+Qi-Blood-Fluid'),
    ('hepatitis', 'Liver+Qi-Blood-Fluid'),
    ('dermatitis', 'Body Surface'),
    ('gastric haemorrhage', 'Stomach+Qi-Blood-Fluid'),
    ('intestinal haemorrhage', 'Small Intestine+Qi-Blood-Fluid'),
    ('tinnitus', 'Kidney'),
    ('dizziness', 'Liver'),
    ('dizzy', 'Liver'),
    ('vertigo', 'Liver'),
    ('tremor', 'Body Surface'),
    ('diarrhoea', 'Small Intestine'),
    ('diarrhea', 'Small Intestine'),
    ('decreased appetite', 'Stomach'),
    ('anorexia', 'Stomach'),
    ('drowsiness', 'Qi-Blood-Fluid'),
    ('alertness decreased', 'Qi-Blood-Fluid'),
    ('feeling sad', 'Qi-Blood-Fluid'),
    ('mental disability', 'Qi-Blood-Fluid'),
    ('delusion', 'Qi-Blood-Fluid'),
    ('headache', 'Qi-Blood-Fluid'),
    ('intermittent headache', 'Qi-Blood-Fluid'),
    ('neoplasm', 'Qi-Blood-Fluid'),
    ('vitreous disorder', 'Qi-Blood-Fluid'),
    ('hypoalbuminaemia', 'Qi-Blood-Fluid'),
    ('blood cholesterol increased', 'Qi-Blood-Fluid'),
    ('teething', 'Qi-Blood-Fluid'),
    ('spina bifida', 'Qi-Blood-Fluid'),
]

SOC_FALLBACK: dict[str, str] = {
    'gastrointestinal disorders': 'Stomach',
    'cardiac disorders': 'Heart',
    'respiratory, thoracic and mediastinal disorders': 'Lung+Qi-Blood-Fluid',
    'hepatobiliary disorders': 'Liver+Qi-Blood-Fluid',
    'skin and subcutaneous tissue disorders': 'Body Surface',
    'ear and labyrinth disorders': 'Kidney',
    'nervous system disorders': 'Body Surface',
    'psychiatric disorders': 'Qi-Blood-Fluid',
    'metabolism and nutrition disorders': 'Qi-Blood-Fluid',
    'eye disorders': 'Qi-Blood-Fluid',
    'congenital, familial and genetic disorders': 'Qi-Blood-Fluid',
    'neoplasms benign, malignant and unspecified': 'Qi-Blood-Fluid',
}


def map_adr_to_tcm_systems(adr_pt: str, soc: str | None = None) -> str:
    paper_map = paper_table6_mapping(adr_pt)
    if paper_map:
        return paper_map
    pt_l = adr_pt.lower()
    for needle, systems in PT_RULES:
        if needle in pt_l:
            return systems
    if soc:
        soc_l = soc.lower()
        for key, label in SOC_FALLBACK.items():
            if key in soc_l:
                return label
    return 'Qi-Blood-Fluid'
