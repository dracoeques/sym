import asyncio
import websockets

async def client():
    uri = "ws://localhost:8000/wstest"
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            print(f"< {message}")

asyncio.run(client())
