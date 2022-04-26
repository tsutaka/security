import socket
import threading

IP = "0.0.0.0"
PORT = 9998

def main():
    # ソケット作成
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 対象IPとポートを指定
    server.bind((IP, PORT))
    # 最大接続数を指定
    server.listen(5)

    print(f'[*] Listening on {IP}:{PORT}')

    while True:
        # 接続をキャッチ
        client, address = server.accept()
        print(f'[*] Accepted connection from {address[0]}:{address[1]}')
        # 新規スレッド作成
        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()

def handle_client(client_socket):
    with client_socket as sock:
        request = sock.recv(1024)
        print(f'[*] Received:{request.decode("utf-8")}')
        sock.send(b'ACK')

if __name__ == "__main__":
    main()