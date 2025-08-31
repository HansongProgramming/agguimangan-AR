from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import httpx
from fastapi import APIRouter
import os

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/landing", response_class=HTMLResponse)
async def landing():
    with open("templates/Augmented-reality-landing.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/ar", response_class=HTMLResponse)
async def ar():
    with open("templates/Augmented-reality.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/main", response_class=HTMLResponse)
async def main():
    with open("templates/main.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

debug = APIRouter()

@debug.get("/debug-static")
def debug_static():
    base = "static/nft"
    return {
        "cwd": os.getcwd(),
        "static_exists": os.path.exists("static"),
        "nft_exists": os.path.exists(base),
        "nft_files": os.listdir(base) if os.path.exists(base) else "none"
    }

app.include_router(debug)
