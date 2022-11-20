import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from PyQt5.QtGui import QPixmap
from Ui_TutorResult import *
from extensions.definitions import RESULT_DIR, _songSentences, _songLyrics, CHART_TYPE

""" 2022.09.21  修改支援 4 個句子, 3 類音質顯示
    20220926  檔名命名則修改
        --- 檔名 s[第幾句(1, 2, 3, 4)]_[音質種類(pitch, loudness, timbre)]_results.jpg

    # 所有要顯示的 Charts 皆由 RESULT_DIR 目錄取得
"""               
class SingResultWindow(QWidget, Ui_ResultWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.scope = 0

        self.btnPitch.clicked.connect(self.SoundPitch)
        self.btnLoudness.clicked.connect(self.SoundLoudness)
        self.btnTimbre.clicked.connect(self.SoundTimbre)

    def SoundPitch(self):
        # self.lblChartTitle.setText("音高曲線第一句")
        selIdx = self.cbxSentence.currentIndex()        # 0 ~ 3
        '''20221120 更改sTitle的音高曲線 >> Pitch Contour'''
        sTitle = f"Pitch Contour {_songSentences[selIdx]}"
        self.lblChartTitle.setText(sTitle)
        self.lblLyrics.setText(_songLyrics[selIdx])

        # pngFile = os.path.join(ROOT_DIR, "images", "小咪陳鳳桂1-1.png")
        # self.lblChart.setPixmap(QPixmap(pngFile))

        # nVoiceType = 1        # 1 --> Pitch
        sVoiceType = "pitch" 
        # nLyrics = 1           # 1 --> 第一句
        nLyrics = selIdx + 1    # 0 ~ 3 ==> 1 ~ 4

        """ 20220926  檔名命名則修改
                --- 檔名 s[第幾句(1, 2, 3, 4)]_[音質種類(pitch, loudness, timbre)]_results.jpg
         """           
        # # 檔名 LINE_ALBUM_[音質種類(Pitch-1, Loudness-2, Timbre-3)]_[第幾句(1, 2, 3, 4)].jpg
        # fileName = f"LINE_ALBUM_{nVoiceType}{nLyrics}.jpg" 
        fileName = f"s{nLyrics}_{sVoiceType}_results.{CHART_TYPE}"      # 預設要顯示的檔名

        # filePath = os.path.join(ROOT_DIR, "temp", fileName)
        filePath = os.path.join(RESULT_DIR, fileName)
        if not os.path.exists(filePath):
            QMessageBox.warning(None, "警告", f"分析結果({filePath})不存在 !!!")
        self.lblChart.setPixmap(QPixmap(filePath))
    
    def SoundLoudness(self):
        # self.lblChartTitle.setText("響度曲線第一句")
        selIdx = self.cbxSentence.currentIndex()
        '''20221120 更改sTitle的響度曲線 >> Loudness Contour'''
        sTitle = f"Loudness{_songSentences[selIdx]}"
        self.lblChartTitle.setText(sTitle)
        self.lblLyrics.setText(_songLyrics[selIdx])

        # nVoiceType = 2      # 2 --> Loudness 
        sVoiceType = "loudness"
        # nLyrics = 1         # 1 --> 第一句
        nLyrics = selIdx + 1

        # # 檔名 LINE_ALBUM_[音質種類(Pitch-1, Loudness-2, Timbre-3)]_[第幾句(1, 2, 3, 4)].jpg
        # fileName = f"LINE_ALBUM_{nVoiceType}{nLyrics}.jpg" 
        fileName = f"s{nLyrics}_{sVoiceType}_results.{CHART_TYPE}" 

        # filePath = os.path.join(ROOT_DIR, "temp", fileName)
        filePath = os.path.join(RESULT_DIR, fileName)
        if not os.path.exists(filePath):
            QMessageBox.warning(None, "警告", f"分析結果({filePath})不存在 !!!")
        self.lblChart.setPixmap(QPixmap(filePath))

    def SoundTimbre(self):
        # self.lblChartTitle.setText("音色曲線第一句")
        selIdx = self.cbxSentence.currentIndex()
        '''20221120 更改sTitle的音色曲線 >> Timbre Distribution'''
        sTitle = f"Timbre Distribution{_songSentences[selIdx]}"
        self.lblChartTitle.setText(sTitle)
        self.lblLyrics.setText(_songLyrics[selIdx])

        # nVoiceType = 3      # 3 --> Timbre 
        sVoiceType = "timbre"
        # nLyrics = 1         # 1 --> 第一句
        nLyrics = selIdx + 1

        # 檔名 LINE_ALBUM_[音質種類(Pitch-1, Loudness-2, Timbre-3)]_[第幾句(1, 2, 3, 4)].jpg
        # fileName = f"LINE_ALBUM_{nVoiceType}{nLyrics}.jpg" 
        fileName = f"s{nLyrics}_{sVoiceType}_results.{CHART_TYPE}" 

        # filePath = os.path.join(ROOT_DIR, "temp", fileName)
        filePath = os.path.join(RESULT_DIR, fileName)
        if not os.path.exists(filePath):
            QMessageBox.warning(None, "警告", f"分析結果({filePath})不存在 !!!")
        self.lblChart.setPixmap(QPixmap(filePath))

    def SegmentDefaultSet(self, scope, paragraph):
        self.scope = scope
        self.lblScope.setText(f"{scope}")

        sVoiceType = "pitch"
        selIdx = 0
        self.cbxSentence.model().item(0).setEnabled(True)
        self.cbxSentence.model().item(1).setEnabled(True)
        self.cbxSentence.model().item(2).setEnabled(True)
        self.cbxSentence.model().item(3).setEnabled(True)
        if paragraph == 1:
            self.cbxSentence.model().item(2).setEnabled(False)
            self.cbxSentence.model().item(3).setEnabled(False)
        if paragraph == 2:
            selIdx = 2
            self.cbxSentence.model().item(0).setEnabled(False)
            self.cbxSentence.model().item(1).setEnabled(False)
        nLyrics = selIdx + 1 
        
        '''20221120 更改sTitle的音高曲線 >> Pitch Contour'''
        sTitle = f"Pitch Contour {_songSentences[selIdx]}"
        self.lblChartTitle.setText(sTitle)
        self.lblLyrics.setText(_songLyrics[selIdx])
        self.cbxSentence.setCurrentIndex(selIdx)

        # 檔名 LINE_ALBUM_[音質種類(Pitch-1, Loudness-2, Timbre-3)]_[第幾句(1, 2, 3, 4)].jpg
        # fileName = f"LINE_ALBUM_{nVoiceType}{nLyrics}.jpg" 
        fileName = f"s{nLyrics}_{sVoiceType}_results.{CHART_TYPE}" 

        # self.lblChartTitle.setText("音高曲線第一句")
        # self.lblLyrics.setText(_songLyrics[0])
        # self.cbxSentence.setCurrentIndex(0)

        # # imgFile = os.path.join(ROOT_DIR, "temp", picture)
        # imgFile = os.path.join(RESULT_DIR, picture)
        # print(imgFile)
        # self.sing_result.lblChart.setPixmap(QPixmap(imgFile))
        filePath = os.path.join(RESULT_DIR, fileName)
        if not os.path.exists(filePath):
            QMessageBox.warning(None, "警告", f"分析結果({filePath})不存在 !!!")
        print(filePath)
        self.lblChart.setPixmap(QPixmap(filePath))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = SingResultWindow()
    myWin.show()
    sys.exit(app.exec_())
