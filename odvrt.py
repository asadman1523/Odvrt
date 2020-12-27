import pathlib
import sys
import re
import time
import threading

from PyQt5.QtCore import Qt

import main_func
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QTableWidgetItem, QFileDialog, QDialog, QPushButton, QLabel
from qt_view import Ui_MainWindow


class MainWindow(QtWidgets.QMainWindow):
    fileList = []
    downloadImage = False
    configPath = pathlib.Path('config.ini')
    confirmDialog = None

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setAcceptDrops(True)
        # 讀取設定
        try:
            if not self.configPath.exists():
                self.configPath.touch()
            text = self.configPath.read_text()
            textSet = text.split('\n')
            for t in textSet:
                if "downloadImg" in t:
                    result = re.findall('\w+$', t)
                    if result[0] == "True":
                        self.ui.downloadImgCheckBox.setChecked(True)
                        self.downloadImage = True
                    else:
                        self.ui.downloadImgCheckBox.setChecked(False)
                        self.downloadImage = False
        except:
            # print("Unexpected error:", sys.exc_info()[0])
            raise
        # 讀取設定
        # 開啟
        self.ui.openButton.clicked.connect(openBtnClicked)
        self.ui.action1.triggered.connect(openBtnClicked)
        # 執行
        self.ui.runButton.clicked.connect(runBtnClicked)
        self.ui.action2.triggered.connect(runBtnClicked)
        # 刪除
        self.ui.delButton.clicked.connect(delBtnClicked)
        self.ui.action5.triggered.connect(delBtnClicked)

        # 下載縮圖
        self.ui.downloadImgCheckBox.stateChanged.connect(downloadImgChecked)
        self.fileNames = []

        # 設定作者link
        self.ui.action3.triggered.connect(openAuthorUrl)
        self.ui.action4.triggered.connect(openProductUrl)

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
            self.fileNames = list(dict.fromkeys(self.fileNames))
            updateFileList()
        except:
            # print("Unexpected error:", sys.exc_info()[0])
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
    dialog = QFileDialog()
    dialog.setFileMode(QFileDialog.ExistingFiles)
    dialog.setOption(QFileDialog.ShowDirsOnly, False)
    if dialog.exec():
        window.fileNames = dialog.selectedFiles() + window.fileNames
        window.fileNames = list(dict.fromkeys(window.fileNames))
        updateFileList()


def runBtnClicked():
    window.confirmDialog = QDialog()
    window.confirmDialog.setFixedWidth(480)
    window.confirmDialog.setFixedHeight(100)
    window.confirmDialog.setWindowTitle("上車?")
    label = QLabel(window.confirmDialog)
    label.setText("確定要更改列表中的檔案名稱?\n\n按確定後代表同意自負任何檔案毀損責任，與本產品無關")
    label.move(10, 10)

    btn = QPushButton(window.confirmDialog)
    btn.setText("確定")
    btn.move(380, 70)
    btn.clicked.connect(showRunningAndRun)

    btn = QPushButton(window.confirmDialog)
    btn.setText("取消")
    btn.move(300, 70)
    btn.clicked.connect(lambda: window.confirmDialog.close())
    window.confirmDialog.setWindowModality(Qt.ApplicationModal)
    window.confirmDialog.exec_()


def showRunningAndRun():
    window.confirmDialog.close()
    runningDialog = QDialog()
    runningDialog.setFixedWidth(200)
    runningDialog.setFixedHeight(100)
    runningDialog.setWindowTitle("處理中")
    # runningDialog.setWindowModality(Qt.ApplicationModal)
    label = QLabel(runningDialog)
    label.move(50, 50)
    try:
        t = threading.Thread(target=_run(runningDialog, label))
        t.start()
    except:
        print("Unexpected error:", sys.exc_info())
        raise


def _run(dialog, label):
    dialog.show()
    i = 0
    while i < len(window.fileNames):
        try:
            main_func.rename([window.fileNames[i]], window.downloadImage)
        except:
            pass
        time.sleep(1)
        i = i + 1
    dialog.close()


def openAuthorUrl(self):
    try:
        url = QtCore.QUrl('https://github.com/asadman1523')
        QtGui.QDesktopServices.openUrl(url)
    except:
        # print("Unexpected error:", sys.exc_info())
        raise


def openProductUrl(self) -> object:
    url = QtCore.QUrl('https://github.com/asadman1523/odvrt')
    QtGui.QDesktopServices.openUrl(url)


def delBtnClicked():
    window.fileNames = []
    window.ui.label.setText("共0個檔案")
    window.ui.tableWidget.setRowCount(0)
    window.setLayout(window.layout())


def downloadImgChecked():
    try:
        if window.ui.downloadImgCheckBox.isChecked():
            window.downloadImage = True
            window.configPath.write_text("downloadImg=True")
        else:
            window.downloadImage = False
            window.configPath.write_text("downloadImg=False")
    except:
        pass


def updateFileList():
    window.ui.tableWidget.setRowCount(len(window.fileNames))
    window.ui.label.setText("共" + str(len(window.fileNames)) + "個檔案")
    i = 0
    while i < len(window.fileNames):
        item = QTableWidgetItem()
        item.setFlags(item.flags() ^ 2)
        item.setText(window.fileNames[i])
        window.ui.tableWidget.setItem(i, 0, item)
        i = i + 1
    window.setLayout(window.layout())


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
