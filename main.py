import sys
import traceback
from pathlib import Path

from PyQt5.QtCore import *
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QFileDialog, QTableWidgetItem, QDialog
from PyQt5.QtGui import QColor

from frontend.ui.window_prodact import Ui_Tennis
from threads.stat_stream import ThreadStat
from threads.time_stream import ThreadTime
from threads.prematch_stream import ThreadPrematch
from threads.photo_stream import ThreadPhoto

import configparser
from frontend.ui.clear_window import CustomMessageBox
from worker import Worker
from database import Data


class ImageDialog(QMainWindow):

    def __init__(self):
        super().__init__()
        self.settings = QSettings('GrabberBMX', 'GrabberBMX')
        # Set up the user interface from Designer.
        self.ui = Ui_Tennis()
        self.ui.setupUi(self)
        self.threadpool = QThreadPool()
        self.ui.pushButton.clicked.connect(self.launch_thread)
        self.ui.lineEdit.editingFinished.connect(self.update_ini)
        self.ui.pushButton_3.clicked.connect(self.pick_database)
        self.ui.pushButton_5.clicked.connect(self.wrapped_clear_database)
        self.ui.pushButton_5.clicked.connect(self.stop_thread)
        try:
            self.load_ini()
        except Exception as error:
            self.show_message_box(("error", 'settings.ini', error))

    def launch_thread(self):
        try:
            if self.mythread_2.isrunning:
                self.mythread_2.isrunning = False
                self.mythread_2 = ThreadStat(mainwindow=self)
                self.mythread_2.signal_button.connect(self.change_button_status)
                self.mythread_2.signal_message_box.connect(self.show_message_box)
                self.mythread_2.start()
            else:
                self.mythread_2 = ThreadStat(mainwindow=self)
                self.mythread_2.signal_button.connect(self.change_button_status)
                self.mythread_2.signal_message_box.connect(self.show_message_box)
                self.mythread_2.start()

        except:
            self.mythread_2 = ThreadStat(mainwindow=self)
            self.mythread_2.signal_button.connect(self.change_button_status)
            self.mythread_2.signal_message_box.connect(self.show_message_box)
            self.mythread_2.start()

    def pick_database(self):
        home_dir = str(Path.home())
        fname = QFileDialog.getOpenFileName(self, 'Выбрать базу данных', home_dir, "*.mdb")
        road_database = fname[0]
        try:
            config = configparser.ConfigParser()
            config.read('settings.ini')
            config.set('DATABASE', 'road', road_database)
            with open('settings.ini', 'w') as configfile:
                config.write(configfile)
        except:
            print(traceback.format_exc())
            return
        self.ui.lineEdit_2.setText(road_database)

    def stop_thread(self):
        try:
            self.mythread_2.isrunning = False
        except:
            pass

    def change_button_status(self, item: tuple):
        try:
            if item[1] == 'Error':
                item[0].setStyleSheet(
                    """ 
                    border-style: outset;
                    border-width: 2px;
                    border-radius: 10px;
                    border-color: black;
                    font: bold 14px;
                    padding: 6px;
                    background-color: red;"""
                )
                item[0].setText(item[2])
            elif item[1] == 'Finish':
                item[0].setStyleSheet(
                    """ 
                    border-style: outset;
                    border-width: 2px;
                    border-radius: 10px;
                    border-color: black;
                    font: bold 14px;
                    padding: 6px;
                    background-color: white;"""
                )
                item[0].setText(item[2])

            elif item[1] == 'Start':
                item[0].setStyleSheet(
                    """ 
                    border-style: outset;
                    border-width: 2px;
                    border-radius: 10px;
                    border-color: black;
                    font: bold 14px;
                    padding: 6px;
                    background-color: green;"""
                )
                item[0].setText(item[2])
        except:
            print(traceback.format_exc())

    def load_ini(self):
        config = configparser.ConfigParser()
        config.read('settings.ini')
        url = config['API']['url']
        database_road = config['DATABASE']['road']
        self.ui.lineEdit.setText(url)
        self.ui.lineEdit_2.setText(database_road)

    def show_message_box(self, item: tuple):
        if item[0] == 'error':
            QMessageBox.warning(self, item[1], f"""<p>{item[2]}</p>""", QMessageBox.StandardButton.Ok)

    def update_ini(self):
        try:
            d = {
                self.ui.lineEdit: ('API', 'url'),
            }
            config = configparser.ConfigParser()
            config.read('settings.ini')
            if d[self.sender()][0] == 'API':
                config.set(d[self.sender()][0], d[self.sender()][1], self.sender().text())

            elif d[self.sender()][0] == 'SETTINGS':
                if self.sender() == self.ui.radioButton:
                    stage_type = '1'
                else:
                    stage_type = '2'
                config.set(d[self.sender()][0], d[self.sender()][1], stage_type)

            with open('settings.ini', 'w', encoding='UTF-8') as configfile:
                config.write(configfile)
        except Exception as error:
            print(error)

    def closeEvent(self, event):
        try:
            self.thread_time.tcp_sender.disconnect()
        except:
            pass

    def clear_database(self, tables):
        try:
            databasa = Data(self.ui.lineEdit_2.text())
        except:
            print(traceback.format_exc())
            self.change_button_status((self.ui.pushButton_5, 'Error', 'БД'))
            return
        try:
            databasa.clear_database(tables)
        except:
            self.change_button_status((self.ui.pushButton_5, 'Error', 'Clear'))
        self.change_button_status((self.ui.pushButton_5, 'Finish', 'Clear'))

    def wrapped_clear_database(self):

        custom_msg_box = CustomMessageBox("Clear Window", "Выберите таблицы для очистки")
        result = custom_msg_box.exec_()
        if result == QDialog.Rejected:
            return
        tables = []
        if custom_msg_box.checkbox1.isChecked():
            tables.append('ZaezdMaps')
        if custom_msg_box.checkbox2.isChecked():
            tables.append('Zaezd')
        if custom_msg_box.checkbox3.isChecked():
            tables.append('Players')

        self.change_button_status((self.ui.pushButton_5, 'Start', 'Clear'))
        try:
            worker = Worker(self.clear_database, tables)
            self.threadpool.start(worker)
        except:
            print(traceback.format_exc())
            self.change_button_status((self.ui.pushButton_5, 'Error', 'Clear'))



app = QApplication(sys.argv)
window = ImageDialog()
window.show()

sys.exit(app.exec())
