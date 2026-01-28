import asyncio
import websockets

async def test():
    uri = "ws://localhost:8000/ws"
    try:
        async with websockets.connect(uri) as ws:
            print("Connected to WS")
            while True:
                msg = await ws.recv()
                print("\nReceived:", msg[:200] + "..." if len(msg) > 200 else msg)
    except websockets.exceptions.ConnectionClosed as e:
        print(f"Connection closed: {e.code} {e.reason or '(no reason)'}")
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(test())