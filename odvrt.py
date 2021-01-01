import pathlib
import sys
import re
import time
import threading

from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QTableWidgetItem, QFileDialog, QDialog, QPushButton, QLabel, QProgressBar

from RenameTool import RenameTool
from qt_view import Ui_MainWindow


class MainWindow(QtWidgets.QMainWindow):
    fileList = []
    fileNames = None
    downloadImage = False
    configPath = pathlib.Path('config.ini')
    progressbar = None
    _func = None

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
        self.ui.openButton.clicked.connect(self.openBtnClicked)
        self.ui.action1.triggered.connect(self.openBtnClicked)
        # 執行
        self.ui.runButton.clicked.connect(self.runBtnClicked)
        self.ui.action2.triggered.connect(self.runBtnClicked)
        # 刪除
        self.ui.delButton.clicked.connect(self.delBtnClicked)
        self.ui.action5.triggered.connect(self.delBtnClicked)

        # 下載縮圖
        self.ui.downloadImgCheckBox.stateChanged.connect(self.downloadImgChecked)
        self.fileNames = []

        # 設定作者link
        self.ui.action3.triggered.connect(self.openAuthorUrl)
        self.ui.action4.triggered.connect(self.openProductUrl)

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
                self.processDrop(self.fileNames, file_path[i])
            self.fileNames = list(dict.fromkeys(self.fileNames))
            self.updateFileList()
        except:
            # print("Unexpected error:", sys.exc_info()[0])
            raise

    def processDrop(self, obj, filePath):
        p = pathlib.Path(filePath)
        if p.is_dir():
            for child in p.iterdir():
                self.processDrop(obj, child)
        elif p.is_file():
            if not str(p) in obj:
                return obj.append(str(p))

    def openBtnClicked(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFiles)
        dialog.setOption(QFileDialog.ShowDirsOnly, False)
        if dialog.exec():
            self.fileNames = dialog.selectedFiles() + self.fileNames
            self.fileNames = list(dict.fromkeys(self.fileNames))
            self.updateFileList()

    def runBtnClicked(self):
        self.confirmDialog = QDialog()
        self.confirmDialog.setFixedWidth(480)
        self.confirmDialog.setFixedHeight(100)
        self.confirmDialog.setWindowTitle("上車?")
        label = QLabel(self.confirmDialog)
        label.setText("確定要更改列表中的檔案名稱?\n\n按確定後代表同意自負任何檔案毀損責任，與本產品無關")
        label.move(10, 10)

        btn = QPushButton(self.confirmDialog)
        btn.setText("確定")
        btn.move(380, 70)
        btn.clicked.connect(self.showProgressAndRun)

        btn = QPushButton(self.confirmDialog)
        btn.setText("取消")
        btn.move(300, 70)
        btn.clicked.connect(lambda: self.confirmDialog.close())
        self.confirmDialog.setWindowModality(Qt.ApplicationModal)
        self.confirmDialog.exec_()

    def showProgressAndRun(self):
        try:
            self.confirmDialog.close()
            self.progressbar = self.CustomProgressBar()
            self.progressbar.move(-500, -500)
            self.progressbar.setGeometry(0, 0, 300, 25)
            self.progressbar.setMaximum(100)
            self.progressbar.move(self.window().x() + 50,
                                  self.window().y() + 150)
            self.progressbar.setWindowTitle("執行中...")
            self.progressbar.show()

            self._func = RenameTool(self.fileNames, self.downloadImage)
            self._func.countChanged.connect(self.onCountChanged)
            self._func.finished.connect(self.threadFinished)
            self._func.start()
            self.progressbar.setFunc(self._func)
        except:
            print("Unexpected error:", sys.exc_info())
            raise

    def onCountChanged(self, value):
        try:
            self.progressbar.setValue(value)
        except:
            print("Unexpected error:", sys.exc_info())
            raise

    def threadFinished(self):
        self.progressbar.close()
        self._func.exit(0)

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

    def delBtnClicked(self):
        self.fileNames = []
        self.ui.label.setText("共0個檔案")
        self.ui.tableWidget.setRowCount(0)
        self.setLayout(self.layout())

    def downloadImgChecked(self):
        try:
            if self.ui.downloadImgCheckBox.isChecked():
                self.downloadImage = True
                self.configPath.write_text("downloadImg=True")
            else:
                self.downloadImage = False
                self.configPath.write_text("downloadImg=False")
        except:
            pass

    def updateFileList(self):
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

    class CustomProgressBar(QProgressBar):
        func = None

        def setFunc(self, func : RenameTool):
            self.func = func

        def closeEvent(self, a0: QtGui.QCloseEvent):
            self.func.stopProc = True
            a0.accept()


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
