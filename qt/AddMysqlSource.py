from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox

from qt.UI.AddMysqlSource import Ui_Dialog as Ui_AddMysqlSource
from core.Mysql import MysqlSource
from config import config_mysql


class AddMysqlSource(QDialog, Ui_AddMysqlSource):
    # signal_target_changed = pyqtSlot()

    def __init__(self, parent, target=None):
        super().__init__(parent)
        self.setupUi(self)
        self.textEdit.setReadOnly(True)
        self.textEdit_2.setReadOnly(True)

        self.lineEdit.setText(config_mysql['username'])
        self.lineEdit_2.setText(config_mysql['password'])
        self.lineEdit_3.setText(config_mysql['host'])
        self.lineEdit_4.setText(config_mysql['db'])
        self.target = target
        self.source = None

        self.pushButton.clicked.connect(self.connect_db)
        self.comboBox.currentTextChanged.connect(
            self.show_table_detail
        )

        self.buttonBox.accepted.connect(self.submit)
        self.buttonBox.rejected.connect(self.reject)

    def connect_db(self):
        username = self.lineEdit.text()
        password = self.lineEdit_2.text()
        host = self.lineEdit_3.text()
        database = self.lineEdit_4.text()
        source = MysqlSource(username,
                             password,
                             host,
                             database,
                             self.target)
        ok, msg = source.connect_db()
        self.textEdit.setText(msg)
        if ok:
            self.source = source
            self.list_table()
        else:
            self.source = None
            self.comboBox.clear()
            self.textEdit_2.clear()

    def list_table(self):
        if self.source is None:
            return
        table_list = self.source.list_table()
        self.comboBox.addItems(table_list)
        if table_list:
            self.show_table_detail()

    def show_table_detail(self):
        if self.source is None:
            return
        table = self.source.metadata.tables.get(
            self.comboBox.currentText()
        )
        if table is None:
            return
        fmt = '%-20s%-20s'
        table_info = ['%-17s%-16s' % ('字段名', '字段类型')]
        for c in table.c:
            field_name = str(c.name)
            field_type = str(c.type).split(' ')[0]
            line = fmt % (field_name, field_type)
            table_info.append(line)
        text = '\n'.join(table_info)
        self.textEdit_2.setText(text)

    def submit(self):
        if self.source is None:
            self.alarm('必须连接到数据库并且选择一张表！')
            return
        table_name = self.comboBox.currentText()
        if not table_name:
            self.alarm('表名不可为空!')
            return
        if not self.source.set_table(table_name):
            self.alarm('无法使用表:{}'.format(table_name))
            return
        self.accept()

    def alarm(self, msg):
        QMessageBox.warning(self, 'warning', msg)


if __name__ == '__main__':
    app = QApplication([])
    dialog = AddMysqlSource(None)
    dialog.show()
    app.exec_()