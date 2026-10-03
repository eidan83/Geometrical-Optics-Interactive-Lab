from pathlib import Path
from datetime import datetime
import subprocess, sys, zipfile, shutil, hashlib, json
root=Path(__file__).resolve().parent
stamp=datetime.now().strftime('%Y%m%d_%H%M%S')
for name in ['corrected_browser_results']:
 p=root/name
 if p.exists():p.rename(root/(name+'_previous_'+stamp))
commands=[[sys.executable,'original_QA/software_qa_playwright.py',str(root/'index.html'),'--channel','msedge','--output-dir','corrected_browser_results','--headed'],[sys.executable,'test_focal_browser.py'],[sys.executable,'test_aperture_browser.py']]
import time
start_time=time.time()
results=[]
for command in commands:
 results.append({'script':command[1],'returncode':subprocess.run(command,cwd=root).returncode})
out=root/('GOIL_RC2_full_results_'+stamp+'.zip')
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('run_manifest.json',json.dumps({'source_sha256':hashlib.sha256((root/'index.html').read_bytes()).hexdigest(),'commands':results},indent=2))
 p=root/'corrected_browser_results'
 if p.exists():
  for f in p.rglob('*'):
   if f.is_file():z.write(f,f.relative_to(root))
 for f in root.glob('aperture_results_*.zip'):
  if f.stat().st_mtime>=start_time:z.write(f,f.name)
print('Send this file:',out)
sys.exit(int(any(r['returncode'] for r in results)))
