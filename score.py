#%%
# # 引入 time 模組
import time
# 開始測量程式運行時間
#%% 模組導入
# Usual Libraries
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import sklearn
# Librosa (the mother of audio files)
import librosa
import librosa.display
# import IPython.display as ipd
import warnings
warnings.filterwarnings('ignore')
import os
import pathlib
import csv
from sklearn.metrics.pairwise import cosine_similarity
from sklearn import preprocessing
import matplotlib.pyplot as plt
# plt.rcParams["font.sans-serif"]=["SimHei"] #设置字体
plt.rcParams["axes.unicode_minus"]=False #该语句解决图像中的“-”负号的乱码问题
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei'] # 使用中文字體
from extensions.definitions import ROOT_DIR, _fullrecduration
import math

#%% 
'''輸入老師名稱並開始計算全部的特徵然後計算各句分數，預設為"柯銘峰"'''
'''segment: 第幾句, 1代表第一句'''

def sim_cal(tutor='柯銘峰(生)', mode=3):  
    print(">>>開始計算相似度")
    print('Select Tutor: {}'.format(tutor))
    start = time.time() # 計算用所花的時間
    # general_path = os.getcwd()
    # print(general_path)
    '''windows環境路徑'''
    # general_path = '.' ## windows 相對路徑
    # general_path = '/media/linsj-cilab/PNY CS2140/pythonworks/online_projects/work-w-audio-data-visualise-classify-recommend'   ## linux Path
    # print(list(os.listdir(f'{general_path}')))

    # 只有計算第一句時需要計算相似度。
    '''判斷是否只要伴奏'''
    if tutor == '空弦伴奏':
        score = [100, 100]
    else: # bgm_only==0，其他
        # 要比對用的多個特徵項
        header = 'filename length chroma_stft_mean chroma_stft_var rms_mean rms_var spectral_centroid_mean spectral_centroid_var spectral_bandwidth_mean spectral_bandwidth_var rolloff_mean rolloff_var zero_crossing_rate_mean zero_crossing_rate_var harmony_mean harmony_var perceptr_mean perceptr_var tempo'
        # to_append = f'{filename} {length} {np.mean(chroma_stft)} {np.var(chorma_stft)} {np.mean(rmse)} {np.var(rmse)} {np.mean(spec_cent)} {np.var(spec_cent)} {np.mean(spec_bw)} {np.var(spec_bw)} {np.mean(rolloff)} {np.var(rolloff)} {np.mean(zcr)} {np.var(zcr)} {np.mean(y_harm)} {np.var(y_harm)} {np.mean(y_perc)} {np.var(y_perc)} {tempo}'
        for i in range(1, 21):
            header += f' mfcc{i}_mean'
            header += f' mfcc{i}_var'
        header += ' label'
        header = header.split()

        # 有四句音檔: audio_1.wav, audio_2.wav, audio_3.wav, audio_4.wav
        # recordname = 'record_1.wav', 'record_2.wav', 'record_3.wav', 'record_4.wav'
        '''音檔檔名為audio_?.wav, segment代表?'''

        # 讀取特徵資料庫
        print('Read Database...')
        data = pd.read_csv(f'{ROOT_DIR}/cut_songs/features/whole_song_feature.csv', encoding='utf-8')   # index_col='filename'
        
        """2022.10.12 根據mode選擇計分句數"""
        if mode==1:
            start = 1
            end = 3
        elif mode==2:
            start = 3
            end = 5
        else: # default:整段四句
            start = 1
            end = 5
            
        for r in range(start, end):
            '''10/2 測試音檔/test_audio/audio_1~4.wav，柯銘峰cuts'''
            # wave, sr = librosa.load(f'{ROOT_DIR}/test_audio/audio_{r}.wav', mono=True)  ## load audio files，set sample rate to 16kHz
            wave, sr = librosa.load(f'{ROOT_DIR}/record/record_{r}.wav', mono=True)  ## load audio files，set sample rate to 16kHz
            ## 增加時間軸處理手動修剪
            if r == 1: 
                wave = wave[int(sr*0.4):]
                if tutor != '石惠君':
                    wave = wave[:sr*5]
                if tutor == '柯銘峰' or tutor == '王金櫻':
                    wave = wave[:sr*4]
            if r == 2:
                wave = wave[int(sr*0.5):int(sr*_fullrecduration[3]-sr*0.5)]
            if r == 3:
                wave = wave[int(sr*0.5):int(sr*_fullrecduration[7]-sr*0.5)]
            if r == 4:
                wave = wave[int(sr*0.1):]
            
            '''20221014 不修剪音訊檔，因為雜訊過多'''
            # trim_wave, y_index = librosa.effects.trim(wave, top_db=25) # 修剪音訊檔
            trim_wave = wave
            print('第{}句特徵計算中...'.format(r))

            ## 評分的特徵項
            print('>>>Feature Extracting...')
            length = librosa.get_duration(y=trim_wave, sr=sr)  ## length
            rmse = librosa.feature.rms(y=trim_wave) ## rmse
            chroma_stft = librosa.feature.chroma_stft(y=trim_wave, sr=sr)   ## chroma色度圖，可用於分析音樂的音高，捕獲音樂的和聲和旋律特徵，同時對音色和樂器的變化具有魯棒性
            spec_cent = librosa.feature.spectral_centroid(y=trim_wave, sr=sr)   ## spectral centroid
            spec_bw = librosa.feature.spectral_bandwidth(y=trim_wave, sr=sr)    ## spectral bandwidth
            rolloff = librosa.feature.spectral_rolloff(y=trim_wave, sr=sr)  ## spectral bandwidth
            zcr = librosa.feature.zero_crossing_rate(y=trim_wave)     ## zero-crossing rate bug點
            y_harm, y_perc = librosa.effects.hpss(y=trim_wave)   ## harmony & perceptral
            tempo, _ = librosa.beat.beat_track(y=trim_wave, sr=sr)  ## tempo
            mfcc = librosa.feature.mfcc(y=trim_wave, sr=sr, n_mfcc=20)     ## mfcc1~20，default:n_mfcc=20 
            f_name = f'record_{r}'
            to_append = f'{f_name} {round(length, 2)} {np.mean(chroma_stft)} {np.var(chroma_stft)} {np.mean(rmse)} {np.var(rmse)} {np.mean(spec_cent)} {np.var(spec_cent)} {np.mean(spec_bw)} {np.var(spec_bw)} {np.mean(rolloff)} {np.var(rolloff)} {np.mean(zcr)} {np.var(zcr)} {np.mean(y_harm)} {np.var(y_harm)} {np.mean(y_perc)} {np.var(y_perc)} {tempo}'
            for e in mfcc:
                to_append += f' {np.mean(e)} {np.var(e)}' 
            to_append += f' {r}' # 加入label
            writer = [(to_append.split())]
            dfNew = pd.DataFrame(writer, columns=header)
            data = data.append(dfNew, ignore_index=True) 
            # 存到data(dataframe)，等待餘弦比較&寫入csv，存儲。 未來可以擴展到錄音保存後&ranking.
        
        # 寫入到compare.csv，等待比對&檢驗。
        print('\nWrite in data')
        data.to_csv('compare.csv', index=False)
        # 略
        data = data.set_index('filename')
        # data
        # 比對前的前處理
        # Extract labels
        labels = data[['label']]

        # Drop labels from original dataframe
        data = data.drop(columns=['length','label'])

        # Scale the data
        data_scaled=preprocessing.scale(data)
        # print('Scaled data type:', type(data_scaled))
        
        # 進行相似度計算
        # Cosine similarity
        print('Do similarity comparison...')
        similarity = cosine_similarity(data_scaled)
        # print("Similarity shape:", similarity.shape)

        # Convert into a dataframe and then set the row index and column names as labels
        sim_df_labels = pd.DataFrame(similarity)
        sim_df_names = sim_df_labels.set_index(labels.index)
        sim_df_names.columns = labels.index
        # sim_df_names.tail()
        
        ## 取得對應的相似度數值
        score = []
        for sc in range(start, end): # 確認幾句的分數
            score.append(sim_df_names[f'record_{sc}'][f'{tutor}1-{sc}'])
        
    print('\nSimilarity Score: \n{}'.format(score)) ## 相似度分數，需在轉換
    
    # 結束測量程式運行時間
    end = time.time()
    # 輸出結果
    print("計算結束，共花費時間：%f 秒" % (end - start))
    return score


