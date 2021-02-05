import csv
from bs4 import BeautifulSoup
from collections import namedtuple
import re
from selenium import webdriver
from configparser import ConfigParser


cfg = ConfigParser()
cfg.read("globals.cfg", encoding='utf-8')
group_name = cfg.get("main", "group_name")
middle_saving_csv = cfg.get("main", "middle_saving_csv")
web_driver = cfg.get("main", "web_driver")


def get_content(url, week_index):

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(web_driver, options=options)

    driver.get(url)
    requiredHtml = driver.page_source

    result = []
    soup = BeautifulSoup(requiredHtml, 'html5lib')

    g_data = soup.find_all(
        "div", {"class": "sc-container"})

    for item in g_data:

        day = item.find_all(
            "div", {"class": "sc-table-col sc-day-header sc-gray"})[0]
        date = day.contents[0]
        week_day = day.find_all("span", {"class": "sc-day"})[0].contents[0]
        content = item.find_all(
            "div", {"class": "sc-table sc-table-detail"})[0]
        lessons = content.find_all("div", {"class": "sc-table-row"})

        for lesson in lessons:

            lesson_time = lesson.find(
                "div", {"class": "sc-table-col sc-item-time"}).contents[0]

            lesson_type = lesson.find(
                "div", {"class": "sc-table-col sc-item-type"}).contents[0]

            lesson_name = lesson.find(
                "span", {"class": "sc-title"}).contents[0]

            try:
                lector = lesson.find(
                    "span", {"class": "sc-lecturer"}).contents[0]
            except Exception:
                lector = ''

            locations = lesson.find_all(
                "div", {"class": "sc-table-col sc-item-location"})
            locations = list(map(lambda x: re.sub(
                r'[\t\v\r\n\f]+', '', x.text).replace('\xa0', ''), locations))
            location = list(filter(lambda x: x, locations))[0]

            result.append([str(week_index),
                           f"{date}.21",
                           week_day,
                           lesson_time.split('–')[0].strip(),
                           lesson_time.split('–')[1].strip(),
                           lesson_type,
                           lesson_name,
                           lector,
                           location])

    return result


def run():
    lessons = []
    columns = ['week_index', 'lesson_date', 'week_day', 'lesson_time_start',
               'lesson_time_finish', 'lesson_type', 'lesson_name', 'lector', 'location']

    for i in range(1, 19):
        lessons += get_content(
            f"https://mai.ru/education/schedule/detail.php?group={group_name}&week={i}", i)

    with open(middle_saving_csv, 'w', encoding='utf-8', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',')
        spamwriter.writerow(columns)
        for lesson in lessons:
            spamwriter.writerow(lesson)


if __name__ == "__main__":
    run()
