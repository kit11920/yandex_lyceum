import sys
import sqlite3
from random import choice, randrange
from PyQt5 import uic
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QTableWidgetItem,
                             QColorDialog, QButtonGroup, QPushButton, QListWidgetItem, QCheckBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QPixmap, QColor

from ui_habits_event import Ui_Form


# ошибка
class MakingError(Exception):
    pass


# считываем слова друга на главном окне----
f = open('friends_words.txt', encoding='utf-8')
WORDS = f.readlines()
f.close()
# -------


# класс загрузки дизайна
class Ui_main(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('interface1.ui', self)
        self.bd = sqlite3.connect('Motivating dairy bd.sqlite')


# виджет home в стеке виджетов ------
class Widgets_in_stack_home(Ui_main):
    def __init__(self):
        super().__init__()

        # checkbox в таблице отвечает за выполненность события
        self.checkbox_groupe = QButtonGroup()
        self.checkbox_groupe.setExclusive(False)
        self.checkbox_groupe.buttonClicked.connect(self.event_done)

        self.checkbox_done = dict()

        self.stackedWidget.currentChanged.connect(self.change_words)

        # ---- установка фразы друга -----
        self.words = choice(WORDS)
        self.f_words.setText(self.words)
        # -----

        # показывает выбранную дату в dateEdit
        self.clndr_home.selectionChanged.connect(self.show_day)

        # ---- регулировка окна 'создать событие' -----
        self.make_event_btn.clicked.connect(self.show_make_event)
        # -----

        # ---- заполняем таблицу с событиями
        self.fill_table_event()

        # ---- обновить таблицу ивентов
        self.update_events_btn.clicked.connect(self.update_events)

        # кнопка показать все
        self.show_all_btn.clicked.connect(self.update_events)

        # показывает события на выбранную дату
        self.clndr_home.selectionChanged.connect(self.events_on_date)

    def events_on_date(self):
        date_bg = self.clndr_home.selectedDate().toString(format=Qt.ISODate)
        date_end = self.clndr_home.selectedDate().addDays(1)
        date_end = date_end.toString(format=Qt.ISODate)
        self.fill_table_event(date_bg + ' 00:00:00', date_end + ' 00:00:00')

    # ---- смена фраз друга -----
    def change_words(self):
        self.words = choice(WORDS)
        self.f_words.setText(self.words)

    # ---- показывает окно создания события -----
    def show_make_event(self):
        self.make_event_w = Make_event(self.clndr_home.selectedDate())
        # передаем дату из календаря
        self.make_event_w.dateEdit_bedin.setDate(self.clndr_home.selectedDate())
        self.make_event_w.dateEdit_end.setDate(self.clndr_home.selectedDate())

        if self.make_event_w.isVisible():
            self.make_event_w.hide()
        else:
            self.make_event_w.show()

    # ----- edit показывает выделенную в календаре дату ----
    def show_day(self):
        ca = self.clndr_home.selectedDate()
        self.dateEdit.setDate(ca)

    # ----- создание таблицы событий -----
    def fill_table_event(self, date_cond_bg=None, date_cond_end=None):
        if date_cond_bg is None or date_cond_end is None:
            result = self.bd.cursor().execute('SELECT * FROM events WHERE done = 0').fetchall()
        else:
            result = result = self.bd.cursor().execute(
                f'SELECT * FROM events WHERE dt_begin >= "{date_cond_bg}" AND '
                f'dt_end <= "{date_cond_end}" AND done = 0').fetchall()

        if len(result) == 0:
            self.table_event.clearContents()
            self.table_event.setRowCount(0)
        else:
            self.table_event.setRowCount(len(result))
            self.table_event.setColumnCount(len(result[0]) - 2)

            for i, elem in enumerate(result):
                id, name, begin, end, type, done = tuple(elem)
                color = self.bd.cursor().execute(
                    f'SELECT typeColor from event_types '
                    f'WHERE typeID = (SELECT type from events WHERE eventID = {id})').fetchone()[0]

                show_elem = [name, begin, end]
                for j, val in enumerate(show_elem):
                    self.table_event.setItem(i, j, QTableWidgetItem(str(val)))
                    self.table_event.item(i, j).setBackground(QColor(color))

                done_chbox = QCheckBox()
                self.checkbox_groupe.addButton(done_chbox)
                self.checkbox_done[done_chbox] = id
                self.table_event.setCellWidget(i, j + 1, done_chbox)

            title = ['название', 'начало', 'конец', 'сделано']
            self.table_event.setHorizontalHeaderLabels(title)
            self.table_event.resizeColumnsToContents()

    def update_events(self):
        self.table_event.clear()
        self.fill_table_event()

    def event_done(self, btn):
        if btn in self.checkbox_done.keys():
            id = self.checkbox_done[btn]
            self.bd.cursor().execute(f'UPDATE events SET done = 1 WHERE eventID = {id}')
            self.bd.commit()


# окно по созданию ивентаи и занесению его в список
class Make_event(QMainWindow):
    def __init__(self, date):
        super().__init__()
        uic.loadUi('make_event2.ui', self)

        self.bd = sqlite3.connect('Motivating dairy bd.sqlite')

        self.dateEdit_bedin.setDate(date)
        next_day = date.addDays(1)
        next_day.addDays(1)
        self.dateEdit_end.setDate(next_day)

        # ---- скрывает и показывает строку время при настройке --------
        self.time_rbtn.setChecked(True)
        self.buttonGroup.buttonClicked.connect(self.show_timeedit)
        # -----------

        # ---- event types -----
        self.get_event_types()
        self.select_type.addItems(self.event_types.keys())
        self.select_type.setStyleSheet(f'background: {self.event_types[self.select_type.currentText()]}')
        self.select_type.currentTextChanged.connect(self.color_combobox)
        # ----

        self.create_end.clicked.connect(self.create_event)

    def get_event_types(self):
        tab_types = self.bd.cursor().execute('select * from event_types').fetchall()
        self.event_types = dict()
        for i in range(len(tab_types)):
            # состав: ключ - название, внутри - цвет и id
            self.event_types[tab_types[i][1]] = [tab_types[i][2], tab_types[i][0]]


    # создать ивент
    def create_event(self):
        try:
            # ---- берем все параметры -----
            name = self.name_event.text()
            # имя события не может быть пустым
            if name == '':
                raise MakingError('Невозможное имя для события')

            type = self.bd.cursor().execute(f'select typeID from event_types '
                                            f'where typeName = '
                                            f'"{self.select_type.currentText()}"').fetchone()[0]

            date_begin = self.dateEdit_bedin.date().toString(format=Qt.ISODate)
            date_end = self.dateEdit_end.date().toString(format=Qt.ISODate)
            if self.time_rbtn.isChecked():  # если время указывали
                time_begin = self.timeEdit_begin.time().toString(format=Qt.ISODate)
                time_end = self.timeEdit_end.time().toString(format=Qt.ISODate)
            else:
                time_begin = time_end = '00:00:00'
            dt_begin = date_begin + ' ' + time_begin
            dt_end = date_end + ' ' + time_end
            # --------

            self.bd.cursor().execute(f'INSERT INTO events (name, dt_begin, dt_end, type, done) '
                                     f'VALUES ("{name}", "{dt_begin}", "{dt_end}", {type}, 0)')
            self.bd.commit()
            self.hide()
        except MakingError as e:
            self.statusBar().showMessage(f'MakingError: {str(e)}')

    # скрывает и показывает строку время при настройке
    def show_timeedit(self):
        if self.time_rbtn.isChecked():
            self.timeEdit_begin.show()
            self.timeEdit_end.show()
        else:
            self.timeEdit_begin.hide()
            self.timeEdit_end.hide()

    # изменяет цвет combobox при смене типа
    def color_combobox(self):
        self.select_type.setStyleSheet(f'background: {self.event_types[self.select_type.currentText()][0]}')
        con = sqlite3.connect('')


class Widgets_in_stack_motivator(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('motivator.ui', self)


        self.generat_btn.clicked.connect(self.generate)

    def generate(self):
        fname = 'motivating pict/' + str(randrange(1, 13)) + '.png'
        pixmap = QPixmap(fname)
        # pixmap = pixmap.scaledToHeight(300)
        self.picture_m.setPixmap(pixmap)
        pixmap.save('motivating pict/now_pic.png')


# виджет окна одной привычки-календарь
class Habbits(QWidget, Ui_Form):
    def __init__(self, id_hbt, name_hbt, color_hbt):
        super().__init__()
        self.setupUi(self)  # загружаем дизайн
        self.bd = sqlite3.connect('Motivating dairy bd.sqlite')

        self.id_hbt = id_hbt
        self.color_hbt = color_hbt
        self.calendarWidget.get_hbt_id_color(id_hbt, color_hbt)

        self.name_hbt_label.setText(name_hbt)

        # в dateEdit по умолканию сегодняшняя дата
        self.dateEdit.setDate(self.calendarWidget.selectedDate())

        self.calendarWidget.selectionChanged.connect(self.show_day)
        self.add_hbt_btn.clicked.connect(self.add_hbt)
        self.delet_btn.clicked.connect(self.del_hbt)

    # добавляет день к оторый было совершено отслеживаемое дело
    def add_hbt(self):
        new_date = self.dateEdit.date().toString(format=Qt.ISODate)
        self.bd.cursor().execute(f'INSERT INTO list_date_habits(date, habitID) '
                                 f'VALUES("{new_date}", {self.id_hbt})')
        self.bd.commit()

    def del_hbt(self):
        d_date = self.calendarWidget.selectedDate().toString(format=Qt.ISODate)
        self.bd.cursor().execute(f'DELETE FROM list_date_habits '
                                 f'WHERE date = "{d_date}" and habitID = {self.id_hbt}')
        self.bd.commit()

    # показывает в dateEdit выбранное число
    def show_day(self):
        ca = self.calendarWidget.selectedDate()
        self.dateEdit.setDate(ca)


class TimeTable(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('timetable_ui.ui', self)
        self.bd = sqlite3.connect('Motivating dairy bd.sqlite')

        self.make_table()
        self.tableWidget.itemChanged.connect(self.save_item)

        self.update_btn.clicked.connect(self.update_table)
        self.add_row_btn.clicked.connect(self.add_row)
        self.delete_row_btn.clicked.connect(self.delete_row)
        self.color_cell_btn.clicked.connect(self.color_cell)
        self.color_event_btn.clicked.connect(self.color_event)

    # загрузка таблицы
    def make_table(self):
        data = self.bd.cursor().execute('SELECT column, row, name_tt, color_tt FROM time_table_bd').fetchall()
        for i, row in enumerate(data):
            r = row[1]
            c = row[0]

            if self.tableWidget.rowCount() <= r:
                self.tableWidget.setRowCount(r + 1)

            name = row[2]
            self.tableWidget.setItem(r, c, QTableWidgetItem(name))
            color = row[3]
            if (not color is None) and color != '':
                self.tableWidget.item(r, c).setBackground(QColor(color))

            self.tableWidget.setHorizontalHeaderLabels(['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС'])
            self.tableWidget.resizeColumnsToContents()

    def update_table(self):
        self.tableWidget.clear()
        self.make_table()

    # когда ячейка менятся это тут же сохр на bd
    def save_item(self, item):
        row = self.tableWidget.row(item)
        column = self.tableWidget.column(item)

        self.bd.cursor().execute(f'UPDATE time_table_bd SET name_tt = "{item.text()}" WHERE row = {row} AND column = {column}')
        self.bd.commit()

    def add_row(self):
        r = self.tableWidget.rowCount()
        self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)

        for i in range(7):  # 7 т к 7 дней недели
            self.bd.cursor().execute(f'INSERT INTO time_table_bd (column, row) VALUES ({i}, {r})')
        self.bd.commit()

    def delete_row(self):
        r = self.tableWidget.rowCount() - 1
        self.tableWidget.setRowCount(self.tableWidget.rowCount() - 1)

        for i in range(7):  # 7 т к 7 дней недели
            self.bd.cursor().execute(f'DELETE FROM time_table_bd WHERE row = {r}')
        self.bd.commit()

    def color_cell(self):
        item = self.tableWidget.selectedItems()
        if len(item) != 0:
            item = item[0]
            r = self.tableWidget.row(item)
            c = self.tableWidget.column(item)

            color = QColorDialog.getColor()
            if color.isValid():
                color = color.name()
                self.bd.cursor().execute(
                    f'UPDATE time_table_bd SET color_tt = "{color}" WHERE row = {r} AND column = {c}')
                self.bd.commit()

    def color_event(self):
        item = self.tableWidget.selectedItems()
        if len(item) != 0:
            item = item[0]
            r = self.tableWidget.row(item)
            c = self.tableWidget.column(item)
            name = item.text()

            color = QColorDialog.getColor()
            if color.isValid():
                color = color.name()
                self.bd.cursor().execute(
                    f'UPDATE time_table_bd SET color_tt = "{color}" WHERE row = {r} AND column = {c}')
                self.bd.cursor().execute(
                    f'UPDATE time_table_bd SET color_tt = "{color}" WHERE name_tt = "{name}"')
                self.bd.commit()


class Settings(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('settings_ui.ui', self)

        self.select_friend_wgt = SelectFriend()
        self.change_btn.clicked.connect(self.open_select_friend_wgt)

        self.change_types_wgt = EventTypesChange()
        self.change_types_btn.clicked.connect(self.open_change_types_wgt)

        self.change_habbit_wgt =Habbits_list()
        self.change_habbits_btn.clicked.connect(self.open_change_habbits)

    def open_select_friend_wgt(self):
        if not self.select_friend_wgt.isVisible():
            self.select_friend_wgt.show()

    def open_change_types_wgt(self):
        if not self.change_types_wgt.isVisible():
            self.change_types_wgt.show()

    def open_change_habbits(self):
        if not self.change_habbit_wgt.isVisible():
            self.change_habbit_wgt.show()


class EventTypesChange(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('change_type_event_ui.ui', self)
        self.bd = sqlite3.connect('Motivating dairy bd.sqlite')

        self.color = QColor()

        self.fill_list_wgt()
        self.color_btn.clicked.connect(self.get_color)
        self.add_type_btn.clicked.connect(self.add_type)
        self.delete_btn.clicked.connect(self.delete_type)

    def fill_list_wgt(self):
        types = self.bd.cursor().execute('SELECT typeName, typeColor FROM EVENT_TYPES').fetchall()

        for i in range(len(types)):
            one_type = QListWidgetItem(types[i][0])
            one_type.setBackground(QColor(types[i][1]))
            self.listWidget.addItem(one_type)

    def get_color(self):
        self.color = QColorDialog.getColor()
        if self.color.isValid():
            self.name_btn.setStyleSheet(f'background-color: {self.color.name()}')

    def add_type(self):
        name = self.name_btn.text()
        if not self.color.isValid():
            color = '#ffffff'
        else:
            color = self.color.name()

        all_names = self.bd.cursor().execute('SELECT typeName from event_types').fetchall()
        for i in range(len(all_names)):
            all_names[i] = all_names[i][0]

        if name not in all_names:
            self.bd.cursor().execute(f'INSERT INTO event_types(typeName, typeColor) VALUES("{name}", "{color}")')
            self.bd.commit()

            self.listWidget.clear()
            self.fill_list_wgt()
        else:
            self.error_label.setText('Событие с таким названием уже существует')

    def delete_type(self):
        list_to_delete = self.listWidget.selectedItems()
        for to_delete in list_to_delete:
            name = to_delete.text()
            self.bd.cursor().execute(
                f'UPDATE events SET type = 1 '
                f'WHERE type = (SELECT typeID FROM event_types WHERE typeName = "{name}")')
            self.bd.cursor().execute(f'DELETE from event_types WHERE typeName = "{name}"')
            self.bd.commit()

        self.listWidget.clear()
        self.fill_list_wgt()


class SelectFriend(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('select_friend_ui.ui', self)

        self.fname = 'now'

        self.all_pics = ['cloud11', 'cloud2', 'cloud3']
        self.ind = 0

        self.next_btn.clicked.connect(self.next_pic)
        self.select_btn.clicked.connect(self.select)

    def next_pic(self):
        self.ind += 1
        self.ind = self.ind % 3
        self.fname = self.all_pics[self.ind]
        pm = QPixmap('friend/' + self.fname + '.png')
        self.label_pic.setPixmap(pm)

    def select(self):
        pm = QPixmap('friend/' + self.fname + '.png')
        pm.save('friend/now.png')
        # сохраним мини версию
        pm = QPixmap('friend/' + self.fname + '_mini.png')
        pm.save('friend/now_mini.png')
        self.hide()


class Habbits_list(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('change_habbits_ui.ui', self)
        self.bd = sqlite3.connect('Motivating dairy bd.sqlite')

        self.hbt_to_delete = None

        self.fill_list()
        self.delete_btn.clicked.connect(self.delete_habbit)

    def fill_list(self):
        habbits = self.bd.cursor().execute('SELECT habitsName FROM habits')
        for one in habbits:
            self.listWidget.addItem(one[0])

    def delete_habbit(self):
        self.hbt_to_delete = self.listWidget.selectedItems()[0].text()
        self.bd.cursor().execute(f'DELETE FROM habits WHERE habitsName = "{self.hbt_to_delete}"')
        self.bd.commit()

        self.listWidget.clear()
        self.fill_list()


# окно приложения от которого открывается доступ к виджетам в стеках
# оболочка с открвающимся мень в которой находятва стеки
# каждый виджет в стеке определяется своим классом, который является для этого родителем
class Main_calendar(Widgets_in_stack_home):
    def __init__(self):
        super().__init__()

        # сприсок окон-кнопок привычек
        # HABBITS[название привычки] = [id, color]
        self.HABBITS = dict()
        self.HABBITS_WGT = dict()
        # self.BUTTONS_HBTS = list()
        self.btn_group_hbts = QButtonGroup()  #

        # ---- регулировка открывающегося меню -----
        self.menu_open = False
        self.menu_frame.hide()
        self.menu_btn.clicked.connect(self.open_menu)
        # -----

        # ---- регулировка открывающегося списка привычек -----
        self.habits_btn_open = False
        self.habits_widget.hide()
        self.habits_btn.clicked.connect(self.open_habits_widget_groupe)
        # -----

        # --- закрепить непостоянные кнопки окон приычек
        self.remake_habbits_widget()

        # --- в стеке виджетов, первым будет показываться осн календарь -----
        self.stackedWidget.setCurrentWidget(self.home)

        # создаем окно настроек
        self.settings = Settings()
        self.stackedWidget.addWidget(self.settings)

        # создаем окно мотиватора
        self.motivator_wgt = Widgets_in_stack_motivator()
        self.stackedWidget.addWidget(self.motivator_wgt)

        # создаем окно расписания
        self.timetable_wgt = TimeTable()
        self.stackedWidget.addWidget(self.timetable_wgt)

        # описсываем кнопки меню
        self.settings_btn.clicked.connect(self.show_settings)
        self.timetable_btn.clicked.connect(self.show_timetable)
        self.motivator_btn.clicked.connect(self.show_motivator)
        self.home_btn.clicked.connect(self.show_home)

        # кнопка обновления, чтобы показывал появившиеся кнопки окон привычек
        self.update_btn.clicked.connect(self.update_btns)

        # открыть окно создания колендаря привычек
        self.make_habit_btn.clicked.connect(self.make_habit)

        # открытие окна привычек
        self.btn_group_hbts.buttonClicked.connect(self.open_window_habbit)

        # конпка удаления окна привычек в окне настроек привычек
        self.settings.change_habbit_wgt.delete_btn.clicked.connect(self.hide_btn_deleted_habbit)  #########################3

    # спрятать кнопку удаленного окна привычек
    def hide_btn_deleted_habbit(self):
        name = self.settings.change_habbit_wgt.hbt_to_delete
        if not name is None:
            btns = self.btn_group_hbts.buttons()
            for btn in btns:
                if btn.text() == name:
                    btn.hide()
                    self.btn_group_hbts.removeButton(btn)

    def show_settings(self):
        self.stackedWidget.setCurrentWidget(self.settings)

    def show_timetable(self):
        self.timetable_wgt.friend_2.setPixmap(QPixmap('friend/now_mini.png'))
        self.stackedWidget.setCurrentWidget(self.timetable_wgt)

    def show_motivator(self):
        self.motivator_wgt.label_2.setPixmap(QPixmap('friend/now_mini.png'))
        self.stackedWidget.setCurrentWidget(self.motivator_wgt)

    def show_home(self):
        self.friend_2.setPixmap(QPixmap('friend/now.png'))
        self.stackedWidget.setCurrentWidget(self.home)

    def make_habit(self):
        self.habbits_maker = MakeHabbits()
        if not self.habbits_maker.isVisible():
            self.habbits_maker.show()

        # когда была созадана новая привычка
        self.habbits_maker.make_habit.clicked.connect(self.habbit_made)

    def habbit_made(self):
        self.settings.change_habbit_wgt.listWidget.clear()
        self.settings.change_habbit_wgt.fill_list()

    def open_window_habbit(self, btn):
        self.HABBITS_WGT[btn.text()].label_2.setPixmap(QPixmap('friend/now_mini.png'))
        self.stackedWidget.addWidget(self.HABBITS_WGT[btn.text()])
        self.stackedWidget.setCurrentWidget(self.HABBITS_WGT[btn.text()])

    def update_btns(self):
        self.remake_habbits_widget()

    def remake_habbits_widget(self):
        # все книпки обращения к окнам календарей привычек в группе
        # self.btn_group_hbts = QButtonGroup()

        hbts_widgets = self.bd.cursor().execute('SELECT * FROM habits').fetchall()

        for i in range(len(hbts_widgets)):
            hbt_name = hbts_widgets[i][1]
            hbt_id = hbts_widgets[i][0]
            hbt_color = hbts_widgets[i][2]
            if hbt_name not in self.HABBITS.keys():
                # HABBITS[название привычки] = [id, color]
                self.HABBITS[hbt_name] = [hbt_id, hbt_color]
                # HABBITS_WGT[название привычки] = [class Habbits]
                self.HABBITS_WGT[hbt_name] = Habbits(hbt_id, hbt_name, hbt_color)

                self.btn = QPushButton(self)
                self.btn.setText(hbt_name)
                self.btn_group_hbts.addButton(self.btn)

                self.layout_btn_hbts.addWidget(self.btn)

    # регулирует открывающееся меню
    def open_menu(self):
        if self.menu_open:
            self.menu_frame.hide()
            self.menu_open = False
        else:
            self.menu_frame.show()
            self.menu_open = True

    # регулирует открывающийся список привычек в окне возможностей
    def open_habits_widget_groupe(self):
        if self.habits_btn_open:
            self.habits_widget.hide()
            self.habits_btn_open = False
        else:
            self.habits_widget.show()
            self.habits_btn_open = True


class MakeHabbits(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('make_habits_event.ui', self)
        self.bd = sqlite3.connect('Motivating dairy bd.sqlite')

        self.color = None

        self.select_color_btn.clicked.connect(self.select_color)
        self.make_habit.clicked.connect(self.make_habbit)

    def select_color(self):
        self.color = QColorDialog.getColor()
        if self.color.isValid():
            self.color_show.setStyleSheet(f'background: {self.color.name()}')

    def make_habbit(self):
        try:
            name = self.name.text()
            if name == '':
                raise MakingError('Невозможное имя для календаря привычек')

            all_names = self.bd.cursor().execute('SELECT habitsName FROM habits').fetchall()
            for i in range(len(all_names)):
                all_names[i] = all_names[i][0]

            if name in all_names:
                raise MakingError('Привычка с таким именем уже существует')

            if not self.color or not self.color.isValid():
                raise MakingError('Выберите цвет')

            self.bd.cursor().execute('INSERT INTO habits(habitsName, color) VALUES(?, ?)',
                                     (name, self.color.name()))
            self.bd.commit()
            self.hide()

        except MakingError as e:
            self.statusBar().showMessage(f'MakingError: {e}')


def exept_hooks(cls, exeption, trades):
    sys.__excepthook__(cls, exeption, trades)


if __name__ == '__main__':
    sys.excepthook = exept_hooks
    app = QApplication(sys.argv)
    main = Main_calendar()
    main.show()
    sys.exit(app.exec())
