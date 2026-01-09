import asyncio
import websockets
import logging
import argparse

async def handler(websocket):
    logging.info(f"Client connected: {websocket.remote_address}")
    try:
        async for message in websocket:
            logging.info(f"Received from {websocket.remote_address}: {message}")
            # Echo back to the client
            await websocket.send(message)
    except websockets.exceptions.ConnectionClosed as e:
        logging.info(f"Client disconnected: {websocket.remote_address} ({e})")
    finally:
        logging.info(f"Connection closed for {websocket.remote_address}")


async def run_server(port, protocol):
    logging.info(f"Starting {protocol} server on 0.0.0.0:{port}")

    ssl_context = None
    if protocol == "wss":
        logging.error("WSS server requires SSL certificates (not implemented in this simplified version).")
        return

    async with websockets.serve(handler, "0.0.0.0", port):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

    parser = argparse.ArgumentParser(description="WebSocket Server (Echo)")
    parser.add_argument("port", type=int, nargs="?", default=1230, help="Port to listen on (default: 1230)")
    parser.add_argument("--protocol", choices=["ws", "wss"], default="ws", help="Protocol (default: ws)")

    args = parser.parse_args()

    try:
        asyncio.run(run_server(args.port, args.protocol))
    except KeyboardInterrupt:
        logging.info("Server stopped.")
