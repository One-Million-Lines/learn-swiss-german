"""SwissSpeak API entry point.

Runs the HTTP API (app.main:app). An in-process audio worker starts with the
app for local development (set RUN_INPROCESS_WORKER=0 to disable); in production
run `python -m scripts.worker` as a separate process.
"""
import signal
import sys

import uvicorn

from app.config import get_settings


def main() -> None:
    settings = get_settings()

    def exit_handler(sig_num, frame):
        sys.exit()

    signal.signal(signal.SIGTERM, exit_handler)
    signal.signal(signal.SIGINT, exit_handler)

    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
