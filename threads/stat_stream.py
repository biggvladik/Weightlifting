import traceback

from PyQt5.QtCore import *
import configparser
from time import sleep
from factory import find_name_by_id, get_score_by_attempt, get_live_data
from database import Data


class ThreadStat(QThread):
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

        self.signal_button.emit((self.mainwindow.ui.pushButton, 'Start', 'Live'))

        while self.isrunning:

            # Получаем данные
            try:
                scores, tricks = get_live_data(config['API']['url'], stage_type)
                self.signal_button.emit((self.mainwindow.ui.pushButton, 'Start', 'Live'))

            except Exception as error:
                print(traceback.format_exc())
                self.signal_button.emit((self.mainwindow.ui.pushButton, 'Error', 'get'))
                print(error)
                continue
            # Получаем ZaezdID
            try:
                zaezd_id = database.get_current_zaezd()
                if zaezd_id is None:
                    raise EOFError
            except Exception as error:
                print(error)
                zaezd_id = None
                self.signal_button.emit((self.mainwindow.ui.pushButton, 'Error', 'zaezd_id'))

            players_emit = []
            # Вставляем очки в БД
            try:
                for score in scores:
                    players_emit.append(
                        score
                    )
                    player_id = database.get_player_id_by_ext_id(str(score['id']))
                    if player_id is None:
                        self.signal_button.emit((self.mainwindow.ui.pushButton, 'Error', 'player_ext'))
                        continue
                    database.update_stat(zaezd_id, player_id, score['total'], score['score_1'], score['score_2'])
            except Exception as error:
                print(error)
                print(traceback.format_exc())
                self.signal_button.emit((self.mainwindow.ui.pushButton, 'Error', 'Scores'))

            # Вставляе Tricks в БД
            try:
                database.update_tricks(tricks, zaezd_id)
            except Exception as error:
                print(error)
                print(traceback.format_exc())
                self.signal_button.emit((self.mainwindow.ui.pushButton, 'Error', 'Tricks'))

            self.signal_player_stat.emit(players_emit)
            sleep(1.5)

        self.signal_button.emit((self.mainwindow.ui.pushButton, 'Finish', 'Live'))
