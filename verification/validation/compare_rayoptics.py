"""Reference comparison using unmodified RayOptics 0.9.8 surface and refraction routines."""
from pathlib import Path
import sys,json,math,csv
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'vendor'))
import numpy as np
from rayoptics.elem.profiles import Spherical
from rayoptics.raytr.raytrace import bend
import validity as v

def trace_library(h,field):
 p=np.array([0.,v.S*math.tan(math.radians(field)),-v.S]);d=np.array([0.,h-p[1],v.S]);d/=np.linalg.norm(d)
 sf=Spherical(c=1/v.R1);_,p=sf.intersect(p,d,1e-12,1);d=bend(d,sf.normal(p),1,v.N)
 p=p-np.array([0.,0.,v.T]);sf=Spherical(c=1/v.R2);_,p=sf.intersect(p,d,1e-12,1);d=bend(d,sf.normal(p),v.N,1)
 yi=p[1]+(v.Q-p[2])*d[1]/d[2]
 return yi
rows=[]
for a in [.25,.5,1,2,3,4,5,6]:
 for angle in [0,2,5,10,15]:
  for h in np.linspace(-a,a,101):
   ref=v.trace(h,angle)[0];external=trace_library(h,angle)
   rows.append({'half_bundle_cm':a,'field_deg':angle,'launch_height_cm':h,'independent_snell_cm':ref,'rayoptics_cm':external,'difference_cm':abs(ref-external)})
with (v.ROOT/'rayoptics_comparison.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
report={'external_package':'rayoptics','version':'0.9.8','routines':'Spherical.intersect, Spherical.normal, raytrace.bend','ray_comparisons':len(rows),'max_abs_image_intercept_difference_cm':max(r['difference_cm'] for r in rows),'tolerance_cm':1e-9,'passed':all(r['difference_cm']<1e-9 for r in rows)}
(v.ROOT/'rayoptics_summary.json').write_text(json.dumps(report,indent=2));print(report)
