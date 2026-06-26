from scripts.summarize_pu_xmsat_results import markdown_metric_row


def test_markdown_metric_row_formats_four_decimals():
    row = markdown_metric_row("MSAT", {"auc": 0.979271, "auprc": 0.977094})
    assert row == "| MSAT | 0.9793 | 0.9771 |"
