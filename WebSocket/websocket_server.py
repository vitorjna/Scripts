import asyncio
import websockets
import logging
import argparse
import ssl

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


async def run_server(port, protocol, certfile=None, keyfile=None):
    logging.info(f"Starting {protocol} server on 0.0.0.0:{port}")

    ssl_context = None
    if protocol == "wss":
        if certfile and keyfile:
            # Create a default SSL context for server use
            ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_context.load_cert_chain(certfile=certfile, keyfile=keyfile)
        else:
            logging.error("WSS server requires SSL certificates (--cert and --key).")
            return

    async with websockets.serve(handler, "0.0.0.0", port, ssl=ssl_context):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

    parser = argparse.ArgumentParser(description="WebSocket Server (Echo)")
    parser.add_argument("port", type=int, nargs="?", default=1230, help="Port to listen on (default: 1230)")
    parser.add_argument("--protocol", choices=["ws", "wss"], default="ws", help="Protocol (default: ws)")
    parser.add_argument("--cert", help="Path to the SSL certificate file (PEM format)")
    parser.add_argument("--key", help="Path to the SSL private key file (PEM format)")

    args = parser.parse_args()

    try:
        asyncio.run(run_server(args.port, args.protocol, args.cert, args.key))
    except KeyboardInterrupt:
        logging.info("Server stopped.")
