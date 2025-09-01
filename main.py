from fastapi import FastAPI, APIRouter
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import httpx
import os

from backend.routes.users import router as user_router
from backend.routes.bookings import router as booking_router
from backend.database import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(user_router)
app.include_router(booking_router)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), status_code=200)


@app.get("/landing", response_class=HTMLResponse)
async def landing():
    with open("templates/Augmented-reality-landing.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), status_code=200)


@app.get("/ar", response_class=HTMLResponse)
async def ar():
    with open("templates/Augmented-reality.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), status_code=200)


@app.get("/main", response_class=HTMLResponse)
async def main():
    with open("templates/main.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), status_code=200)


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

@app.get("/proxy/")
async def proxy(url: str):
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
    return Response(r.content, media_type=r.headers.get("content-type", "application/octet-stream"))
