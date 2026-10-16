# -*- coding: utf-8 -*-
"""
Atualizador das Loterias.
Baixa apenas os concursos novos de cada jogo (cache incremental),
reconstroi a pagina Loterias.html e salva na Area de Trabalho.
Rode pelo atalho "Atualizar Loterias".
"""
import io, json, os, ssl, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "template.html")
BASE = "https://servicebus2.caixa.gov.br/portaldeloterias/api/"
CTX = ssl.create_default_context()
HDRS = {"User-Agent": "Mozilla/5.0 (analise estatistica pessoal)"}

GAMES = ["megasena","lotofacil","quina","duplasena","supersete",
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
        return [num, data, "".join(res)] if res else None
    dez = d.get("listaDezenas") or []
    try: dez = [int(x) for x in dez]
    except Exception: return None
    if not dez: return None
    if slug == "supersete":   return [num, data, *dez]
    if slug == "duplasena":
        d2=[int(x) for x in (d.get("listaDezenasSegundoSorteio") or [])]
        return [num, data, *sorted(dez), *sorted(d2)]
    if slug == "maismilionaria":
        tr=[int(x) for x in (d.get("trevosSorteados") or [])]
        return [num, data, *sorted(dez), *sorted(tr)]
    if slug == "diadesorte":
        mes=MESES.get((d.get("nomeTimeCoracaoMesSorte") or "").strip(),0)
        return [num, data, *sorted(dez), mes]
    return [num, data, *sorted(dez)]

def build(slug):
    cache = os.path.join(HERE, slug+".json")
    have = {}
    if os.path.exists(cache):
        try:
            for row in json.load(open(cache, encoding="utf-8")): have[row[0]] = row
        except Exception: have = {}
    latest = extract(slug, fetch(slug, None))
    if latest is None:
        print(f"[{slug}] sem conexao, mantendo cache ({len(have)})"); 
        return [have[k] for k in sorted(have)]
    last = latest[0]; have[last]=latest
    missing = [n for n in range(1, last+1) if n not in have]
    if missing:
        print(f"[{slug}] baixando {len(missing)} novo(s)...", flush=True)
        with ThreadPoolExecutor(max_workers=12) as ex:
            futs={ex.submit(lambda n=n: extract(slug, fetch(slug,n))):n for n in missing}
            for f in as_completed(futs):
                r=f.result()
                if r: have[r[0]]=r
        for n in [n for n in range(1,last+1) if n not in have]:
            r=extract(slug, fetch(slug,n))
            if r: have[n]=r
    rows=[have[k] for k in sorted(have)]
    json.dump(rows, open(cache,"w",encoding="utf-8"), ensure_ascii=False, separators=(",",":"))
    print(f"[{slug}] ok ({len(rows)} concursos, ate o {last})", flush=True)
    return rows

def desktop_dir():
    home=os.path.expanduser("~")
    for p in [os.path.join(home,"OneDrive","Área de Trabalho"),
              os.path.join(home,"OneDrive","Desktop"),
              os.path.join(home,"Área de Trabalho"),
              os.path.join(home,"Desktop")]:
        if os.path.isdir(p): return p
    return home

def main():
    print("Atualizando loterias (so os concursos novos)...\n")
    data={}
    for g in GAMES:
        data[g]=build(g)
    tpl=io.open(TEMPLATE, encoding="utf-8").read()
    data_js=json.dumps(data, ensure_ascii=False, separators=(",",":"))
    html=tpl.replace("__DATA_JSON__", data_js)
    out=os.path.join(desktop_dir(), "Loterias.html")
    io.open(out,"w",encoding="utf-8").write(html)
    io.open(os.path.join(HERE,"Loterias.html"),"w",encoding="utf-8").write(html)
    print(f"\nPronto! Pagina atualizada em:\n{out}")
    return 0

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("ERRO:", e)
    input("\nPressione ENTER para fechar...")
