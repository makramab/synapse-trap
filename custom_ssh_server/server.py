import socket
import threading
import paramiko
import paramiko.common

key_file = "server.key"

try:
    host_key = paramiko.RSAKey(filename=key_file)
except FileNotFoundError:
    print(f"{key_file} not found. Generating a new RSA key...")
    host_key = paramiko.RSAKey.generate(2048)
    host_key.write_private_key_file(key_file)
    print(f"New RSA key generated and saved to {key_file}.")


class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        return paramiko.common.OPEN_SUCCEEDED

    def get_allowed_auths(self, username):
        return "none"

    def check_auth_none(self, username):
        return paramiko.common.AUTH_SUCCESSFUL

    def check_auth_password(self, username, password):
        return paramiko.common.AUTH_SUCCESSFUL

    def check_auth_publickey(self, username, key):
        return paramiko.common.AUTH_SUCCESSFUL

    def check_auth_interactive(self, username, submethods):
        return paramiko.common.AUTH_FAILED

    def check_auth_interactive_response(self, responses):
        return paramiko.common.AUTH_FAILED

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    # def check_channel_pty_request(
    #     self, channel, term, width, height, pixelwidth, pixelheight, modes
    # ):
    #     return True


def handle_connection(client_socket):
    transport = paramiko.Transport(client_socket)
    transport.add_server_key(host_key)

    server = Server()
    try:
        transport.start_server(server=server)
    except paramiko.SSHException:
        print("SSH negotiation failed.")
        client_socket.close()
        return

    # Accept channel request from the client
    chan = transport.accept()
    if chan is None:
        print("No channel request.")
        transport.close()
        return

    try:
        while True:
            chan.sendall("ubuntu@localhost:~/ $".encode())
            data = chan.recv(1024).decode("utf-8").strip()
            if not data or data.lower() == "exit":
                chan.send("Goodbye!\n".encode())
                break
            chan.send(f"You said: {data}\n".encode())
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
