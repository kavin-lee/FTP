"""
FTP 文件客户端
并发网络功能训练
"""
from socket import *
import sys
from time import sleep

# 全局变量
HOST = '176.234.8.11'
PORT = 10001
ADDR = (HOST, PORT)


# 具体功能
class FtpClient:
    def __init__(self, sockfd):
        self.sockfd = sockfd

    def do_list(self):
        self.sockfd.send(b'L')  # 发送请求
        # 等待回复
        data = self.sockfd.recv(128).decode()
        # Ok表示请求成功
        if data == 'OK':
            # 接收文件列表
            data = self.sockfd.recv(4096)
            print(data.decode())
        else:
            print(data)

    def do_quit(self):
        self.sockfd.send(b'Q')
        self.sockfd.close()
        sys.exit("谢谢使用本产品")

    def do_down(self, filename):
        # 发送请求
        self.sockfd.send(('G ' + filename).encode())
        # 等待回复
        data = self.sockfd.recv(128).decode()
        if data == "OK":
            fd = open(filename, 'wb')
            # 接受内容写入文件
            while True:
                data = self.sockfd.recv(1024)
                if data == b"##":
                    break
                fd.write(data)
            fd.close()
        else:
            print(data)

    def do_up(self, filename):
        try:
            fd = open(filename, 'rb')
        except Exception:
            print("没有该文件")
            return

        filename = filename.split("/")[-1]
        self.sockfd.send(('P ' + filename).encode())
        # 等待回复
        data = self.sockfd.recv(128).decode()
        if data == "OK":
            # 打开本地文件
            while True:
                data = fd.read(1024)
                if not data:
                    sleep(0.1)
                    self.sockfd.send(b'##')
                    break
                self.sockfd.send(data)
            fd.close()
        else:
            print(data)

    def do_back(self):
        self.sockfd.send(b'B')


def request(sockfd):
    ftp = FtpClient(sockfd)
    while True:
        print("===============命令选项==============")
        print("*************   list  *************")
        print("*************  upload  ************")
        print("************* download ************")
        print("*************   back  *************")
        print("*************   quit  *************")
        print("===================================")
        cmd = input("请输入命令:")
        if cmd.strip() == 'list':
            ftp.do_list()
        elif cmd[:8] == 'download':
            filename = cmd.strip().split(" ")[-1]
            ftp.do_down(filename)
        elif cmd.strip() == 'quit':
            ftp.do_quit()
        elif cmd[:6]== 'upload':
            filename = cmd.strip().split(" ")[-1]
            ftp.do_up(filename)
        elif cmd[:4]=='back':
            ftp.do_back()
            print('''                *******************
                            Data   File   Image
                            *******************'''
                  )
            cls = input("请输入文件种类:")
            if cls not in ['Data', 'File', 'Image']:
                print("Sorry input Error!")
                return
            else:
                sockfd.send(cls.encode())
                continue
# 网络搭建
def main():
    sockfd = socket()
    try:
        sockfd.connect(ADDR)
    except Exception as e:
        sys.exit("链接服务器失败")
    # while True:
    else:
        print('''                *******************
                Data   File   Image
                *******************'''
              )
        cls = input("请输入文件种类:")
        if cls not in ['Data', 'File', 'Image']:
            print("Sorry input Error!")
            return
        else:
            sockfd.send(cls.encode())
            request(sockfd)  # 发送具体请求


if __name__ == '__main__':
    main()
