import csv
import glob
import os
import sys
import xml.etree.ElementTree as ET


def main(xml_dir: str, out_dir: str, commit_sha: str) -> None:
    os.makedirs(out_dir, exist_ok=True)
    xml_files = sorted(
        glob.glob(os.path.join(xml_dir, "**", "junit-run-*.xml"), recursive=True),
        key=lambda p: int(os.path.splitext(os.path.basename(p))[0].split("-")[-1]),
    )

    if not xml_files:
        print("No junit-run-*.xml files found!", file=sys.stderr)
        sys.exit(1)

    runs_summary = []
    test_matrix = {}  # test_node -> {run_id: status}

    for path in xml_files:
        run_id = int(os.path.splitext(os.path.basename(path))[0].split("-")[-1])
        tree = ET.parse(path)
        root = tree.getroot()
        suite = root.find("testsuite") if root.tag == "testsuites" else root

        passed = failed = skipped = 0
        duration = float(suite.attrib.get("time", 0.0))

        for tc in suite.findall("testcase"):
            classname = tc.attrib.get("classname", "")
            name = tc.attrib.get("name", "")
            node = f"{classname}::{name}" if classname else name

            if tc.find("failure") is not None or tc.find("error") is not None:
                status = "FAIL"
                failed += 1
            elif tc.find("skipped") is not None:
                status = "SKIP"
                skipped += 1
            else:
                status = "PASS"
                passed += 1

            test_matrix.setdefault(node, {})[run_id] = status

        total = passed + failed + skipped
        runs_summary.append({
            "run_id": run_id,
            "commit_sha": commit_sha,
            "total_cases": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "duration_sec": round(duration, 2),
            "status": "PASS" if failed == 0 and total == 50 else "FAIL",
        })

    # 1. Xuất bảng tổng hợp từng run (20 runs)
    runs_csv = os.path.join(out_dir, "runs-20-summary.csv")
    with open(runs_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["run_id", "commit_sha", "total_cases", "passed", "failed", "skipped", "duration_sec", "status"],
        )
        writer.writeheader()
        writer.writerows(runs_summary)

    # 2. Xuất bảng phân tích flaky ở cấp test case (50 cases x 20 runs = 1000 lượt)
    run_ids = [r["run_id"] for r in runs_summary]
    run_cols = [f"run_{rid:02d}" for rid in run_ids]
    flaky_csv = os.path.join(out_dir, "flaky-20.csv")

    total_executions = 0
    total_inconsistent = 0

    with open(flaky_csv, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["test_case", "pass_count", "fail_count", "inconsistent_executions", "flaky_rate_pct", "stability"] + run_cols
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for node in sorted(test_matrix.keys()):
            results = test_matrix[node]
            statuses = [results.get(rid, "MISSING") for rid in run_ids]
            p_cnt = statuses.count("PASS")
            f_cnt = statuses.count("FAIL")
            executed = p_cnt + f_cnt
            # Số lượt lệch khỏi kết quả đa số (0 nếu 20/20 PASS hoặc 20/20 FAIL)
            inconsistent = min(p_cnt, f_cnt)
            rate = (inconsistent / executed * 100.0) if executed else 0.0

            total_executions += executed
            total_inconsistent += inconsistent

            row = {
                "test_case": node,
                "pass_count": p_cnt,
                "fail_count": f_cnt,
                "inconsistent_executions": inconsistent,
                "flaky_rate_pct": f"{rate:.2f}",
                "stability": "STABLE" if inconsistent == 0 else "FLAKY",
            }
            for rid, st in zip(run_ids, statuses):
                row[f"run_{rid:02d}"] = st
            writer.writerow(row)

    overall_flaky = (total_inconsistent / total_executions * 100.0) if total_executions else 0.0
    print(f"Total runs: {len(runs_summary)} | Total executions: {total_executions} | Inconsistent: {total_inconsistent} | Overall Flaky Rate: {overall_flaky:.2f}%")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])