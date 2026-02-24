import asyncio
import websockets
import logging
import argparse
import ssl
import os
import tempfile
import sys
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.primitives import serialization

# Keep track of connected clients
connected_clients = set()

async def handler(websocket):
    logging.info(f"Client connected: {websocket.remote_address}")
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            logging.info(f"Received from {websocket.remote_address}: {message}")
            # Echo back to the client
            await websocket.send(message)
    except websockets.exceptions.ConnectionClosed as e:
        logging.info(f"Client disconnected: {websocket.remote_address} ({e})")
    finally:
        connected_clients.remove(websocket)
        logging.info(f"Connection closed for {websocket.remote_address}")


async def cli_input_handler():
    """Reads input from the server's command line and broadcasts it to all clients."""
    loop = asyncio.get_event_loop()
    print("Type messages to broadcast them to all connected clients.")
    while True:
        try:
            # sys.stdin.readline is used to avoid issues on Windows in threads
            line = await loop.run_in_executor(None, sys.stdin.readline)
            if not line:
                break
            message = line.strip()
            if message:
                if connected_clients:
                    logging.info(f"Broadcasting message: {message}")
                    # Send to all connected clients
                    if connected_clients:
                        # Using gather to send concurrently to all clients
                        await asyncio.gather(
                            *[client.send(message) for client in connected_clients],
                            return_exceptions=True
                        )
                else:
                    logging.warning("No clients connected. Message not sent.")
        except Exception as e:
            logging.error(f"Error in CLI input handler: {e}")
            await asyncio.sleep(1)


async def run_server(port, protocol, certfile=None, keyfile=None, password=None):
    logging.info(f"Starting {protocol} server on 0.0.0.0:{port}")

    ssl_context = None
    if protocol == "wss":
        if certfile:
            ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

            # Check if it's a P12 file
            if certfile.lower().endswith(('.p12', '.pfx')):
                logging.info(f"Loading PKCS#12 certificate from {certfile}")
                with open(certfile, "rb") as f:
                    p12_data = f.read()

                logging.info(f"PKCS#12 data length: {len(p12_data)}")

                # Parse PKCS12
                p12_password = password.encode() if password else None
                p12 = pkcs12.load_pkcs12(p12_data, p12_password)
                private_key = p12.key
                # In newer cryptography versions, p12.cert and members of p12.additional_certs
                # are PKCS12Certificate objects, which wrap the actual x509 Certificate.
                certificate = p12.cert.certificate if p12.cert else None
                additional_certificates = [c.certificate for c in p12.additional_certs] if p12.additional_certs else []

                if not private_key or not certificate:
                    logging.error("PKCS12 file must contain both a private key and a certificate.")
                    return

                # Convert to PEM format for ssl_context.load_cert_chain compatibility (or use temp files)
                # Alternatively, use a temporary file approach to avoid complex memory-to-SSLContext logic
                with tempfile.NamedTemporaryFile(delete=False) as cert_tmp, \
                     tempfile.NamedTemporaryFile(delete=False) as key_tmp:

                    cert_tmp.write(certificate.public_bytes(serialization.Encoding.PEM))
                    cert_tmp.flush()
                    key_tmp.write(private_key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.TraditionalOpenSSL,
                        encryption_algorithm=serialization.NoEncryption()
                    ))
                    key_tmp.flush()

                    try:
                        ssl_context.load_cert_chain(certfile=cert_tmp.name, keyfile=key_tmp.name)
                    finally:
                        cert_tmp.close()
                        key_tmp.close()
                        os.unlink(cert_tmp.name)
                        os.unlink(key_tmp.name)
            else:
                if keyfile or password:
                    ssl_context.load_cert_chain(certfile=certfile, keyfile=keyfile, password=password)
                else:
                    logging.error("WSS server requires keyfile for PEM certificates.")
                    return
        else:
            logging.error("WSS server requires SSL certificates (--cert).")
            return

    async with websockets.serve(handler, "0.0.0.0", port, ssl=ssl_context):
        # Start the CLI input handler task
        input_task = asyncio.create_task(cli_input_handler())
        try:
            await asyncio.Future()  # run forever
        finally:
            input_task.cancel()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

    parser = argparse.ArgumentParser(description="WebSocket Server (Echo)")
    parser.add_argument("port", type=int, nargs="?", default=1230, help="Port to listen on (default: 1230)")
    parser.add_argument("--protocol", choices=["ws", "wss"], default="ws", help="Protocol (default: ws)")
    parser.add_argument("--cert", help="Path to the SSL certificate file (PEM or P12/PFX format)")
    parser.add_argument("--key", help="Path to the SSL private key file (PEM format, not needed for P12)")
    parser.add_argument("--password", help="Password for the SSL private key or P12 file")

    args = parser.parse_args()

    try:
        asyncio.run(run_server(args.port, args.protocol, args.cert, args.key, args.password))
    except KeyboardInterrupt:
        logging.info("Server stopped.")
