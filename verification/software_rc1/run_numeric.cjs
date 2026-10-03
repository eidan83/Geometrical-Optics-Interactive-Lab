const fs=require('fs'),vm=require('vm'),crypto=require('crypto'),path=require('path');
const input=process.argv[2]||path.join(__dirname,'index.html');
const html=fs.readFileSync(input,'utf8');
function extract(name,occ=0){let re=new RegExp('function '+name+'\\s*\\(','g'),m;for(let i=0;i<=occ;i++){m=re.exec(html);if(!m)throw Error(name)}if(occ<0){const all=[...html.matchAll(re)];m=all[all.length-1];}let a=html.indexOf('{',m.index),depth=1,j=a+1;for(;depth&&j<html.length;j++){if(html[j]==='{')depth++;if(html[j]==='}')depth--;}return html.slice(m.index,j);}
function load(names,pre=''){const ctx=vm.createContext({Math,Number});vm.runInContext(pre+'\n'+names.map(x=>extract(...(Array.isArray(x)?x:[x]))).join('\n'),ctx);return ctx;}
const lens=load(['computeSingleLens']);
const thick=load(['invRadius','compute']);
const trig='const sinD=x=>Math.sin(x*Math.PI/180), cosD=x=>Math.cos(x*Math.PI/180), asinD=x=>Math.asin(Math.max(-1,Math.min(1,x)))*180/Math.PI;';
const prism=load([['calculate',0]],trig),slab=load([['calculate',1]],trig);
const vector=load(['sub','mul','dot','len','norm','add','reflect','refract'].map(n=>[n,-1]));
let rows=[];
function check(group,id,got,want,tol=1e-9){let ok=typeof want==='boolean'?got===want:(!Number.isFinite(want)?got===want: Number.isFinite(got)&&Math.abs(got-want)<=tol*Math.max(1,Math.abs(want)));rows.push({group,id,got,want,tolerance:tol,pass:ok});}
// Independent rational conjugate reference, without the application's clamps.
for(const f of [15,-15])for(const s of [-50,-20,-10,10,20,30,50]){let q=f*s/(s-f);let r=lens.computeSingleLens(f,s);check('thin ordinary',`f=${f},s=${s}:q`,r.s_p,q);check('thin ordinary',`f=${f},s=${s}:M`,r.M,-q/s);}
for(const f of [15,-15])for(const delta of [-.2,-.05,0,.05,.2]){const s=f+delta,r=lens.computeSingleLens(f,s);let expected=delta===0?Infinity:f*s/delta;check('thin focal boundary',`f=${f},s=${s}:q`,r.s_p,expected);}
function mm(a,b){return [[a[0][0]*b[0][0]+a[0][1]*b[1][0],a[0][0]*b[0][1]+a[0][1]*b[1][1]],[a[1][0]*b[0][0]+a[1][1]*b[1][0],a[1][0]*b[0][1]+a[1][1]*b[1][1]]];}
for(const radii of [[20,-20],[-20,20],[0,-20],[20,0]])for(const s of [-30,10,45]){
 let p={n0:1,n:1.52,R1:radii[0],R2:radii[1],t:4,s,y:6},r=thick.compute(p);
 let surf=(n1,n2,R)=>[[1,0],[R===0?0:-(n2-n1)/R,1]];
 let M=mm(surf(p.n,p.n0,p.R2),mm([[1,p.t/p.n],[0,1]],surf(p.n0,p.n,p.R1)));
 ['A','B','C','D'].forEach((k,i)=>check('thick matrix',JSON.stringify(p)+':'+k,r[k],M[Math.floor(i/2)][i%2]));
 // Trace two independent paraxial rays from same object to infer image intersection.
 let ray=v=>[M[0][0]*v[0]+M[0][1]*v[1],M[1][0]*v[0]+M[1][1]*v[1]];
 let a=ray([0,-p.n0*p.y/p.s]),b=ray([p.y,0]);let q=p.n0*(b[0]-a[0])/(a[1]-b[1]);let yi=a[0]+q*a[1]/p.n0;
 check('thick conjugate',JSON.stringify(p)+':q',r.q,q);check('thick conjugate',JSON.stringify(p)+':M',r.m,yi/p.y);check('thick determinant',JSON.stringify(p),r.determinant,1);
}
for(const i of [0,30,45,70,85]){let p={t:8,n:1.5,n0:1,i},r=slab.calculate(p),theta=Math.asin(Math.sin(i*Math.PI/180)/1.5);check('slab',`i=${i}:r`,r.r,theta*180/Math.PI);check('slab',`i=${i}:shift`,r.d,8*Math.sin(i*Math.PI/180-theta)/Math.cos(theta));check('slab',`i=${i}:OPL`,r.opl,12/Math.cos(theta));}
let critical=Math.asin(1/1.5)*180/Math.PI;for(const delta of [-.001,.001])check('slab critical',`critical+${delta}`,slab.calculate({t:8,n:1,n0:1.5,i:critical+delta}).tir,delta>0);
let imin=Math.asin(.75)*180/Math.PI,r=prism.calculate({A:60,n:1.5,n0:1,i:imin});check('prism minimum','r1',r.r1,30);check('prism minimum','r2',r.r2,30);check('prism minimum','deviation',r.delta,2*imin-60);
for(const i of [0,30,70,85]){let a=i*Math.PI/180,r=vector.refract({x:Math.cos(a),y:Math.sin(a)},{x:-1,y:0},1,1.5);check('vector Snell',`i=${i}:sin(r)`,r.dir.y,Math.sin(a)/1.5);check('vector Snell',`i=${i}:unit`,Math.hypot(r.dir.x,r.dir.y),1);}
for(const delta of [-.001,.001]){let a=(critical+delta)*Math.PI/180;check('vector TIR',`critical+${delta}`,vector.refract({x:Math.cos(a),y:Math.sin(a)},{x:-1,y:0},1.5,1).tir,delta>0);}