#%% 定義畫圖函式
def normalize(x, axis=0):
            return sklearn.preprocessing.minmax_scale(x, axis=axis)
        
def seg_plot(segment, tutor='柯銘峰(生)'):
    start = time.time() # 計算用所花的時間
    # 假設選擇學習柯老師
    print('Tutor: {}'.format(tutor))
    '''10/2 測試音檔/test_audio/audio_1~4.wav，柯銘峰cuts'''
    # wave, sr = librosa.load(f'{ROOT_DIR}/test_audio/audio_{segment}.wav', mono=True) 
    wave, sr = librosa.load(f'{ROOT_DIR}/record/record_{segment}.wav', mono=True)  ## load audio files，set sample rate to 16kHz
    '''20221014 更新錄音時間軸'''
    if segment == 1: 
        wave = wave[int(sr*0.4):]
        if tutor != '石惠君(旦)':
            wave = wave[:sr*5]
        if tutor == '柯銘峰(生)' or tutor == '王金櫻(旦)':
            wave = wave[:sr*4]
    if segment == 2:
        wave = wave[int(sr*0.5):]
    if segment == 3:
        wave = wave[int(sr*1.45):]
    if segment == 4:
        wave = wave[int(sr*0.1):]
    '''修剪音檔，去尾段'''
    trim_wave, y_index = librosa.effects.trim(wave, top_db=25) # 修剪音訊檔
    # trim_wave = wave
    print('第{}句畫圖中...'.format(segment))
    
    ## 1. 畫出比較圖
    '''音檔檔名為record_?.wav, segment代表?'''
    ### 1.1 畫出音高曲線圖
    print('>>>Sentence {} Pitch Contour Calculating...'.format(segment))
    plt.rcParams["figure.figsize"] = (20, 5)
    # # 音高頻率估計，解析度設定 resolution = 0.5
    # f0_1, _, _ = librosa.pyin(trim_wave, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'), sr=sr, resolution = 0.5)
    # times1 = librosa.times_like(f0_1)
    # 只要伴奏則不需要load原檔
    if tutor != '空弦伴奏':
        tutor_wave = f'{ROOT_DIR}/cut_songs/{segment}/{tutor}1-{segment}.wav' # 選擇比較用的author音檔
        y2, _ = librosa.load(tutor_wave, mono=True)
        y2_trim, _ = librosa.effects.trim(y2, top_db=25)
        f0_2, _, _ = librosa.pyin(y2_trim, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'), sr=sr, resolution = 1)
        times2 = librosa.times_like(f0_2)
        # 將tutor和input音檔的標準化
        rate = np.max(abs(y2)) / np.max(abs(trim_wave))
        for sample in range(len(trim_wave)):
            trim_wave[sample] = trim_wave[sample] * rate
    # 音高頻率估計，解析度設定 resolution = 0.5
    f0_1, _, _ = librosa.pyin(trim_wave, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'), sr=sr, resolution = 1)
    times1 = librosa.times_like(f0_1)
    
    # 畫圖
    librosa.display.waveshow(trim_wave, sr=sr, alpha=0.2)
    plt.plot(times1, normalize(f0_1), label='Student', color='r', linewidth=2)
    if tutor != '空弦伴奏': # 只要伴奏則不需要load導師音檔
        plt.plot(times2, normalize(f0_2), 'g--', label=f'Tutor:{tutor}', linewidth=2)
    plt.legend(loc='best') 
    plt.title(f'Segment {segment} pitch contour compared with {tutor}') 
    plt.axis('on') 
    plt.grid()
    plt.savefig(f'{ROOT_DIR}/results/s{segment}_pitch_results.jpg') 
    plt.clf() 

    ### 1.2 畫出響度曲線圖
    # Compute the short-time energy using a list comprehension:
    print('>>>Sentence {} Loudness Contour Calculating...'.format(segment))
    hop_length = 256
    frame_length = 512
    energy1 = np.array([
        sum(abs(trim_wave[i:i+frame_length]**2))
        for i in range(0, len(trim_wave), hop_length)
    ])
    frames1 = range(len(energy1))
    t1 = librosa.frames_to_time(frames1, sr=sr, hop_length=hop_length)
    if tutor != '空弦伴奏': # 只要伴奏則不需要load導師音檔
        energy2 = np.array([
            sum(abs(y2_trim[i:i+frame_length]**2))
            for i in range(0, len(y2_trim), hop_length)
        ]) 
        frames2 = range(len(energy2))
        t2 = librosa.frames_to_time(frames2, sr=sr, hop_length=hop_length)
    librosa.display.waveshow(trim_wave, sr=sr, alpha=0.3)
    plt.plot(t1, energy1/energy1.max(), 'r', label='Student', linewidth=2)             # normalized for visualization
    if tutor != '空弦伴奏': # 只要伴奏則不需要load導師音檔
        plt.plot(t2, energy2/energy2.max(), 'g--', label=f'Tutor:{tutor}', linewidth=2)             # normalized for visualization
    plt.legend(loc='best')
    plt.title(f"Segment {segment} loudness contour compared with {tutor}")
    plt.xlabel('Time(s)')
    plt.grid()
    plt.savefig(f'{ROOT_DIR}/results/s{segment}_loudness_results.jpg') # 位置待確認
    plt.clf()

    ### 1.3 畫出音色分布圖
    if tutor == '空弦伴奏':
        print('>>>sentence {} Timbre Cpectrogram Calculating...'.format(segment))
        D1 = librosa.amplitude_to_db(np.abs(librosa.stft(trim_wave)), ref=np.max)
        fig, ax = plt.subplots()
        ax.img = librosa.display.specshow(D1, x_axis='time', y_axis='log', ax=ax)
        ax.set(title='Student Timbre')
        fig.colorbar(ax.img, ax=ax, format="%+2.f dB")
        ax.plot(times1, f0_1, label='Student', color='cyan', linewidth=2)
        ax.legend(loc='upper right')
        plt.xlabel('Time(s)')
        plt.axis('on') 
        plt.grid()
        plt.savefig(f'{ROOT_DIR}/results/s{segment}_timbre_results.jpg') 
        plt.clf()
    else: # '空弦伴奏'以外
        print('>>>sentence {} Timbre Cpectrogram Calculating...'.format(segment))
        D1 = librosa.amplitude_to_db(np.abs(librosa.stft(trim_wave)), ref=np.max)
        D2 = librosa.amplitude_to_db(np.abs(librosa.stft(y2_trim)), ref=np.max)
        fig, ax = plt.subplots(1,2)
        ax[0].img = librosa.display.specshow(D1, x_axis='time', y_axis='log', ax=ax[0])
        ax[0].set(title='Student Timbre')
        fig.colorbar(ax[0].img, ax=ax, format="%+2.f dB")
        ax[0].plot(times1, f0_1, label='Student', color='cyan', linewidth=2)
        ax[0].legend(loc='upper right')
        ax[1].img = librosa.display.specshow(D2, x_axis='time', y_axis='log', ax=ax[1])
        ax[1].set(title=f'{tutor} Tutor Timbre')
        ax[1].plot(times2, f0_2, label=f'Tutor:{tutor}', color='blue', linewidth=2)
        ax[1].legend(loc='upper right')
        plt.xlabel('Time(s)')
        plt.axis('on') 
        ax[0].grid()
        ax[1].grid()
        plt.savefig(f'{ROOT_DIR}/results/s{segment}_timbre_results.jpg') 
        plt.clf()
    
    # 結束測量程式運行時間
    end = time.time()
    print("花費時間：%f 秒" % (end - start))


'''計算分數from [-1,1] map2 [60,100]'''
'''20221120 更改分數範圍=[0,100]'''
def map(data, MIN=0, MAX=100):
    """
    归一化映射到任意区间
    :param data: 数据
    :param MIN: 目标数据最小值
    :param MAX: 目标数据最小值
    :return:
    """
    # d_min = np.max(data)    # 当前数据最大值
    # d_max = np.min(data)    # 当前数据最小值
    d_min = -1
    d_max = 1
    return MIN +(MAX-MIN)/(d_max-d_min) * (data - d_min)
    

    
if __name__ == "__main__":
    print('>>>計算系統導入成功')
    print('計算結束')
