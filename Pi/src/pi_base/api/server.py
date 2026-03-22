from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect

from ..bridge_app import BridgeApp


def create_http_app(bridge: BridgeApp) -> FastAPI:
    app = FastAPI(title="pi-bridge-base", version="0.1.0")

    @app.get("/health")
    async def health() -> dict:
        await bridge.mark_http_get("/health")
        return {
            "status": "ok",
            "uart_connected": bridge.uart.is_connected,
            "ws_connected": bridge.remote_ws.is_connected,
        }

    @app.get("/state")
    async def state() -> dict:
        await bridge.mark_http_get("/state")
        return await bridge.snapshot()

    @app.get("/mcu/send")
    async def mcu_send(data: str) -> dict:
        await bridge.mark_http_get("/mcu/send")
        try:
            return await bridge.send_to_mcu(data)
        except Exception as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    @app.get("/ws/send")
    async def ws_send(data: str) -> dict:
        await bridge.mark_http_get("/ws/send")
        try:
            return await bridge.send_to_remote_ws(data)
        except Exception as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    @app.websocket("/ws/local")
    async def ws_local(websocket: WebSocket) -> None:
        await bridge.local_ws_hub.connect(websocket)
        try:
            await websocket.send_json({"event": "connected", "scope": "local-monitor"})
            while True:
                # Keep socket open and allow user messages for future commands.
                _ = await websocket.receive_text()
        except WebSocketDisconnect:
            pass
        finally:
            await bridge.local_ws_hub.disconnect(websocket)

    return app
