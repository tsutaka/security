import socket

target_host = "www.google.com"
target_port = 80

# ソケットオブジェクトの作成
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# サーバへの接続
client.connect((target_host, target_port))

# データの送信
client.send(b"GET / HTTP/1.1\r\nHost: google.com\r\n\r\n")

# データの受信
response = client.recv(4096)

print(response.decode())
client.close()