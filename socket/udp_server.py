import socket

target_host = "127.0.0.1"
target_port = 9997

# ソケットオブジェクトの作成
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# データの受信
server.bind((target_host, target_port))

while True:
    #データを待ち受け
    data, address = server.recvfrom(4096)
    print("receive data : [{}]  from {}".format(data.decode("utf-8"),address))
server.close()


