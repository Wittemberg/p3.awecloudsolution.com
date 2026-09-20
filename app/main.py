"""Bootstrap operacional. Nenhum dado de cliente é recebido nesta etapa."""
import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="P3 — Prevenção de Perdas", version="0.1.0", docs_url=None, redoc_url=None)

@app.get("/", response_class=HTMLResponse)
def home():
    return """<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>P3 — Prevenção de Perdas</title><style>
:root{font-family:system-ui,sans-serif;color:#172b3a;background:#f3f6f8}
body{margin:0;padding:clamp(1rem,5vw,4rem)}main{max-width:48rem;margin:auto}
h1{font-size:clamp(2rem,5vw,3rem);overflow-wrap:anywhere}
section{background:white;padding:1.5rem;border-radius:1rem;border:1px solid #ccd8e0}
p{line-height:1.6}a{color:#135b8a}a:focus-visible{outline:3px solid #135b8a}
</style></head><body><main><p>P3 · Prevenção de perdas no varejo</p>
<h1>Evidências para apoiar a auditoria humana</h1><section>
<h2>Projeto em preparação</h2><p>A plataforma está na fase de definição e validação.
A operação com eventos de PDV, vídeos e ocorrências ainda não está disponível.</p>
<p>Este ambiente valida a instalação inicial.</p><a href="/api/health">Consultar disponibilidade</a>
</section></main></body></html>"""

@app.get("/api/hello")
def hello():
    return {"message": "P3 — Prevenção de Perdas"}

@app.get("/api/health")
def health():
    return {"status": "ok", "stage": "bootstrap", "revision": os.getenv("APP_REVISION", "local")}


@app.get('/api/contracts/0.1.0/{document}')
def contract_document(document: str):
    """Read-only artifacts; ingestion remains unimplemented."""
    import json
    from pathlib import Path
    from fastapi import HTTPException

    allowed = {'event.schema.json', 'openapi.json', 'catalog.json', 'examples.json'}
    if document not in allowed:
        raise HTTPException(status_code=404, detail='Contract document not found')
    path = Path(__file__).parent / 'contracts' / 'v0_1_0' / document
    return json.loads(path.read_text())
