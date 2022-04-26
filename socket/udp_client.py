import socket

target_host = "127.0.0.1"
target_port = 9997

# ソケットオブジェクトの作成
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# データの送信
client.sendto(b"AAABBBCCC", (target_host, target_port))

client.close()