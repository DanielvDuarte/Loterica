# -*- coding: utf-8 -*-
import io, json, os
HERE = r"C:\Users\danie\MegaSena"
GAMES = ["megasena","lotofacil","quina","duplasena","supersete",
         "diadesorte","maismilionaria","timemania","loteca"]
data = {}
for g in GAMES:
    data[g] = json.load(open(os.path.join(HERE, g+".json"), encoding="utf-8"))
tpl = io.open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
assert "__DATA_JSON__" in tpl
data_js = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
html = tpl.replace("__DATA_JSON__", data_js)

desk = os.path.join(os.path.expanduser("~"), "OneDrive", "\u00c1rea de Trabalho")
out = os.path.join(desk, "Loterias.html")
io.open(out, "w", encoding="utf-8").write(html)
io.open(os.path.join(HERE, "Loterias.html"), "w", encoding="utf-8").write(html)
print("OK", out)
print("tamanho_kb", round(len(html.encode("utf-8"))/1024, 1))
for g in GAMES:
    print(f"  {g:16} {len(data[g]):>5} concursos")
