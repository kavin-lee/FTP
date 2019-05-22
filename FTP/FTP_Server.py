"""
FTP 文件服务器
并发网络功能训练
"""
from socket import *
from threading import Thread
import sys, os
from time import sleep

# 全局变量
HOST = '0.0.0.0'
PORT = 10001
ADDR = (HOST, PORT)
FTP = "/home/tarena/ftp/"  # 文件库路径


# 将客户端的请求功能封装为一个类
class FtpServer:
    def __init__(self, connfd, FTP_PATH):
        self.connfd = connfd
        self.path = FTP_PATH

    def do_list(self):
        # 获取文件列表
        files = os.listdir(self.path)
        if not files:
            self.connfd.send("该文件类别为空".encode())
            return
        else:
            self.connfd.send(b'OK')
            sleep(0.1)

        fs = ""
        for file in files:
            if file[0] != '.' and \
                    os.path.isfile((self.path + file)):
                fs += file + '\n'
        self.connfd.send(fs.encode())

    def download(self, filename):
        try:
            fd = open(self.path + filename, 'rb')
        except Exception:
            self.connfd.send("该文件不存在".encode())
            return
        else:
            self.connfd.send(b'OK')
            sleep(0.1)
        # 发文件内容
        while True:
            data = fd.read(1024)
            if not data:
                sleep(0.1)
                self.connfd.send(b'##')
                break
            self.connfd.send(data)
        fd.close()

    def upload(self, filename):
        if os.path.exists(self.path + filename):
            self.connfd.send("该文件已存在".encode())
            return
        self.connfd.send(b'OK')
        fd = open(self.path + filename, 'wb')
        # 接受文件
        while True:
            data = self.connfd.recv(1024)
            if data == b"##":
                break
            fd.write(data)
        fd.close()

    def do_back(self):
        self.path = FTP
        print(self.path)


def handle(connfd):
    # 选择文件夹
    cls = connfd.recv(1024).decode()
    FTP_PATH = FTP + cls + '/'
    print(FTP_PATH)
    ftp = FtpServer(connfd, FTP_PATH)
    while True:
        # 接受客户端的请求
        data = connfd.recv(1024).decode()
        # 如果客户端断开返回data为空,第一时间做判断,避免服务器崩溃
        if not data or data[0] == "Q":
            return
        elif data[0] == "L":
            ftp.do_list()
        elif data[0] == "G":
            filename1 = data.split(" ")[-1]
            ftp.download(filename1)
        elif data[0] == "P":
            filename2 = data.split(" ")[-1]
            ftp.upload(filename2)
        elif data[0] == "B":
            ftp.do_back()


def main():
    sockfd = socket()
    sockfd.getsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sockfd.bind(ADDR)
    sockfd.listen(5)
    print("Listen the port 10000...")
    while True:
        try:
            connfd, addr = sockfd.accept()
        except KeyboardInterrupt:
            sys.exit("退出服务器")
        except Exception as e:
            print(e)
            continue
        print("连接的客户端是:", addr)
        # 创建线程处理请求
        client = Thread(target=handle, args=(connfd,))
        client.setDaemon(True)
        client.start()


if __name__ == '__main__':
    main()
