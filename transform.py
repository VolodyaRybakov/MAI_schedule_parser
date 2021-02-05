import csv
import datetime as DT
from collections import namedtuple
from configparser import ConfigParser

from prettytable import PrettyTable

cfg = ConfigParser()
cfg.read("globals.cfg", encoding='utf-8')
schedule_file = cfg.get("main", "target_schedule_file")
middle_saving_csv = cfg.get("main", "middle_saving_csv")

Lesson = namedtuple(
    'Lesson', ['week_index', 'lesson_date', 'week_day', 'lesson_time_start', 'lesson_time_finish', 'lesson_type', 'lesson_name', 'lector', 'location'])

ShortLesson = namedtuple(
    'ShortLesson', ['lesson_type', 'lesson_name', 'lector', 'location'])

week_days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб']

open(schedule_file, 'w', encoding='utf-8').close()


class DaySchedule():
    def __init__(self, week_day):
        self.week_day = week_day
        self.first_week, self.second_week = get_dates(self.week_day)
        self.table = []
        self.schedule = {'09:00': {'first_week': {'lesson': set(), 'dates': set()},
                                   'second_week': {'lesson': set(), 'dates': set()}},
                         '10:45': {'first_week': {'lesson': set(), 'dates': set()},
                                   'second_week': {'lesson': set(), 'dates': set()}},
                         '13:00': {'first_week': {'lesson': set(), 'dates': set()},
                                   'second_week': {'lesson': set(), 'dates': set()}},
                         '14:45': {'first_week': {'lesson': set(), 'dates': set()},
                                   'second_week': {'lesson': set(), 'dates': set()}},
                         '16:30': {'first_week': {'lesson': set(), 'dates': set()},
                                   'second_week': {'lesson': set(), 'dates': set()}},
                         '18:15': {'first_week': {'lesson': set(), 'dates': set()},
                                   'second_week': {'lesson': set(), 'dates': set()}}
                         }
        self.finish_times = {'09:00': '10:30',
                             '10:45': '12:15',
                             '13:00': '14:30',
                             '14:45': '16:15',
                             '16:30': '18:00',
                             '18:15': '19:45'}

    def append(self, lesson: Lesson):
        if int(lesson.week_index) % 2:
            week = 'first_week'
        else:
            week = 'second_week'
        self.schedule[lesson.lesson_time_start][week]['lesson'].add(ShortLesson(
            lesson.lesson_type, lesson.lesson_name, lesson.lector, lesson.location))
        self.schedule[lesson.lesson_time_start][week]['dates'].add(
            lesson.lesson_date)

    def __get_sorted_schedule(self):
        self.table = []

        for time_start in self.schedule:

            for week_counter in self.schedule[time_start]:
                lesson_info = [self.week_day,
                               f"{time_start}-{self.finish_times[time_start]}"]

                tmp = self.schedule[time_start][week_counter]
                lesson = ShortLesson('', '', '', '') if not len(
                    tmp['lesson']) else list(tmp['lesson'])[0]

                lesson_info.append(1 if week_counter == 'first_week' else 2)
                lesson_info.append(lesson.lesson_type)
                lesson_info.append(lesson.lesson_name)
                lesson_info.append(lesson.lector)
                lesson_info.append(lesson.location)

                chk_dates = self.first_week if week_counter == 'first_week' else self.second_week

                except_for = list(chk_dates.difference(
                    tmp['dates']))  # Кроме указанных
                only = list(tmp['dates'].intersection(chk_dates))  # Только эти

                except_for.sort(
                    key=lambda x: DT.datetime.strptime(x, '%d.%m.%y'))
                only.sort(key=lambda x: DT.datetime.strptime(x, '%d.%m.%y'))

                if len(tmp['dates']) == len(chk_dates):
                    dates = 'Все дни'
                elif not len(tmp['dates']):
                    dates = ''
                elif len(except_for) < len(only):
                    dates = f"Кроме {', '.join([x[:-3] for x in except_for])}"
                elif len(except_for) >= len(only):
                    dates = f"Только {', '.join([x[:-3] for x in only])}"
                else:
                    dates = ''

                lesson_info.append(dates)

                self.table.append(lesson_info)

    def get_ptable(self):
        self.__get_sorted_schedule()

        x = PrettyTable()
        x.field_names = ["Week day", "Time", "Week index",
                         "Lesson type", "Lesson name", "Lector", "Location", "Dates"]

        for lesson in self.table:
            x.add_row(lesson)

        print(x)

    def get_latex_table(self):

        self.__get_sorted_schedule()

        with open(schedule_file, 'a', encoding='utf-8') as f:
            f.write(
                "\\begin{tabular}{|p{1cm}|p{2.1cm}|p{0.7cm}|p{1cm}|p{9cm}|p{4cm}|p{2.5cm}|p{2.5cm}|}\n")
            f.write("\\hline\n")
            f.write(
                "День нед. & Время & № нед. & Тип & Название & Преподаватель & Ауд. & Даты \\\\\n")
            f.write("\\hhline{|=|=|=|=|=|=|=|=|}\n")
            for i, item in enumerate(self.table):
                if i == 0:
                    row = "\\multirow{12}{*}{%s} & \\multirow{2}{*}{%s} & %s & %s & %s & %s & %s & %s" % (
                        item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7])
                else:
                    if i % 2:
                        row = "\\cline{3-8} & & %s & %s & %s & %s & %s & %s" % (
                            item[2], item[3], item[4], item[5], item[6], item[7])
                    else:
                        row = "\\cline{2-8} & \\multirow{2}{*}{%s} & %s & %s & %s & %s & %s & %s" % (
                            item[1], item[2], item[3], item[4], item[5], item[6], item[7])
                row += "\\\\"
                f.write(f"{row}\n")
            f.write("\\hline\n\\end{tabular}\n\\newpage\n\n")


def get_dates(week_day):
    week_day_number = 0
    for i, w_d in enumerate(week_days):
        if w_d == week_day:
            week_day_number = i

    date_fmt = '%d.%m.%y'
    step = DT.timedelta(days=7)
    init_step = DT.timedelta(days=week_day_number)
    start_date = DT.datetime.strptime('08.02.21', date_fmt) + init_step
    last_date = DT.datetime.strptime('13.06.21', date_fmt) + init_step

    first_week = set()
    second_week = set()
    i = 1
    while start_date <= last_date:
        if i % 2:
            first_week.add(start_date.strftime(date_fmt))
        else:
            second_week.add(start_date.strftime(date_fmt))

        i += 1
        start_date += step

    return (first_week, second_week)


def run():
    results = []
    with open(middle_saving_csv, encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            results.append(row)

    lessons = []
    for lesson in results[1:]:
        lessons.append(Lesson(week_index=lesson[0],
                              lesson_date=lesson[1],
                              week_day=lesson[2],
                              lesson_time_start=lesson[3],
                              lesson_time_finish=lesson[4],
                              lesson_type=lesson[5],
                              lesson_name=lesson[6],
                              lector=lesson[7],
                              location=lesson[8]))

    schedule_by_week_days = []
    for i, w_d in enumerate(week_days):
        schedule_by_week_days.append(
            list(filter(lambda x: x.week_day == w_d, lessons)))

    day_schedules = []
    for i, day in enumerate(schedule_by_week_days):
        s_schedule = DaySchedule(week_days[i])
        for lesson in day:
            s_schedule.append(lesson)
        day_schedules.append(s_schedule)

    for schedule in day_schedules:
        # schedule.get_table()
        schedule.get_latex_table()


if __name__ == "__main__":
    run()
