const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync(__dirname+'/index.html','utf8');
function extract(n){const start=html.indexOf('function '+n+'(');assert(start>=0,n);let a=html.indexOf('{',start),i=a+1,d=1;while(d){if(html[i]==='{')d++;if(html[i]==='}')d--;i++;}return html.slice(start,i);}
let e,inputs={},queue=[],commits=0,renders=0;
const ctx={Math,Number,JSON,console,clamp:(x,a,b)=>Math.max(a,Math.min(b,x)),num:(x,d)=>Number.isFinite(Number(x))?Number(x):d,
 state:{selected:'L',ambient:1},badge:{},$:()=>({}),byId:()=>e,nameOf:()=> 'Thick lens',fmt:(x,n)=>Number(x).toFixed(n),escapeHtml:x=>String(x),elementPhysicsSummary:()=>'',thickLensEffectiveF:()=>20,
 renderSvg:()=>renders++,commit:()=>commits++,setTimeout:fn=>queue.push(fn),syncGlobalUI:()=>{}};
ctx.inspector={set innerHTML(s){this.html=s;inputs={};for(const m of s.matchAll(/<input ([^>]+)>/g)){const tag=m[1];const key=tag.match(/data-v21-prop="([^"]+)"/)[1];inputs[key]={dataset:{v21Prop:key},type:tag.match(/type="([^"]+)"/)[1],value:tag.match(/value="([^"]*)"/)[1],readonly:tag.includes(' readonly'),events:{},addEventListener(k,f){this.events[k]=f},blur(){this.blurred=true;}};}},get innerHTML(){return this.html},querySelectorAll(){return Object.values(inputs).filter(x=>!x.readonly)}};
vm.createContext(ctx);vm.runInContext(extract('sanitize')+'\n'+extract('renderInspector'),ctx);
const results=[];function test(name,f){f();results.push({name,pass:true});}
function fresh(){e={id:'L',type:'thickLens',x:60,y:0,width:5,n:1.52,R1:28,R2:-28,aperture:24,angle:0};ctx.sanitize(e);ctx.renderInspector();}
function edit(k,value){const i=inputs[k];i.value=String(value);i.events.input();i.events.change();while(queue.length)queue.shift()();}
fresh();
test('Legacy aperture initializes requested value',()=>assert.equal(e.requestedAperture,24));
test('Intermediate radius typing leaves model untouched',()=>{inputs.R1.value='2';inputs.R1.events.input();assert.equal(e.R1,28);assert.equal(e.aperture,24);inputs.R1.value='20';inputs.R1.events.input();assert.equal(e.R1,28);});
test('Completed radius applies once without shrinking aperture',()=>{inputs.R1.events.change();while(queue.length)queue.shift()();assert.equal(e.R1,20);assert.equal(e.aperture,24);assert.equal(commits,1);});
test('Smaller radius constrains applied aperture but retains request',()=>{edit('R1',10);assert.equal(e.aperture,18.2);assert.equal(e.requestedAperture,24);assert.equal(Number(inputs.requestedAperture.value),24);assert.equal(Number(inputs.__usedAperture.value),18.2);assert(ctx.inspector.innerHTML.includes('limited by the surface radii'));});
test('Increasing radius restores requested aperture',()=>{edit('R1',30);assert.equal(e.aperture,24);});
test('Second surface and sign change retain requested aperture',()=>{edit('R2',-8);assert(Math.abs(e.aperture-14.56)<1e-12);edit('R2',30);assert.equal(e.aperture,24);});
test('Explicit new aperture replaces old request',()=>{edit('requestedAperture',16);edit('R1',6);edit('R1',30);assert.equal(e.aperture,16);assert.equal(e.requestedAperture,16);});
test('JSON persistence retains constrained request and restores it',()=>{edit('R1',6);e=JSON.parse(JSON.stringify(e));ctx.sanitize(e);assert.equal(e.requestedAperture,16);e.R1=30;ctx.sanitize(e);assert.equal(e.aperture,16);});
test('Final geometry is independent of input order',()=>{const a={...e,aperture:24,requestedAperture:24,R1:28,R2:-28};a.R1=3;ctx.sanitize(a);a.R2=-20;ctx.sanitize(a);a.R1=20;ctx.sanitize(a);const b={...a,aperture:24,requestedAperture:24};ctx.sanitize(b);assert.equal(a.aperture,b.aperture);assert.equal(a.aperture,24);});
test('Empty input preserves prior model',()=>{ctx.renderInspector();edit('R1','');assert.equal(e.R1,30);});
test('Enter ends editing through blur',()=>{let prevented=false;inputs.R1.events.keydown({key:'Enter',preventDefault(){prevented=true}});assert(prevented&&inputs.R1.blurred);});
test('Aperture is placed after both radii',()=>{const keys=Object.keys(inputs);assert(keys.indexOf('requestedAperture')>keys.indexOf('R2'));});
let scripts=0;for(const m of html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)){if(m[1].trim()){new vm.Script(m[1]);scripts++;}}
fs.writeFileSync(__dirname+'/aperture_test_results.json',JSON.stringify({scope:'Extracted application functions and input-event handlers with stub DOM; not browser rendering',passed:results.length,inline_scripts_parsed:scripts,results},null,2));console.log(results.length+' aperture checks passed; '+scripts+' inline scripts parsed.');
