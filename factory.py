import traceback

import requests
import os
from urllib.parse import unquote, urlparse


def get_time(url: str):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }
    response = requests.get(url, timeout=1, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return int(data) // 60, int(data) % 60
    return None


def find_name_by_id(player_id: int, players: list):
    for player in players:
        if player['id'] == player_id:
            return player['first_name'], player['last_name']


def find_photo_by_id(player_id: int, players: list):
    for player in players:
        if player['id'] == player_id:
            return player['icon']


def create_packet_time(show: str, minutes: int, seconds: int):
    s = f'*/1/{show}/0/{minutes}/{seconds}/#'
    return s


def get_score_by_attempt(attempts_data, attempt):
    if attempts_data:
        for item in attempts_data:
            if item.get('attempt') == attempt:
                score = item.get('score')
                if score is not None:
                    # Если число (int или float), форматируем в строку с запятой
                    if isinstance(score, (int, float)):
                        return str(score).replace('.', ',')
                    # Если уже строка, просто возвращаем (можно добавить замену точки на запятую, если нужно)
                    return str(score)
                return 0
    return 0


def get_live_data(url: str, stage_type: str):
    data = requests.get(url, timeout=3).json()

    score_res = []
    tricks_res = []
    for stage in data['stages']:
        if stage['name'] == 'Квалификация':
            stage_kval_id = stage['id']
            res_kval = stage['results']
        elif stage['name'] == 'Финал':
            res_final = stage['results']
            stage_final_id = stage['id']

    stage_id = (lambda x: stage_kval_id if x == 'Квалификация' else stage_final_id)(stage_type)
    res = (lambda x: res_kval if x == 'Квалификация' else res_final)(stage_type)

    for player in res:
        score_res.append(
            {
                'id': str(player['user_id']),
                'score_1': get_score_by_attempt(player['attempts'], 1),
                'score_2': get_score_by_attempt(player['attempts'], 2),
                'total': str(player['total']),
            }
        )

    runs_final = [x for x in data['runs'] if x['stage_id'] == stage_id]

    for item in runs_final:
        tricks_res.append({
            'id': item['user_id'],
            'tricks': (lambda x: x if x else [])(item['tricks']),
            'attempt': item['attempt'],
        })

    return score_res, tricks_res


def find_user_index(data, user_id):
    for index, item in enumerate(data):
        if item.get('user_id') == user_id:
            return index + 1
    return None


def get_prematch_data(url: str, stage_type: str):

    data = requests.get(url, timeout=5).json()

    len_kval = 0
    stage_final_id = 0
    stage_kval_id = 0
    for stage in data['stages']:
        if stage['name'] == 'Квалификация':
            stage_kval_id = stage['id']
            len_kval = len(stage['results'])
        elif stage['name'] == 'Финал':
            stage_final_id = stage['id']

    players = []

    if stage_type == 'Финал':
        runs_final = [x for x in data['runs'][len_kval * 2::] if x['attempt'] == 1 and x['stage_id'] == stage_final_id]
        for stage in data['stages']:
            if stage['name'] == 'Финал':
                for player in stage['results']:
                    players.append({
                        'name': find_name_by_id(player['user_id'], data['participants'])[0],
                        'surname': find_name_by_id(player['user_id'], data['participants'])[1],
                        'id': player['user_id'],
                        'bib': find_user_index(runs_final, player['user_id']),
                        'photo': find_photo_by_id(player['user_id'], data['participants']),
                    })
    else:
        runs_kval = [x for x in data['runs'] if x['attempt'] == 1 and x['stage_id'] == stage_kval_id]

        for stage in data['stages']:
            if stage['name'] == 'Квалификация':
                for player in stage['results']:
                    players.append({
                        'name': find_name_by_id(player['user_id'], data['participants'])[0],
                        'surname': find_name_by_id(player['user_id'], data['participants'])[1],
                        'id': player['user_id'],
                        'bib': find_user_index(runs_kval, player['user_id']),
                        'photo': find_photo_by_id(player['user_id'], data['participants']),
                    })

    return players


def load_photo(d: list, base_road: str):
    res = []
    for player in d:

        if len(player['photo']) != 0:
            try:
                response = requests.get(player['photo'], stream=True)
                response.raise_for_status()
                filename = os.path.basename(unquote(urlparse(player['photo']).path))
                road_save = f'{base_road}/{filename}'
                player['road_save'] = road_save
                with open(road_save, 'wb') as file:
                    for chunk in response.iter_content(1024):
                        file.write(chunk)

                res.append({'id': player['id'], 'road_save': road_save})
            except:
                pass

    return res
