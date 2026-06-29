from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Any


CSV_FIELDS = [
    "contribution_group",
    "rank",
    "feature",
    "node_type",
    "node_id",
    "path_features",
    "case_count",
    "occurrence_count",
    "mean_score_drop",
    "max_score_drop",
    "positive_drop_count",
    "negative_drop_count",
]

CLAIM_BOUNDARY_CN = (
    "本报告只解释当前已量化案例中的局部扰动敏感性；不是因果效应、不是 SHAP 值、不是外部临床验证。"
)


def load_contribution_payload(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text())


def _rounded(value: float) -> float:
    return round(float(value), 10)


def _case_key(case_index: int, case: dict[str, Any]) -> str:
    return f"{case_index}:{case.get('source', 'unknown')}:{case.get('herb_id')}:{case.get('adr_id')}"


def _path_features(row: dict[str, Any]) -> str:
    features = row.get("features")
    if isinstance(features, list):
        return ";".join(str(feature) for feature in features)
    if features:
        return str(features)
    return str(row.get("path_features", ""))


def _empty_bucket(**metadata: Any) -> dict[str, Any]:
    return {
        **metadata,
        "case_keys": set(),
        "score_drops": [],
    }


def _finalize_bucket(bucket: dict[str, Any]) -> dict[str, Any]:
    drops = [float(value) for value in bucket["score_drops"]]
    positive = [value for value in drops if value > 0]
    negative = [value for value in drops if value < 0]
    output = {
        key: value
        for key, value in bucket.items()
        if key not in {"case_keys", "score_drops"}
    }
    output.update(
        {
            "case_count": len(bucket["case_keys"]),
            "occurrence_count": len(drops),
            "mean_score_drop": _rounded(mean(drops)) if drops else 0.0,
            "max_score_drop": _rounded(max(drops)) if drops else 0.0,
            "positive_drop_count": len(positive),
            "negative_drop_count": len(negative),
        }
    )
    return output


def _sort_contributions(rows: list[dict[str, Any]], label_field: str) -> list[dict[str, Any]]:
    return sorted(
        rows,
        key=lambda row: (
            -float(row["mean_score_drop"]),
            -float(row["max_score_drop"]),
            str(row.get(label_field, "")),
        ),
    )


def _aggregate_nodes(
    payload: dict[str, Any],
    node_type: str,
    top_k: int,
) -> list[dict[str, Any]]:
    buckets: dict[tuple[str, str], dict[str, Any]] = {}
    for case_index, case in enumerate(payload.get("cases", []), start=1):
        case_key = _case_key(case_index, case)
        for row in case.get("node_contributions", []):
            if str(row.get("node_type")) != node_type:
                continue
            feature = str(row.get("feature", ""))
            node_id = str(row.get("node_id", ""))
            bucket = buckets.setdefault(
                (feature, node_id),
                _empty_bucket(
                    feature=feature,
                    node_type=node_type,
                    node_id=node_id,
                    path_features="",
                ),
            )
            bucket["case_keys"].add(case_key)
            bucket["score_drops"].append(float(row.get("score_drop", 0.0)))
    return _sort_contributions([_finalize_bucket(bucket) for bucket in buckets.values()], "feature")[:top_k]


def _aggregate_pathways(payload: dict[str, Any], top_k: int) -> list[dict[str, Any]]:
    buckets: dict[str, dict[str, Any]] = {}
    for case_index, case in enumerate(payload.get("cases", []), start=1):
        case_key = _case_key(case_index, case)
        for row in case.get("path_contributions", []):
            path_features = _path_features(row)
            bucket = buckets.setdefault(
                path_features,
                _empty_bucket(
                    feature=str(row.get("feature", "")),
                    node_type="",
                    node_id="",
                    path_features=path_features,
                ),
            )
            bucket["case_keys"].add(case_key)
            bucket["score_drops"].append(float(row.get("score_drop", 0.0)))
    return _sort_contributions([_finalize_bucket(bucket) for bucket in buckets.values()], "path_features")[:top_k]