const benchNames=['num','clamp','rad','deg','add','sub','mul','dot','cross','len','norm','perp','unit','rotate','uid','isSource','nameOf','prismHeightFromApex','defaultElement','lineEnds','lensEnds','detectorActiveEnds','polygon','mirrorPoints','raySegment','boardExit','reflect','refract','candidateLine','nearestInteraction','sourceRays','traceAll'];
const bench=load(benchNames.map(n=>[n,-1]),'var serial=1, WORLD={w:120,h:60,cy:30}, EPS=.025, MAX_STEPS=42;var state={elements:[],ambient:1,rayLimit:14,showNormals:false};');
function e(type,x,y){return bench.defaultElement(type,x,y);}
// Reconstruct the supplied camera geometry; tests are numerical, without UI execution.
let source=e('pointSource',10,6),stop=e('aperture',47,0),L=e('convexLens',55,0),screen=e('screen',85,0);
Object.assign(source,{spread:22,rays:14});Object.assign(stop,{opening:10,length:56});Object.assign(L,{f:18,aperture:28});screen.length=38;
bench.state.elements=[source,stop,L,screen];let camera=bench.traceAll();
check('bench baseline','camera rays',camera.paths.length,14);check('bench baseline','camera interactions',camera.interactions,26);check('bench baseline','camera screen hits',camera.hits.length,6);
source=e('parallelSource',8,0);Object.assign(source,{width:18,rays:14,power:1});L=e('convexLens',52,0);Object.assign(L,{f:18,aperture:25});let detector=e('photodetector',70,0);Object.assign(detector,{activeLength:2.5,efficiency:1});bench.state.elements=[source,L,detector];let focus=bench.traceAll().detectorReadings[detector.id];
check('bench baseline','focus detector power',focus.power,1);check('bench baseline','focus detector relative',focus.relative,100);check('bench baseline','focus detector signal',focus.focus,100);
source=e('parallelSource',8,0);Object.assign(source,{width:10,rays:11,power:1});stop=e('aperture',40,0);Object.assign(stop,{opening:4,length:30});detector=e('photodetector',80,0);Object.assign(detector,{activeLength:20,length:24,efficiency:.8});bench.state.elements=[source,stop,detector];let clip=bench.traceAll().detectorReadings[detector.id];
check('bench aperture','five of eleven rays',clip.hits,5);check('bench aperture','power incl efficiency',clip.power,5*.8/11);
source=e('parallelSource',8,0);Object.assign(source,{width:0,rays:1,power:1});let slabEl=e('slab',40,0);Object.assign(slabEl,{width:10,height:40,n:1.5});let mirror=e('planeMirror',70,0);Object.assign(mirror,{angle:45,length:20});screen=e('screen',70,20);Object.assign(screen,{angle:0,length:20});bench.state.elements=[source,slabEl,mirror,screen];let mixed=bench.traceAll();
check('bench mixed noncoaxial','one hit',mixed.hits.length,1);check('bench mixed noncoaxial','two refractions reflection screen',mixed.interactions,4);check('bench mixed noncoaxial','screen hit x',mixed.hits[0].p.x,70);check('bench mixed noncoaxial','screen hit y',mixed.hits[0].p.y,20);
const output={source_sha256:crypto.createHash('sha256').update(html).digest('hex'),method:'Execute unmodified function text extracted from supplied HTML in Node VM. No browser, DOM, UI, or original 13-test suite execution.',counts:{total:rows.length,passed:rows.filter(x=>x.pass).length,failed:rows.filter(x=>!x.pass).length},rows};
const json=JSON.stringify(output,(_,v)=>typeof v==='number'&&!Number.isFinite(v)?String(v):v,2);fs.writeFileSync(path.join(__dirname,'numeric_results.json'),json);console.log(JSON.stringify(output.counts));console.log(JSON.stringify(rows.filter(x=>!x.pass),(_,v)=>typeof v==='number'&&!Number.isFinite(v)?String(v):v,2));
