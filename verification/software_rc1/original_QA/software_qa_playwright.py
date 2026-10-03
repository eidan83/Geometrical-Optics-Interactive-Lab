from __future__ import annotations

import argparse
import csv
import json
import platform
import statistics
import sys
import time
from datetime import datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from playwright.sync_api import Browser, Page, sync_playwright


PROFILES = [
    ("Desktop", 1440, 900, False, False),
    ("Tablet landscape", 1024, 768, True, False),
    ("Tablet portrait", 768, 1024, True, False),
    ("Phone portrait", 390, 844, True, True),
    ("Phone landscape", 844, 390, True, True),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run functional, responsive-layout, and timing checks for "
            "Geometrical Optics Interactive Lab."
        )
    )
    parser.add_argument(
        "target",
        help=(
            "Path to the self-contained simulator HTML file or an http(s) URL "
            "for the deployed application"
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("fresh_results"),
        help="Folder for newly generated result files (default: fresh_results)",
    )
    parser.add_argument(
        "--channel",
        choices=["chromium", "chrome", "msedge", "chrome-beta", "msedge-beta"],
        help="Installed browser channel, for example msedge",
    )
    parser.add_argument(
        "--executable",
        type=Path,
        help="Optional path to a Chromium-family browser executable",
    )
    parser.add_argument("--headed", action="store_true", help="Show the browser while tests run")
    return parser.parse_args()


def playwright_version() -> str:
    try:
        return version("playwright")
    except PackageNotFoundError:
        return "unknown"


def normalize_minus(value: str) -> str:
    return value.replace("−", "-").strip()


def text(page: Page, selector: str) -> str:
    return page.locator(selector).text_content().strip()


def percentile_95(values: list[float]) -> float:
    ordered = sorted(values)
    index = max(0, round(0.95 * (len(ordered) - 1)))
    return ordered[index]


def timing_stats(values: list[float]) -> dict[str, float]:
    return {
        "median_ms": round(statistics.median(values), 2),
        "p95_ms": round(percentile_95(values), 2),
    }


def add_test(results: dict[str, Any], name: str, passed: bool, evidence: Any) -> None:
    results["functional"].append({"test": name, "pass": bool(passed), "evidence": evidence})


def is_http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def open_simulator(page: Page, source: dict[str, str], timeout: int = 30000) -> None:
    if source["kind"] == "url":
        page.goto(source["value"], wait_until="domcontentloaded", timeout=timeout)
    else:
        page.set_content(source["value"], wait_until="domcontentloaded", timeout=timeout)
    page.wait_for_selector('[data-tab="single"]', timeout=timeout)
    page.wait_for_timeout(200)


def run_profile_checks(browser: Browser, source: dict[str, str], results: dict[str, Any]) -> None:
    for name, width, height, touch, mobile in PROFILES:
        context = browser.new_context(
            viewport={"width": width, "height": height},
            has_touch=touch,
            is_mobile=mobile,
        )
        page = context.new_page()
        page_errors: list[str] = []
        console_errors: list[str] = []
        page.on("pageerror", lambda error: page_errors.append(str(error)))
        page.on(
            "console",
            lambda message: console_errors.append(message.text) if message.type == "error" else None,
        )
        page.on("dialog", lambda dialog: dialog.accept())

        started = time.perf_counter()
        open_simulator(page, source)
        load_ms = (time.perf_counter() - started) * 1000

        all_tabs_operable = True
        for tab in ["single", "double", "maker", "mirrors", "thick", "prism", "abcd"]:
            locator = page.locator(f'[data-tab="{tab}"]')
            locator.tap(timeout=5000) if touch else locator.click(timeout=5000)
            page.wait_for_timeout(30)
            all_tabs_operable = all_tabs_operable and page.locator(f"#tab-{tab}").is_visible()

        load_example = page.locator("#v21-load-example")
        load_example.tap(timeout=5000) if touch else load_example.click(timeout=5000)
        page.wait_for_timeout(80)

        metrics = page.evaluate(
            """()=>{
                const doc = document.documentElement;
                const board = document.getElementById('v21-bench-board').getBoundingClientRect();
                const add = document.getElementById('v21-add-element').getBoundingClientRect();
                const tabHeights = [...document.querySelectorAll('.tab-button')]
                    .map(x => x.getBoundingClientRect().height);
                return {
                    scrollWidth: doc.scrollWidth,
                    innerWidth: innerWidth,
                    boardWidth: board.width,
                    boardHeight: board.height,
                    addWidth: add.width,
                    addHeight: add.height,
                    minTabHeight: Math.min(...tabHeights)
                };
            }"""
        )

        results["profiles"].append(
            {
                "profile": name,
                "viewport": f"{width}x{height}",
                "touch": touch,
                "load_ms": round(load_ms, 1),
                "all_tabs_operable": all_tabs_operable,
                "horizontal_overflow_px": max(
                    0, round(metrics["scrollWidth"] - metrics["innerWidth"], 1)
                ),
                "bench_px": f'{metrics["boardWidth"]:.0f}x{metrics["boardHeight"]:.0f}',
                "add_button_px": f'{metrics["addWidth"]:.0f}x{metrics["addHeight"]:.0f}',
                "minimum_tab_height_px": round(metrics["minTabHeight"], 1),
                "camera_optical_elements": text(page, "#v21-element-count"),
                "camera_rays": text(page, "#v21-ray-count"),
                "page_errors": page_errors,
                "console_errors": console_errors,
            }
        )
        context.close()


def run_functional_checks(browser: Browser, source: dict[str, str], results: dict[str, Any]) -> None:
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    page = context.new_page()
    page_errors: list[str] = []
    console_errors: list[str] = []
    page.on("pageerror", lambda error: page_errors.append(str(error)))
    page.on(
        "console",
        lambda message: console_errors.append(message.text) if message.type == "error" else None,
    )
    page.on("dialog", lambda dialog: dialog.accept())
    open_simulator(page, source)

    thin = {"s_prime": text(page, "#image-distance"), "M": text(page, "#magnification")}
    add_test(
        results,
        "Thin-lens calculation",
        thin == {"s_prime": "30.00 cm", "M": "-1.000"},
        thin,
    )

    page.click('[data-tab="double"]')
    page.wait_for_timeout(60)
    double = {
        "s1_prime": text(page, "#dl_s1p"),
        "s2_prime": text(page, "#dl_s2p"),
        "M_total": text(page, "#dl_Mtot"),
    }
    add_test(
        results,
        "Sequential two-lens calculation",
        double["s1_prime"].startswith("21.43")
        and double["s2_prime"].startswith("-42.22")
        and normalize_minus(double["M_total"]).startswith("-1.333"),
        double,
    )

    page.click('[data-tab="maker"]')
    page.wait_for_timeout(60)
    maker = {"f": text(page, "#lm-f-value"), "P": text(page, "#lm-p-value")}
    add_test(
        results,
        "Lens-maker calculation",
        maker["f"].startswith("19.23") and maker["P"].startswith("5.20"),
        maker,
    )

    page.click('[data-tab="mirrors"]')
    page.wait_for_timeout(60)
    mirror = {
        "s_prime": text(page, "#mirror-image-distance"),
        "M": text(page, "#mirror-magnification"),
    }
    add_test(
        results,
        "Spherical-mirror calculation",
        mirror["s_prime"].startswith("10.00") and normalize_minus(mirror["M"]).startswith("-0.333"),
        mirror,
    )

    page.click('[data-tab="thick"]')
    page.wait_for_timeout(80)
    thick = {
        "tl-efl": text(page, "#tl-efl"),
        "tl-power": text(page, "#tl-power"),
        "tl-q": text(page, "#tl-q"),
        "tl-mag": text(page, "#tl-mag"),
    }
    thick_ok = (
        thick["tl-efl"] == "+19.912 cm"
        and thick["tl-power"] == "5.0221 D"
        and thick["tl-q"] == "+53.176 cm"
        and normalize_minus(thick["tl-mag"]) == "-1.73897"
    )
    add_test(results, "Thick-lens matrix outputs", thick_ok, thick)

    page.click('[data-tab="prism"]')
    page.wait_for_timeout(80)
    prism = {
        "pr-r1": text(page, "#pr-r1"),
        "pr-r2": text(page, "#pr-r2"),
        "pr-e": text(page, "#pr-e"),
        "pr-delta": text(page, "#pr-delta"),
    }
    prism_ok = (
        prism["pr-r1"] == "30.000°"
        and prism["pr-r2"] == "30.000°"
        and prism["pr-e"].startswith("48.59")
        and prism["pr-delta"] == "+37.181°"
    )
    add_test(results, "Prism refraction outputs", prism_ok, prism)

    page.evaluate("document.querySelector('[data-prism-preset=\"tir\"]').click()")
    page.wait_for_timeout(60)
    prism_tir = text(page, "#pr-note")
    add_test(
        results,
        "Prism total internal reflection",
        "total internal reflection" in prism_tir.lower(),
        prism_tir,
    )

    page.click("#pr-mode-slab")
    page.wait_for_timeout(70)
    slab = {
        "sl-r": text(page, "#sl-r"),
        "sl-e": text(page, "#sl-e"),
        "sl-d": text(page, "#sl-d"),
        "sl-status": text(page, "#sl-status"),
    }
    slab_ok = (
        slab["sl-r"] == "28.126°"
        and slab["sl-e"] == "45.000°"
        and slab["sl-d"] == "+2.6331 cm"
        and "parallel" in slab["sl-status"].lower()
    )
    add_test(results, "Parallel-slab outputs", slab_ok, slab)

    page.evaluate("document.querySelector('[data-slab-preset=\"tir\"]').click()")
    page.wait_for_timeout(60)
    slab_tir = text(page, "#sl-status")
    add_test(
        results,
        "Slab total internal reflection",
        "total internal reflection" in slab_tir.lower(),
        slab_tir,
    )

    page.click('[data-tab="abcd"]')
    page.wait_for_timeout(70)
    page.select_option("#v21-example-select", "camera")
    page.click("#v21-load-example")
    page.wait_for_timeout(80)
    camera = {
        "v21-element-count": text(page, "#v21-element-count"),
        "v21-ray-count": text(page, "#v21-ray-count"),
        "v21-interaction-count": text(page, "#v21-interaction-count"),
        "v21-screen-hits": text(page, "#v21-screen-hits"),
    }
    add_test(
        results,
        "Camera multi-element propagation",
        camera == {
            "v21-element-count": "3",
            "v21-ray-count": "14",
            "v21-interaction-count": "26",
            "v21-screen-hits": "6",
        },
        camera,
    )

    page.select_option("#v21-example-select", "focusmeter")
    page.click("#v21-load-example")
    page.wait_for_timeout(80)
    detector = {
        "v21-detector-name": text(page, "#v21-detector-name"),
        "v21-detector-power": text(page, "#v21-detector-power"),
        "v21-detector-relative": text(page, "#v21-detector-relative"),
        "v21-detector-focus": text(page, "#v21-detector-focus"),
    }
    add_test(
        results,
        "Detector/focus signal",
        detector == {
            "v21-detector-name": "Digital Power Meter",
            "v21-detector-power": "1.0000 mW",
            "v21-detector-relative": "100.0%",
            "v21-detector-focus": "100.0/100",
        },
        detector,
    )

    before = len(page.evaluate("window.v21ProjectIO.exportObject().bench.elements"))
    page.select_option("#v21-element-select", "ruler")
    page.click("#v21-add-element")
    page.wait_for_timeout(60)
    after = len(page.evaluate("window.v21ProjectIO.exportObject().bench.elements"))
    page.click("#v21-undo")
    page.wait_for_timeout(40)
    undone = len(page.evaluate("window.v21ProjectIO.exportObject().bench.elements"))
    page.click("#v21-redo")
    page.wait_for_timeout(40)
    redone = len(page.evaluate("window.v21ProjectIO.exportObject().bench.elements"))
    history = {
        "before": before,
        "after_add": after,
        "after_undo": undone,
        "after_redo": redone,
    }
    add_test(
        results,
        "Add/undo/redo state history",
        after == before + 1 and undone == before and redone == after,
        history,
    )

    exported_object = page.evaluate("window.v21ProjectIO.exportObject()")
    exported_count = len(exported_object["bench"]["elements"])
    page.click("#v21-clear")
    page.wait_for_timeout(50)
    cleared_count = len(page.evaluate("window.v21ProjectIO.exportObject().bench.elements"))
    page.evaluate(
        '(obj)=>window.v21ProjectIO.importObject(obj,"Round trip")', exported_object
    )
    page.wait_for_timeout(60)
    restored_count = len(page.evaluate("window.v21ProjectIO.exportObject().bench.elements"))
    persistence = {
        "exported": exported_count,
        "cleared": cleared_count,
        "restored": restored_count,
        "format": exported_object["format"],
        "version": exported_object["version"],
    }
    add_test(
        results,
        "Project export/import round trip",
        cleared_count == 0 and restored_count == exported_count,
        persistence,
    )

    performance = page.evaluate(
        """async()=>{
            const waitFrames = () => new Promise(resolve =>
                requestAnimationFrame(() => requestAnimationFrame(resolve)));
            const lensTimings = [];
            const benchTimings = [];
            document.querySelector('[data-tab="single"]').click();
            await waitFrames();
            const input = document.getElementById('object-distance');
            for (let i=0; i<12; i++) {
                const started = performance.now();
                input.value = 25 + i;
                input.dispatchEvent(new Event('input', {bubbles:true}));
                await waitFrames();
                lensTimings.push(performance.now() - started);
            }
            document.querySelector('[data-tab="abcd"]').click();
            await waitFrames();
            const select = document.getElementById('v21-example-select');
            const button = document.getElementById('v21-load-example');
            const examples = ['camera','microscope','kepler','newtonian'];
            for (let i=0; i<8; i++) {
                select.value = examples[i % examples.length];
                const started = performance.now();
                button.click();
                await waitFrames();
                benchTimings.push(performance.now() - started);
            }
            return {lensTimings, benchTimings};
        }"""
    )
    results["performance"] = {
        "single_lens_update_to_two_frames": timing_stats(performance["lensTimings"]),
        "bench_example_load_to_two_frames": timing_stats(performance["benchTimings"]),
    }

    results["functional_summary"] = {
        "passed": sum(item["pass"] for item in results["functional"]),
        "total": len(results["functional"]),
        "page_errors": page_errors,
        "console_errors": console_errors,
    }
    context.close()


def write_outputs(output_dir: Path, results: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    json_text = json.dumps(results, indent=2, ensure_ascii=False)
    (output_dir / "optics_qa_results.json").write_text(json_text, encoding="utf-8")

    with (output_dir / "functional_tests.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=["Test", "Pass", "Evidence"])
        writer.writeheader()
        for item in results["functional"]:
            writer.writerow(
                {
                    "Test": item["test"],
                    "Pass": item["pass"],
                    "Evidence": json.dumps(item["evidence"], ensure_ascii=False),
                }
            )

    profile_fields = [
        "profile",
        "viewport",
        "touch",
        "load_ms",
        "all_tabs_operable",
        "horizontal_overflow_px",
        "bench_px",
        "add_button_px",
        "minimum_tab_height_px",
        "camera_optical_elements",
        "camera_rays",
        "page_errors",
        "console_errors",
    ]
    with (output_dir / "viewport_tests.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=profile_fields)
        writer.writeheader()
        for item in results["profiles"]:
            row = dict(item)
            row["page_errors"] = json.dumps(row["page_errors"], ensure_ascii=False)
            row["console_errors"] = json.dumps(row["console_errors"], ensure_ascii=False)
            writer.writerow(row)

    with (output_dir / "performance_summary.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=["Operation", "Median_ms", "P95_ms"])
        writer.writeheader()
        for operation, values in results["performance"].items():
            writer.writerow(
                {
                    "Operation": operation,
                    "Median_ms": values["median_ms"],
                    "P95_ms": values["p95_ms"],
                }
            )

    summary = results["functional_summary"]
    console_text = (
        f"Run timestamp: {results['run_timestamp']}\n"
        f"Environment: {results['environment']}\n"
        f"Browser: {results['browser']}\n"
        f"Functional tests: {summary['passed']}/{summary['total']} passed\n"
        f"Page errors: {len(summary['page_errors'])}\n"
        f"Console errors: {len(summary['console_errors'])}\n\n"
        f"Full machine-readable output\n{json_text}\n"
    )
    (output_dir / "optics_qa_console.txt").write_text(console_text, encoding="utf-8")


def main() -> int:
    args = parse_args()
    if args.executable and not args.executable.is_file():
        print(f"Browser executable not found: {args.executable}", file=sys.stderr)
        return 2

    if is_http_url(args.target):
        source = {"kind": "url", "value": args.target}
        simulator_source = "remote web deployment"
    else:
        html_path = Path(args.target)
        if not html_path.is_file():
            print(f"HTML file not found: {html_path}", file=sys.stderr)
            return 2
        source = {"kind": "html", "value": html_path.read_text(encoding="utf-8")}
        simulator_source = html_path.name

    results: dict[str, Any] = {
        "run_timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "environment": platform.platform(),
        "python": platform.python_version(),
        "playwright": playwright_version(),
        "browser": "",
        "launch_mode": "",
        "simulator_source": simulator_source,
        "profiles": [],
        "functional": [],
        "performance": {},
    }

    with sync_playwright() as playwright:
        launch_kwargs: dict[str, Any] = {"headless": not args.headed}
        if args.executable:
            launch_kwargs["executable_path"] = str(args.executable.resolve())
            results["launch_mode"] = f"executable: {args.executable.name}"
        elif args.channel and args.channel != "chromium":
            launch_kwargs["channel"] = args.channel
            results["launch_mode"] = f"channel: {args.channel}"
        else:
            results["launch_mode"] = "Playwright Chromium"

        browser = playwright.chromium.launch(**launch_kwargs)
        results["browser"] = f"Chromium-family browser {browser.version}"
        run_profile_checks(browser, source, results)
        run_functional_checks(browser, source, results)
        browser.close()

    write_outputs(args.output_dir, results)

    summary = results["functional_summary"]
    all_profiles_ok = all(
        item["all_tabs_operable"]
        and item["horizontal_overflow_px"] == 0
        and not item["page_errors"]
        and not item["console_errors"]
        for item in results["profiles"]
    )
    success = (
        summary["passed"] == summary["total"]
        and not summary["page_errors"]
        and not summary["console_errors"]
        and all_profiles_ok
    )

    print(f"Results written to: {args.output_dir.resolve()}")
    print(f"Functional tests: {summary['passed']}/{summary['total']} passed")
    print(f"Responsive profiles: {'passed' if all_profiles_ok else 'check results'}")
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
