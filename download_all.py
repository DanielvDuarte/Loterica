# -*- coding: utf-8 -*-
"""Baixa o historico completo de cada loteria e salva um cache json por jogo."""
import json, os, ssl, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "https://servicebus2.caixa.gov.br/portaldeloterias/api/"
CTX = ssl.create_default_context()
HDRS = {"User-Agent": "Mozilla/5.0 (analise estatistica pessoal)"}

# slug -> arquivo de cache. megasena ja existe (megasena_data.json)
GAMES = ["lotofacil","quina","duplasena","supersete",
         "diadesorte","maismilionaria","timemania","loteca"]
MESES = {m:i+1 for i,m in enumerate(
  ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho",
   "Agosto","Setembro","Outubro","Novembro","Dezembro"])}

def fetch(slug, n, retries=4):
    url = BASE+slug if n is None else f"{BASE}{slug}/{n}"
    for a in range(retries):
        try:
            req = urllib.request.Request(url, headers=HDRS)
            with urllib.request.urlopen(req, timeout=30, context=CTX) as r:
                return json.load(r)
        except Exception:
            time.sleep(0.5*(a+1))
    return None

def extract(slug, d):
    if not d: return None
    num = d.get("numero")
    if num is None: return None
    num = int(num); data = d.get("dataApuracao","")
    if slug == "loteca":
        res=[]
        for m in (d.get("listaResultadoEquipeEsportiva") or []):
            g1,g2 = m.get("nuGolEquipeUm"), m.get("nuGolEquipeDois")
            if g1 is None or g2 is None: res.append("?")
            elif g1>g2: res.append("1")
            elif g1<g2: res.append("2")
            else: res.append("X")
        if not res: return None
        return [num, data, "".join(res)]
    dez = d.get("listaDezenas") or []
    try: dez = [int(x) for x in dez]
    except Exception: return None
    if not dez: return None
    if slug == "supersete":
        return [num, data, *dez]                       # 7 digitos 0-9, ordem das colunas
    if slug == "duplasena":
        d2 = [int(x) for x in (d.get("listaDezenasSegundoSorteio") or [])]
        return [num, data, *sorted(dez), *sorted(d2)]  # 6 + 6
    if slug == "maismilionaria":
        tr = [int(x) for x in (d.get("trevosSorteados") or [])]
        return [num, data, *sorted(dez), *sorted(tr)]  # 6 + 2 trevos
    if slug == "diadesorte":
        mes = MESES.get((d.get("nomeTimeCoracaoMesSorte") or "").strip(), 0)
        return [num, data, *sorted(dez), mes]          # 7 + mes(1-12)
    return [num, data, *sorted(dez)]                   # lotofacil, quina, timemania

def build(slug):
    cache = os.path.join(HERE, slug+".json")
    have = {}
    if os.path.exists(cache):
        try:
            for row in json.load(open(cache, encoding="utf-8")):
                have[row[0]] = row
        except Exception: have = {}
    latest = extract(slug, fetch(slug, None))
    if latest is None:
        print(f"[{slug}] ERRO ao obter ultimo concurso"); return
    last = latest[0]; have[last] = latest
    missing = [n for n in range(1, last+1) if n not in have]
    print(f"[{slug}] ultimo={last} baixar={len(missing)} cache={len(have)-1}", flush=True)
    if missing:
        done=0
        with ThreadPoolExecutor(max_workers=12) as ex:
            futs={ex.submit(lambda n=n: extract(slug, fetch(slug,n))):n for n in missing}
            for f in as_completed(futs):
                r=f.result()
                if r: have[r[0]]=r
                done+=1
                if done%300==0: print(f"  [{slug}] {done}/{len(missing)}", flush=True)
        faltam=[n for n in range(1,last+1) if n not in have]
        for n in faltam:
            r=extract(slug, fetch(slug,n))
            if r: have[n]=r
    rows=[have[k] for k in sorted(have)]
    json.dump(rows, open(cache,"w",encoding="utf-8"), ensure_ascii=False, separators=(",",":"))
    faltam=[n for n in range(1,last+1) if n not in have]
    print(f"[{slug}] OK total={len(rows)} faltaram={len(faltam)}", flush=True)

if __name__ == "__main__":
    only = sys.argv[1:] or GAMES
    for g in only:
        build(g)
    print("TUDO PRONTO", flush=True)
