import csv
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest


def _module():
    from scripts import export_pu_xmsat_top_predictions as export

    return export


class FakeNames:
    def __init__(self):
        self.herbs = {
            0: SimpleNamespace(
                primary="Herb Zero",
                latin="Latin zero",
                chinese="零号草药",
                pinyin="ling hao",
            ),
            1: SimpleNamespace(
                primary="Herb One",
                latin="Latin one",
                chinese="一号草药",
                pinyin="yi hao",
            ),
        }
        self.adrs = {
            0: SimpleNamespace(primary="ADR zero", meddra_pt="ADR PT zero"),
            1: SimpleNamespace(primary="ADR one", meddra_pt="ADR PT one"),
            2: SimpleNamespace(primary="ADR two", meddra_pt="ADR PT two"),
        }

    def herb_display(self, herb_id):
        rec = self.herbs[herb_id]
        return f"{rec.chinese}（{rec.latin}）"

    def adr_display(self, adr_id):
        return self.adrs[adr_id].meddra_pt


class FakePredictor:
    def __init__(self):
        self.n_herb = 2
        self.n_adr = 3
        self.known_map = {0: {1}}
        self.names = FakeNames()
        self.score_calls = []
        self.path_map = {
            (1, 0): ["一号草药 -> Compound #12 -> Target #20 <- ADR PT zero"],
            (1, 2): ["知识图谱中未发现该 CMM–ADR 对的显式短路径（模型仍基于嵌入推断）"],
            (0, 2): [{"path": "零号草药 -> Compound #8 -> Target #9 <- ADR PT two"}],
        }

    def score_herb_all_adrs(self, herb_id, batch_size=2048):
        self.score_calls.append((herb_id, batch_size))
        scores = {
            0: np.array([0.11, 0.99, 0.70]),
            1: np.array([0.95, 0.20, 0.81]),
        }
        return scores[herb_id]

    def explain_herb_adr(self, herb_id, adr_id):
        return self.path_map.get((herb_id, adr_id), [])


def test_default_top_k_is_at_least_50():
    export = _module()

    assert export.DEFAULT_TOP_K >= 50
    assert export.build_arg_parser().parse_args([]).top_k >= 50


def test_known_positive_pairs_are_excluded_from_ranked_rows():
    export = _module()

    payload = export.build_top_prediction_export(
        FakePredictor(),
        checkpoint_path="saved_models/pu_xmsat_pilot_fold0.pt",
        top_k=5,
    )

    pairs = [(row["herb_id"], row["adr_id"]) for row in payload["rows"]]
    assert (0, 1) not in pairs
    assert pairs[:3] == [(1, 0), (1, 2), (0, 2)]
    assert [row["rank"] for row in payload["rows"]] == list(range(1, len(payload["rows"]) + 1))


def test_rows_include_required_fields_and_conservative_mechanism_metadata():
    export = _module()

    payload = export.build_top_prediction_export(
        FakePredictor(),
        checkpoint_path="saved_models/pu_xmsat_pilot_fold0.pt",
        top_k=3,
    )

    explicit = payload["rows"][0]
    placeholder = payload["rows"][1]
    required_fields = {
        "herb_id",
        "herb_name",
        "herb_latin",
        "herb_chinese",
        "herb_pinyin",
        "adr_id",
        "adr_pt",
        "prediction_score",
        "score",
        "original_score",
        "rank",
        "has_explicit_mechanism_path",
        "mechanism_path_count",
        "explicit_mechanism_path_count",
        "top_mechanism_paths",
        "candidate_source",
        "checkpoint_path",
    }

    assert required_fields.issubset(explicit.keys())
    assert explicit["has_explicit_mechanism_path"] is True
    assert explicit["mechanism_path_count"] == 1
    assert explicit["explicit_mechanism_path_count"] == 1
    assert placeholder["top_mechanism_paths"]
    assert placeholder["mechanism_path_count"] == 1
    assert placeholder["has_explicit_mechanism_path"] is False
    assert placeholder["explicit_mechanism_path_count"] == 0


def test_json_csv_and_markdown_preserve_checkpoint_context_and_claim_boundary(tmp_path):
    export = _module()
    payload = export.build_top_prediction_export(
        FakePredictor(),
        checkpoint_path="saved_models/pu_xmsat_pilot_fold0.pt",
        top_k=2,
    )
    output_json = tmp_path / "pu_xmsat_top_predictions.json"
    output_csv = tmp_path / "pu_xmsat_top_predictions.csv"
    output_md = tmp_path / "PU_XMSAT_TOP_PREDICTIONS_EXPORT.md"

    export.write_top_prediction_artifacts(payload, output_json, output_csv, output_md)

    saved = json.loads(output_json.read_text())
    csv_rows = list(csv.DictReader(output_csv.open()))
    markdown = output_md.read_text()

    assert saved["checkpoint_path"] == "saved_models/pu_xmsat_pilot_fold0.pt"
    assert saved["checkpoint_context"]["is_final_10fold_export"] is False
    assert "not final" in saved["checkpoint_context"]["scope_limitations"].lower()
    assert saved["claim_boundary"] in markdown
    assert "not final 10-fold export" in markdown.lower()
    assert csv_rows[0]["checkpoint_path"] == "saved_models/pu_xmsat_pilot_fold0.pt"
    assert csv_rows[0]["is_final_10fold_export"] == "False"


def test_formal_fold_checkpoint_can_be_marked_as_final_export():
    export = _module()

    payload = export.build_top_prediction_export(
        FakePredictor(),
        checkpoint_path=(
            "saved_models/pu_xmsat_formal/"
            "pu_xmsat_full_msat_pu_hybrid_seed2026_pairs66015_valf1_u0p2_rn0p8_fold0.pt"
        ),
        top_k=2,
        checkpoint_is_final_pu_xmsat=True,
    )

    assert payload["checkpoint_context"]["is_final_10fold_export"] is True
    assert payload["checkpoint_context"]["checkpoint_context"] == "final_10fold_pu_xmsat_export"


def test_help_describes_checkpoint_argument(capsys):
    export = _module()
    parser = export.build_arg_parser()

    with pytest.raises(SystemExit) as excinfo:
        parser.parse_args(["--help"])

    assert excinfo.value.code == 0
    help_text = capsys.readouterr().out
    assert "PU-XMSAT" in help_text
    assert "--checkpoint" in help_text
