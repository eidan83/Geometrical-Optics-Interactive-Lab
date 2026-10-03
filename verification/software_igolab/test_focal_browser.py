import os
from pathlib import Path
from datetime import datetime
import hashlib,json,math
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent
out=ROOT/'corrected_browser_results'/'focal_checks';out.mkdir(parents=True,exist_ok=True)
html=(ROOT/'index.html').read_text(encoding='utf-8')
rows=[];errors=[]
def number(text):
 text=text.replace('−','-')
 return math.inf if '∞' in text else float(text.split()[0])
def close(a,b):
 return a==b if math.isinf(b) else math.isfinite(a) and abs(a-b)<=max(.011,abs(b)*1e-6)
with sync_playwright() as p:
 browser=p.chromium.launch(**({'executable_path': os.environ['IGOLAB_BROWSER']} if os.environ.get('IGOLAB_BROWSER') else {'channel':'msedge'}), headless=os.environ.get('IGOLAB_HEADLESS') == '1')
 page=browser.new_page(viewport={'width':1440,'height':1000})
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('console',lambda msg:errors.append(msg.text) if msg.type=='error' else None)
 page.set_content(html,wait_until='domcontentloaded');page.wait_for_timeout(400)
 def fill(id,value):
  page.locator('#'+id).fill(str(value));page.locator('#'+id).press('Tab');page.wait_for_timeout(120)
 def shot(name,tab):
  page.evaluate('(id)=>document.getElementById(id).classList.add("v15-details-open")',tab)
  page.screenshot(path=str(out/(name+'.png')),full_page=True)
 for i,(f,s) in enumerate([(15,14.95),(15,15.05),(15,15),(-15,-15),(-15,-14.95),(-15,-15.05),(-15,30),(15,-15)]):
  try:
   page.click('[data-tab="single"]');fill('focal-length-input',f);fill('object-distance-input',s)
   q=number(page.locator('#image-distance').inner_text());nature=page.locator('#image-nature').inner_text()
   active=page.locator('#tab-single .lens-option.active[data-type]').get_attribute('data-type')
   shown=float(page.locator('#focal-length-input').input_value());expected=math.inf if s==f else f*s/(s-f)
   want_type='convex' if f>0 else 'concave'
   want_nature='collimated output; no finite image' if s==f else ('real ' if expected>0 else 'virtual ')+('inverted' if -expected/s<0 else 'upright')
   passed=close(q,expected) and active==want_type and shown==f and nature==want_nature
   rows.append({'test':f'single f={f},s={s}','pass':passed,'q':q,'expected':expected,'type':active,'input':shown,'nature':nature})
   shot('single_'+str(i+1),'tab-single')
  except Exception as e: rows.append({'test':f'single f={f},s={s}','pass':False,'error':str(e)})
 # Type buttons, magnitude slider/drag path, reset, and visible clamp must stay synchronized.
 for i,(action,expected) in enumerate([('concave',-15),('convex',15),('negative_input',-15),('range',-20),('zero',-20),('clamp',-40),('reset',15)]):
  try:
   if action in ('concave','convex'):page.click(f'#tab-single .lens-option[data-type="{action}"]')
   elif action=='negative_input':fill('focal-length-input',-15)
   elif action=='range':page.locator('#focal-length').evaluate('(el)=>{el.value=20;el.dispatchEvent(new Event("input",{bubbles:true}));}')
   elif action=='zero':fill('focal-length-input',0)
   elif action=='clamp':fill('focal-length-input',-100)
   else:page.click('#reset-btn')
   page.wait_for_timeout(150)
   v=float(page.locator('#focal-length-input').input_value());typ=page.locator('#tab-single .lens-option.active[data-type]').get_attribute('data-type')
   rows.append({'test':'single synchronization '+action,'pass':v==expected and typ==('convex' if expected>0 else 'concave'),'input':v,'type':typ})
  except Exception as e:rows.append({'test':action,'pass':False,'error':str(e)})
 page.click('[data-tab="double"]')
 for i,(f,s) in enumerate([(15,14.95),(15,15.05),(15,15),(-15,-15),(-15,-14.95),(-15,-15.05)]):
  try:
   fill('dl_f1_input',f);fill('dl_f2_input',20);fill('dl_s1_input',s);fill('dl_d_input',35)
   q=number(page.locator('#dl_s1p').inner_text());q2=number(page.locator('#dl_s2p').inner_text())
   expected=math.inf if f==s else f*s/(s-f);s2=math.inf if math.isinf(expected) else 35-expected
   expected2=20 if math.isinf(s2) else 20*s2/(s2-20)
   typ=page.locator('#tab-double .lens-option.active[data-lens1]').get_attribute('data-lens1')
   rows.append({'test':f'double f1={f},s1={s}','pass':close(q,expected) and close(q2,expected2) and typ==('convex' if f>0 else 'concave'),'q':q,'expected':expected,'q2':q2,'expected2':expected2,'type':typ})
   shot('double_'+str(i+1),'tab-double')
  except Exception as e:rows.append({'test':f'double f1={f},s1={s}','pass':False,'error':str(e)})
 browser.close()
report={'timestamp':datetime.now().astimezone().isoformat(),'source_sha256':hashlib.sha256((ROOT/'index.html').read_bytes()).hexdigest(),'total':len(rows),'passed':sum(r['pass'] for r in rows),'failed':sum(not r['pass'] for r in rows),'browser_errors':errors,'rows':rows}
def safe(v):
 if isinstance(v,float) and not math.isfinite(v):return str(v)
 if isinstance(v,dict):return {k:safe(x) for k,x in v.items()}
 if isinstance(v,list):return [safe(x) for x in v]
 return v
(out/'focal_browser_results.json').write_text(json.dumps(safe(report),ensure_ascii=False,indent=2),encoding='utf-8')
print('Focal/UI checks:',report['passed'],'/',report['total'],'; browser errors:',len(errors))
raise SystemExit(1 if report['failed'] or errors else 0)
