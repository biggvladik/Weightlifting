from PyQt5.QtCore import *
import configparser
from factory import find_name_by_id, get_prematch_data
from database import Data


class ThreadPrematch(QThread):
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

        self.signal_button.emit((self.mainwindow.ui.pushButton_2, 'Start', 'Prematch'))

        # Получаем данные
        try:
            players = get_prematch_data(config['API']['url'], stage_type)
        except Exception as error:
            self.signal_message_box.emit(('error', 'Ошибка получения данных!', error))
            self.signal_button.emit((self.mainwindow.ui.pushButton_2, 'Finish', 'Prematch'))
            return

        # Получаем ZaezdID
        try:
            zaezd_id = database.get_current_zaezd()
            if zaezd_id is None:
                raise EOFError
        except Exception as error:
            self.signal_button.emit((self.mainwindow.ui.pushButton_2, 'Finish', 'Prematch'))
            self.signal_message_box.emit(('error', 'Zaezd не зафиксирован!', error))
            return

        players_emit = []
        # Вставляем спортсменов в БД
        try:
            for player in players:
                players_emit.append(player)
                database.insert_player(player)
                database.insert_player_zaezdmaps(zaezd_id, player['id'], player['bib'])

        except Exception as error:
            self.signal_message_box.emit(('error', 'Ошибка вставки в Players/Zaezdmaps', error))

        self.signal_player_stat.emit(players_emit)
        self.signal_button.emit((self.mainwindow.ui.pushButton_2, 'Finish', 'Prematch'))
