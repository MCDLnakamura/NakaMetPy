# Copyright 2021 nakamura_yuki
# 
from .util import jma_rain_lat, jma_rain_lon

def load_jmara_grib2(file, tar_flag=False, tar_contentname=None):
  r'''気象庁解析雨量やレーダー雨量を返す関数

  欠損値は負の値として表現される

  Parameters
  --------
  file: `str`
    file path 
    ファイルのPATH
  tar_flag: `bool`
    file type whether file is tar or GRIB2 (not tar).
  tar_contentname: `str`
    content name in tar file.

  Returns
  -------
  rain: `numpy.ma.MaskedArray`
    Units(単位) [mm/h]

  Note
  -----
  The same as util.load_jmara_grib2.
  '''
  from .util import load_jmara_grib2 as _func
  return _func(file, tar_flag, tar_contentname)

jma_rain_lat = jma_rain_lat
jma_rain_lon = jma_rain_lon


def get_jmara_lat():
  r'''解析雨量の緯度を返す関数

  Returns
  -------
  lat: `numpy.ndarray`

  Note
  -----
  The same as util.get_jmara_lat.
  '''
  from .util import get_jmara_lat as _func
  return _func()

def get_jmara_lon():
  r'''解析雨量の経度を返す関数

  Returns
  -------
  lon: `numpy.ndarray`
  
  Note
  -----
  The same as util.get_jmara_lon.
  '''
  from .util import get_jmara_lon as _func
  return _func()



