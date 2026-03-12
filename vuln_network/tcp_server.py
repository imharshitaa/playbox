# network/tcp_server.py -- naive TCP server that parses a 4-byte length header (vulnerable)
import socket
import struct

HOST = '0.0.0.0'
PORT = 9001


def handle(conn):
    try:
        # read 4-byte length header (big-endian)
        raw = conn.recv(4)
        if len(raw) < 4:
            return
        (n,) = struct.unpack(">I", raw)
        # naive: refuses to limit n (vuln: large allocation)
        data = conn.recv(n)
        conn.sendall(b"OK:" + data[:50])
    except Exception as e:
        conn.sendall(b"ERR:" + str(e).encode())
    finally:
        conn.close()


def start_tcp_server(host=HOST, port=PORT):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(5)
    print("listening on", port)
    while True:
        conn, addr = s.accept()
        handle(conn)


if __name__ == "__main__":
    start_tcp_server()
