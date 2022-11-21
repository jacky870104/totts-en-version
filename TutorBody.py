import os, sys
import shutil
import threading
import time
from datetime import datetime
from PyQt5.QtWidgets import QWidget, QDesktopWidget
from numpy import block
from Ui_TutorBody import *
# from extensions.definitions import IMAGE_DIR, RESULT_DIR, CHART_DIR, BACKUP_DIR, _songLyrics, CHART_TYPE, _songFeatures, MUSIC_DIR
from extensions.definitions import *
from extensions.definitions import _songLyrics, _songFeatures, _fulllyricsduration, _headlyricsduration, _taillyricsduration, _fullrecduration, _headrecduration, _tailrecduration

# from configs import GTutors, GMusics

# play music
# from playsound import playsound
import simpleaudio as sa
# recording
# import sounddevice as sd
# from scipy.io.wavfile import write
import wave
import pyaudio
"""import 自定義的score.py"""
import score
import numpy as np


""" 2022.09.26 
       # 將設定值搬至 extensions.definitions 檔案裏
            -- RESULT_DIR, CHART_DIR, BACKUP_DIR, _songLyrics, _songSentences, ...etc.

       # 建立 charts 目錄(CHART_DIR)存 12 張圖
            -- 檔名 s[第幾句(1, 2, 3, 4)]_[音質種類(pitch, loudness, timbre)]_results.png
            -- pitch: 音高; loudness: 響度; timbre: 音色  
                .... ex: s1_pitch_results.png  ==> 音高第一句

       # 建立 results 目錄(RESULT_DIR)存當次(最新一次) AI 分析結果
       # 建立 backup 目錄(BACKUP_DIR)存每次 AI 分析結果 
"""
# _songLyrics = ["身騎白馬走三關",
#                 "改換素衣回中原",
#                 "放下西涼無人管",
#                 "思念三姐王寶釧 (三姐王寶釧)"]

