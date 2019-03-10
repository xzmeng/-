import datetime

from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QApplication, QMessageBox, QComboBox

from core.Excel import Excel
from core.Mongodb import Mongodb
from core.Mssql import MssqlTarget, MssqlSource
from qt.UI.AddFieldsMap import Ui_Dialog as Ui_AddFieldsMap


class AddFieldsMap(QDialog, Ui_AddFieldsMap):
    def __init__(self, parent, source):
        super().__init__(parent)
        self.setupUi(self)
        self.source = source
        self.pushButton.clicked.connect(self.add_map)
        self.pushButton_2.clicked.connect(self.remove_map)
        self.pushButton_3.clicked.connect(self.add_filter)
        self.pushButton_4.clicked.connect(self.remove_filter)
        self.buttonBox.accepted.connect(self.submit)
        self.buttonBox.rejected.connect(self.reject)
        self.checkBox.setChecked(False)

        self.show_fields_map()
        self.show_filters()

        pass

    def show_fields_map(self):
        if self.source.tag:
            self.lineEdit.setText(self.source.tag)

        if self.source.incremental:
            self.checkBox.setChecked(True)
        else:
            self.checkBox.setChecked(False)

        fields_map = self.source.fields_map
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderLabels(
            ['源字段名', '目标字段名']
        )

        if not fields_map:
            self.tableWidget.setRowCount(0)
        else:
            self.tableWidget.setRowCount(len(fields_map))
            row_num = 0
            for target_name, source_name in fields_map.items():
                source_item = QTableWidgetItem(source_name)
                target_item = QTableWidgetItem(target_name)
                self.tableWidget.setItem(row_num, 0, source_item)
                self.tableWidget.setItem(row_num, 1, target_item)
                row_num += 1

    def show_filters(self):
        filters = self.source.filters_tuple
        self.tableWidget_2.setColumnCount(4)
        self.tableWidget_2.setHorizontalHeaderLabels(
            ['源字段名', '字段类型', '策略类型', '值']
        )
        if not filters:
            self.tableWidget_2.setRowCount(0)
        else:
            self.tableWidget_2.setRowCount(len(filters))
            row_num = 0
            for source_name, filter_type, filter_value in filters:
                source_item = QTableWidgetItem(source_name)
                field_type_combo = FieldTypeCombox()
                filter_type_combo = FilterTypeComboBox()
                filter_type_combo.setCurrentText(
                    FilterTypeComboBox.type_to_chinese[filter_type]
                )
                value_item = QTableWidgetItem(filter_value)
                self.tableWidget_2.setItem(row_num, 0, source_item)
                self.tableWidget_2.setCellWidget(row_num, 1, field_type_combo)
                self.tableWidget_2.setCellWidget(row_num, 2, filter_type_combo)
                self.tableWidget_2.setItem(row_num, 3, value_item)
                row_num += 1

    def add_map(self):
        row_count = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row_count)
        self.tableWidget.setItem(
            row_count, 0, QTableWidgetItem('')
        )
        self.tableWidget.setItem(
            row_count, 1, QTableWidgetItem('')
        )

    def remove_map(self):
        if self.tableWidget.rowCount() == 0:
            return
        current_row = self.tableWidget.currentRow()
        if current_row < 0:
            self.alarm('请选择需要删除的行！')
            return
        self.tableWidget.removeRow(current_row)

    def add_filter(self):
        row_count = self.tableWidget_2.rowCount()
        self.tableWidget_2.insertRow(row_count)
        self.tableWidget_2.setItem(
            row_count, 0, QTableWidgetItem('')
        )
        self.tableWidget_2.setCellWidget(
            row_count, 1, FieldTypeCombox()
        )
        self.tableWidget_2.setCellWidget(
            row_count, 2, FilterTypeComboBox()
        )
        self.tableWidget_2.setItem(
            row_count, 3, QTableWidgetItem('')
        )

    def remove_filter(self):
        if self.tableWidget_2.rowCount() == 0:
            return
        current_row = self.tableWidget_2.currentRow()
        if current_row < 0:
            self.alarm('请选择需要删除的行！')
            return
        self.tableWidget_2.removeRow(current_row)

    def check_fields_map(self):
        source_detail = self.source.get_current_table_detail()
        target_detail = self.source.target.get_current_table_detail()
        fields_map = {}
        row_count = self.tableWidget.rowCount()
        for row_num in range(row_count):
            source_name = self.tableWidget.item(row_num, 0).text()
            target_name = self.tableWidget.item(row_num, 1).text()
            if source_name not in source_detail:
                self.alarm('第{}行源字段名"{}"在源表中不存在!'.format(
                    row_num + 1, source_name))
                return False
            if target_name not in target_detail:
                self.alarm('第{}行目标字段名"{}"在目标表中不存在!'.format(
                    row_num + 1, target_name))
                return False
            if target_name in fields_map:
                self.alarm('第{}行存在到目标字段"{}"的重复映射!'.format(
                    row_num + 1, target_name))
                return False
            fields_map[target_name] = source_name
        if not fields_map:
            self.alarm('至少有一个字段映射!')
            return False
        else:
            self.source.fields_map = fields_map
            return True

    def check_filters(self):
        source_detail = self.source.get_current_table_detail()
        row_count = self.tableWidget_2.rowCount()
        filters = []
        for row_num in range(row_count):
            source_name = self.tableWidget_2.item(row_num, 0).text()
            if source_name not in source_detail:
                self.alarm('第{}行源字段名"{}"在源表中不存在!'.format(
                    row_num + 1, source_name))
                return False
            field_type = self.tableWidget_2.cellWidget(row_num, 1).currentText()
            filter_type_zh = self.tableWidget_2.cellWidget(row_num, 2).currentText()
            filter_type = FilterTypeComboBox.chinese_to_type[filter_type_zh]
            filter_value_text = self.tableWidget_2.item(row_num, 3).text()
            try:
                if field_type == 'str':
                    filter_value = filter_value_text
                elif field_type == 'int':
                    filter_value = int(filter_value_text)
                elif field_type == 'float':
                    filter_value = float(filter_value_text)
                elif field_type == 'bool':
                    filter_value = True if filter_value_text.lower() == 'true' else False
                elif field_type == 'datetime':
                    filter_value = datetime.datetime(*[int(x) for x in filter_value_text.split('-')])
            except Exception as e:
                self.alarm(str(e))
                return False
            filters.append((source_name, filter_type, filter_value))
        print(filters)
        for field_filter in filters:
            self.source.filters = []
            self.source.add_filter(*field_filter)
        filters_tuple = [(str(x), str(y), str(z)) for x, y, z in filters]
        self.source.filters_tuple = filters_tuple
        return True

    def check_filters_mongo_excel(self):
        row_count = self.tableWidget_2.rowCount()
        filters = []
        for row_num in range(row_count):
            source_name = self.tableWidget_2.item(row_num, 0).text()
            field_type = self.tableWidget_2.cellWidget(row_num, 1).currentText()
            filter_type_zh = self.tableWidget_2.cellWidget(row_num, 2).currentText()
            filter_type = FilterTypeComboBox.chinese_to_type[filter_type_zh]
            filter_value_text = self.tableWidget_2.item(row_num, 3).text()
            try:
                if field_type == 'str':
                    filter_value = filter_value_text
                elif field_type == 'int':
                    filter_value = int(filter_value_text)
                elif field_type == 'float':
                    filter_value = float(filter_value_text)
                elif field_type == 'bool':
                    filter_value = True if filter_value_text.lower() == 'true' else False
                elif field_type == 'datetime':
                    filter_value = datetime.datetime(*[int(x) for x in filter_value_text.split('-')])
            except Exception as e:
                self.alarm(str(e))
                return False
            filters.append((source_name, filter_type, filter_value))
        print(filters)
        for field_filter in filters:
            if isinstance(self.source, Mongodb):
                self.source.filters = {}
            if isinstance(self.source, Excel):
                self.source.filters = []
            self.source.add_filter(*field_filter)
        filters_tuple = [(str(x), str(y), str(z)) for x, y, z in filters]
        self.source.filters_tuple = filters_tuple
        return True

    def check_fields_map_mongo(self):
        target_detail = self.source.target.get_current_table_detail()
        fields_map = {}
        row_count = self.tableWidget.rowCount()
        for row_num in range(row_count):
            source_name = self.tableWidget.item(row_num, 0).text()
            target_name = self.tableWidget.item(row_num, 1).text()
            source_name, target_name = source_name.strip(), target_name.strip()
            if not source_name or not target_name:
                continue
            if target_name not in target_detail:
                self.alarm('第{}行目标字段名"{}"在目标表中不存在!'.format(
                    row_num + 1, target_name))
                return False
            if target_name in fields_map:
                self.alarm('第{}行存在到目标字段"{}"的重复映射!'.format(
                    row_num + 1, target_name))
                return False
            fields_map[target_name] = source_name
        if not fields_map:
            self.alarm('至少有一个字段映射!')
            return False
        else:
            self.source.fields_map = fields_map
            return True

    def check_fields_map_excel(self):
        source_columns = self.source.get_column_names()
        target_detail = self.source.target.get_current_table_detail()
        fields_map = {}
        row_count = self.tableWidget.rowCount()
        for row_num in range(row_count):
            source_name = self.tableWidget.item(row_num, 0).text()
            target_name = self.tableWidget.item(row_num, 1).text()
            if source_name not in source_columns:
                self.alarm('第{}行源字段名"{}"在源表中不存在!'.format(
                    row_num + 1, source_name))
                return False
            if target_name not in target_detail:
                self.alarm('第{}行目标字段名"{}"在目标表中不存在!'.format(
                    row_num + 1, target_name))
                return False
            if target_name in fields_map:
                self.alarm('第{}行存在到目标字段"{}"的重复映射!'.format(
                    row_num + 1, target_name))
                return False
            fields_map[target_name] = source_name
        if not fields_map:
            self.alarm('至少有一个字段映射!')
            return False
        else:
            self.source.fields_map = fields_map
            return True

    def submit(self):
        tag = self.lineEdit.text().strip()
        if not tag:
            self.source.tag = None
        else:
            self.source.tag = tag

        if self.checkBox.isChecked():
            self.source.incremental = True
        else:
            self.source.incremental = False

        if isinstance(self.source, Mongodb):
            if self.check_fields_map_mongo() and self.check_filters_mongo_excel():
                self.accept()
                return
            else:
                self.alarm('策略存在错误!')
                return

        if isinstance(self.source, Excel):
            if self.check_fields_map_excel() and self.check_filters_mongo_excel():
                self.accept()
                return
            else:
                self.alarm('策略存在错误!')
                return

        if self.check_fields_map() and self.check_filters():
            self.accept()

    def alarm(self, msg):
        QMessageBox.warning(self, 'warning', msg)


