from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "figures"


def draw_box(c, x, y, w, h, title, body, fill, stroke=colors.HexColor("#1f2937")):
    c.setStrokeColor(stroke)
    c.setLineWidth(1.1)
    c.setFillColor(fill)
    c.roundRect(x, y, w, h, 8, stroke=1, fill=1)
    c.setFillColor(colors.HexColor("#111827"))
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(x + 8, y + h - 16, title)
    c.setFont("Helvetica", 7.2)
    text = c.beginText(x + 8, y + h - 29)
    text.setLeading(9.0)
    for line in body.split("\n"):
        text.textLine(line)
    c.drawText(text)


def draw_arrow(c, x1, y1, x2, y2, color=colors.HexColor("#374151")):
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(1.2)
    c.line(x1, y1, x2, y2)
    dx = 7 if x2 >= x1 else -7
    c.line(x2, y2, x2 - dx, y2 + 4)
    c.line(x2, y2, x2 - dx, y2 - 4)


def method_overview():
    path = FIG_DIR / "method_overview.pdf"
    w, h = 720, 300
    c = canvas.Canvas(str(path), pagesize=(w, h))
    c.setTitle("PU-XMSAT study design")
    c.setFillColor(colors.HexColor("#111827"))
    c.setFont("Helvetica-Bold", 13)
    c.drawString(28, h - 28, "PU-XMSAT study design: isolate the supervision change while preserving the reproduced MSAT protocol")
    c.setFont("Helvetica", 7.2)
    c.setFillColor(colors.HexColor("#4b5563"))
    c.drawString(28, h - 42, "The method keeps the reproduced graph backend fixed and changes how unobserved CMM-ADR pairs enter training.")

    y = 132
    box_w = 142
    gap = 34
    xs = [28, 28 + box_w + gap, 28 + 2 * (box_w + gap), 28 + 3 * (box_w + gap)]
    fills = [
        colors.HexColor("#e0f2fe"),
        colors.HexColor("#ecfdf5"),
        colors.HexColor("#fef3c7"),
        colors.HexColor("#ede9fe"),
    ]
    draw_box(c, xs[0], y, box_w, 86, "Reproduced MSAT anchor", "Official 10 folds\nValidation/test positives hidden\nBaseline metrics locked", fills[0])
    draw_box(c, xs[1], y, box_w, 86, "PU pair construction", "Observed positives\nReliable negatives\nDown-weighted unlabeled pairs", fills[1])
    draw_box(c, xs[2], y, box_w, 86, "Weighted PU training", "Same MSAT backend\nWeighted BCE objective\nValidation-F1 threshold", fills[2])
    draw_box(c, xs[3], y, box_w, 86, "Paper-facing outputs", "10-fold comparison\nSeed robustness and weights\nMechanism/evidence triage", fills[3])
    for i in range(3):
        draw_arrow(c, xs[i] + box_w + 3, y + 43, xs[i + 1] - 5, y + 43)

    c.setFont("Helvetica-Bold", 8.2)
    c.setFillColor(colors.HexColor("#111827"))
    c.drawString(xs[1], 94, "Reliable-negative score combines:")
    chips = [
        ("model score", "#dbeafe"),
        ("graph support", "#dcfce7"),
        ("positive similarity", "#fef9c3"),
        ("ADR frequency", "#fee2e2"),
        ("mechanism flags", "#ede9fe"),
    ]
    cx = xs[1]
    for label, fill in chips:
        tw = 58 + len(label) * 2.0
        c.setFillColor(colors.HexColor(fill))
        c.setStrokeColor(colors.HexColor("#6b7280"))
        c.roundRect(cx, 70, tw, 18, 6, stroke=1, fill=1)
        c.setFillColor(colors.HexColor("#111827"))
        c.setFont("Helvetica", 6.8)
        c.drawCentredString(cx + tw / 2, 75.6, label)
        cx += tw + 7

    c.setFillColor(colors.HexColor("#374151"))
    c.setFont("Helvetica", 7.1)
    c.drawString(28, 30, "Claim boundary: improved incomplete-label supervision and mechanism prioritization, not causal ADR incidence or full Table 5/6 reproduction.")
    c.showPage()
    c.save()


