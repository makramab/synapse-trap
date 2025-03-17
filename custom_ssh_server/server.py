import socket
import threading
import paramiko
import paramiko.common

host_key = paramiko.RSAKey.generate(2048)


class Server(paramiko.ServerInterface):
    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.common.OPEN_SUCCEEDED
        return paramiko.common.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if username == "testuser" and password == "testpass":
            return paramiko.common.AUTH_SUCCESSFUL
        return paramiko.common.AUTH_FAILED


def handle_connection(client_socket):
    transport = paramiko.Transport(client_socket)
    transport.add_server_key(paramiko.RSAKey.generate(2048))

    server = Server()
    try:
        transport.start_server(server=server)
    except paramiko.SSHException:
        print("SSH negotiation failed.")
        client_socket.close()
        return

    # Accept channel request from the client
    chan = transport.accept(20)
    if chan is None:
        print("No channel request.")
        transport.close()
        return

    chan.send(b"This is a custom SSH Server > .\n")
    try:
        while True:
            chan.send(b"Type something (or 'exit' to quit): ")
            data = chan.recv(1024).decode("utf-8").strip()
            if not data or data.lower() == "exit":
                chan.send(b"Goodbye!\n")
                break
            chan.send(b"You said: {data}\n")
    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        chan.close()
        transport.close()


if __name__ == "__main__":
    HOST, PORT = "127.0.0.1", 2200

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(100)

    print(f"SSH server listening on {HOST}:{PORT}...")

    try:
        while True:
            client_socket, addr = sock.accept()
            print(f"Connection received from {addr}")
            threading.Thread(target=handle_connection, args=(client_socket,)).start()
    except KeyboardInterrupt:
        print("Server shutting down.")
    finally:
        sock.close()
