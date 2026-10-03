@echo off
cd /d "%~dp0"
if exist corrected_browser_results (
  powershell -NoProfile -Command "Move-Item -LiteralPath 'corrected_browser_results' -Destination ('previous_corrected_' + (Get-Date -Format 'yyyyMMdd_HHmmss_fff'))"
)
if exist corrected_browser_results (
  echo Could not preserve previous results. Please rename the results folder and try again.
  pause
  exit /b 1
)
py original_QA\software_qa_playwright.py "%~dp0index.html" --channel msedge --output-dir corrected_browser_results --headed
py test_focal_browser.py
powershell -NoProfile -Command "Compress-Archive -Path 'corrected_browser_results' -DestinationPath ('GOIL_corrected_results_' + (Get-Date -Format 'yyyyMMdd_HHmmss_fff') + '.zip')"
echo Please send the GOIL_corrected_results ZIP file.
pause