class FilterTypeComboBox(QComboBox):
    chinese_to_type = {
        '大于': 'gt',
        '大于等于': 'ge',
        '小于': 'lt',
        '小于等于': 'le',
        '等于': 'eq',
        '包含': 'contain',
        '不包含': 'notcontain',
    }
    type_to_chinese = {
        'gt': '大于',
        'ge': '大于等于',
        'lt': '小于',
        'le': '小于等于',
        'eq': '等于',
        'contain': '包含',
        'notcontain': '不包含'
    }
    type_names = [
        '大于', '大于等于', '小于', '小于等于',
        '等于', '包含', '不包含'
    ]

    def __init__(self):
        super().__init__()
        self.addItems(self.type_names)


class FieldTypeCombox(QComboBox):
    type_names = ['int', 'float', 'str', 'datetime', 'bool']

    def __init__(self):
        super().__init__()
        self.addItems(self.type_names)


if __name__ == '__main__':
    target = MssqlTarget('sa', '132132qq', 'a')
    target.connect_db()
    target.set_table('fake_target')

    source = MssqlSource('sa', '132132qq', 'a', target)
    source.connect_db()
    source.set_table('fake_mssql')

    app = QApplication([])
    dialog = AddFieldsMap(None, source)
    dialog.show()
    app.exec_()
