import datetime
import sys

from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem, QPushButton, QMessageBox

from qt.AddExcelSource import AddExcelSource
from qt.AddFieldsMap import AddFieldsMap
from qt.AddMongoSource import AddMongoSource
from qt.AddMssqlSource import AddMssqlSource
from qt.AddMysqlSource import AddMysqlSource
from qt.UI.MainWindow import Ui_MainWindow
from qt.SetTarget import SetTarget
from core.Task import Task
from matplotlib import pyplot as plt


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.target = None
        self.sources = []

        self.textEdit.setReadOnly(True)
        self.textEdit.setReadOnly(True)
        self.textEdit.setText('未连接')
        self.pushButton.clicked.connect(self.set_target)
        self.pushButton_2.setEnabled(False)
        self.pushButton_4.setEnabled(False)
        self.pushButton_5.setEnabled(False)
        self.pushButton_6.setEnabled(False)
        self.pushButton_2.clicked.connect(self.add_mssql_source)

        self.pushButton_4.clicked.connect(self.add_mysql_source)
        self.pushButton_6.clicked.connect(self.add_mongo_source)
        self.pushButton_5.clicked.connect(self.add_excel_source)
        self.pushButton_3.clicked.connect(self.merge)
        self.pushButton_3.setEnabled(False)

        self.pushButton_7.clicked.connect(self.table_bar)
        self.pushButton_8.clicked.connect(self.table_pie)
        self.pushButton_9.clicked.connect(self.tag_bar)
        self.pushButton_10.clicked.connect(self.tag_pie)

        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(
            ['数据源', '', '']
        )

        self.table_info = None
        self.tag_info = None

    def set_target(self):
        set_target = SetTarget(self)
        result = set_target.exec_()

        if result:
            self.target = set_target.target
            text = '已经连接到了数据库{}\n当前选择的表为{}'.format(
                'mssql', self.target.table.name
            )
            self.textEdit.setText(
                text
            )
            self.target_changed()

    def target_changed(self):
        self.sources = []
        self.pushButton_2.setEnabled(True)
        self.pushButton_4.setEnabled(True)
        self.pushButton_5.setEnabled(True)
        self.pushButton_6.setEnabled(True)
        self.repaint_sources()

    def add_mssql_source(self):
        add_mssql_source = AddMssqlSource(self, self.target)
        result = add_mssql_source.exec_()

        if result:
            self.sources.append(add_mssql_source.source)
            self.repaint_sources()

    def add_mysql_source(self):
        add_mysql_source = AddMysqlSource(self, self.target)
        result = add_mysql_source.exec_()

        if result:
            self.sources.append(add_mysql_source.source)
            self.repaint_sources()

    def add_mongo_source(self):
        add_mongo_source = AddMongoSource(self, self.target)
        result = add_mongo_source.exec_()
        if result:
            self.sources.append(add_mongo_source.source)
            self.repaint_sources()

    def add_excel_source(self):
        add_excel_source = AddExcelSource(self, self.target)
        result = add_excel_source.exec_()

        if result:
            self.sources.append(add_excel_source.source)
            self.repaint_sources()

    def repaint_sources(self):
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(len(self.sources))
        row_count = 0
        for source in self.sources:
            source_name = QTableWidgetItem(str(source))
            edit_button = EditButton(self, source)
            remove_button = RemoveButton(self, source)
            self.tableWidget.setItem(row_count, 0, source_name)
            self.tableWidget.setCellWidget(row_count, 1, edit_button)
            self.tableWidget.setCellWidget(row_count, 2, remove_button)
            row_count += 1
        if len(self.sources) > 0:
            self.pushButton_3.setEnabled(True)
        else:
            self.pushButton_3.setEnabled(False)

    def merge(self):
        for source in self.sources:
            if not source.fields_map:
                self.alarm('存在映射为空的源:{},请检查！'.format(str(source)))
                return

        task = Task()
        task.add_sources(self.sources)
        task.merge()

        info = '\n{}:\n'.format(datetime.datetime.utcnow())
        for x in task.stats:
            info += '数据源:{}, 标签:{}, 抽取数目:{}, 去重丢弃:{}\n'.format(
                x[0], x[1], x[2], x[3]
            )
        orig_text = self.textEdit_2.toPlainText()
        self.textEdit_2.setText(orig_text + info)

        self.table_info, self.tag_info = task.merge_completed()

    def alarm(self, msg):
        QMessageBox.warning(self, 'warning', msg)

    def table_bar(self):
        if not self.table_info:
            self.alarm('当前没有数据源统计信息！')
            return
        else:
            names = [x[0] for x in self.table_info]
            values = [x[1] for x in self.table_info]
            plt.bar(names, values)
            plt.show()

    def table_pie(self):
        if not self.table_info:
            self.alarm('当前没有数据源统计信息！')
            return
        else:
            names = [x[0] for x in self.table_info]
            values = [x[1] for x in self.table_info]
            print(names, values)
            plt.pie(values, labels=names, autopct='%1.1f%%', shadow=False, startangle=90)
            plt.show()

    def tag_bar(self):
        if not self.tag_info:
            self.alarm('当前没有标签源统计信息！')
            return
        else:
            names = [x for x in self.tag_info]
            values = [x for x in self.tag_info.values()]
            print(names, values)
            plt.bar(names, values)
            plt.show()

    def tag_pie(self):
        if not self.tag_info:
            self.alarm('当前没有标签统计信息！')
            return
        else:
            names = [x for x in self.tag_info]
            values = [x for x in self.tag_info.values()]
            plt.pie(values, labels=names, autopct='%1.1f%%', shadow=False, startangle=90)
            plt.show()


class EditButton(QPushButton):
    def __init__(self, parent, source):
        super().__init__('编辑')
        self.clicked.connect(self.edit)
        self.source = source
        self.parent = parent

    def edit(self):
        add_fields_map = AddFieldsMap(self.parent, self.source)
        add_fields_map.exec_()


class RemoveButton(QPushButton):
    def __init__(self, parent, source):
        super().__init__('删除')
        self.clicked.connect(self.remove)
        self.source = source
        self.parent = parent

    def remove(self):
        self.parent.sources.remove(self.source)
        self.parent.repaint_sources()


if __name__ == '__main__':
    app = QApplication([])
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())