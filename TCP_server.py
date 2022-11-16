# author:jerry wong
# date:2022 08 11 17:00
import threading
from time import sleep

from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtNetwork import QHostAddress, QTcpServer


class TCP_server_Qthread_Function(QObject):
    signal_TCP_server_qthread_function_init = pyqtSignal()

    signal_Pushbutton_Open = pyqtSignal(object)
    signal_Pushbutton_Open_flage = pyqtSignal(object)
    signal_readyRead = pyqtSignal(object)
    signal_newclient = pyqtSignal(object)

    signal_closeclient = pyqtSignal(object)

    signal_senddata = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.state = 0  # 0 未打开， 1 已打开， 2 关闭
        self.listClient = []

        # 监听到的client
        self.newclient = []
        self.newclient.insert(0,"All (" + str(len(self.newclient)) + ")")


    def TCP_server_qthread_function_init(self):
        self.tcpserversocket = QTcpServer()
        # 创建新的接收信号套接字的信号
        self.tcpserversocket.newConnection.connect(self.newConnection)

    def newConnection(self):
        # print("新的服务器套接字")
        tcpClientsocket = self.tcpserversocket.nextPendingConnection()
        # print("新的接收套接字", tcpClientsocket.peerAddress().toString(), tcpClientsocket.peerPort())
        # 收到信息的信号
        tcpClientsocket.readyRead.connect(self.slot_readRead)
        # 断开收发套接字的信号
        tcpClientsocket.disconnected.connect(self.updatestate)
        self.listClient.append(tcpClientsocket)

        del self.newclient[0]
        self.newclient.insert(0,"All (" + str(len(self.listClient)) + ")")
        self.newclient.append(tcpClientsocket.peerAddress().toString() + ":" + str(tcpClientsocket.peerPort()))
        self.signal_newclient.emit(self.newclient)

    def updatestate(self):
        print("更新listClient")
        for i in range(len(self.listClient)):
            if self.listClient[i].state() == 0:
                del self.listClient[i]
                break

    def slot_readRead(self):
        for i in range(len(self.listClient)):
            # 套接字有无数据
            if self.listClient[i].bytesAvailable() > 0:
                buf = self.listClient[i].readAll()
                data = {}
                data["ip"] = self.listClient[i].peerAddress().toString()
                data['port'] = self.listClient[i].peerPort()
                data['buf'] = buf
                # print("TCP server收到的数据", data['ip'], data['port'], data['buf'])
                self.signal_readyRead.emit(data)

    def slot_Pushbutton_Open(self, parameters):
        if self.state == 0:
            if self.tcpserversocket.listen(QHostAddress(parameters['ip']), int(parameters['port'])):
                print("TCP Server打开成功")
                self.state = 1
                self.signal_Pushbutton_Open_flage.emit(1)
            else:
                print("TCP Server打开失败")
                self.signal_Pushbutton_Open_flage.emit(0)
            self.signal_newclient.emit(self.newclient)
        else:
            for i in range(len(self.listClient)):
                self.listClient[i].disconnected.disconnect(self.updatestate)
                self.listClient[i].readyRead.disconnect(self.slot_readRead)
                self.listClient[i].close()
            self.listClient.clear()
            self.tcpserversocket.close()
            self.state = 0
            self.signal_Pushbutton_Open_flage.emit(2)

            self.newclient.clear()
            self.newclient.insert(0, "All (" + str(len(self.listClient)) + ")")

    def slot_closeclient(self,parameter):
        print("TCP Server断开",parameter)
        if parameter.find("All") >= 0:
            for i in range(len(self.listClient)):
                self.listClient[i].disconnected(self.updatestate)
                self.listClient[i].readyRead.disconnect(self.slot_readRead)
                self.listClient[i].close()
            self.newclient.clear()
            self.listClient.clear()
            self.newclient.insert(0, "All (" + str(len(self.listClient)) + ")")
            self.signal_newclient.emit(self.newclient)
        else:
            for i in range(len(self.listClient)):
                ip = self.listClient[i].peerAddress().toString()
                port = self.listClient[i].peerPort()
                ip_port = ip + ":" +str(port)
                if parameter == ip_port:
                    # 断开连接
                    self.listClient[i].disconnected(self.updatestate)
                    self.listClient[i].readyRead.disconnect(self.slot_readRead)
                    self.listClient[i].close()
                    del self.listClient[i]
                    # 去除数据
                    self.newclient.remove(ip_port)

                    # 更新显示
                    del self.newclient[0]
                    self.newclient.insert(0,"All (" + str(len(self.listClient)) + ")")
                    self.signal_newclient.emit(self.newclient)
                    return

    def slot_senddata(self,parameter):
        if self.state != 1:
            return
        if parameter['ip_port'].find('All') >= 0:
            for i in range(len(self.listClient)):
                self.listClient[i].write(parameter['data'])
        else:
            for i in range(len(self.listClient)):
                ip = self.listClient[i].peerAddress().toString()
                port = self.listClient[i].peerPort()
                ip_port = ip + ":" +str(port)
                if parameter['ip_port'] == ip_port:
                    self.listClient[i].write(parameter['data'])




