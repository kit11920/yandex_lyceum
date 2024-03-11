from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
import sqlite3

class MyCalendar(QtWidgets.QCalendarWidget):
    def __init__(self, parent=None):
        QtWidgets.QCalendarWidget.__init__(self, parent)
        self.bd = sqlite3.connect('Motivating dairy bd.sqlite')
        self.hbt_id = -1
        self.hbt_color = QtGui.QColor()

    def paintCell(self, painter, rect, date):
        QtWidgets.QCalendarWidget.paintCell(self, painter, rect, date)

        if self.hbt_id != -1:
            dates = self.bd.cursor().execute(f'SELECT date FROM list_date_habits '
                                             f'WHERE habitID = {self.hbt_id}').fetchall()

            for i in range(len(dates)):
                dates[i] = dates[i][0]

            if date.toString(format=QtCore.Qt.ISODate) in dates:

                # painter.setBrush(QtGui.QColor(0, 20, 200, 50)) - оригинал без просветов
                painter.setBrush(self.hbt_color)
                painter.setPen(QtGui.QColor(0, 0, 0, 0))  #убираем рамку
                painter.drawRect(rect)


    def get_hbt_id_color(self, id_, color_):
        self.hbt_id = id_
        self.hbt_color.setNamedColor(color_)
        self.hbt_color.setAlpha(190)


