import os
import re
import sys
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt


def parse_cobertura_safe(xml_path: str) -> ET.Element:
    with open(xml_path, "r", encoding="utf-8") as f:
        raw = f.read()

    # Escape raw '<' and '>' inside attribute values (e.g., name="<Main>$", signature="(List<string>)")
    def escape_attr(match: re.Match) -> str:
        prefix, val = match.group(1), match.group(2)
        val = val.replace("<", "&lt;").replace(">", "&gt;")
        return f'{prefix}"{val}"'

    sanitized = re.sub(r'(\b(?:name|signature)=)"([^"]*)"', escape_attr, raw)
    return ET.fromstring(sanitized)


def main(xml_path: str, out_png: str) -> None:
    root = parse_cobertura_safe(xml_path)

    overall_branch = float(root.attrib["branch-rate"]) * 100.0
    overall_line = float(root.attrib["line-rate"]) * 100.0

    labels = []
    branch_rates = []
    line_rates = []

    for cls in root.findall(".//class"):
        name = cls.attrib.get("name", "")
        if "Controllers." in name:
            short_name = name.split("Controllers.")[-1]
        elif name == "Program":
            short_name = "Program (Startup)"
        else:
            continue
        labels.append(short_name)
        branch_rates.append(float(cls.attrib["branch-rate"]) * 100.0)
        line_rates.append(float(cls.attrib["line-rate"]) * 100.0)

    labels.append("TỔNG HỆ THỐNG")
    branch_rates.append(overall_branch)
    line_rates.append(overall_line)

    x = range(len(labels))
    width = 0.36

    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=150)
    bars_branch = ax.bar([i - width / 2 for i in x], branch_rates, width, label="Branch Coverage (%)", color="#2563eb")
    bars_line = ax.bar([i + width / 2 for i in x], line_rates, width, label="Line Coverage (%)", color="#10b981")

    ax.axhline(70.0, color="#dc2626", linestyle="--", linewidth=1.5, label="Ngưỡng cam kết Branch Coverage (70%)")

    ax.set_ylabel("Tỷ lệ bao phủ (%)")
    ax.set_title("Độ bao phủ mã nguồn Backend SUT (DATN_TestSUT - Cobertura)")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=15, ha="right")
    ax.set_ylim(0, 112)
    ax.grid(axis="y", linestyle=":", alpha=0.6)
    ax.legend(loc="lower right")

    for bar in bars_branch:
        h = bar.get_height()
        ax.annotate(f"{h:.1f}%", xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=8.5, fontweight="bold")

    for bar in bars_line:
        h = bar.get_height()
        ax.annotate(f"{h:.1f}%", xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=8.5)

    os.makedirs(os.path.dirname(out_png), exist_ok=True)
    plt.tight_layout()
    plt.savefig(out_png)
    print(f"Saved chart to {out_png} | Overall Branch: {overall_branch:.2f}%, Line: {overall_line:.2f}%")


if __name__ == "__main__":
    xml_file = sys.argv[1] if len(sys.argv) > 1 else "evidence/metrics/coverage.xml"
    png_file = sys.argv[2] if len(sys.argv) > 2 else "evidence/metrics/coverage-chart.png"
    main(xml_file, png_file)