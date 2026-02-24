import asyncio
import websockets
import logging
import argparse
import ssl
import sys

async def handle_connection(websocket):
    """
    Handles the connection by running both send and receive loops.
    Returns True if the user requested to quit, False otherwise.
    """
    logging.info(f"Connected to {websocket.remote_address}")
    user_quit = False

    async def send_loop():
        nonlocal user_quit
        while True:
            try:
                # Use run_in_executor to avoid blocking the event loop with input()
                # Use sys.stdin.readline for more robust input handling in threads
                line = await asyncio.get_event_loop().run_in_executor(None, lambda: sys.stdin.readline())
                if not line:
                    break
                message = line.strip()
                if message.lower() == 'quit':
                    user_quit = True
                    await websocket.close()
                    break
                if message:
                    await websocket.send(message)
            except Exception as e:
                logging.error(f"Error sending message: {e}")
                break

    async def recv_loop():
        try:
            async for message in websocket:
                logging.info(f"Received from server: {message}")
        except websockets.exceptions.ConnectionClosed:
            logging.info("Connection closed by server")
        except Exception as e:
            logging.error(f"Error receiving message: {e}")

    # Run both loops concurrently
    done, pending = await asyncio.wait(
        [
            asyncio.create_task(send_loop()),
            asyncio.create_task(recv_loop()),
        ],
        return_when=asyncio.FIRST_COMPLETED,
    )

    # Cancel the remaining task
    for task in pending:
        task.cancel()

    return user_quit


async def run_client(url):
    ssl_context = None
    if url.startswith("wss://"):
        # Simple SSL context to match server's style (ignoring verification for flexibility)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

    while True:
        try:
            logging.info(f"Connecting to {url}")
            async with websockets.connect(url, ssl=ssl_context) as websocket:
                if await handle_connection(websocket):
                    logging.info("Exiting as requested by user.")
                    break
        except Exception as e:
            logging.error(f"Connection failed or lost: {e}")

        logging.info("Retrying in 5 seconds...")
        await asyncio.sleep(5)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

    parser = argparse.ArgumentParser(description="WebSocket Client")
    parser.add_argument("url", nargs="?", default="ws://127.0.0.1:1230",
                        help="WebSocket URL (e.g., ws://127.0.0.1:1230 or wss://...)")

    args = parser.parse_args()

    try:
        asyncio.run(run_client(args.url))
    except KeyboardInterrupt:
        logging.info("Client stopped.")
