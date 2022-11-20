import os

# ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(".")
TEMP_DIR = os.path.join(ROOT_DIR, "temp")
RESULT_DIR = os.path.join(ROOT_DIR, "results")
CHART_DIR = os.path.join(ROOT_DIR, "charts")
BACKUP_DIR = os.path.join(ROOT_DIR, "backup")
MUSIC_DIR = os.path.join(ROOT_DIR, "musics")
IMAGE_DIR = os.path.join(ROOT_DIR, "images")
CONFIG_DIR = os.path.join(ROOT_DIR, "configs")
RECORD_DIR = os.path.join(ROOT_DIR, "record")

CHART_TYPE = "jpg"
DEFAULT_TUTOR = "C02"

_songLyrics = ["身騎白馬 走三關",
                "改換素衣回中原",
                "放下西涼無人管",
                "思念三姐王寶釧 (三姐王寶釧)"]

_songSentences = ["sentence 1",
                    "sentence 2",
                    "sentence 3",
                    "sentence 4"]

_songFeatures = ["pitch",
                    "loudness",
                    "timbre"]

'''
    lyrics
    0:00~0:18 身騎白馬 
    0.18~0:32 走三關 改換素衣回中原，需要調整成"改"之前換字幕
    0:30~0:45 放下西涼無人管
    0:45~1:01 思念三姐王寶釧(三姐王寶釧) 
    2022.10.13 尚須根據分段去做show時間的調整
'''

# _lyricsduration = [ 18, 14, 15, 16] # lyrics也要用
_fulllyricsduration = [ 18, 11, 15, 19] 
_headlyricsduration = [ 18, 10]    # 分兩段的話，0:00~0:28(0:29) 
_taillyricsduration = [ 12, 23]   # 0:29~end

'''
    records
    10/10 前奏、第一段、sleep、第二段、sleep、第三段、sleep、第四段、(結束)
    錄四段
        前奏 6s
        0:06~0:13 身騎白馬 7s
        間奏1 2s
        0.15~0:28走三關 改換素衣回中原 13s
        間奏2 5s
        0:33~0:42放下西涼無人管 9s
        間奏3 3s
        0:45~1:00思念三姐王寶釧(三姐王寶釧) 16s
        尾奏
'''
# _recordsduration = [ 6, 7, 2, 13, 5, 9, 3, 15] # 錄音和休息時長
_fullrecduration = [7, 6, 2, 12,  # 前段 共28秒
                    5, 8, 6, 13 ] # 後段 共32秒
_headrecduration = [7, 6, 2, 12]  
_tailrecduration = [3, 8, 6, 13]

# 20221014下歌點
''' 
    間奏 0~7
1.  7.07~11.002 7~11 4s
    間奏 11~15 4s
2.  15.771~26.9 15(=15.5)~27(=26.5) 需要trim 12
    間奏 27~32 5s 27~29=2/29~32=3
3.  32.933~39.584 32(=32.5)~40(=39.5) 8
    間奏 40~46 6s
4.  46.403~59.376 46(46.3)~60 13 需要trim 
    結束
    
'''