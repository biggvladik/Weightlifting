import pyodbc


class Data:
    def __init__(self, road):
        self.static_road = 'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + road
        self.conn = pyodbc.connect(self.static_road)

    def update_stat(self, zaezd_id, player_id, points, score_1, score_2):
        cursor = self.conn.cursor()

        sql_update = """
                        UPDATE ZaezdMaps SET ZaezdPlayerPoints = ?,ZaezdPlayerPointsSum = ?,
                        ZaezdPlayerPoint_1 = ?, ZaezdPlayerPoint_2 = ?
                        WHERE ZaezdID = ? AND ZaezdPlayerID = ?
                     """
        if points:
            points = str(points).replace('.', ',')

        cursor.execute(sql_update, (
            points, points,
            score_1, score_2,
            zaezd_id, player_id)
                       )
        cursor.commit()
        cursor.close()

    def clear_table(self):
        cursor = self.conn.cursor()

        sql = """
                        DELETE * From StatisticNew
                      """
        cursor.execute(sql)
        cursor.commit()
        cursor.close()

    def get_current_zaezd(self):
        cursor = self.conn.cursor()
        sql = "SELECT ZaezdID from Zaezd WHERE ZaezdCurrent = ?"
        res = cursor.execute(sql, -1).fetchone()
        cursor.close()
        if res is not None and len(res) == 1:
            return res[0]

        return None

    def get_player_id_by_ext_id(self, player_id_ext: str):
        cursor = self.conn.cursor()
        sql_select = """
                        SELECT PlayerID FROM Players WHERE PlayerID_EXT = ?
                     """
        player_id = cursor.execute(sql_select, player_id_ext).fetchone()
        if player_id is None:
            return None
        return player_id[0]

    def insert_player(self, item: dict):
        cursor = self.conn.cursor()
        sql_update = """
                UPDATE Players SET PlayerID_EXT = ? WHERE F = ? AND I = ?
              """
        sql_insert = """
                        INSERT into Players (PlayerID_EXT,F,I) VALUES (?,?,?)
                     """
        check_player = self.get_player_id_by_ext_id(item['id'])
        if check_player is None:
            cursor.execute(sql_insert, (item['id'], item['surname'].upper(), item['name'].title()))
        else:
            cursor.execute(sql_update, (item['id'], item['surname'].upper(), item['name'].title()))

        cursor.commit()
        cursor.close()

    def insert_player_zaezdmaps(self, zaezd_id: str, player_id_ext: str, position: int):
        cursor = self.conn.cursor()
        sql_check = """SELECT ZaezdID FROM ZaezdMaps WHERE  ZaezdID = ? AND ZaezdPlayerID = ?"""

        sql_insert = """ INSERT INTO ZaezdMaps (ZaezdID,ZaezdPlayerID,ZaezdPlayerPosition) VALUES (?,?,?)"""

        player_id = self.get_player_id_by_ext_id(str(player_id_ext))
        check = cursor.execute(sql_check, (zaezd_id, player_id)).fetchone()
        if check is None:
            cursor.execute(sql_insert, (zaezd_id, player_id, position))

        cursor.commit()
        cursor.close()

    def clear_database(self, tables):
        cursor = self.conn.cursor()
        for table in tables:
            sql = f"""Delete from {table}"""
            cursor.execute(sql)

        self.conn.commit()

    def update_tricks(self, data: list, zaezd_id: str):
        cursor = self.conn.cursor()

        sql_check = """
                        SELECT ZaezdID FROM Tricks
                        WHERE ZaezdID = ? AND PlayerID = ? AND Attempt = ? AND TrickCode = ? AND TrickTime = ?
                    """
        sql_insert = """
                        INSERT INTO Tricks (ZaezdID,PlayerID,Attempt,TrickOrder,TrickName, TrickCode,TrickTime)
                        VALUES (?,?,?,?,?,?,?)
                     """
        for player in data:
            player_id = self.get_player_id_by_ext_id(player['id'])

            for trick_number, trick in enumerate(player['tricks'], start=1):
                flag_check = cursor.execute(sql_check, (
                    zaezd_id, player_id, player['attempt'], trick['code'], trick['time'])
                                            ).fetchone()
                if not flag_check:
                    cursor.execute(sql_insert, (
                        zaezd_id, player_id, player['attempt'], trick_number, trick['name'], trick['code'],
                        trick['time']
                    ))
        cursor.commit()
        cursor.close()

    def update_foto(self, data: list):
        cursor = self.conn.cursor()

        sql_update = """
                       UPDATE Players SET Foto = ? WHERE PlayerID_EXT = ? 
                    """

        for player in data:
            cursor.execute(sql_update, (player['road_save'], player['id']))

        cursor.commit()
        cursor.close()
