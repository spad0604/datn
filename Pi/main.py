import asyncio
import logging
import os

from uvicorn import Config, Server

from src.pi_base.api.server import create_http_app
from src.pi_base.bridge_app import BridgeApp
from src.pi_base.config import Settings


def _load_dotenv(dotenv_path: str = ".env") -> None:
    if not os.path.exists(dotenv_path):
        return

    with open(dotenv_path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


async def run() -> None:
    _load_dotenv()
    settings = Settings.from_env()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    bridge = BridgeApp(settings)
    app = create_http_app(bridge)

    config = Config(
        app=app,
        host=settings.http_host,
        port=settings.http_port,
        log_level="info",
    )
    server = Server(config)

    async with bridge:
        await server.serve()


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass
