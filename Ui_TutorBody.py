# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\WorkSJ\VoiceGui\TutorBody.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_BodyWindow(object):
    def setupUi(self, BodyWindow):
        BodyWindow.setObjectName("BodyWindow")
        BodyWindow.resize(643, 829)
        self.horizontalLayout = QtWidgets.QHBoxLayout(BodyWindow)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.lblMusic = QtWidgets.QLabel(BodyWindow)
        font = QtGui.QFont()
        font.setFamily("Adobe Devanagari")
        font.setPointSize(20)
        self.lblMusic.setFont(font)
        self.lblMusic.setAlignment(QtCore.Qt.AlignCenter)
        self.lblMusic.setObjectName("lblMusic")
        self.verticalLayout.addWidget(self.lblMusic)
        self.lblMotion = QtWidgets.QLabel(BodyWindow)
        self.lblMotion.setText("")
        self.lblMotion.setPixmap(QtGui.QPixmap("d:\\WorkSJ\\VoiceGui\\images/conductor.png"))
        self.lblMotion.setScaledContents(True)
        self.lblMotion.setObjectName("lblMotion")
        self.verticalLayout.addWidget(self.lblMotion)
        self.lblSongLyric = QtWidgets.QLabel(BodyWindow)
        font = QtGui.QFont()
        font.setFamily("細明體")
        font.setPointSize(20)
        self.lblSongLyric.setFont(font)
        self.lblSongLyric.setAlignment(QtCore.Qt.AlignCenter)
        self.lblSongLyric.setObjectName("lblSongLyric")
        self.verticalLayout.addWidget(self.lblSongLyric)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.retranslateUi(BodyWindow)
        QtCore.QMetaObject.connectSlotsByName(BodyWindow)

    def retranslateUi(self, BodyWindow):
        _translate = QtCore.QCoreApplication.translate
        BodyWindow.setWindowTitle(_translate("BodyWindow", "Body Motion"))
        self.lblMusic.setText(_translate("BodyWindow", "PlayMusic"))
        self.lblSongLyric.setText(_translate("BodyWindow", "Song Lyric"))
