from pathlib import Path
import json,hashlib,zipfile
from datetime import datetime
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent
out=ROOT/('aperture_results_'+datetime.now().strftime('%Y%m%d_%H%M%S'));out.mkdir()
rows=[];errors=[]
with sync_playwright() as p:
 browser=p.chromium.launch(channel='msedge',headless=False)
 page=browser.new_page(viewport={'width':1440,'height':1000})
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content((ROOT/'index.html').read_text(encoding='utf-8'),wait_until='domcontentloaded')
 page.click('[data-tab="abcd"]')
 page.evaluate('''() => window.v21ProjectIO.importObject({elements:[{id:'apertureTestLens',type:'thickLens',x:60,y:0,angle:0,n:1.52,width:5,aperture:24,R1:28,R2:-28}],ambient:1},'Aperture test')''')
 page.locator('[data-eid="apertureTestLens"]').first.dispatch_event('dblclick')
 page.wait_for_timeout(150)
 def element():return page.evaluate("() => window.v21ProjectIO.exportObject().bench.elements[0]")
 def field(k):return page.locator('[data-v21-prop="'+k+'"]')
 def edit(k,v):
  field(k).fill(str(v));field(k).press('Tab');page.wait_for_timeout(150)
 def check(name,fn):
  try:
   fn();rows.append({'test':name,'pass':True})
  except Exception as e:rows.append({'test':name,'pass':False,'error':str(e)})
 def near(a,b):assert abs(a-b)<1e-8,(a,b)
 def typing():
  field('R1').fill('2');near(element()['R1'],28);near(element()['aperture'],24)
  field('R1').fill('20');near(element()['R1'],28)
  field('R1').press('Enter');page.wait_for_timeout(150);near(element()['R1'],20);near(element()['aperture'],24)
 check('Typing 2 then 20 does not shrink the aperture',typing)
 def constrain():
  edit('R1',10);near(element()['requestedAperture'],24);near(element()['aperture'],18.2)
  near(float(field('requestedAperture').input_value()),24);near(float(field('__usedAperture').input_value()),18.2)
  page.screenshot(path=str(out/'limited_aperture.png'),full_page=True)
 check('Constraint displays applied aperture and keeps request',constrain)
 def restore():
  edit('R1',30);near(element()['aperture'],24)
  edit('R2',-8);near(element()['aperture'],14.56)
  edit('R2',-30);near(element()['aperture'],24)
  page.screenshot(path=str(out/'restored_aperture.png'),full_page=True)
 check('Both surfaces restore requested aperture',restore)
 def change_request():
  edit('requestedAperture',16);edit('R1',6);edit('R1',30);near(element()['aperture'],16)
 check('Explicit aperture change is preserved',change_request)
 def persistence():
  edit('R1',6)
  saved=page.evaluate('() => window.v21ProjectIO.exportObject()')
  page.evaluate('(s) => window.v21ProjectIO.importObject(s)',saved)
  page.locator('[data-eid="apertureTestLens"]').first.dispatch_event('dblclick');page.wait_for_timeout(150)
  near(element()['requestedAperture'],16);edit('R1',30);near(element()['aperture'],16)
 check('Export/import preserves aperture intent',persistence)
 version=browser.version;browser.close()
report={'source_sha256':hashlib.sha256((ROOT/'index.html').read_bytes()).hexdigest(),'browser':version,'checks':rows,'page_errors':errors,'passed':sum(r['pass'] for r in rows),'total':len(rows)}
(out/'results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
archive=out.with_suffix('.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for f in out.iterdir():z.write(f,f.name)
print(json.dumps(report,indent=2));print('Results:',archive)
raise SystemExit(0 if all(r['pass'] for r in rows) and not errors else 1)
