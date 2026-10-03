const fs=require('fs'),vm=require('vm'),crypto=require('crypto');
const html=fs.readFileSync(__dirname+'/index.html','utf8');
function functions(name){const out=[];for(const m of html.matchAll(new RegExp('function '+name+'\\s*\\(','g'))){let a=html.indexOf('{',m.index),d=1,i=a+1;while(d){if(html[i]==='{')d++;if(html[i]==='}')d--;i++;}out.push(html.slice(m.index,i));}return out;}
const rows=[];
function check(name,got,want){const pass=Number.isFinite(want)?Number.isFinite(got)&&Math.abs(got-want)<=1e-10*Math.max(1,Math.abs(want)):got===want;rows.push({name,got,want,pass});}
for(const name of ['computeSingleLens','computeLens','singleLensCalc','lens'])for(const [i,src] of functions(name).entries()){
 if(name==='computeLens'&&!src.includes('f_eff'))continue;
 const ctx=vm.createContext({Math,Number});vm.runInContext(src,ctx);
 for(const f of [5,15,40,-5,-15,-40])for(const delta of [-.05,0,.05,1e-7,-1e-7,1]){
 const s=f+delta,r=ctx[name](f,s),q=typeof r==='number'?r:(r.s_p??r.sp);
 check(name+'#'+i+': f='+f+',s='+s,q,s===f?Infinity:f*s/(s-f));
 }
}
const calc=functions('calculateImageProperties')[0], classify=functions('classifyImage')[0];
for(const f of [15,-15])for(const s of [14.95,15,15.05,-15,-15.05,-14.95,30]){
 const ctx=vm.createContext({Math,Number,lensType:f>0?'convex':'concave',focalLength:Math.abs(f),objectDistance:s,objectHeight:4.76});vm.runInContext(calc+'\n'+classify,ctx);const r=ctx.calculateImageProperties();check('single main f='+f+',s='+s,r.s_prime,s===f?Infinity:f*s/(s-f));if(s===f)rows.push({name:'infinity classification',pass:ctx.classifyImage(r.s_prime,r.M).nature==='collimated output; no finite image'});
}
const report={method:'Extracted numeric functions and classification; no browser execution.',source_sha256:crypto.createHash('sha256').update(html).digest('hex'),total:rows.length,passed:rows.filter(r=>r.pass).length,failed:rows.filter(r=>!r.pass).length,rows};
fs.writeFileSync(__dirname+'/focal_numeric_results.json',JSON.stringify(report,(_,v)=>typeof v==='number'&&!Number.isFinite(v)?String(v):v,2));console.log({total:report.total,passed:report.passed,failed:report.failed});if(report.failed)process.exitCode=1;
