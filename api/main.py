from fastapi import FastAPI

app = FastAPI(title="Reddit Signed Network Miner API")


@app.get("/health")
async def health():
    return {"status": "ok"}
