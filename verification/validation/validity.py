"""Exact meridional spherical-surface reference, cm; not the GOIL bench tracer."""
from pathlib import Path
import numpy as np, math, json, csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
N=1.52;R1=20.;R2=-20.;T=4.;S=45.
def surface(n1,n2,r):return np.array([[1.,0.],[-(n2-n1)/r,1.]])
M=surface(N,1,R2)@np.array([[1,T/N],[0,1]])@surface(1,N,R1)
A,B,C,D=M.ravel();Q=-(A*S+B)/(C*S+D);MAG=A+Q*C;EFL=-1/C

def intersect(p,d,vertex,radius):
 center=np.array([vertex+radius,0.]);w=p-center
 b=np.dot(w,d);disc=b*b-np.dot(w,w)+radius*radius
 if disc<0:raise ValueError('miss')
 candidates=[]
 for distance in [-b-math.sqrt(disc),-b+math.sqrt(disc)]:
  if distance<=1e-10:continue
  hit=p+distance*d
  # Select the vertex-side hemisphere, not the opposite spherical cap.
  if (hit[0]-center[0])*radius<=1e-9:candidates.append((distance,hit))
 if not candidates:raise ValueError('no forward cap intersection')
 hit=min(candidates,key=lambda x:x[0])[1]
 normal=(hit-center)/abs(radius)
 return hit,normal

def snell(d,normal,n1,n2):
 if np.dot(d,normal)>0:normal=-normal
 cosi=-np.dot(d,normal);eta=n1/n2;k=1-eta*eta*(1-cosi*cosi)
 if k<0:raise ValueError('TIR')
 out=eta*d+(eta*cosi-math.sqrt(k))*normal
 return out/np.linalg.norm(out)

def trace(h,field):
 yo=S*math.tan(math.radians(field));p=np.array([-S,yo]);direction=np.array([S,h-yo]);direction/=np.linalg.norm(direction)
 hit1,norm1=intersect(p,direction,0,R1);d1=snell(direction,norm1,1,N)
 hit2,norm2=intersect(hit1,d1,T,R2);d2=snell(d1,norm2,N,1)
 if d2[0]<=0:raise ValueError('backward exit')
 img=hit2[1]+(T+Q-hit2[0])*d2[1]/d2[0]
 axis=math.inf if abs(d2[1])<1e-14 else hit2[0]-T-hit2[1]*d2[0]/d2[1]
 return img,axis,hit1,hit2,d2

if __name__=='__main__':
 checks={}
 small=trace(1e-4,0)[1];checks['paraxial_limit_relative_error']=abs(small-Q)/Q
 checks['matrix_determinant']=float(np.linalg.det(M))
 checks['mirror_symmetry_error_cm']=abs(trace(2,5)[0]+trace(-2,-5)[0])
 checks['normal_incidence_snell_error']=float(np.max(np.abs(snell(np.array([1.,0]),np.array([-1.,0]),1,N)-[1,0])))
 apertures=[.25,.5,1,2,3,4,5,6];fields=[0,2,5,10,15]
 rows=[]
 for a in apertures:
  for field in fields:
   rays=[trace(h,field) for h in np.linspace(-a,a,101)]
   yy=np.array([r[0] for r in rays]);reference=MAG*S*math.tan(math.radians(field))
   err=yy-reference
   rows.append(dict(half_bundle_cm=a,field_deg=field,rays=101,paraxial_image_cm=reference,rms_error_cm=float(np.sqrt(np.mean(err**2))),max_error_cm=float(np.max(np.abs(err))),rms_error_percent_EFL=float(100*np.sqrt(np.mean(err**2))/EFL),max_surface_height_cm=max(max(abs(r[2][1]),abs(r[3][1])) for r in rays)))
 with (ROOT/'validity_grid.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
 axial=[dict(height_cm=a,exact_q_cm=trace(a,0)[1],paraxial_q_cm=Q,relative_focus_error_percent=100*abs(trace(a,0)[1]-Q)/Q) for a in apertures]
 with (ROOT/'axial_focus.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=axial[0]);w.writeheader();w.writerows(axial)
 res={'geometry':dict(n=N,R1_cm=R1,R2_cm=R2,thickness_cm=T,object_distance_cm=S),'matrix':M.tolist(),'paraxial_q_cm':Q,'magnification':MAG,'efl_cm':EFL,'reference_checks':checks,'axial':axial,'grid':rows,'definition':'Bundle half-width a specified at front vertex plane; field=atan(object_height/s). 101 equally weighted meridional launch rays per combination. No Fresnel power weighting. Error relative to first-order predicted image height, normalized by EFL.'}
 (ROOT/'validity_results.json').write_text(json.dumps(res,indent=2))
 plt.rcParams.update({'font.size':9,'font.family':'DejaVu Sans'})
 fig,axes=plt.subplots(1,2,figsize=(7.0,2.9),layout='constrained')
 axes[0].plot(apertures,[r['relative_focus_error_percent'] for r in axial],'o-',color='#1f567d',lw=1.3,ms=3)
 axes[0].axhline(1,color='gray',ls='--',lw=.8);axes[0].set(xlabel='Axial ray height at vertex plane (cm)',ylabel='Longitudinal focus error (%)')
 for field in fields:
  z=[r for r in rows if r['field_deg']==field];axes[1].plot(apertures,[r['rms_error_percent_EFL'] for r in z],marker='o',ms=2,lw=1,label=str(field)+'°')
 axes[1].axhline(1,color='gray',ls='--',lw=.8);axes[1].set(xlabel='Incident bundle half-width (cm)',ylabel='RMS image error / EFL (%)');axes[1].legend(title='Field angle',frameon=False,fontsize=7)
 for ax in axes:ax.spines[['top','right']].set_visible(False);ax.grid(alpha=.15)
 fig.savefig(ROOT/'validity_figure.png',dpi=300);fig.savefig(ROOT/'validity_figure.pdf')
 print(json.dumps({'q':Q,'efl':EFL,'checks':checks,'axial':axial,'grid_selected':[r for r in rows if r['half_bundle_cm'] in [1,2,4,6] and r['field_deg'] in [0,5,10,15]]},indent=2))
