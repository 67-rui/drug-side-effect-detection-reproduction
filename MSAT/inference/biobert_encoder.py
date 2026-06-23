"""BioBERT CLS encoder aligned with MSAT graph node features."""

from __future__ import annotations

import os
from functools import lru_cache

import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer

DEFAULT_MODEL = 'dmis-lab/biobert-base-cased-v1.2'


def _prefer_local_only() -> bool:
    return os.environ.get('MSAT_BIOBERT_LOCAL_ONLY', '1').lower() in ('1', 'true', 'yes')


@lru_cache(maxsize=1)
def _load_model(model_name: str = DEFAULT_MODEL):
    local_only = _prefer_local_only()
    load_kwargs = {'local_files_only': True} if local_only else {}

    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name, **load_kwargs)
        model = AutoModel.from_pretrained(model_name, **load_kwargs)
    except OSError as exc:
        if local_only:
            raise RuntimeError(
                f'BioBERT 本地缓存不可用: {model_name}\n'
                '请先在可联网环境运行一次以下命令完成下载：\n'
                f'  python -c "from transformers import AutoModel, AutoTokenizer; '
                f"AutoTokenizer.from_pretrained('{model_name}'); "
                f"AutoModel.from_pretrained('{model_name}')\"\n"
                '或设置 MSAT_BIOBERT_LOCAL_ONLY=0 允许联网下载。'
            ) from exc
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModel.from_pretrained(model_name)

    model.eval()
    return tokenizer, model


def encode_texts(texts: list[str], batch_size: int = 64, model_name: str = DEFAULT_MODEL) -> np.ndarray:
    """Return CLS embeddings (768-d) for each text."""
    if not texts:
        return np.zeros((0, 768), dtype=np.float32)

    tokenizer, model = _load_model(model_name)
    out_rows: list[np.ndarray] = []

    for start in range(0, len(texts), batch_size):
        batch = texts[start : start + batch_size]
        inputs = tokenizer(
            batch,
            padding=True,
            truncation=True,
            max_length=128,
            return_tensors='pt',
        )
        with torch.no_grad():
            hidden = model(**inputs).last_hidden_state[:, 0, :].numpy()
        out_rows.append(hidden.astype(np.float32))

    return np.vstack(out_rows)


def score_nodes(node_x: np.ndarray, candidate_emb: np.ndarray) -> np.ndarray:
    """Raw dot product, matching Zenodo precomputed node features."""
    return node_x @ candidate_emb.T
