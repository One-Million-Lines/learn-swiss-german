import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api_shared import vtlog, package_name, config
from api_content import router as content_router
import signal
import sys
import os


app = FastAPI(
    title="Grüezi API",
    description="Swiss German learning platform API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url=None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5306",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5306",
        "onemillionlines.com",
        "www.onemillionlines.com",
        "https://onemillionlines.com",
        "https://www.onemillionlines.com",
        "https://api.onemillionlines.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(content_router)


@app.get("/")
async def root():
    return {"service": package_name, "status": "running"}


@app.get("/health")
async def health():
    return {"status": "ok"}


def exit_handler(sig_num, frame):
    vtlog.info("Stopping application: {0}".format(package_name))
    sys.exit()


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, exit_handler)
    signal.signal(signal.SIGINT, exit_handler)

    port = int(config.get("APP_PORT", "5020"))
    host = config.get("APP_HOST", "0.0.0.0")

    vtlog.info("Starting Grüezi API", port=port, host=host)
    uvicorn.run(app, port=port, host=host, log_level="info")
