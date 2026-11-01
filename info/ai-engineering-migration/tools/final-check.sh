#!/usr/bin/env bash
# Verifies every original page against the assembled content (no 'skipped' lists counted).
S="/c/Users/balaj/AppData/Local/Temp/claude/C--Users-balaj-Documents-scaler-education-journey/71ef8431-9172-4ca6-ba7c-fbb548e18ca4/scratchpad/conv"
cd "$S" && node -e '
const fs=require("fs"),path=require("path");const out=[];
const walk=d=>fs.readdirSync(d,{withFileTypes:true}).forEach(e=>{const p=path.join(d,e.name);if(e.isDirectory())walk(p);else{const t=fs.readFileSync(p,"utf8");if(p.endsWith(".json")){const w=(v,k)=>{if(typeof v==="string")out.push(k==="svg"?v.replace(/<[^>]+>/g," "):v);else if(v&&typeof v==="object")Object.entries(v).forEach(([a,b])=>w(b,a));};w(JSON.parse(t));}else out.push(t);}});
walk(process.argv[1]);fs.writeFileSync("corpus.txt",out.join("\n"));' "${1:-$S/assembled}"
cd /c/Users/balaj/Documents/balajiraghuram.github.io
for f in $(find . -name '*.html' -not -path './.git/*' | sed 's|^\./||' | sort); do
  k=$(echo $f | sed 's|/index.html||; s|\.html||; s|/|-|g' | tr A-Z a-z)
  VERBOSE=1 node "$S/verify.mjs" . "$f" "$S/corpus.txt" > "$S/out/$k.final.txt"
  head -1 "$S/out/$k.final.txt"
done