class SingBodyWindow(QWidget, Ui_BodyWindow):
    def __init__(self, play_music, title, show_pic, paragraph, ai_type=1, parent=None):
        super().__init__()
        self.setupUi(self)

        # self._lock = lock
        self._parent = parent
        self.play_music = play_music       # 撥放音樂檔名  
        self.title = title                  # 老師的 Title 名 ex: 柯銘峰(生)
        self.show_pic = show_pic            # 老師劇照(顯示的圖形)檔名
        self.paragraph = paragraph      # 1: 前段  2: 後段   0: 全首
        self.ai_type = ai_type              # 1: 曲段  2: 身段   3: 綜合  

        '''20221120 加入改變名字對應語言的function'''
        self.cn_name = self.cn_name_transform(self.title)
        # ''' 確認TutorMain選擇的選項
        #     1.音樂檔名
        #     2.圖檔名
        #     3.分段
        #     4.模式
        #     '''
        # print('1.音樂檔名: {}'.format(self.play_music))
        # print('2.圖檔名: {}'.format(self.show_pic))
        # print('3.分段: {}'.format(self.paragraph))
        # print('4.模式: {}'.format(self.ai_type))
        # runmode
        self.only_play = False

        self.setUIElements()
        
        """ RuntimeError: threads can only be started once """
        # self.thread_music = threading.Thread(target = self.playMusic)
        # self.thread_lyrics = threading.Thread(target = self.showLyrics)
        # self.thread_controller = threading.Thread(target=self.coachEnding)

    def setUIElements(self):
        '''2022/10/10 改動為換成指定tutor的picture'''
        fileNamePath = os.path.join(IMAGE_DIR, f"{self.show_pic}")
        print(fileNamePath)
        self.lblMotion.setPixmap(QtGui.QPixmap(fileNamePath))
        self.resize(640, 934)
        self.moveCenter()
        # fileNamePath = os.path.join(IMAGE_DIR, "conductor.png")
        # QtGui.QPixmap(fileNamePath)

        # self.resize(933, 934)
        # self.moveCenter()

    def moveCenter(self):
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

    def playMusic(self):
        try:
            print('t1_music_playing...')
            self.lblMusic.setText("Music Playing")

            # filename = os.path.join(MUSIC_DIR, "柯銘峰.wav")
            filename = os.path.join(MUSIC_DIR, self.play_music)
            wave_obj = sa.WaveObject.from_wave_file(filename)
            play_obj = wave_obj.play()
            play_obj.wait_done()  # Wait until sound has finished playing
            
            self.lblMusic.setText("Music Ended")
        except Exception as e:
            print(f"Unexpected error: {filename}...{str(e)}")
            self.lblMusic.setText(str(e))

    def showLyrics(self):
        # if self.paragraph == 0: # 整段
        #     for i in range(4):
        #         self.lblSongLyric.setText(_songLyrics[i])
        #         # time.sleep(6)           # 20220927 調整為與 playMusic 相同時間 6 *4 == 24 seconds 
        #         time.sleep(15)
        # if self.paragraph in {1,2}: # 前/後段
        #     for i in range(2):
        #         self.lblSongLyric.setText(_songLyrics[i + 2 * (self.paragraph - 1)])
        #         # time.sleep(6)           # 20220927 調整為與 playMusic 相同時間 6 *4 == 24 seconds 
        #         time.sleep(15)
        if self.paragraph == 1:     # 前段
            for i in range(0,2):
                self.lblSongLyric.setText(_songLyrics[i])
                time.sleep(_headlyricsduration[i])
        elif self.paragraph == 2:
            for i in range(2,4):    # 後段
                self.lblSongLyric.setText(_songLyrics[i])
                time.sleep(_taillyricsduration[i-2])
        else: 
            for i in range(0,4):    # 整首
                self.lblSongLyric.setText(_songLyrics[i])
                time.sleep(_fulllyricsduration[i])

    '''10/10 將錄音變成一個功能，供重複呼叫和調整秒數'''
    def rec_songs(self, segment, seconds):
        chunk = 1024  # Record in chunks of 1024 samples
        sample_format = pyaudio.paInt16  # 16 bits per sample
        channels = 1
        fs = 44100  # Record at 44100 samples per second
        # seconds = 15
        filename = os.path.join(RECORD_DIR, f"record_{segment}.wav")
        p = pyaudio.PyAudio()  # Create an interface to PortAudio

        print(f'第{segment}次，錄音開始')

        stream = p.open(format=sample_format,
                        channels=channels,
                        rate=fs,
                        frames_per_buffer=chunk,
                        input=True)

        frames = []  # Initialize array to store frames

        # Store data in chunks for 3 seconds
        for i in range(0, int(fs / chunk * seconds)):
            data = stream.read(chunk)
            frames.append(data)

        # Stop and close the stream 
        stream.stop_stream()
        stream.close()
        # Terminate the PortAudio interface
        p.terminate()

        print(f'第{segment}次結束')

        # Save the recorded data as a WAV file
        wf = wave.open(filename, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(sample_format))
        wf.setframerate(fs)
        wf.writeframes(b''.join(frames))
        wf.close()
    
    def takeRecording(self):
        '''
        錄四段
        前奏 6s
        0:06~0:13 身騎白馬 7s
        間奏1 2s
        0.15~0:28走三關 改換素衣回中原 13s
        間奏2 5s
        0:33~0:42放下西涼無人管 9s
        間奏3 3s
        0:45~1:01思念三姐王寶釧(三姐王寶釧) 16s
        尾奏
        '''
        print("t3_recording")
        ''' 2022.10.12 先僅測試前段，用if判斷式分模式
            '''
        if self.paragraph == 1: # 前段
            print("選擇模式:{}，前段".format(self.paragraph))
            # 第一句 
            time.sleep(_headrecduration[0])
            self.rec_songs(segment=1, seconds=_headrecduration[1])
            # 第二句 
            time.sleep(_headrecduration[2])
            self.rec_songs(segment=2, seconds=_headrecduration[3])
        elif self.paragraph == 2: # 後段
            print("選擇模式:{}，後段".format(self.paragraph))
            # 第三句
            time.sleep(_tailrecduration[0])
            self.rec_songs(segment=3, seconds=_tailrecduration[1])
            # 第四句
            time.sleep(_tailrecduration[2])
            self.rec_songs(segment=4, seconds=_tailrecduration[3])
        else: # mode=3，整段
            print("選擇模式:{}，整段".format(self.paragraph))
            # 第一句 
            time.sleep(_fullrecduration[0])
            self.rec_songs(segment=1, seconds=_fullrecduration[1])
            # 第二句 
            time.sleep(_fullrecduration[2])
            self.rec_songs(segment=2, seconds=_fullrecduration[3])
            # 第三句
            time.sleep(_fullrecduration[4])
            self.rec_songs(segment=3, seconds=_fullrecduration[5])
            # 第四句
            time.sleep(_fullrecduration[6])
            self.rec_songs(segment=4, seconds=_fullrecduration[7])
        
        print('錄音結束')
        
        # nRecs = 4
        # if self.paragraph in {1,2}:
        #     nRecs = 2
        # for c in range(nRecs):
        #     print(nRecs)
        # print('錄音結束')


    def coachStart(self, onlyPlay = False):
        self.only_play = onlyPlay
        
        # 2022.10.12 only for debug
        """ 
        self.play_music = play_music       # 撥放音樂檔名  
        self.title = title                  # 老師的 Title 名 ex: 柯銘峰(生)
        self.show_pic = show_pic            # 老師劇照(顯示的圖形)檔名
        self.paragraph = paragraph      # 1: 前段  2: 後段   0: 全首
        self.ai_type = ai_type 
         """
        print(f"1.音樂檔名:{self.play_music}\n2.導師:{self.title}\n3.圖檔名:{self.show_pic}\n4.AI模式:{self.ai_type}\n5.分段:{self.paragraph}")

        self.thread_music = threading.Thread(target = self.playMusic)
        self.thread_lyrics = threading.Thread(target = self.showLyrics)
        self.thread_recording = threading.Thread(target = self.takeRecording)
        self.thread_controller = threading.Thread(target=self.coachEnding)

        self.thread_music.start()
        # self.playMusic()
        self.thread_lyrics.start()
        self.thread_recording.start()
        
        """ 若將 結束工作寫在此, 會造成負責 GUI thread 等在此...
        造成 TutorBody 的 UI 無法正當更新.
        ==> 修改為另外啟動一個 thread (self.thread_controller) 去等待
         """
        # ## 顯示歌詞結束後, 立即計算 (Analysis)
        # self.thread_lyrics.join()
        # self.lblSongLyric.setText("Singing Analysis....")
        # time.sleep(6)

        # if self.thread_music.is_alive():
        #     self.lblSongLyric.setText("Waiting for Music playing....")
        #     self.thread_music.join()

        # ## next step 顯示結果
        # self.hide()
        self.thread_controller.start()

    def coachEnding(self):
        # # enter the sync area with TutorMain to lock the Show Of TutorResult-UI
        # self._lock.acquire()
        # print("Lock acquired by TutorBody...")

        """
            # 2022.09.27 改為 recording 結束後立即開始做 aiAnalysis
          """       
        # ## 等待歌詞顯示結束後, 立即計算 (Analysis)
        # self.thread_lyrics.join()
        # self.lblSongLyric.setText("Singing Analysis....")
        self.thread_recording.join()

        """ Results """
        if not self.only_play:
            # 清空上次 Ai 產生的結果
            # resultDir = os.path.join(ROOT_DIR, "results")
            if os.path.exists(RESULT_DIR) and os.path.isdir(RESULT_DIR):
                shutil.rmtree(RESULT_DIR)
            os.makedirs(RESULT_DIR)  

            # 分析結果放於 results 目錄
            # 目前暫時將 charts 的相關檔案 copy 進 results 目錄, 當作是 AI 分析的結果
            self.aiAnalysis()

            # 備份 分析結果
            self.backupResult()
        else:
            if self.thread_music.is_alive():
                self.lblSongLyric.setText("Waiting for Music ending....")
                self.thread_music.join()
            self.hide()

    """ 2022.09.21 更動
            所有要顯示的 資訊皆暫存於 RESULT_DIR 目錄下
        2022.09.27 更動
            改為分 4 句做 AI 分析
      """
    def aiAnalysis(self):
        # time.sleep(6)           # 預計 AI 計算分析需花 6 分鐘

        """ 2022.09.27 修改為 分 4 句各自分別做 AI 分析
            ** 第一句完成就顯示結果, 其他 3 句於背景中繼續做分析
                -- 修改 UI (TutorResult.ui) 加入 ProgressBar 顯示目前背景完成的進度
        """
        # # 暫時採複製 charts 底下的 png 檔至 results 目錄模擬 AI 分析並產生結果
        # # 建議產生於 results 目錄底下的檔案檔名不包含時間 ==> 如此, 可便利 TutorResult 顯示時採用固定檔名
        # # srcDir = os.path.join(ROOT_DIR, "charts")
        # for file in os.listdir(CHART_DIR):
        #     srcFilePath = os.path.join(CHART_DIR, file)
        #     targetFilePath = os.path.join(RESULT_DIR, file)
        #     shutil.copyfile(srcFilePath, targetFilePath)
        
        # 分析第一句
        """ 2022.09.30 由於 segmentAanlysis 需要執行約 6 秒 ((此 controller thread 未完成, 且未將控制權交回)), 
        於此時設定 self.lblSongLyric.setText("Start Ai Analysis...s1") 並不會立即顯示 
        (需 controller 交回控制權時, ex: self.thread_music.join() 時, 但執行此動作之前另外做了 
        self.lblSongLyric.setText("Waiting for Music ending...."); 因此我們會發現 "Start Ai Analysis...s1" 會一閃而過
        後顯示 "Waiting for Music ending...."

            --- 所以於 TutorMain 加入一新的 signal (showStatusSignal), TutorBody's controller 透過 emit 的方式
                直接送給 TutorMain 給 MainThread 去立即顯示訊息
        """
        '''第一句分析&計算相似度----------------'''
        '''2022.10.12 增加分兩段練習：前二句&後二句'''
        '''
            假設只有前二句，先第一句
            然後再加上判斷後二句的if
            選擇練習:
            前半段-->分析第1、2句
            後半段-->分析第3、4句
        '''
        # 2022.10.12 modified by Jinn
        # # self.lblSongLyric.setText("Start Ai Analysis...s1")
        # self._parent.showStatusSignal.emit("Start Ai Analysis...s1")
        # self.segmentAnalysis(1)
        startSegment = 1
        endSegment = 4
        if self.paragraph == 1:
            endSegment = 2
        if self.paragraph == 2:
            startSegment = 3
        self._parent.showStatusSignal.emit(f"Start Ai Analysis...s{startSegment}")
        self.segmentAnalysis(startSegment)
        #              
        # 第一包分析完成, 等待音樂播放完畢 (檢查是否播放完)
        if self.thread_music.is_alive():
            self.lblSongLyric.setText("Waiting for Music ending....")
            self.thread_music.join()

        # self._lock.release()
        # print("Lock released by TutorBody...")

        """ next step 顯示結果
            向 TutorMain 發出 自行客製化的 signal --> showResutSignal
            ==> 使用 PyQt5 signal/slot 的自定義 signal , 將 GUI 的顯示交結主 thread (MainThread) 執行
            ==> 預設顯示 s1_pitch_results.png
            ==> 顯示第一句結果時, AI 繼續於背景分析第 2,3,4 句
         """
        # 關閉自己本身的 UI
        time.sleep(2)
        self.hide()
        ## 
        # for debug
        print("emit showResultSignal signal...")

        """ 20220921  修改支援 4 個句子, 3 類音質顯示
                --- 檔名 LINE_ALBUM_[音質種類(pitch-1, loudness-2, timbre-3)]_[第幾句(1, 2, 3, 4)].png
            20220926  檔名命名則修改
                --- 檔名 s[第幾句(1, 2, 3, 4)]_[音質種類(pitch, loudness, timbre)]_results.png

            # pitch: 音高; loudness: 響度; timbre: 音色

        """
    
        # self._parent.showResultSignal.emit(85, "小咪陳鳳桂1-1.png")
        nVoiceType = "pitch"      # 1 --> pitch 
        nLyrics = 1         # 1 --> 第一句
        # 2022.10.12 added by Jinn
        if self.paragraph == 2:
            nLyrics = 3             # 後段由第 3 句開始顯示

        # 檔名 LINE_ALBUM_[音質種類(pitch, loudness, timbre)]_[第幾句(1, 2, 3, 4)].png
        fileName = f"s{nLyrics}_{nVoiceType}_results.{CHART_TYPE}"      # 預設要顯示的檔名
        scope = score.map(np.mean(self.score)) # 顯示的分數
        """20221120 更改self.title 為 self.cn_name"""
        if self.cn_name == '空弦伴奏':
            scope = 100 
        print("Ai Scope: {}  default picture: {}".format(scope, fileName))     
        self._parent.showResultSignal.emit(scope, fileName)        # 向 TutorMain 發送 showResultSignal

        # 2022.10.12 modified by Jinn
        # # AI 繼續於背景分析第 2,3,4 句
        # for i in range(2,5):        # 2,3,4 句
        #     self.segmentAnalysis(i)
        sRange = startSegment + 1
        eRange = endSegment + 1
        # print(f"sRange: {sRange}  eRange: {eRange}")
        for i in range(sRange, eRange):
            # print(f"index: {i}")        
            self.segmentAnalysis(i)


    """ segment : 第幾句 [1,2,3,4] """
    """ 2022.09.27 加入 progressbar 發生
        QWidget::repaint: Recursive repaint detected
        QBackingStore::endPaint() called with active painter; did you forget to destroy it or call QPainter::end() on it?
        QBackingStore::endPaint() called with active painter; did you forget to destroy it or call QPainter::end() on it?
        一开始的思路是，新建一个线程不停设置progressbar的value，然后在主线程中启动子线程就可以了，但是和投屏线程一起启动的话就会报上面提到的错误。

        子进程只负责发射信号，progressbar的value由主进程负责修改，这样就不会报错。
     """
    def segmentAnalysis(self, segment):
        """ 有 4 句, 每一句假設各佔 progressbar 25%; 另假設每一句分析要花 6 秒 """
        # time.sleep(6)           # 預計 AI 計算分析需花 6 分鐘

        baseValue = 0
        if self.paragraph == 1:
            baseValue = 50

        """2022.10.13 計算函式更動"""
        '''只有第一句時才需要計算相似度'''
        """20221120 更改tutor=self.title 為 tutor=self.cn_name"""
        if segment == 1:
            self.score = score.sim_cal(tutor=self.cn_name, mode=self.paragraph)
        elif self.paragraph == 2 and segment == 3:
            self.score = score.sim_cal(tutor=self.cn_name, mode=self.paragraph)
        else:
            print("else")
        
        '''畫出對應句子的圖檔,segment=[1:4], 和選擇的tutor'''
        """20221120 更改輸入tutor=self.title 為 tutor=self.cn_name"""
        score.seg_plot(segment=segment, tutor=self.cn_name)
        
        '''進度條'''
        # 2022.10.12 added by Jinn
        for i in range(1, 7):        # 1 ~ 6  (共 6 秒) [4%, 8%, 12%, 16%, 20%, 24%, 29%, 33%, ...]
            # self._parent.sing_result.pbarAnalysis.setValue(25 * (segment-1) + i*4)
            value = 25 * (segment-1) + i*4 + baseValue
            # print(f"progressSignal emit: {value}")
            self._parent.showProgressSignal.emit(value)
            # time.sleep(1)

        # self._parent.sing_result.pbarAnalysis.setValue(5*5*segment)     # 調為 [25%, 50%, 75%, 100%]
        value = 5*5*segment + baseValue
        # print(f"progressSignal emit: {value}")
        self._parent.showProgressSignal.emit(value)
            
        # 暫時採複製 charts 底下的 png 檔至 results 目錄模擬 AI 分析並產生結果
        # 建議產生於 results 目錄底下的檔案檔名不包含時間 ==> 如此, 可便利 TutorResult 顯示時採用固定檔名
        # srcDir = os.path.join(ROOT_DIR, "charts")
        # for featureName in _songFeatures:
        #     file = f"s{segment}_{featureName}_results.{CHART_TYPE}"
        #     srcFilePath = os.path.join(CHART_DIR, file)
        #     targetFilePath = os.path.join(RESULT_DIR, file)
        #     shutil.copyfile(srcFilePath, targetFilePath)


    # 中英文title轉換，輸入英文名，輸出對應的中文名。
    def cn_name_transform(self, en_name):
        if en_name == 'Ming-Feng Ke':
            cn_name = "柯銘峰(生)"
        elif en_name == 'Xiao Mi':
            cn_name = "小咪(生)"
        elif en_name == 'Ya-Fen Hsu':
            cn_name = "許亞芬(生)"
        elif en_name == 'Chun-Mei Kuo':
            cn_name = "郭春美(生)"
        elif en_name == 'Kai-Lin Suen':
            cn_name = "孫凱琳(生)"
        elif en_name == 'Jin-Ying Wang':
            cn_name = "王金櫻(旦)"
        elif en_name == 'Huei-Jun Shih':
            cn_name = "石惠君(旦)"
        elif en_name == 'Yi-Fan Gu':
            cn_name = "古翊汎(生)"
        elif en_name == "Yue-Ling Liang":
            cn_name = "梁越玲(生)"
        else: ## en_name == 'Music only':
            cn_name = "空弦伴奏"
        
        return cn_name # 回傳對應的中文名
        

    def backupResult(self):
        """ Backup """
        # 依日期及時間 備份儲存每次 tutor 的結果
        dtNow = datetime.now()
        sToday = dtNow.strftime("%Y%m%d")
        sTime = dtNow.strftime("%H%M")            
        bkupToday = os.path.join(BACKUP_DIR, sToday)
        if not os.path.exists(bkupToday):
            os.makedirs(bkupToday)          # 建立目錄(日期)....YYYYmmdd

        bkupDir = os.path.join(bkupToday, sTime)
        if os.path.exists(bkupDir) and os.path.isdir(bkupDir):
            shutil.rmtree(bkupDir)
        os.makedirs(bkupDir)                # 建立子目錄(時分)....HHMM
        
        # 依日期/時間 備份儲存每次 tutor 的結果
        for file in os.listdir(RESULT_DIR):
            srcFilePath = os.path.join(RESULT_DIR, file)
            targetFilePath = os.path.join(bkupDir, file)
            shutil.copyfile(srcFilePath, targetFilePath)    
        # 錄音檔4段: record_x.wav
        for file in os.listdir(RECORD_DIR):
            recFilePath = os.path.join(RECORD_DIR, file)            
            targetFilePath = os.path.join(bkupDir, file)
            shutil.copyfile(srcFilePath, targetFilePath)