import logging
import threading
import time
import websocket
import ssl
import argparse

keep_running = True

def on_message(ws, message):
    logging.info(f"Received from server: {message}")


def on_error(ws, error):
    logging.error(f"WebSocket error: {error}")


def on_close(ws, close_status_code, close_msg):
    logging.info(f"Connection closed: {close_status_code} - {close_msg}")


def send_messages_client(ws):
    global keep_running
    while keep_running:
        try:
            msg = input("> ")
            if msg.lower() == 'quit':
                keep_running = False
                ws.close()
                break
            ws.send(msg)
        except (EOFError, KeyboardInterrupt):
            ws.close()
            break
        except Exception as e:
            logging.error(f"Error sending message: {e}")
            break


def on_open(ws):
    logging.info("Connection opened")
    threading.Thread(target=send_messages_client, args=(ws,), daemon=True).start()


def run_client(url):
    logging.info(f"Connecting to {url}")
    protocol = "wss" if url.startswith("wss://") else "ws"

    try:
        while keep_running:
            try:
                ws = websocket.WebSocketApp(url,
                                            on_message=on_message,
                                            on_error=on_error,
                                            on_close=on_close,
                                            on_open=on_open)

                sslopt = {"cert_reqs": ssl.CERT_NONE, "check_hostname": False} if protocol == "wss" else None
                ws.run_forever(ping_interval=10, ping_timeout=2, sslopt=sslopt)

            except Exception as e:
                logging.error(f"Connection failed, retrying in 5s: {e}")
                time.sleep(5)
    except KeyboardInterrupt:
        logging.info("Client stopped.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

    parser = argparse.ArgumentParser(description="WebSocket Client")
    parser.add_argument("url", nargs="?", default="ws://127.0.0.1:1230",
                        help="WebSocket URL (e.g., ws://127.0.0.1:1230 or wss://...)")

    args = parser.parse_args()
    run_client(args.url)
