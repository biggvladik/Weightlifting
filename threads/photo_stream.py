from PyQt5.QtCore import *
import configparser
from factory import find_name_by_id, get_prematch_data, load_photo
from database import Data


class ThreadPhoto(QThread):
    signal_button = pyqtSignal(tuple)
    signal_message_box = pyqtSignal(tuple)
    signal_player_stat = pyqtSignal(list)

    def __init__(self, mainwindow):
        super().__init__()
        self.isrunning = True
        self.mainwindow = mainwindow

    def run(self):
        try:
            config = configparser.ConfigParser()
            config.read('settings.ini', encoding='utf-8')
            stage_type = (lambda x: 'Финал' if x == '2' else 'Квалификация')(config['SETTINGS']['stage_type'])
        except Exception as error:
            self.signal_message_box.emit(('error', 'settings.ini', error))
            return

        try:
            database = Data(config['DATABASE']['road'])
        except Exception as error:
            self.signal_message_box.emit(('error', 'База данных!', error))
            return

        self.signal_button.emit((self.mainwindow.ui.pushButton_6, 'Start', 'Photo'))

        # Получаем данные
        try:
            players = get_prematch_data(config['API']['url'], stage_type)
        except Exception as error:
            self.signal_message_box.emit(('error', 'Ошибка получения данных!', error))
            self.signal_button.emit((self.mainwindow.ui.pushButton_6, 'Finish', 'Photo'))
            return

        #  Скачиваем фотки
        try:
            data_res = load_photo(players, config['SETTINGS']['photo_directory'])
        except Exception as error:
            self.signal_message_box.emit(('error', "load_photo(players,config['SETTINGS']['photo_directory']", error))
            self.signal_button.emit((self.mainwindow.ui.pushButton_6, 'Finish', 'Photo'))
            return

        # Вставляем фотки в БД
        try:
            database.update_foto(data_res)
        except Exception as error:
            self.signal_message_box.emit(('error', "  database.update_foto(data_res)", error))
            self.signal_button.emit((self.mainwindow.ui.pushButton_6, 'Finish', 'Photo'))
            return

        self.signal_button.emit((self.mainwindow.ui.pushButton_6, 'Finish', 'Photo'))
