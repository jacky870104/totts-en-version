import sys
import os
import csv
# import threading
# import time
from PyQt5.QtCore import pyqtSignal, Qt, QCoreApplication
from PyQt5.QtWidgets import QMainWindow, QApplication, QListWidgetItem, QDesktopWidget
from PyQt5.QtGui import QPixmap

# from matplotlib.pyplot import cla
from TutorResult import SingResultWindow
from Ui_TutorMain import Ui_MainWindow
# from Ui_TutorBody import *
from TutorBody import SingBodyWindow

# ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
from extensions.definitions import IMAGE_DIR, RESULT_DIR, _songLyrics, CONFIG_DIR, CHART_TYPE, DEFAULT_TUTOR

""" Global Variables """
# GTutors = []
# from configs.tutors import loadGTutors
# loadGTutors()
# from configs import loadGTutors
# GTutors = loadGTutors()
from configs import GTutors, GMusics

""" 2022.09.21   disable radiobutton 身段 及 綜合  ==> 目前尚未支援此功能
 """
class SingMainWindow(QMainWindow, Ui_MainWindow):
    showResultSignal = pyqtSignal(int, str)     # 客製化的 signal, 接受 2 個 args
    """ 2022.09.27 加入 progressbar 發生
        QWidget::repaint: Recursive repaint detected
        QBackingStore::endPaint() called with active painter; did you forget to destroy it or call QPainter::end() on it?
        QBackingStore::endPaint() called with active painter; did you forget to destroy it or call QPainter::end() on it?

        子进程只负责发射信号，progressbar的value由主进程负责修改，这样就不会报错。
     """
    showProgressSignal = pyqtSignal(int)        # 客製化 signal, 提供 TutorBody 發出 progressbar value change
    showStatusSignal = pyqtSignal(str)          # 客製化 signal, 提供 TutorBody 發出 status message

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # # 建立 lock
        # self.lock = threading.Lock()

        # 初始化 UI 預設值
        self.analysis_type = 1      # 1: 曲段  2: 身段   3: 綜合
        self.analysis_paragraph = 0   # 1: 前段  2: 後段   0: 全首
        # self.sing_body = SingBodyWindow(self.lock)
        # self.sing_body = SingBodyWindow(parent=self)
        self.sing_result = SingResultWindow()

        """ RuntimeError: threads can only be started once """
        # self.thread_result = threading.Thread(target=self.showResult)

        self.setUIElements()
        
        # 在 __init__ 裡建立新的連結訊號
        self.radSong.clicked.connect(self.analysisTypeSelected)
        self.radBody.clicked.connect(self.analysisTypeSelected)      
        self.radComposite.clicked.connect(self.analysisTypeSelected)

        self.radSegFrom.clicked.connect(self.analysisParagraphSelected)
        self.radSegBack.clicked.connect(self.analysisParagraphSelected)
        self.radSegWhole.clicked.connect(self.analysisParagraphSelected)

        # 2022.11.03 modified by Jinn
        self.btnStart.clicked.connect(self.startAnalysis)
        self.btnPlay.clicked.connect(lambda: self.startAnalysis(True))

        # 2022.09.26 更改檔案命名規則... 第一次給副檔名 (.png); 第二次 .jpg; 第三次 .png
        # self.btnResult.clicked.connect(lambda: self.showResultWin(0, "LINE_ALBg_tutorsUM_11.jpg",))
        self.btnResult.clicked.connect(lambda: self.showResultWin(0, f"s1_pitch_results.{CHART_TYPE}"))

        # 2022.10.04 QListWidget (lstTutor)...選擇老師時
        self.lstTutor.itemSelectionChanged.connect(self.selectTutor)


        ## Signal Event
        self.showResultSignal.connect(self.showResultWin)
        self.showProgressSignal.connect(self.setProgressBar)
        self.showStatusSignal.connect(self.displayStatusBar)

    def setUIElements(self):
        global GTutors

        self.lblTutorPicture.setPixmap(QPixmap("images/C02-en.png"))

        
        # 設定 analysis type (radio button group) 
        if self.analysis_type == 1:
            self.radSong.setChecked(True)
        if self.analysis_type == 2:
            self.radBody.setChecked(True)
        if self.analysis_type == 3:
            self.radComposite.setChecked(True)

        """ 2020.10.07 將此功能移至 configs/tutors.py 中
                將 tutors 全域變數名改名字為  GTutors
         """
        ## 2022.10.04 改為可設定 (configs/GTutors.csv) 的清單
        # GTutors = []
        # tutorFilePath = os.path.join(CONFIG_DIR, "tutors.csv")
        # if os.path.exists(tutorFilePath):
        #     with open(tutorFilePath, mode='r', encoding='utf-8') as csv_file:
        #         csv_reader = csv.DictReader(csv_file)
        #         for tutor in csv_reader:
        #             tutor["order"] = int(tutor["order"]) 
        #             GTutors.append(tutor)
        #     if len(GTutors) >  0:
        #         GTutors.sort(key=lambda x: x["order"])

        # 2022.10.12 GTutors 拆分音樂為 "前段-1" "後段-2" "全首-0"
        # GTutors 只含 "全首-0" 的資訊; 想使用全部請 import GMusics
        _translate = QCoreApplication.translate
        if len(GTutors) > 0:
            self.lstTutor.clear()
            for tutor in GTutors:
                item = QListWidgetItem()
                item.setTextAlignment(Qt.AlignLeading|Qt.AlignVCenter)
                item.setText(_translate("MainWindow", tutor["title"]))
                self.lstTutor.addItem(item)
                if (tutor["id"] == DEFAULT_TUTOR):
                    self.lstTutor.setCurrentItem(item)


        
        # 2022.09.14 發現 designer 設定 lstTutor 的 spacing = 5 .... pyuic5 未產生相關 py 程式碼
        self.lstTutor.setSpacing(5)
        self.lstTutor.setFocus()
        self.resize(918, 915)

        # # Main UI
        # self.resize(598, 564)


    def analysisTypeSelected(self):
        # 設定 analysis type (radio button group) 
        if self.radSong.isChecked():
            self.analysis_type = 1
        if self.radBody.isChecked():
            self.analysis_type = 2
        if self.radComposite.isChecked():
            self.analysis_type = 3

    def analysisParagraphSelected(self):
        # 設定 analysis paragraph (radio button group) 
        if self.radSegFrom.isChecked():
            self.analysis_paragraph = 1
        if self.radSegBack.isChecked():
            self.analysis_paragraph = 2
        if self.radSegWhole.isChecked():
            self.analysis_paragraph = 0


    def selectTutor(self):
        qIndx = self.lstTutor.currentIndex()
        selIndx = qIndx.row()
        print(f"index: {selIndx}")
        picFileName = GTutors[selIndx]["picture"]
        imgFile = os.path.join(IMAGE_DIR, picFileName)
        self.lblTutorPicture.setPixmap(QPixmap(imgFile))


    # marked by Jinn at 2022.10.12
    # # 定義 startAnalysis 動作內容
    # def startAnalysis(self):
    #     print(f"analysis_type: {self.analysis_type}")
    #     # print(f"Tutor: {self.lstTutor.currentItem().text()}")
    #     qIdx = self.lstTutor.currentIndex()
    #     selIndx = qIdx.row()
    #     print(f"index: {selIndx}")
    #     musicFileName = GTutors[selIndx]["music"]

    #     self.sing_body = SingBodyWindow(play_music=musicFileName, parent=self)
    #     self.sing_body.show()
    #     self.sing_body.coachStart()
    def startAnalysis(self, onlyPlay = False):
        print(f"running mode(only_play): {onlyPlay}")      
        print(f"analysis_type: {self.analysis_type}")
        print(f"analysis_paragraph: {self.analysis_paragraph}")
        # print(f"Tutor: {self.lstTutor.currentItem().text()}")
        qIdx = self.lstTutor.currentIndex()
        selIndx = qIdx.row()
        print(f"Tutor Title(index): {selIndx}")
        selTitle = self.lstTutor.currentItem().text()

        selParagraph = self.analysis_paragraph
        tutor = next((item for item in GMusics if item["title"] == selTitle and item["paragraph"] == selParagraph), None)
        musicFile = tutor["music"]
        tutorPicFile = GTutors[selIndx]["picture"]

        if not tutor == None:
            self.sing_body = SingBodyWindow(play_music=musicFile, title=selTitle,
                    show_pic=tutorPicFile, paragraph=selParagraph, ai_type=self.analysis_type, parent=self)
            self.sing_body.show()
            self.sing_body.coachStart(onlyPlay)
        else:
            print(f"startAnalysis...Title ({selTitle}) Paragraph({selParagraph}) cannot found in GMusics !!!")


    def showResultWin(self, scope, picture):
        """ 2022.09.21 加入...將 Ai 計算好的 scope 儲存在 RESULT_DIR 目錄底下 scope.csv 檔案內
            **  if scope == 0 為使用者直接 click TutorMain 的 Result button; 系統將由 RESULT_DIR 顯示最後一次(上一次) Ai 分析結果
                    此時系統將由 scope.csv 讀取最後一次的分數(scope)
                if scope > 0
                    將來自 TutorBody 所做 Ai 分析分數存入檔案 scope.csv
         """
        # 
        scopeFile = os.path.join(RESULT_DIR, "scope.csv")
        if scope == 0:
            self.sing_result.pbarAnalysis.hide()
            if os.path.exists(scopeFile):
                with open(scopeFile, mode='r') as csv_file:
                    csv_reader = csv.DictReader(csv_file)
                    line_counts = 0
                    for row in csv_reader:
                        if line_counts == 0:
                            print(f'scope.csv\'s Column names are {", ".join(row)}')
                            scope = row["scope"]
                            print(f'\tscope: {scope}')
                        line_counts += 1
        else:
            self.sing_result.pbarAnalysis.show()
            with open(scopeFile, mode='w', newline='') as scope_file:
                csv_writer = csv.writer(scope_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

                csv_writer.writerow(['scope'])
                csv_writer.writerow([scope])

        print(f"Scope: {scope}  PictureFileName: {picture}")

        # 2022.10.12 marked by Jinn
        # self.sing_result.scope = scope
        # self.sing_result.lblScope.setText(f"{scope}")

        # self.sing_result.lblChartTitle.setText("音高曲線第一句")
        # self.sing_result.lblLyrics.setText(_songLyrics[0])
        # self.sing_result.cbxSentence.setCurrentIndex(0)

        # # imgFile = os.path.join(ROOT_DIR, "temp", picture)
        # imgFile = os.path.join(RESULT_DIR, picture)
        # print(imgFile)
        # self.sing_result.lblChart.setPixmap(QPixmap(imgFile))
        # # self.sing_result.show()
        self.sing_result.SegmentDefaultSet(scope, self.analysis_paragraph)
        self.sing_result.showMaximized()
    
    def setProgressBar(self, value):
        self.sing_result.pbarAnalysis.setValue(value)

    def displayStatusBar(self, value):
        self.sing_body.lblSongLyric.setText(value)

    def moveCenter(self):
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

  
if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = SingMainWindow()
    myWin.lstTutor.setFocus()
    myWin.show()
    myWin.moveCenter()
    # myWin.showMaximized()
    sys.exit(app.exec_())