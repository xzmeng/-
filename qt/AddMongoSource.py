from PyQt5.QtWidgets import QDialog

from core.Mongodb import Mongodb
from qt.UI.AddMongoSource import Ui_Dialog as Ui_AddMongoSource
from config import config_mongodb


class AddMongoSource(QDialog, Ui_AddMongoSource):
    def __init__(self, parent, target):
        super().__init__(parent)
        self.setupUi(self)
        self.target = target
        self.source = None
        self.buttonBox.accepted.connect(self.submit)
        self.buttonBox.rejected.connect(self.reject)

        self.lineEdit.setText(config_mongodb['fake_db'])
        self.lineEdit.setText(config_mongodb['fake_collection'])

    def submit(self):
        database = self.lineEdit.text()
        collection = self.lineEdit_2.text()
        self.source = Mongodb(database, collection, self.target)
        self.accept()