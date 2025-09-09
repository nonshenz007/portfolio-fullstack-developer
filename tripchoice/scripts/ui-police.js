// blocks rogue colors & Tailwind arbitrary hex like text-[#123]
const fs=require('fs'), path=require('path');
const ROOT=process.cwd();
const allowed=['#071C3C','#FDFDF9','#4A5365','#AEB5BC','#ED6B08','#0647AE'];
const rxHex=/#([0-9a-fA-F]{3,8})/g, rxTW=/\[(#?[0-9a-fA-F]{3,8})\]/g;
let bad=[];
function scan(p){if(p.includes('node_modules'))return;
  const s=fs.statSync(p); if(s.isDirectory()) fs.readdirSync(p).forEach(f=>scan(path.join(p,f)));
  else if(/\.(tsx?|jsx?|css|mdx?)$/.test(p)){const t=fs.readFileSync(p,'utf8');
    (t.match(rxHex)||[]).forEach(h=>{const H=h.toUpperCase(); if(!allowed.map(a=>a.toUpperCase()).includes(H)) bad.push([p,h]);});
    (t.match(rxTW)||[]).forEach(m=>bad.push([p,m]));
  }}
scan(path.join(ROOT,'./'));
if(bad.length){console.error('❌ UI-Police: Found rogue colors:\n',
  bad.map(([p,h])=>`- ${p}: ${h}`).join('\n')); process.exit(1);}
console.log('✅ UI-Police: clean.');