import asyncio
import websockets
import json

async def connection_handler(websocket, path):
    print("Client connected!")
    try:
        async for message in websocket:
            # Parse the received JSON data
            try:
                data = json.loads(message)
                print("Received JSON data:", data)
                # You can process the data here
            except json.JSONDecodeError:
                print("Received invalid JSON data")
    except websockets.ConnectionClosed:
        print("Client disconnected!")

# Start the server
async def main():
    async with websockets.serve(connection_handler, "localhost", 8765):
        print("WebSocket server running on ws://localhost:8765")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
