from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox

from core.Excel import Excel
from qt.UI.AddExcelSource import Ui_Dialog as Ui_AddExcelSource


class AddExcelSource(QDialog, Ui_AddExcelSource):
    def __init__(self, parent, target):
        super().__init__(parent)
        self.setupUi(self)

        self.textEdit.setReadOnly(True)
        self.pushButton.clicked.connect(self.open_file)
        self.target = target
        self.source = None
        self.buttonBox.accepted.connect(self.submit)
        self.buttonBox.rejected.connect(self.reject)

    def open_file(self):
        fname, _ = QFileDialog.getOpenFileName(
            self, 'Open file', '..\\core\\'
        )
        if not fname.endswith('.xlsx'):
            self.alarm('打开的文件不是Excel文件!')
            return
        else:
            self.textEdit.setText(str(fname))
            self.source = Excel(fname, self.target)

    def submit(self):
        if self.source is None:
            self.alarm('请选择一个Excel文件!')
            return
        self.accept()

    def alarm(self, msg):
        QMessageBox.warning(self, 'warning', msg)