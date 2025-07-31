
from PyQt5.QtCore import *
import configparser
from factory import get_time, create_packet_time
from time import sleep
from tcp_sender import TCP_sender


class ThreadTime(QThread):
    signal_button = pyqtSignal(tuple)
    signal_time = pyqtSignal(tuple)
    signal_message_box = pyqtSignal(tuple)

    def __init__(self, mainwindow):
        super().__init__()
        self.isrunning = True
        self.mainwindow = mainwindow
        self.tcp_sender = TCP_sender()

    def run(self):
        try:
            config = configparser.ConfigParser()
            config.read('settings.ini', encoding='utf-8')
        except Exception as error:
            self.signal_message_box.emit(('error', 'settings.ini', error))
            return

        try:

            self.tcp_sender.connect(config['OUTPUT']['host'], int(config['OUTPUT']['port']))
            self.signal_button.emit((self.mainwindow.ui.pushButton_4, 'Start', 'Start time'))
        except Exception as error:
            self.signal_message_box.emit(('error', 'TCP в титровалке', error))

        self.signal_button.emit((self.mainwindow.ui.pushButton_4, 'Start', 'Start time'))
        while self.isrunning:
            show = (lambda x: '1' if x else '0')(self.mainwindow.ui.checkBox.isChecked())

            try:
                timer = get_time(self.mainwindow.ui.lineEdit_3.text())
                print(timer)
                packet = create_packet_time(show, *timer)

                self.signal_button.emit((self.mainwindow.ui.pushButton_4, 'Start', 'Start time'))
            except Exception as error:
                self.signal_button.emit((self.mainwindow.ui.pushButton_4, 'Error', 'Start time'))
                print(error)
                continue

            try:
                print(packet)
                self.tcp_sender.send_data(packet)
            except Exception as error:
                print(error)
                self.signal_button.emit((self.mainwindow.ui.pushButton_4, 'Error', 'tcp'))

            self.signal_time.emit(timer)

            sleep(float(self.mainwindow.ui.comboBox_2.currentText()))
        self.tcp_sender.disconnect()
        self.signal_button.emit((self.mainwindow.ui.pushButton_4, 'Finish', 'Start time'))
