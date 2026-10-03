# iGOLab — Automated QA Supplement

This package contains the Playwright-based automated test script and the recorded result files used to verify the principal calculations, interface functions, project persistence, performance, and responsive layouts of the published web application.

## Web application tested

**Live application:**  
https://eidan83.github.io/Geometrical-Optics-Interactive-Lab/

The test is run directly against the published GitHub Pages deployment. No local `index.html` file is required or included in this package.

## Package contents

- `software_qa_playwright.py` — automated functional, responsive-layout, persistence, and timing tests.
- `requirements.txt` — required Python package specification.
- `recorded_results/` — result files retained for the submitted manuscript.

## Requirements

- Windows 10 or Windows 11.
- Python 3 installed and available through the `py` command.
- An active internet connection.
- Either Playwright Chromium or an installed Microsoft Edge browser.

## Installation on Windows

1. Extract this ZIP package.
2. Open **Command Prompt** inside the extracted folder.
3. Confirm that Python is available:

```bat
py --version
```

4. Install the Python dependency:

```bat
py -m pip install -r requirements.txt
```

5. Install the Playwright Chromium browser:

```bat
py -m playwright install chromium
```

## Run the test on the published application

Run the following command exactly as shown:

```bat
py software_qa_playwright.py "https://eidan83.github.io/Geometrical-Optics-Interactive-Lab/" --output-dir fresh_results --headed
```

The browser window will open and the test will move automatically through the simulator modules. Do not interact with the browser until the test is complete and the browser closes.

The `--headed` option displays the browser while the test runs. It may be removed for a background run:

```bat
py software_qa_playwright.py "https://eidan83.github.io/Geometrical-Optics-Interactive-Lab/" --output-dir fresh_results
```

## Alternative: run with Microsoft Edge

When Microsoft Edge is already installed, the test can be run without downloading Playwright Chromium:

```bat
py software_qa_playwright.py "https://eidan83.github.io/Geometrical-Optics-Interactive-Lab/" --channel msedge --output-dir fresh_results --headed
```

## Expected completion message

A successful run ends with messages similar to:

```text
Functional tests: 13/13 passed
Responsive profiles: passed
```

The exact timing values and browser version may differ between computers.

## Newly generated result files

Each run creates the selected output folder, such as `fresh_results`, containing:

- `optics_qa_results.json`
- `functional_tests.csv`
- `viewport_tests.csv`
- `performance_summary.csv`
- `optics_qa_console.txt`

## Repeating the test

Before repeating a run with the same output-folder name, delete only the newly generated folder:

```bat
rmdir /s /q fresh_results
```

Then run the test command again. Do not delete or overwrite `recorded_results` unless the submitted reference results are intentionally being replaced.

## Scope of the automated checks

The script performs 13 functional checks, including thin-lens, two-lens, lens-maker, spherical-mirror, thick-lens, prism, parallel-slab, optical-bench, detector, undo/redo, and project export/import checks. It also evaluates five responsive viewport profiles and records browser-console and page errors.

## Review note

The live URL identifies the public software project. It is included here to permit direct verification of the deployed application. Its use or disclosure during blinded peer review remains subject to the journal editor's decision and review procedures.
