# author:jerry wong
# date:2022 08 11 17:00
import threading
from time import sleep

from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtNetwork import QUdpSocket, QHostAddress


class UDP_Qthread_Function(QObject):
    signal_UDP_qthread_function_init = pyqtSignal()
    signal_Pushbutton_Open = pyqtSignal(object)
    signal_Pushbutton_Open_flage = pyqtSignal(object)
    signal_readyRead = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.state = 0  # 0 未打开， 1 已打开， 2 关闭

    def UDP_qthread_function_init(self):
        # sleep(1)
        # print("UDP的线程id",threading.currentThread().ident)
        self.udpsocket = QUdpSocket()
        self.udpsocket.readyRead.connect(self.slot_readyRead)

    def slot_readyRead(self):
        # print("AAAA")
        buf = bytes()
        buf, ip, port = self.udpsocket.readDatagram(1024)

        data = {}
        print(type(ip))
        data['ip'] = ip.toString()
        data['port'] = port
        data['buf'] = buf
        self.signal_readyRead.emit(data)

    def slot_Pushbutton_Open(self, parameters):
        if self.state == 0:
            if self.udpsocket.bind(QHostAddress(parameters['ip']), int(parameters['port'])):
                print("UDP打开成功")
                self.state = 1
                self.signal_Pushbutton_Open_flage.emit(1)
            else:
                print("UDP打开失败")
                self.signal_Pushbutton_Open_flage.emit(0)
        else:
            self.udpsocket.close()
            self.state = 0
            self.signal_Pushbutton_Open_flage.emit(2)
