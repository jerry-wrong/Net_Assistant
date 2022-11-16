# author:jerry wong
# date:2022 08 11 17:00
import threading
from time import sleep

from PyQt6.QtCore import pyqtSignal,QObject
from PyQt6.QtNetwork import QHostAddress, QTcpSocket


class TCP_client_Qthread_Function(QObject):
    signal_TCP_client_qthread_function_init = pyqtSignal()
    signal_Pushbutton_Open = pyqtSignal(object)
    signal_Pushbutton_Open_flage = pyqtSignal(object)
    signal_readyRead = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.state = 0  # 0 未打开， 1 已打开， 2 关闭

    def TCP_client_qthread_function_init(self):
        self.tcpsocket = QTcpSocket()
        # 连接成功之后的信号connected
        self.tcpsocket.connected.connect(self.connected)
        self.tcpsocket.readyRead.connect(self.slot_readRead)
        self.tcpsocket.disconnected.connect(self.disconnected)

    def slot_readRead(self):
        buf = self.tcpsocket.readAll()
        data = {}
        data['buf'] = buf
        # print("TCP server收到的数据", data['ip'], data['port'], data['buf'])
        self.signal_readyRead.emit(data)

    def slot_Pushbutton_Open(self, parameters):
        print("打开TCP Client",parameters)
        if self.state == 0:
            # 连接之后没有返回值
            self.tcpsocket.connectToHost(QHostAddress(parameters['ip']), int(parameters['port']))
        else:
            self.tcpsocket.close()
            self.state = 0
            self.signal_Pushbutton_Open_flage.emit(2)

    def connected(self):
        print("连接成功")
        self.state = 1
        self.signal_Pushbutton_Open_flage.emit(1)

    def disconnected(self):
        print("TCP Client断开连接")
        self.state = 0
        self.signal_Pushbutton_Open_flage.emit(2)
