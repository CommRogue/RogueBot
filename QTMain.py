from PyQt5 import QtCore, QtGui, QtWidgets
from main import main
from multiprocessing import Process
import multiprocessing
import os
import qdarkstyle
from PyQt5.QtGui import QIcon
import sys
import nacl

class Ui_MainWindow(object):
    def clicked(self):
        self.directoryNoExist.hide()
        if not self.running:
            self.startButton.setText("Stop")
            self.startButton.setStyleSheet("background-color: red")
            self.process = Process(target=main)
            self.process.start()
            self.running = True

        else:
            self.startButton.setText("Start")
            self.startButton.setStyleSheet("background-color: green")
            self.process.terminate()
            self.process.join()
            self.running = False

    def __init__(self):
        self.running = False

    def openDirectory(self):
        path = os.getenv("LOCALAPPDATA")+"\\DiscordBot"
        if os.path.exists(path):
            path = os.path.realpath(path)
            os.startfile(path)
        else:
            self.directoryNoExist.show()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(537, 436)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.startButton = QtWidgets.QPushButton(self.centralwidget)
        self.startButton.setGeometry(QtCore.QRect(110, 220, 301, 101))
        font = QtGui.QFont()
        font.setFamily("Arial Black")
        font.setPointSize(34)
        font.setKerning(True)
        font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        self.startButton.setFont(font)
        self.startButton.setMouseTracking(False)
        self.startButton.setObjectName("startButton")
        self.Title = QtWidgets.QLabel(self.centralwidget)
        self.Title.setGeometry(QtCore.QRect(170, 15, 311, 101))
        font = QtGui.QFont()
        font.setFamily("Amiri Quran")
        font.setPointSize(48)
        self.Title.setFont(font)
        self.Title.setObjectName("Title")
        self.directoryButton = QtWidgets.QPushButton(self.centralwidget)
        self.directoryButton.setGeometry(QtCore.QRect(170, 330, 171, 41))
        self.directoryButton.setObjectName("directoryButton")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(180, 130, 221, 28))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(70, 30, 111, 101))
        self.label_2.setText("")
        self.label_2.setPixmap(QtGui.QPixmap("resources/91_Discord_logo_logos-512.webp"))
        self.label_2.setScaledContents(True)
        self.label_2.setObjectName("label_2")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.directoryButton.clicked.connect(self.openDirectory)
        self.startButton.clicked.connect(self.clicked)
        self.directoryNoExist = QtWidgets.QLabel(self.centralwidget)
        self.directoryNoExist.setGeometry(QtCore.QRect(50, 370, 461, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.directoryNoExist.setFont(font)
        self.directoryNoExist.setObjectName("directoryNoExist")
        self.directoryNoExist.setStyleSheet("color: red")
        self.directoryNoExist.hide()
        self.startButton.setStyleSheet("background-color: green")
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "RogueBot"))
        MainWindow.setWindowIcon(QIcon("../91_Discord_logo_logos-512.webp"))
        self.startButton.setText(_translate("MainWindow", "Start"))
        self.Title.setText(_translate("MainWindow", "RogueBot"))
        self.directoryButton.setText(_translate("MainWindow", "Open Configuration Directory"))
        self.label.setText(_translate("MainWindow", "Made by Rogue#0478"))
        self.directoryNoExist.setText(_translate("MainWindow", "The configuration directory doesn\'t exist. Please run the bot once to create it."))


if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    app.setStyleSheet(qdarkstyle.load_stylesheet())

    MainWindow.show()
    sys.exit(app.exec_())