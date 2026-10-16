const fs=require("fs");
const html=fs.readFileSync("C:\\Users\\danie\\MegaSena\\Loterias.html","utf8");
const m=html.match(/<script>([\s\S]*?)<\/script>/);
if(!m){console.log("ERRO: script nao encontrado");process.exit(1);}
function fakeEl(){return {_h:"",style:{},dataset:{},classList:{toggle(){},add(){},remove(){}},
  set innerHTML(v){this._h=v;},get innerHTML(){return this._h;},
  set textContent(v){this._t=v;},get textContent(){return this._t;},
  value:"6",querySelectorAll(){return [];},appendChild(){},click(){},remove(){}};}
const els={};
function gE(id){if(!els[id])els[id]=fakeEl();return els[id];}
global.localStorage={_d:{},getItem(k){return this._d[k]||null;},setItem(k,v){this._d[k]=v;},removeItem(k){delete this._d[k];}};
global.document={getElementById:gE,querySelectorAll:()=>[],
  createElement:()=>fakeEl(),body:{appendChild(){},removeChild(){}}};
global.URL={createObjectURL:()=>"blob:x",revokeObjectURL(){}};
global.Blob=function(){};
let code=m[1];
try{eval(code);}catch(e){console.log("ERRO ao carregar:",e.message);process.exit(1);}
const slugs=["megasena","lotofacil","quina","duplasena","supersete","diadesorte","maismilionaria","timemania","loteca"];
let falhas=0;
for(const s of slugs){
  try{
    selecionar(s);
    const jogos=(els["jogos"]&&els["jogos"]._h)||"";
    const analise=(els["analise"]&&els["analise"]._h)||"";
    const okGen=jogos.length>0&&/class="jogo"/.test(jogos);
    const okAna=analise.length>0&&!/Sem dados/.test(analise);
    // testa cupom: adiciona todos e confere total
    addTodos();
    if(!okGen||!okAna)falhas++;
    console.log(`${s.padEnd(15)} gera:${okGen?'OK':'X'} analise:${okAna?'OK':'X'}`);
  }catch(e){console.log(`${s.padEnd(15)} ERRO: ${e.message}`);falhas++;}
}
try{
  renderCupom();
  const cup=(els["cupom"]&&els["cupom"]._h)||"";
  const temTotal=/Total: R\$/.test(cup);
  const nItens=(cup.match(/class="citem"/g)||[]).length;
  if(!temTotal||!nItens)falhas++;
  console.log(`\ncupom itens=${nItens} total_render:${temTotal?'OK':'X'}`);
  baixar(); // nao deve lancar
  console.log("baixar(): OK");
}catch(e){console.log("cupom ERRO:",e.message);falhas++;}
console.log(falhas===0?"\nTUDO OK":`\n${falhas} FALHA(S)`);
process.exit(falhas?1:0);
