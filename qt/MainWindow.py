import sys

from PyQt5.QtWidgets import QMainWindow, QApplication

from qt.UI.MainWindow import Ui_MainWindow
from qt.SetTarget import SetTarget


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.target = None

        self.textEdit.setReadOnly(True)
        self.textEdit.setText('未连接')
        self.pushButton.clicked.connect(self.set_target)

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



if __name__ == '__main__':
    app = QApplication([])
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())