def _top_row(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not rows:
        return None
    return sorted(rows, key=lambda row: (-float(row.get("score_drop", 0.0)), str(row.get("feature", ""))))[0]


def _feature_label(row: dict[str, Any] | None, fallback: str = "none") -> str:
    if not row:
        return fallback
    if row.get("path_features"):
        label = str(row["path_features"])
    else:
        label = str(row.get("feature", fallback))
    drop = float(row.get("score_drop", row.get("mean_score_drop", 0.0)))
    return f"{label} ({drop:.6f})"


def _case_summary(case: dict[str, Any]) -> dict[str, Any]:
    subgraph = case.get("mechanism_subgraph", {})
    nodes = list(subgraph.get("nodes", []))
    node_features = {str(node.get("feature")) for node in nodes if node.get("feature")}
    quantified_features = {
        str(row.get("feature"))
        for row in case.get("node_contributions", [])
        if row.get("feature")
    }
    compound_nodes = [node for node in nodes if node.get("node_type") == "compound"]
    target_nodes = [node for node in nodes if node.get("node_type") == "target"]
    quantified_count = len(node_features & quantified_features)
    total_nodes = len(node_features)
    component_rows = [
        row for row in case.get("node_contributions", []) if row.get("node_type") == "compound"
    ]
    target_rows = [
        row for row in case.get("node_contributions", []) if row.get("node_type") == "target"
    ]
    path_rows = list(case.get("path_contributions", []))

    return {
        "source": case.get("source", "unknown"),
        "herb_id": int(case.get("herb_id", -1)),
        "adr_id": int(case.get("adr_id", -1)),
        "original_score": float(case.get("original_score", 0.0)),
        "subgraph_node_count": total_nodes,
        "compound_node_count": len(compound_nodes),
        "target_node_count": len(target_nodes),
        "edge_count": len(subgraph.get("edges", [])),
        "path_count": len(subgraph.get("paths", [])),
        "quantified_node_count": quantified_count,
        "node_quantification_coverage": f"{quantified_count}/{total_nodes}",
        "all_subgraph_nodes_quantified": bool(total_nodes and quantified_count == total_nodes),
        "top_component": _top_row(component_rows),
        "top_target": _top_row(target_rows),
        "top_pathway": _top_row(path_rows),
    }


def _positive_feature_count(rows: list[dict[str, Any]]) -> int:
    return sum(1 for row in rows if int(row.get("positive_drop_count", 0)) > 0)


def build_mechanism_explanation_layer(
    contribution_payload: dict[str, Any],
    top_k: int = 10,
) -> dict[str, Any]:
    case_summaries = [_case_summary(case) for case in contribution_payload.get("cases", [])]
    component_contributions = _aggregate_nodes(contribution_payload, "compound", top_k)
    target_contributions = _aggregate_nodes(contribution_payload, "target", top_k)
    pathway_contributions = _aggregate_pathways(contribution_payload, top_k)

    completion = {
        "case_count": len(case_summaries),
        "subgraph_case_count": sum(1 for case in case_summaries if case["subgraph_node_count"] > 0),
        "all_subgraph_nodes_quantified": bool(case_summaries)
        and all(case["all_subgraph_nodes_quantified"] for case in case_summaries),
        "component_count": len(component_contributions),
        "target_count": len(target_contributions),
        "pathway_count": len(pathway_contributions),
        "positive_component_count": _positive_feature_count(component_contributions),
        "positive_target_count": _positive_feature_count(target_contributions),
        "positive_pathway_count": _positive_feature_count(pathway_contributions),
    }

    return {
        "experiment": "mechanism_explanation_layer",
        "created_at": datetime.now().isoformat(),
        "source_experiment": contribution_payload.get("experiment", "unknown"),
        "checkpoint_path": contribution_payload.get("checkpoint_path", "unknown"),
        "checkpoint_context": contribution_payload.get("checkpoint_context", "not specified"),
        "source_claim_boundary": contribution_payload.get("claim_boundary", ""),
        "claim_boundary": CLAIM_BOUNDARY_CN,
        "top_k": top_k,
        "completion": completion,
        "case_summaries": case_summaries,
        "component_contributions": component_contributions,
        "target_contributions": target_contributions,
        "pathway_contributions": pathway_contributions,
    }


def _format_float(value: Any) -> str:
    return f"{float(value):.6f}"


def _contribution_rows(layer: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for group, key in [
        ("component", "component_contributions"),
        ("target", "target_contributions"),
        ("pathway", "pathway_contributions"),
    ]:
        for rank, row in enumerate(layer.get(key, []), start=1):
            rows.append({"contribution_group": group, "rank": rank, **row})
    return rows


def _markdown_contribution_table(rows: list[dict[str, Any]], label: str) -> list[str]:
    lines = [
        f"## {label}",
        "",
        "| Rank | Feature | Cases | Occurrences | Mean drop | Max drop | Positive | Negative |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for rank, row in enumerate(rows, start=1):
        feature = row.get("path_features") or row.get("feature")
        lines.append(
            f"| {rank} | `{feature}` | {row['case_count']} | {row['occurrence_count']} | "
            f"{_format_float(row['mean_score_drop'])} | {_format_float(row['max_score_drop'])} | "
            f"{row['positive_drop_count']} | {row['negative_drop_count']} |"
        )
    if not rows:
        lines.append("| 0 | `none` | 0 | 0 | 0.000000 | 0.000000 | 0 | 0 |")
    lines.append("")
    return lines


def _write_markdown(path: Path, layer: dict[str, Any]) -> None:
    completion = layer["completion"]
    lines = [
        "# PU-XMSAT 机制解释层完成报告",
        "",
        "本报告把解释层产物合并为一个论文/汇报入口：关键机制子图、成分贡献、靶点贡献和机制路径贡献。",
        "",
        f"- 机制案例数: {completion['case_count']}",
        f"- 已提取关键机制子图案例数: {completion['subgraph_case_count']}",
        f"- 完整子图节点均已量化: {'yes' if completion['all_subgraph_nodes_quantified'] else 'no'}",
        f"- 正向成分贡献条目: {completion['positive_component_count']}",
        f"- 正向靶点贡献条目: {completion['positive_target_count']}",
        f"- 正向机制路径贡献条目: {completion['positive_pathway_count']}",
        f"- Checkpoint: `{layer.get('checkpoint_path', 'unknown')}`",
        f"- Checkpoint context: {layer.get('checkpoint_context', 'not specified')}",
        "",
        layer["claim_boundary"],
        "",
        "## 关键机制子图",
        "",
        "| Case | Source | Key subgraph | Node coverage | Top component | Top target | Top pathway |",
        "| ---: | --- | --- | --- | --- | --- | --- |",
    ]
    for index, case in enumerate(layer.get("case_summaries", []), start=1):
        subgraph_text = (
            f"{case['subgraph_node_count']} nodes "
            f"({case['compound_node_count']} components, {case['target_node_count']} targets), "
            f"{case['edge_count']} edges, {case['path_count']} paths"
        )
        lines.append(
            f"| {index} | `{case['source']}` herb {case['herb_id']} -> ADR {case['adr_id']} | "
            f"{subgraph_text} | {case['node_quantification_coverage']} | "
            f"`{_feature_label(case['top_component'])}` | "
            f"`{_feature_label(case['top_target'])}` | "
            f"`{_feature_label(case['top_pathway'])}` |"
        )
    lines.append("")
    lines.extend(_markdown_contribution_table(layer.get("component_contributions", []), "成分贡献"))
    lines.extend(_markdown_contribution_table(layer.get("target_contributions", []), "靶点贡献"))
    lines.extend(_markdown_contribution_table(layer.get("pathway_contributions", []), "机制路径贡献"))
    lines.extend(
        [
            "## 论文写作边界",
            "",
            "- 可以写：当前两个机制案例均完成关键子图抽取，并对成分、靶点、机制路径进行局部置零扰动评分。",
            "- 可以写：score drop 为原始预测分数减去遮蔽后分数，正值表示遮蔽后模型分数下降。",
            "- 不要写：这些贡献是因果贡献、SHAP 归因、临床机制证明，或最终 PU checkpoint 的严格归因。",
            "",
        ]
    )
    path.write_text("\n".join(lines))


def write_mechanism_explanation_outputs(
    layer: dict[str, Any],
    output_json: Path,
    output_csv: Path,
    output_md: Path,
) -> None:
    for path in (output_json, output_csv, output_md):
        path.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(layer, ensure_ascii=False, indent=2))
    with output_csv.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        for row in _contribution_rows(layer):
            writer.writerow({field: row.get(field, "") for field in CSV_FIELDS})
    _write_markdown(output_md, layer)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build PU-XMSAT mechanism explanation layer handoff")
    parser.add_argument("--input", default="results/contribution_quantification.json")
    parser.add_argument("--output-json", default="results/mechanism_explanation_layer.json")
    parser.add_argument("--output-csv", default="results/mechanism_explanation_layer.csv")
    parser.add_argument("--output-md", default="results/PU_XMSAT_MECHANISM_EXPLANATION_LAYER.md")
    parser.add_argument("--top-k", type=int, default=10)
    args = parser.parse_args()

    payload = load_contribution_payload(args.input)
    layer = build_mechanism_explanation_layer(payload, top_k=args.top_k)
    write_mechanism_explanation_outputs(
        layer,
        output_json=Path(args.output_json),
        output_csv=Path(args.output_csv),
        output_md=Path(args.output_md),
    )
    print(
        json.dumps(
            {
                "case_count": layer["completion"]["case_count"],
                "all_subgraph_nodes_quantified": layer["completion"]["all_subgraph_nodes_quantified"],
                "component_count": layer["completion"]["component_count"],
                "target_count": layer["completion"]["target_count"],
                "pathway_count": layer["completion"]["pathway_count"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
