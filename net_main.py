# author:jerry wong
# date:2022 08 11 15:46
from PyQt6.QtGui import QIcon
from PyQt6.QtNetwork import QNetworkInterface, QAbstractSocket
from PyQt6.QtWidgets import QWidget, QApplication, QMessageBox
from PyQt6.QtCore import QThread, QTimer

import UDP
import TCP_client
import TCP_server
import netassistant
import sys
import threading


class InitForm(QWidget):
    def __init__(self):
        super(InitForm, self).__init__()
        self.ui = netassistant.Ui_NetAssistant()
        self.ui.setupUi(self)
        self.setWindowTitle("Dell Net Assistant")

        # 各个模块初始化
        print("主线程id", threading.current_thread().ident)
        self.UDP_Init()
        self.TCP_client_Init()
        self.TCP_server_Init()
        # 界面初始化
        self.UI_Init()

    def UDP_Init(self):
        # 创建线程
        self.UDP_QThread = QThread()
        self.UDP_qthread_function = UDP.UDP_Qthread_Function()

        # 把方法移动到线程中
        self.UDP_qthread_function.moveToThread(self.UDP_QThread)
        self.UDP_QThread.start()
        self.UDP_qthread_function.signal_UDP_qthread_function_init.connect(
            self.UDP_qthread_function.UDP_qthread_function_init)
        self.UDP_qthread_function.signal_Pushbutton_Open.connect(self.UDP_qthread_function.slot_Pushbutton_Open)
        self.UDP_qthread_function.signal_Pushbutton_Open_flage.connect(self.slot_pushButton_Open_flage)
        self.UDP_qthread_function.signal_readyRead.connect(self.slot_readyRead)
        self.UDP_qthread_function.signal_UDP_qthread_function_init.emit()

    def TCP_client_Init(self):
        # 创建线程
        self.TCP_client_QThread = QThread()
        self.TCP_client_qthread_function = TCP_client.TCP_client_Qthread_Function()

        # 把方法移动到线程中
        self.TCP_client_qthread_function.moveToThread(self.TCP_client_QThread)
        self.TCP_client_QThread.start()


        self.TCP_client_qthread_function.signal_TCP_client_qthread_function_init.connect(
            self.TCP_client_qthread_function.TCP_client_qthread_function_init)

        self.TCP_client_qthread_function.signal_Pushbutton_Open.connect(self.TCP_client_qthread_function.slot_Pushbutton_Open)
        self.TCP_client_qthread_function.signal_Pushbutton_Open_flage.connect(self.slot_pushButton_Open_flage)
        self.TCP_client_qthread_function.signal_readyRead.connect(self.slot_readyRead)

        self.TCP_client_qthread_function.signal_TCP_client_qthread_function_init.emit()

        # 主动关闭客户端
        self.ui.pushButton_CllientClose.clicked.connect(self.pushButton_clientclose)

    def TCP_server_Init(self):
        # 创建线程
        self.TCP_server_QThread = QThread()
        self.TCP_server_qthread_function = TCP_server.TCP_server_Qthread_Function()

        # 把方法移动到线程中
        self.TCP_server_qthread_function.moveToThread(self.TCP_server_QThread)
        self.TCP_server_QThread.start()
        self.TCP_server_qthread_function.signal_TCP_server_qthread_function_init.connect(
            self.TCP_server_qthread_function.TCP_server_qthread_function_init)
        self.TCP_server_qthread_function.signal_Pushbutton_Open.connect(self.TCP_server_qthread_function.slot_Pushbutton_Open)
        self.TCP_server_qthread_function.signal_Pushbutton_Open_flage.connect(self.slot_pushButton_Open_flage)
        self.TCP_server_qthread_function.signal_readyRead.connect(self.slot_readyRead)
        self.TCP_server_qthread_function.signal_TCP_server_qthread_function_init.emit()

        self.TCP_server_qthread_function.signal_newclient.connect(self.slot_newclient)


        self.TCP_server_qthread_function.signal_closeclient.connect(self.TCP_server_qthread_function.slot_closeclient)
    def UI_Init(self):
        comboBox_type = {"UDP", "TCP Client", "TCP Server"}
        self.ui.comboBox_type.addItems(comboBox_type)
        # 更新界面用信号和槽，connect绑定在信号建立界面
        # currentTextChanged改变文本的时候发出信号，并传递参数
        self.comboBox_type(self.ui.comboBox_type.currentText())
        self.ui.comboBox_type.currentTextChanged.connect(self.comboBox_type)
        self.ui.lineEdit_Port.setText("5362")

        # 绑定点击open的信号和槽函数
        self.ui.pushButton_Open.clicked.connect(self.pushButton_Open)

        # 发送
        self.ui.pushButton_Send.clicked.connect(self.slot_pushButtonsend)
        self.TCP_server_qthread_function.signal_senddata.connect(self.TCP_server_qthread_function.slot_senddata)


        # 定时
        self.time_send = QTimer()
        self.time_send.timeout.connect(self.timeout_send)

        self.ui.checkBox_HexSend.stateChanged.connect(self.slot_checkBox_hexsend)


        self.ui.checkBox_TimeSend.stateChanged.connect(self.slot_checkBox_timesend)

        self.ui.lineEdit_IntervalTime.setText("100")
    def comboBox_type(self, str):
        scan_ip = self.search_ip()
        self.ui.comboBox_ip.clear()
        self.ui.comboBox_ip.addItems(scan_ip)
        if str == "UDP":
            print("选中UDP")
            self.ui.label_ip.setText("(2)local host address")
            self.ui.label_port.setText("(3)local host port")
            self.ui.comboBox_ip.setEditable(False)
            self.ui.widget_client.show()
        elif str == "TCP Server":
            print("选中TCP Server")
            self.ui.label_ip.setText("(2)local host address")
            self.ui.label_port.setText("(3)local host port")
            self.ui.comboBox_ip.setEditable(False)
            self.ui.widget_client.show()
        else:
            print("选中TCP Client")
            self.ui.label_ip.setText("(2)remote host address")
            self.ui.label_port.setText("(3)remote host port")
            self.ui.comboBox_ip.setEditable(True)
            self.ui.widget_client.hide()

    def search_ip(self):
        list_ip = QNetworkInterface.allAddresses()
        scan_ip = []
        for ip in list_ip:
            # print(ip.toString())
            if ip.isNull():
                continue
            # 填入ip
            nprotocol = ip.protocol()
            if nprotocol == ip.protocol().IPv4Protocol:
                # print(ip.toString())
                scan_ip.append(ip.toString())
        return scan_ip

    def pushButton_Open(self):
        choose_type = self.ui.comboBox_type.currentText()
        parameter = {}
        parameter["ip"] = self.ui.comboBox_ip.currentText()
        parameter["port"] = self.ui.lineEdit_Port.text()

        if choose_type == "UDP":
            print("打开UDP")
            self.UDP_qthread_function.signal_Pushbutton_Open.emit(parameter)

        elif choose_type == "TCP Server":
            print("打开TCP Server")
            self.TCP_server_qthread_function.signal_Pushbutton_Open.emit(parameter)
        else:
            print("打开TCP Client")
            self.TCP_client_qthread_function.signal_Pushbutton_Open.emit(parameter)

    def slot_pushButton_Open_flage(self,state):
        print("打开状态",state)
        if state == 0:
            print("打开失败")
            QMessageBox.warning(self,"警告","打开失败，检查是否被占用")

        elif state == 1:
            print("打开成功")
            self.ui.pushButton_Open.setText("关闭")
            self.ui.pushButton_Open.setStyleSheet("color:red")
            self.ui.comboBox_type.setEnabled(False)
            self.ui.comboBox_ip.setEnabled(False)
            self.ui.lineEdit_Port.setEnabled(False)
        else:
            print("关闭")
            self.ui.pushButton_Open.setText("打开")
            self.ui.pushButton_Open.setStyleSheet("color:black")
            self.ui.comboBox_type.setEnabled(True)
            self.ui.comboBox_ip.setEnabled(True)
            self.ui.lineEdit_Port.setEnabled(True)

    def slot_readyRead(self):
        pass

    def slot_checkBox_hexsend(self,state):
        print("16进制",state)
        if state == 2:
            send_text = self.ui.textEdit_Send.toPlainText()
            byte_text = str.encode(send_text)
            view_data = ""
            for i in range(0,len(byte_text)):
                view_data = view_data + "{:02x}".format(byte_text[i]) + "+"
            self.ui.textEdit_Send.sendText(view_data)
        else:
            send_list = []
            send_text = self.ui.textEdit_Send.toPlainText()
            while send_text != "":
                try:
                    num = int(send_text[0:2],16)
                except:
                    QMessageBox.warning(self,"wrong message","Please enter the right hex")
                    return
                send_text = send_text[2:].strip()
                send_list.append(num)
            input_s = bytes(send_list)
            self.ui.textEdit_Send.setText(input_s.decode())




    def timeout_send(self):
        self.slot_pushButtonsend()

    def slot_checkBox_timesend(self,state):
        "都选定时器"
        if state == 2:
            time_data = self.ui.lineEdit_IntervalTime.text()
            self.time_send.start(int(time_data))
        else:
            self.time_send.stop()

    # def slot_readyRead(self,data):

    def slot_pushButtonsend(self,data):
        send_buff = ""
        if self.ui.checkBox_HexSend.checkState() == self.ui.checkBox_HexSend.checkState().Checked:
            send_list = []
            send_text = self.ui.textEdit_Send.toPlainText()
            while send_text != "":
                try:
                    num = int(send_text[0:2],16)
                except:
                    QMessageBox.warning(self,"wrong message","Please enter the right hex")
                    return
                send_text = send_text[2:].strip()
                send_list.append(num)
            input_s = bytes(send_list).decode()
            if self.ui.checkBox_SendEnd.checkState() == self.ui.checkBox_SendEnd.checkState().Checked:
                send_buff = input_s + '\r\n'
            else:
                send_buff = input_s
        else:
            if self.ui.checkBox_SendEnd.checkState() == self.ui.checkBox_SendEnd.checkState().Checked:
                send_buff = self.ui.textEdit_Send.toPlainText() + "\r\n"
            else:
                send_buff = self.ui.textEdit_Send.toPlainText()
        byte_data = str.encode(send_buff)
        print(send_buff)

        choose_type = self.ui.comboBox_type.currentText()
        parameter = {}
        parameter['ip_port'] = self.ui.comboBox_ip.currentText()
        parameter['data'] = byte_data
        if choose_type == "UDP":
            print("UDP收到数据",data['ip'],data['port'],data['buf'])
        elif choose_type == "TCP Server":
            self.TCP_server_qthread_function.signal_senddata.emit(parameter)
            # print("TCP Server收到数据", data['ip'],data['port'],data['buf'])
        else:
            print("TCP Client收到数据", data['buf'])


    def slot_newclient(self,parameter):
        self.ui.comboBox_ClientIp.clear()
        self.ui.comboBox_ClientIp.addItems(parameter)

    def pushButton_clientclose(self):
        print("断开客户端")
        ip_port = self.ui.comboBox_ClientIp.currentText()
        self.TCP_server_qthread_function.signal_closeclient.emit(ip_port)

    def closeEvent(self, event):
        print("窗口关闭")
        # 关闭UDP对象
        self.UDP_QThread.quit()
        self.UDP_QThread.wait()
        # 删除方法
        del self.UDP_qthread_function

        # 关闭TCP_Client对象
        self.TCP_server_QThread.quit()
        self.TCP_server_QThread.wait()
        # 删除方法
        del self.TCP_server_qthread_function

        # 关闭TCP_Server对象
        self.TCP_client_QThread.quit()
        self.TCP_client_QThread.wait()
        # 删除方法
        del self.TCP_client_qthread_function


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('adell.ico'))
    w1 = InitForm()
    w1.show()

    sys.exit(app.exec())
