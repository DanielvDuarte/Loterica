# -*- coding: utf-8 -*-
"""
Servidor local das Loterias.
Abre a pagina no navegador e deixa o botao "Atualizar" funcionar (ele chama
/atualizar, que baixa os resultados novos pelo Python e recarrega a pagina).
Enquanto esta janela estiver aberta, a pagina funciona. Feche para encerrar.
"""
import json, os, sys, threading, webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import atualizar

try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass

HERE = os.path.dirname(os.path.abspath(__file__))
PORT = 8777

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=HERE, **k)
    def log_message(self, *a):  # silencia o log de cada request
        pass
    def _json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json;charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)
    def end_headers(self):
        # evita cache do html para a pagina recarregar atualizada
        if self.path.split("?")[0].endswith(".html") or self.path in ("/", ""):
            self.send_header("Cache-Control", "no-store")
        super().end_headers()
    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/atualizar":
            print(">> Atualizando a pedido da pagina...")
            try:
                resumo = atualizar.rebuild_all(log=print)
                self._json(200, {"ok": True, "resumo": resumo})
            except Exception as e:
                self._json(500, {"ok": False, "erro": str(e)})
            return
        if path in ("/", ""):
            self.path = "/Loterias.html"
        return super().do_GET()

def main():
    # garante que a pagina existe (gera na 1a vez, sem precisar baixar nada se ja ha cache)
    if not os.path.exists(os.path.join(HERE, "Loterias.html")):
        print("Gerando a pagina pela primeira vez...")
        try: atualizar.rebuild_all(log=print)
        except Exception as e: print("Aviso:", e)
    url = f"http://127.0.0.1:{PORT}/Loterias.html"
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print("="*56)
    print(" Loterias rodando em:", url)
    print(" O botao 'Atualizar' no topo da pagina ja funciona.")
    print(" Mantenha esta janela aberta. Feche-a para encerrar.")
    print("="*56)
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()

if __name__ == "__main__":
    try:
        main()
    except OSError as e:
        print("Nao consegui iniciar o servidor (porta ocupada?).", e)
        input("ENTER para sair...")
