from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI()

@app.get("/api")
async def hello_world():
    return {"message": "Hello World"}

dist_path = Path(__file__).parent.parent.parent / "frontend" / "dist"
app.mount("/assets", StaticFiles(directory=dist_path / "assets"), name="assets")

@app.get("/")
async def serve_frontend():
    return FileResponse(dist_path / "index.html")
