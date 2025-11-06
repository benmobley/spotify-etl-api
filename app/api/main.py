from fastapi import FastAPI
from . import tracks

app = FastAPI()
app.include_router(tracks.router, prefix="/api")

@app.get("/health")
def health():
    return {"ok": True}
