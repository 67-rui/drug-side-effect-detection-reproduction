import csv
import json

import numpy as np

from scripts.build_target_name_candidates import (
    build_target_name_candidate_report,
    parse_hgnc_candidates,
    write_outputs,
)


def test_parse_hgnc_candidates_keeps_approved_symbol_name_and_ids():
    text = "\n".join(
        [
            "hgnc_id\tsymbol\tname\tstatus\talias_symbol\tprev_symbol\tuniprot_ids",
            "HGNC:1\tGENEA\talpha target protein\tApproved\tA1|A2\tOLD1\tP00001",
            "HGNC:2\tGENEB\tbeta target protein\tEntry Withdrawn\t\t\tP00002",
            "HGNC:3\tGENEC\tgamma target protein\tApproved\t\t\t",
        ]
    )

    candidates = parse_hgnc_candidates(text)

    assert [candidate.symbol for candidate in candidates] == ["GENEA", "GENEC"]
    assert candidates[0].text == "GENEA alpha target protein"
    assert candidates[0].aliases == ["A1", "A2"]
    assert candidates[0].uniprot_ids == ["P00001"]


def test_build_target_name_candidate_report_ranks_targets_with_injected_encoder():
    queue = {
        "rows": [
            {"feature": "target:15721", "node_type": "target", "node_id": 15721},
            {"feature": "compound:821", "node_type": "compound", "node_id": 821},
            {"feature": "target:11486", "node_type": "target", "node_id": 11486},
        ]
    }
    hgnc_text = "\n".join(
        [
            "hgnc_id\tsymbol\tname\tstatus\talias_symbol\tprev_symbol\tuniprot_ids",
            "HGNC:1\tGENEA\talpha target protein\tApproved\t\t\tP00001",
            "HGNC:2\tGENEB\tbeta target protein\tApproved\t\t\tP00002",
            "HGNC:3\tGENEC\tgamma target protein\tApproved\t\t\tP00003",
        ]
    )
    target_features = {
        15721: np.array([0.92, 0.08, 0.00], dtype=np.float32),
        11486: np.array([0.10, 0.86, 0.04], dtype=np.float32),
    }

    def fake_encode(texts, batch_size=64):
        vectors = {
            "GENEA alpha target protein": [1.0, 0.0, 0.0],
            "GENEB beta target protein": [0.0, 1.0, 0.0],
            "GENEC gamma target protein": [0.0, 0.0, 1.0],
        }
        return np.asarray([vectors[text] for text in texts], dtype=np.float32)

    report = build_target_name_candidate_report(
        queue_payload=queue,
        hgnc_tsv_text=hgnc_text,
        target_features=target_features,
        encode_fn=fake_encode,
        top_k=2,
    )

    assert report["summary"]["target_count"] == 2
    assert report["summary"]["candidate_source"] == "HGNC complete set"
    assert "candidate" in report["claim_boundary"].lower()
    first = report["targets"][0]
    assert first["node_id"] == 15721
    assert first["top_candidate"]["symbol"] == "GENEA"
    assert first["top_candidate"]["score"] == 0.92
    assert first["top_candidate"]["margin"] == 0.84
    second = report["targets"][1]
    assert second["top_candidate"]["symbol"] == "GENEB"


def test_write_outputs_creates_target_candidate_json_csv_and_markdown(tmp_path):
    report = {
        "summary": {"target_count": 1, "candidate_source": "HGNC complete set"},
        "claim_boundary": "candidate mappings only",
        "targets": [
            {
                "node_id": 15721,
                "feature": "target:15721",
                "top_candidate": {
                    "rank": 1,
                    "symbol": "GENEA",
                    "name": "alpha target protein",
                    "hgnc_id": "HGNC:1",
                    "uniprot_ids": ["P00001"],
                    "score": 0.92,
                    "margin": 0.84,
                    "mapping_status": "candidate_only",
                },
                "candidates": [
                    {
                        "rank": 1,
                        "symbol": "GENEA",
                        "name": "alpha target protein",
                        "hgnc_id": "HGNC:1",
                        "uniprot_ids": ["P00001"],
                        "score": 0.92,
                        "margin": 0.84,
                        "mapping_status": "candidate_only",
                    }
                ],
            }
        ],
    }

    out_json = tmp_path / "target_candidates.json"
    out_csv = tmp_path / "target_candidates.csv"
    out_md = tmp_path / "target_candidates.md"
    write_outputs(report, out_json, out_csv, out_md)

    assert json.loads(out_json.read_text())["summary"]["target_count"] == 1
    rows = list(csv.DictReader(out_csv.open()))
    assert rows[0]["feature"] == "target:15721"
    assert rows[0]["symbol"] == "GENEA"
    assert "Target Name Candidate Report" in out_md.read_text()