def metric_delta():
    path = FIG_DIR / "metric_delta.pdf"
    w, h = 520, 320
    c = canvas.Canvas(str(path), pagesize=(w, h))
    c.setTitle("Hybrid PU-XMSAT deltas versus MSAT")
    c.setFillColor(colors.HexColor("#111827"))
    c.setFont("Helvetica-Bold", 12.5)
    c.drawString(30, h - 28, "Hybrid PU-XMSAT improves the reproduced MSAT baseline across seeds")
    c.setFillColor(colors.HexColor("#4b5563"))
    c.setFont("Helvetica", 7.2)
    c.drawString(30, h - 42, "Bars show fold-mean metric deltas versus the reproduced MSAT anchor; p values are paired across the same 10 folds.")

    metrics = ["AUC", "AUPRC", "F1", "MCC"]
    seed2026 = [0.001149, 0.000834, 0.003613, 0.005889]
    seed1337 = [0.001121, 0.000888, 0.003316, 0.005811]
    p2026 = ["p=0.0004", "p=0.0031", "p=0.0074", "p=0.0179"]
    p1337 = ["p=0.0016", "p=0.0563", "p=0.0087", "p=0.0153"]
    maxv = 0.0062
    left = 90
    base = 72
    plot_w = 370
    row_gap = 48
    bar_h = 12
    col1 = colors.HexColor("#2563eb")
    col2 = colors.HexColor("#f97316")
    grid = colors.HexColor("#d1d5db")

    c.setStrokeColor(grid)
    c.setLineWidth(0.5)
    for tick in [0.0, 0.002, 0.004, 0.006]:
        x = left + tick / maxv * plot_w
        c.line(x, base - 18, x, base + row_gap * 4 - 18)
        c.setFillColor(colors.HexColor("#6b7280"))
        c.setFont("Helvetica", 6.8)
        c.drawCentredString(x, base - 33, f"{tick:.3f}")
    c.setFillColor(colors.HexColor("#374151"))
    c.setFont("Helvetica", 7.2)
    c.drawCentredString(left + plot_w / 2, 21, "Mean delta versus reproduced MSAT")

    for i, metric in enumerate(metrics):
        y = base + (3 - i) * row_gap
        c.setFillColor(colors.HexColor("#111827"))
        c.setFont("Helvetica-Bold", 8.0)
        c.drawRightString(left - 12, y + 3, metric)
        for j, (val, ptxt, col) in enumerate([(seed2026[i], p2026[i], col1), (seed1337[i], p1337[i], col2)]):
            yy = y + (7 if j == 0 else -9)
            bw = val / maxv * plot_w
            c.setFillColor(col)
            c.rect(left, yy, bw, bar_h, stroke=0, fill=1)
            c.setFillColor(colors.HexColor("#111827"))
            c.setFont("Helvetica", 6.6)
            c.drawString(left + bw + 5, yy + 2.6, f"+{val:.4f} ({ptxt})")

    c.setFillColor(col1)
    c.rect(310, h - 62, 9, 9, stroke=0, fill=1)
    c.setFillColor(colors.HexColor("#111827"))
    c.setFont("Helvetica", 7.2)
    c.drawString(323, h - 61, "seed 2026")
    c.setFillColor(col2)
    c.rect(382, h - 62, 9, 9, stroke=0, fill=1)
    c.setFillColor(colors.HexColor("#111827"))
    c.drawString(395, h - 61, "seed 1337")
    c.showPage()
    c.save()


def mechanism_workflow():
    path = FIG_DIR / "mechanism_workflow.pdf"
    w, h = 720, 310
    c = canvas.Canvas(str(path), pagesize=(w, h))
    c.setTitle("Mechanism and evidence workflow")
    c.setFillColor(colors.HexColor("#111827"))
    c.setFont("Helvetica-Bold", 13)
    c.drawString(28, h - 28, "Mechanism interpretation workflow: from prediction to conservative evidence boundary")
    c.setFillColor(colors.HexColor("#4b5563"))
    c.setFont("Helvetica", 7.2)
    c.drawString(28, h - 42, "The explanation layer prioritizes review targets without upgrading predictions to confirmed adverse-reaction evidence.")

    y = 150
    box_w = 122
    gap = 20
    xs = [28 + i * (box_w + gap) for i in range(5)]
    fill = [
        colors.HexColor("#fef3c7"),
        colors.HexColor("#e0f2fe"),
        colors.HexColor("#dcfce7"),
        colors.HexColor("#ede9fe"),
        colors.HexColor("#fee2e2"),
    ]
    draw_box(c, xs[0], y, box_w, 82, "Candidate pair", "CMM node\nADR node\nPrediction score", fill[0])
    draw_box(c, xs[1], y, box_w, 82, "Mechanism paths", "Parse compounds\nParse targets\nKeep available paths", fill[1])
    draw_box(c, xs[2], y, box_w, 82, "Key subgraph", "Compound/target nodes\nMechanism edges\nCase-level summary", fill[2])
    draw_box(c, xs[3], y, box_w, 82, "Local perturbation", "Mask one node\nMask one path\nScore drop = sensitivity", fill[3])
    draw_box(c, xs[4], y, box_w, 82, "Evidence boundary", "Manual evidence grade\nExternal support status\nNo causal upgrade", fill[4])
    for i in range(4):
        draw_arrow(c, xs[i] + box_w + 3, y + 41, xs[i + 1] - 5, y + 41)

    c.setFillColor(colors.HexColor("#111827"))
    c.setFont("Helvetica-Bold", 8.2)
    c.drawString(42, 98, "Current case-study outcome")
    c.setStrokeColor(colors.HexColor("#9ca3af"))
    c.setLineWidth(0.8)
    c.roundRect(40, 36, 640, 52, 7, stroke=1, fill=0)
    c.setFont("Helvetica", 7.1)
    c.setFillColor(colors.HexColor("#374151"))
    lines = [
        "Zhishi--diarrhoea: 11 nodes / 8 edges / 14 paths; top path drop 0.010074, but external evidence remains direction-conflicting.",
        "Fragaria--altered-consciousness: one parsed path; top path drop 0.000021, so mechanism sensitivity is negligible.",
        "Interpretation: useful for triage and hypothesis generation; insufficient for confirmed external validation or causal effect claims.",
    ]
    t = c.beginText(55, 75)
    t.setLeading(11)
    for line in lines:
        t.textLine(line)
    c.drawText(t)
    c.showPage()
    c.save()


if __name__ == "__main__":
    FIG_DIR.mkdir(exist_ok=True)
    method_overview()
    metric_delta()
    mechanism_workflow()
    print("Wrote figure PDFs to", FIG_DIR)
