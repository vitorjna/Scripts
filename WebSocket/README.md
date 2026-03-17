# WebSocket Client and Server

These scripts provide a simple way to interact with WebSocket servers and run a basic echo server for testing and development purposes.

## Features

### Client (`websocket_client.py`)
- **Simple Connection**: Connect to any WebSocket server using a single URL argument (e.g., `ws://` or `wss://`).
- **Concurrent I/O**: Sends and receives messages concurrently.
- **Automatic Reconnection**: Includes retry logic for connection failures (retries every 5 seconds).
- **Graceful Exit**: Type `quit` to cleanly close the connection and exit.
- **Flexible SSL**: Bypasses SSL certificate verification, making it easy to test against servers with self-signed certificates.

### Server (`websocket_server.py`)
- **Echo Functionality**: Automatically echoes back any received messages to the client that sent them.
- **Broadcast Support**: Type messages directly into the server's console to broadcast them to all connected clients.
- **Protocol Support**: Supports both standard (`ws://`) and secure (`wss://`) connections.
- **Secure Connections (SSL/TLS)**: Easily configure secure servers using PEM key/cert files or PKCS#12 (`.p12`/`.pfx`) bundles.

## Setup and Usage

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/vitorjna/Scripts.git
    cd Scripts/WebSocket
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Server**:
    By default, the server listens on `0.0.0.0:1230` with `ws`.
    ```bash
    python websocket_server.py [PORT] [--protocol {ws,wss}] [--cert CERT] [--key KEY] [--password PASSWORD]
    ```
    **Options:**
    *   `port`: Port to listen on (default: `1230`)
    *   `--protocol`: Protocol to use, `ws` or `wss` (default: `ws`)
    *   `--cert`: Path to the SSL certificate file (`.pem` or `.p12`/`.pfx` format)
    *   `--key`: Path to the SSL private key file (`.pem` format)
    *   `--password`: Password for the SSL private key or P12 file

    Examples:
    ```bash
    # Basic server
    python websocket_server.py 1230

    # Secure server with P12 configuration
    python websocket_server.py 1230 --protocol wss --cert cert.p12 --password "my_password"
    ```
    Once the server is running, any message typed in the server's console and submitted by pressing **Enter** will be broadcast to all connected clients.

4.  **Run the Client**:
    By default, the client connects to `ws://127.0.0.1:1230`.
    ```bash
    python websocket_client.py [URL]
    ```
    **Options:**
    *   `url`: The WebSocket URL to connect to (default: `ws://127.0.0.1:1230`)

    Examples:
    ```bash
    python websocket_client.py ws://127.0.0.1:1230
    ```
    Once connected, type a message and press **Enter** to send. Type `quit` to exit.

## Project Structure

-   `websocket_client.py`: The client-side script for connecting and sending messages.
-   `websocket_server.py`: The server-side script for receiving and echoing messages.
-   `requirements.txt`: Lists the necessary Python packages (`websockets`, `cryptography`).
