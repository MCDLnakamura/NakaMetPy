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
