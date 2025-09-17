# server/app/main.py
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from .pipelines.registry import PIPELINE_MANAGER

app = FastAPI(title="AI Backend")

BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = next((p for p in [BASE_DIR / "web", Path("/app/app/web")] if p.exists()), BASE_DIR / "web")

# 정적 폴더는 /static 으로 마운트 (충돌 방지)
app.mount("/static", StaticFiles(directory=str(WEB_DIR), html=False), name="static")

@app.get("/")
def root():
    return HTMLResponse('<a href="/web">Open Viewer</a>')

# 뷰어를 명시적으로 파일로 서빙 (index.html)
@app.get("/web")
@app.get("/web/index.html")
def web_index():
    return FileResponse(WEB_DIR / "index.html")

@app.get("/healthz")
def health():
    return {"ok": True}

@app.post("/pipelines/start")
def start_pipelines():
    PIPELINE_MANAGER.start()
    return {"status": "started"}

@app.post("/pipelines/stop")
def stop_pipelines():
    PIPELINE_MANAGER.stop()
    return {"status": "stopped"}

@app.get("/pipelines/status")
def status():
    return PIPELINE_MANAGER.status()
