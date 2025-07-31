from playwright.sync_api import sync_playwright
from pathlib import Path
import csv


def parse_results_table():
    driver_path = "./chromium-1179/chrome-win/chrome.exe"
    url = "http://localhost:8080/displays/resultsSimple?fop=A"

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=driver_path)
        page = browser.new_page()
        page.goto(url)

        # Ждем загрузки таблицы
        page.wait_for_selector("table.results")

        # Получаем все строки с результатами
        rows = page.query_selector_all("table.results tr.athlete")

        results = []

        for row in rows:
            # Извлекаем данные из каждой колонки
            try:
                position = row.query_selector("td.start div").inner_text().strip()
                name = row.query_selector("td.name div").inner_text().strip()
                category = row.query_selector("td.category div").inner_text().strip()
                yob = row.query_selector("td.yob div").inner_text().strip()
                rank = row.query_selector("td.custom1 div").inner_text().strip()
                team = row.query_selector("td.club .clubName div").inner_text().strip()
            except Exception as e:
                print(f"Ошибка при извлечении основных данных: {e}")
                continue

            # Результаты рывка (первые 3 попытки после первого vspacer)
            snatch_results = []
            snatch_cells = row.query_selector_all(
                "xpath=.//td[contains(@class, 'fail') or contains(@class, 'good') or contains(@class, 'empty')][position() <= 3]")

            for cell in snatch_cells[:3]:  # Берем только первые 3 попытки
                try:
                    class_name = cell.get_attribute("class") or ""
                    weight = cell.query_selector("div").inner_text().strip()
                    if "fail" in class_name:
                        snatch_results.append(f"fail({weight})")
                    elif "good" in class_name:
                        snatch_results.append(f"good({weight})")
                    else:
                        snatch_results.append(weight)
                except:
                    snatch_results.append("")

            # Результаты толчка (последующие 3 попытки после второго vspacer)
            jerk_results = []
            jerk_cells = row.query_selector_all(
                "xpath=.//td[contains(@class, 'fail') or contains(@class, 'good') or contains(@class, 'empty')][position() > 3 and position() <= 6]")

            for cell in jerk_cells[:3]:  # Берем только первые 3 попытки толчка
                try:
                    class_name = cell.get_attribute("class") or ""
                    weight = cell.query_selector("div").inner_text().strip()
                    if "fail" in class_name:
                        jerk_results.append(f"fail({weight})")
                    elif "good" in class_name:
                        jerk_results.append(f"good({weight})")
                    else:
                        jerk_results.append(weight)
                except:
                    jerk_results.append("")

            # Сумма
            try:
                total = row.query_selector("td.total div").inner_text().strip()
            except:
                total = ""

            results.append({
                'Позиция': position,
                'ФИО': name,
                'Категория': category,
                'Год рождения': yob,
                'Разряд': rank,
                'Команда': team,
                'Рывок 1': snatch_results[0] if len(snatch_results) > 0 else '',
                'Рывок 2': snatch_results[1] if len(snatch_results) > 1 else '',
                'Рывок 3': snatch_results[2] if len(snatch_results) > 2 else '',
                'Толчок 1': jerk_results[0] if len(jerk_results) > 0 else '',
                'Толчок 2': jerk_results[1] if len(jerk_results) > 1 else '',
                'Толчок 3': jerk_results[2] if len(jerk_results) > 2 else '',
                'Сумма': total
            })

        print(results)
        browser.close()


if __name__ == "__main__":
    parse_results_table()