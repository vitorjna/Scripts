# WebSocket Client and Server

These scripts provide a simple way to interact with WebSocket servers and run a basic echo server for testing and development purposes.

## Features

- **Simplified WebSocket Client**: Easily connect to any WebSocket server using a single URL argument.
- **Simplified WebSocket Echo Server**: Quickly spin up a local WebSocket server that echoes back any received messages.
- **Protocol Support**: Supports both standard (`ws://`) and secure (`wss://`) connections.
- **Automatic Reconnection**: The client includes basic retry logic for connection failures.

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
    By default, the server listens on `0.0.0.0:1230`.
    ```bash
    python websocket_server.py [PORT]
    ```
    Example:
    ```bash
    python websocket_server.py 1230
    ```

4.  **Run the Client**:
    By default, the client connects to `ws://127.0.0.1:1230`.
    ```bash
    python websocket_client.py [URL]
    ```
    Example:
    ```bash
    python websocket_client.py ws://127.0.0.1:1230
    ```
    Once connected, type a message and press **Enter** to send. Type `quit` to exit.

## Project Structure

-   `websocket_client.py`: The client-side script for connecting and sending messages.
-   `websocket_server.py`: The server-side script for receiving and echoing messages.
-   `requirements.txt`: Lists the necessary Python packages (`websockets`, `cryptography`).
