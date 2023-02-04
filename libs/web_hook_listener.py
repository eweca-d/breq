import socket
import multiprocessing as mp


def set_listener(port: int) -> mp.Queue:
    q = mp.Queue()
    p = mp.Process(target=listener, args=(port, q))
    p.start()
    return q


def listener(port: int, q: mp.Queue):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', port))
    s.listen(5)
    while True:
        conn, addr = s.accept()
        while True:
            # typical web hook info is less than 1024 bytes
            data = conn.recv(1024)
            msg = data.decode()
            q.put(msg)
            break
        conn.sendall(b'HTTP/1.1 200 OK\r\n\r\n')
        conn.close()


if __name__ == '__main__':
    q = set_listener(8048)
    while True:
        print(q.get())