def load_jmara(year='2005',month='10',day='21',hour='00',mimute='00'):
  r'''全国合成レーダーGPVを返す関数
  '''
  import urllib.request
  import tempfile
  import os 
  _url = f"http://database.rish.kyoto-u.ac.jp/arch/jmadata/data/jma-radar/synthetic/original/{year}/{month}/{day}/Z__C_RJTD_{year}{month}{day}{hour}{mimute}00_RDR_JMAGPV__grib2.tar"
  _fd, _tmpfile = tempfile.mkstemp()
  _req = urllib.request.Request(_url)
  try:
    with urllib.request.urlopen(_req) as _res:
      _urlData = _res.read()
      with open(_tmpfile ,mode='wb') as f:
        f.write(_urlData)
      _tar_contentname=f"Z__C_RJTD_{year}{month}{day}{hour}{mimute}00_RDR_JMAGPV_Ggis1km_Prr10lv_ANAL_grib2.bin"
      _data=load_jmara_grib2(_tmpfile, tar_flag=True, tar_contentname=_tar_contentname)
      os.remove(_tmpfile)
      return _data
  except urllib.error.HTTPError as err:
    print(err.code)
  except urllib.error.URLError as err:
    print(err.reason)

    def load_jma_amedas(prec_no,block_no,year='2020',month='1',day='1'):
  r'''アメダスの値を返す関数
  参考:https://met-learner.hatenablog.jp/entry/2019/12/15/123637
  '''
  # import time
  from datetime import datetime
  import numpy as np
  import urllib.request
  # とりあえずpandasでかく 
  # インストールの時にコンフリクトを起こす可能性があるので出来るだけ外部ライブラリは増やしたくない
  import pandas as pd

  # 地点によって形式が異なる
  kind='a' #赤丸
  _url = f'http://www.data.jma.go.jp/obd/stats/etrn/view/10min_{kind}1.php?prec_no={prec_no}&block_no={block_no}&year={year}&month={month}&day={day}&view=p1'
  try:
    _tables = pd.io.html.read_html(_url)
    _flag=True
  except AttributeError:
    _flag=False
  except ValueError:
    _flag=False

  if _flag==False:
    kind='s' #赤二重丸
    _url = f'http://www.data.jma.go.jp/obd/stats/etrn/view/10min_{kind}1.php?prec_no={prec_no}&block_no={block_no}&year={year}&month={month}&day={day}&view=p1'
    _tables = pd.io.html.read_html(_url)
    try:
      _tables = pd.io.html.read_html(_url)
      _flag=True
    except AttributeError:
      print("地点エラー")
    except ValueError:
      print("地点エラー")



  ##### スクレイピング #####
  _tables = pd.io.html.read_html(_url)
  _df = _tables[0].iloc[:,1:] 
  _df = _df.reset_index(drop = True)

  ##### 列名を指定 #####
  if kind=='s':
    _df.columns = ['PRESSURE','SLP','PRC', 'TEMP', 'RH','WS_MEAN', 'WD_MEAN', 'WS_GUST', 'WD_GUST', 'SUN']
  else :
    _df.columns = ['PRC', 'TEMP', 'RH','WS_MEAN', 'WD_MEAN', 'WS_GUST', 'WD_GUST', 'SUN']

  ##### 欠測値の処理 #####
  _df = _df.replace('///', None) # --- '///' を欠測値として処理
  _df = _df.replace('×', None) # --- '×' を欠測値として処理
  _df = _df.replace('\s\)', '', regex = True) # --- ')' が含まれる値を正常値として処理
  _df = _df.replace('.*\s\]', None, regex = True) # --- ']' が含まれる値を欠測値として処理
  _df = _df.replace('#', None) # --- '#'が含まれる値を欠測値として処理
  _df = _df.replace('--', None) # --- '--'が含まれる値を欠測値として処理

  ##### 風向を北0°で時計回りの表記に変更 #####
  _df.loc[:,['WD_MEAN', 'WD_GUST']] = _df.loc[:,['WD_MEAN', 'WD_GUST']].replace('北北東', '22.5')
  _df.loc[:,['WD_MEAN', 'WD_GUST']] = _df.loc[:,['WD_MEAN', 'WD_GUST']].replace('東北東', '67.5')
  _df.loc[:,['WD_MEAN', 'WD_GUST']] = _df.loc[:,['WD_MEAN', 'WD_GUST']].replace('東南東', '112.5')
  _df.loc[:,['WD_MEAN', 'WD_GUST']] = _df.loc[:,['WD_MEAN', 'WD_GUST']].replace('南南東', '157.5')
  _df.loc[:,['WD_MEAN', 'WD_GUST']] = _df.loc[:,['WD_MEAN', 'WD_GUST']].replace('南南西', '202.5')
  _df.loc[:,['WD_MEAN', 'WD_GUST']] = _df.loc[:,['WD_MEAN', 'WD_GUST']].replace('西南西', '247.5')
  _df.loc[:,['WD_MEAN', 'WD_GUST']] = _df.loc[:,['WD_MEAN', 'WD_GUST']].replace('西北西', '292.5')
  _df.loc[:,['WD_MEAN', 'WD_GUST']] = _df.loc[:,['WD_MEAN', 'WD_GUST']].replace('北北西', '337.5')
  _df.loc[:,['WD_MEAN', 'WD_GUST']] = _df.loc[:,['WD_MEAN', 'WD_GUST']].replace('北東', '45.0')
  _df.loc[:,['WD_MEAN', 'WD_GUST']] = _df.loc[:,['WD_MEAN', 'WD_GUST']].replace('南東', '135.0')
  _df.loc[:,['WD_MEAN', 'WD_GUST']] = _df.loc[:,['WD_MEAN', 'WD_GUST']].replace('南西', '225.0')
  _df.loc[:,['WD_MEAN', 'WD_GUST']] = _df.loc[:,['WD_MEAN', 'WD_GUST']].replace('北西', '315.0')
  _df.loc[:,['WD_MEAN', 'WD_GUST']] = _df.loc[:,['WD_MEAN', 'WD_GUST']].replace('北', '360.0')
  _df.loc[:,['WD_MEAN', 'WD_GUST']] = _df.loc[:,['WD_MEAN', 'WD_GUST']].replace('東', '90.0')
  _df.loc[:,['WD_MEAN', 'WD_GUST']] = _df.loc[:,['WD_MEAN', 'WD_GUST']].replace('南', '180.0')
  _df.loc[:,['WD_MEAN', 'WD_GUST']] = _df.loc[:,['WD_MEAN', 'WD_GUST']].replace('西', '270.0')
  _df.loc[:,['WD_MEAN', 'WD_GUST']] = _df.loc[:,['WD_MEAN', 'WD_GUST']].replace('静穏', '-888.8')

  ##### 時刻列を追加 #####
  # _df['DATE'] = pd.date_range(datetime(year, month, day, 0, 10, 0), periods = len(_df), freq = '10T')
  _df['DATE'] = pd.date_range(datetime(int(year), int(month), int(day), 0, 10, 0), periods = len(_df), freq = '10T')

  ##### 年/月/日/時/分/秒 の各列を追加 #####
  _df['YEAR'] = _df['DATE'].dt.year
  _df['MONTH'] = _df['DATE'].dt.month
  _df['DAY'] = _df['DATE'].dt.day
  _df['HOUR'] = _df['DATE'].dt.hour
  _df['MINUTE'] = _df['DATE'].dt.minute
  _df['SECOND'] = _df['DATE'].dt.second
  return _df
