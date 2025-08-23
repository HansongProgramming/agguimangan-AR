from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import httpx

app = FastAPI()

DROPBOX_URL = "https://dl.dropboxusercontent.com/scl/fi/2tvf3vofrpf56s4xkc1b4/hostel.mp4?raw=1"

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/video")
async def proxy_video():
    async with httpx.AsyncClient() as client:
        r = await client.stream("GET", DROPBOX_URL)
        return StreamingResponse(
            r.aiter_bytes(),
            media_type="video/mp4",
            headers={"Access-Control-Allow-Origin": "*"}
        )
