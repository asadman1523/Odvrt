import pathlib
import sys
import main_func
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem
from qt_view import Ui_MainWindow


class MainWindow(QtWidgets.QMainWindow):
    fileList = []

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setAcceptDrops(True)
        # 開啟
        self.ui.openButton.clicked.connect(openBtnClicked)
        self.ui.action1.triggered.connect(openBtnClicked)
        # 執行
        self.ui.runButton.clicked.connect(runBtnClicked)
        self.ui.action2.triggered.connect(runBtnClicked)

        self.ui.delButton.clicked.connect(delBtnClicked)
        self.ui.action5.triggered.connect(delBtnClicked)

        self.fileNames = []

    # drag and drop
    def dragEnterEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        try:
            file_path = str(event.mimeData().text())
            file_path = file_path.replace('file:///', '').strip()
            file_path = file_path.split('\n')
            # print(fileNames)
            # Count
            for i in range(len(file_path)):
                processDrop(self.fileNames, file_path[i])

            self.ui.tableWidget.setRowCount(len(self.fileNames))
            self.ui.label.setText("共" + str(len(self.fileNames)) + "個檔案")
            i = 0
            while i < len(self.fileNames):
                item = QTableWidgetItem()
                item.setFlags(item.flags() ^ 2)
                item.setText(self.fileNames[i])
                self.ui.tableWidget.setItem(i, 0, item)
                i = i + 1
            self.setLayout(self.layout())
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise


def processDrop(obj, filePath):
    p = pathlib.Path(filePath)
    if p.is_dir():
        for child in p.iterdir():
            processDrop(obj, child)
    elif p.is_file():
        if not str(p) in obj:
            return obj.append(str(p))


def openBtnClicked():
    print()


def runBtnClicked():
    i = 0
    while i < len(window.fileNames):
        main_func.rename([window.fileNames[i]])
        i = i + 1


def delBtnClicked():
    window.fileNames = []
    window.ui.label.setText("共0個檔案")
    window.ui.tableWidget.setRowCount(0)
    window.setLayout(window.layout())


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
