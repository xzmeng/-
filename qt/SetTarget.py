from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox

from qt.CreateTable import CreateTable
from qt.UI.SetTarget import Ui_Dialog as Ui_SetTarget
from core.Mssql import MssqlTarget


class SetTarget(QDialog, Ui_SetTarget):
    # signal_target_changed = pyqtSlot()

    def __init__(self, parent, target=None):
        super().__init__(parent)
        self.setupUi(self)
        self.textEdit.setReadOnly(True)
        self.textEdit_2.setReadOnly(True)
        self.pushButton_2.setEnabled(False)

        self.lineEdit.setText('sa')
        self.lineEdit_2.setText('132132qq')
        self.lineEdit_3.setText('a')
        self.target = target
        if self.target is not None:
            self.textEdit.setText("已经成功连接到数据库")
            self.list_table()

        self.pushButton.clicked.connect(self.connect_db)
        self.pushButton_2.clicked.connect(self.create_table)
        self.comboBox.currentTextChanged.connect(
            self.show_table_detail
        )

        self.buttonBox.accepted.connect(self.submit)
        self.buttonBox.rejected.connect(self.reject)

    def connect_db(self):
        username = self.lineEdit.text()
        password = self.lineEdit_2.text()
        dsn = self.lineEdit_3.text()

        target = MssqlTarget(username,
                             password,
                             dsn)
        ok, msg = target.connect_db()
        self.textEdit.setText(msg)
        if ok:
            self.target = target
            self.pushButton_2.setEnabled(True)
            self.list_table()
        else:
            self.target = None
            self.comboBox.clear()
            self.textEdit_2.clear()

    def list_table(self):
        if self.target is None:
            return
        table_list = self.target.list_table()
        self.comboBox.addItems(table_list)
        if table_list:
            self.show_table_detail()

    def show_table_detail(self):
        if self.target is None:
            return
        table = self.target.metadata.tables.get(
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

    def create_table(self):
        create_table = CreateTable(self, self.target)
        result = create_table.exec_()
        if result:
            self.comboBox.addItem(create_table.table_name)

    def submit(self):
        if self.target is None:
            self.alarm('必须连接到数据库并且选择一张表！')
            return
        table_name = self.comboBox.currentText()
        if not table_name:
            self.alarm('表名不可为空!')
            return
        if not self.target.set_table(table_name):
            self.alarm('无法使用表:{}'.format(table_name))
            return
        self.accept()

    def alarm(self, msg):
        QMessageBox.warning(self, 'warning', msg)

    def emit_target_changed_singal(self):
        pass


if __name__ == '__main__':
    app = QApplication([])
    dialog = SetTarget(None)
    dialog.show()
    app.exec_()
