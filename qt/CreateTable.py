from PyQt5.QtWidgets import QDialog, QComboBox, QTableWidgetItem, QMessageBox

from qt.UI.CreateTable import Ui_Dialog as Ui_CreateTable


class CreateTable(QDialog, Ui_CreateTable):

    def __init__(self, parent, target):
        super().__init__(parent)
        self.setupUi(self)
        self.target = target
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderLabels(
            ['字段名', '字段类型']
        )

        self.pushButton.clicked.connect(self.add_field)
        self.pushButton_2.clicked.connect(self.remove_field)
        self.table_name = None
        self.buttonBox.accepted.connect(self.submit)
        self.buttonBox.rejected.connect(self.reject)

    def add_field(self):
        row_count = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row_count)
        self.tableWidget.setItem(
            row_count, 0, QTableWidgetItem('')
        )
        self.tableWidget.setCellWidget(
            row_count, 1, FieldTypeCombox()
        )

    def remove_field(self):
        if self.tableWidget.rowCount() == 0:
            return
        current_row = self.tableWidget.currentRow()
        if current_row < 0:
            self.alarm('请选择需要删除的行！')
            return
        self.tableWidget.removeRow(current_row)

    def create(self):
        table_name = self.lineEdit.text()
        if table_name.strip() == '':
            self.alarm('表名不可为空!')
            return

        if table_name in self.target.list_table():
            self.alarm('表已经存在,请更改表名!')
            return
        row_count = self.tableWidget.rowCount()
        fields = {}
        for i in range(row_count):
            field_name = self.tableWidget.item(i, 0).text()
            field_type = self.tableWidget.cellWidget(i, 1).currentText()
            if field_name.strip() == '':
                self.alarm('存在空字段名!')
                return
            if field_name in fields:
                self.alarm('字段名"{}"重复出现!'.format(field_name))
                return
            fields[field_name] = field_type
        if not fields:
            self.alarm('至少需要一个字段！')
            return
        print(fields, table_name)
        self.target.create_table(table_name, fields)
        self.table_name = table_name
        return True

    def submit(self):
        if self.create():
            self.accept()
            return
        else:
            self.alarm('信息有误,请检查！')
            return

    def alarm(self, msg):
        QMessageBox.warning(self, 'warning', msg)


class FieldTypeCombox(QComboBox):
    type_names = ['int', 'float', 'string', 'datetime', 'bool']

    def __init__(self):
        super().__init__()
        self.addItems(self.type_names)



