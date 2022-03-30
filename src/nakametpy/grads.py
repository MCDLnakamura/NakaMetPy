# Copyright 2022 nakamura_yuki. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

import numpy as np
from numpy import ma
import re
import os
import glob
import warnings
import datetime

class GrADS:
  """
  A nakametpy.grads `GrADS` is a collection of dimensions and variables. 

  The following class variables are read-only.

  **`dimensions`**: The `dimensions` dictionary maps the names of
  dimensions defined for the `Dataset` to instances of the
  `Dimension` class.

  **`variables`**: The `variables` dictionary maps the names of variables
  defined for this `Dataset` or `Group` to instances of the
  `Variable` class.
  """
  def __init__(self, filename, s2n=True, endian=None, do_squeeze=True):
    """
      **`__init__(self, filename, s2n=True, endian=None, do_squeese=True`**
      
      `GrADS` constructor which is simular to netCDF4-Python `Dataset` constructor.
      
      **`filename`**: Name of GrADS control file to handle GrADS binary data.
      
      **`s2n`**: Data saved direction in ydef.
      
      **`endian`**: Endian of the binary data. `big_endian`, `little_endian` and `native_endian` are available.
      
      **`do_squeeze`**: Whether drop dimension which have only one element. Default is True.
    """
    self.filename = filename
    self.do_squeese = do_squeeze
    self.dimensions = dict()
    
    with open(self.filename) as f:
      lines = f.readlines()
      
    _sidx = 1E30 # provisional value
    _eidx = None
    _var_idx = []
    _nzdims = []
    
    for idx, line in enumerate(lines):
      if "*" in line[:3]: # check for comment out
        continue
      else:
        if "dset" in line.lower():
          _binname = _get_line_list(line)[1]
          _binname = _replace_template(_binname)
          if "/" == _binname[0]: # is this enough ?
            self.binname = glob.glob(_binname)[0]
          else:
            self.binname = glob.glob(os.path.join(os.path.dirname(self.filename), _binname))[0]
          continue
            
        if "undef" in line.lower():
          self.undef = float(_get_line_list(line)[1])
          continue
          
        if "options" in line.lower():
          if "big_endian" in line.lower():
            self.endian = "big_endian"
          elif "little_endian" in line.lower():
            self.endian = "little_endian"
          else:
            self.endian = "native_endian"
          continue
          
        if "xdef" in line.lower():
          if "linear" in line.lower():
            _xdef = _get_line_list(line)
            self.dimensions["xdef"] = Dimension(np.arange(float(_xdef[3]), float(_xdef[3])+float(_xdef[1])*float(_xdef[4]), float(_xdef[4])), "xdef")
            self.nx = int(_xdef[1])
          else:
            warnings.warn("Debug Warning: Currently, Only 'LINEAR' is supported in XDEF.")
          continue
          
        if "ydef" in line.lower():
          if "linear" in line.lower():
            _ydef = _get_line_list(line)
            self.dimensions["ydef"] = Dimension(np.arange(float(_ydef[3]), float(_ydef[3])+float(_ydef[1])*float(_ydef[4]), float(_ydef[4]))[::(-1)**(int(s2n)+1)], "ydef") # if s2n is True -> +1, if False -> -1
            self.ny = int(_ydef[1])
          else:
            warnings.warn("Debug Warning: Currently, Only 'LINEAR' is supported in YDEF.")
          continue
          
        if "zdef" in line.lower():
          if "levels" in line.lower():
            _zdef = _get_line_list(line)
            _zdef = [float(_izdef) for _izdef in _zdef[3:int(_zdef[1])+3]]
            self.dimensions["zdef"] = Dimension(np.array(_zdef), "zdef")
          else:
            warnings.warn("Debug Warning: Currently, Only 'LEVELS' is supported in ZDEF.")
          continue
          
        if "tdef" in line.lower():
          if "linear" in line.lower():
            _tdef = _get_line_list(line)
            _init_dt = datetime.datetime.strptime(_tdef[3].title(), "%HZ%d%b%Y")
            self.nt = int(_tdef[1])
            if _tdef[4][-2:].lower() == "hr":
              self.dimensions["tdef"] = Dimension(np.array([_init_dt + i*datetime.timedelta(hours=int(_tdef[4][:-2])) for i in range(int(_tdef[1]))]), "tdef")
            elif _tdef[4][-2:].lower() == "dy":
              self.dimensions["tdef"] = Dimension(np.array([_init_dt + i*datetime.timedelta(days=int(_tdef[4][:-2])) for i in range(int(_tdef[1]))]), "tdef")
            elif _tdef[4][-2:].lower() == "mo":
              self.dimensions["tdef"] = Dimension(np.array([_init_dt + i*datetime.timedelta(months=int(_tdef[4][:-2])) for i in range(int(_tdef[1]))]), "tdef")
          else:
            warnings.warn("Debug Warning: Currently, Only 'LINEAR' is supported in TDEF.")
          continue

        if bool(re.match("^vars", line.lower())):
          _sidx = idx
          _nvar2 = int(_get_line_list(line)[1])
          continue
        if bool(re.match("^endvars", line.lower())):
          _eidx = idx
          continue
        if (_sidx<idx) and (_eidx==None):
          _var_idx.append(idx)
          _inzdim = int(_get_line_list(line)[1])
          if _inzdim==0:
            _nzdims.append(1)
          else:
            _nzdims.append(_inzdim)
          
    if endian!=None:
      self.endian = endian
    if len(_var_idx)!=_nvar2:
      warnings.warn("The Number of variables is NOT match.")
      
    self.variables = _get_vars(self, lines, _var_idx, _nzdims, do_squeeze)

def _get_vars(self, lines, idx_list, nz_list, do_squeese): # self : grads.GrADS object
  variables = dict()
  for inidx, iline_idx in enumerate(idx_list):
    iline = lines[iline_idx]
    _ivar_list = _get_line_list(iline)
    varname = _ivar_list[0]
    idesc = None
    
    if "**" in iline:
      idesc = iline[(iline.index("**") + 1):].replace("\n", "").strip()
      if idesc == " ":
        idesc = None
    elif "*" in iline:
      idesc = iline[iline.index("*"):].replace("\n", "").strip()
      if idesc == " ":
        idesc = None
    else:
      idesc = None
    
    varids = np.cumsum(np.array(nz_list))
    _loop_block = varids[-1]
    varids = list(varids[:-1])
    varids.insert(0,0)
    varids = np.array(varids)
    
    variables[_ivar_list[0]] = Variable(self.binname, varname, varids[inidx],\
                        _loop_block, self.nx, self.ny, nz_list[inidx],\
                        self.nt, self.endian, self.undef, idesc, do_squeese)
  
  return variables      

def _get_line_list(line):
  return [i for i in re.split("[\s\t\n^,]+", \
          line.replace("\n", "", 1).strip()) if i != ""]
  
def _replace_template(dset):
  for i in range(1, 5, 1):
    dset = re.sub(f"%[a-z]{i}", "?"*i, dset)
  return dset
            
class Variable:
  def __init__(self, binname, varname, varid, loop_block, nx, ny, nz, nt, endian, undef, desc, do_squeese):
    self._name = varname
    self._undef = undef
    self._binname = binname
    self._varid = varid
    self._loop_block = loop_block
    self._endian = endian
    self._nx = nx
    self._ny = ny
    self._nz = nz
    self._nt = nt
    self._dtype = np.float32
    self._desc = desc
    self._do_squeese = do_squeese

  def __array__(self):
    return self[...]

  def __repr__(self):
    return self.__str__()

  def __getitem__(self, elem):
    return _sel(self._binname, self._varid, self._loop_block, self._endian,\
      self._nx, self._ny, self._nz, self._nt, self._undef, self._do_squeese)[elem]

  def __str__(self):
    ncdump = [repr(type(self))]
    ncdump.append(f'{self._dtype} {self._name}({self._nt}, {self._nz}, {self._ny}, {self._nx})')
    ncdump.append(f"    description: {self._desc}")
    ncdump.append(f"    _FillValue: {self._undef}")
    return "\n".join(ncdump)

  def sel(self,  zidx=None, tidx=None):
    return _sel(self._binname, self._varid, self._loop_block, self._endian, self._nx, self._ny, self._nz, self._nt, self._undef, self._do_squeese,  zidx, tidx)

def _sel(binname, varid, loop_block, endian, nx, ny, nz, nt, undef, do_squeese,  zidx=None, tidx=None):
  with open(binname, "rb") as f:
    _data = []
    if (zidx==None)&(tidx==None): # get ALL
      for _i in range(nt):
        f.seek((_i*loop_block+varid)*nx*ny*4, os.SEEK_SET)
        _data.append(ma.masked_equal(ma.masked_array(np.fromfile(f,\
          dtype=_endian2simbole(endian)+"f4", count=nx*ny*nz)), value=undef).reshape(nz, ny, nx))
    else:
      if tidx==None: # get specific z level (get ALL in t)
        if isinstance(zidx, int):
          for _i in range(nt):
            f.seek((_i*loop_block+varid+zidx)*nx*ny*4, os.SEEK_SET)
            _data.append([ma.masked_equal(ma.masked_array(np.fromfile(f,\
              dtype=_endian2simbole(endian)+"f4", count=ny*nx)), value=undef).reshape(ny, nx)])
        elif isinstance(zidx, (list, tuple, np.ndarray)):
          for _i in range(nt):
            _idata = []
            for izidx in zidx:
              f.seek((varid+_i*loop_block+izidx)*nx*ny*4, os.SEEK_SET)
              _idata.append(ma.masked_equal(ma.masked_array(np.fromfile(f, dtype=_endian2simbole(endian)+"f4", count=ny*nx)), value=undef).reshape(ny, nx))
            _data.append(ma.masked_array(_idata))
      elif zidx==None: # get specific t time (get ALL in z)
        if isinstance(tidx, int):
          f.seek((tidx*loop_block+varid)*nx*ny*4, os.SEEK_SET)
          _data.append(ma.masked_equal(ma.masked_array(np.fromfile(f, dtype=_endian2simbole(endian)+"f4", count=nx*ny*nz)), value=undef).reshape(nz, ny, nx))
        elif isinstance(tidx, (list, tuple, np.ndarray)):
          for _itidx in tidx:
            f.seek((_itidx*loop_block+varid)*nx*ny*4, os.SEEK_SET)
            _data.append(ma.masked_equal(ma.masked_array(np.fromfile(f, dtype=_endian2simbole(endian)+"f4", count=nx*ny*nz)), value=undef).reshape(nz, ny, nx))
      else:
        if isinstance(tidx, int):
          if isinstance(zidx, int):
            f.seek((tidx*loop_block+varid)*nx*ny*4, os.SEEK_SET)
            _data.append([ma.masked_equal(ma.masked_array(np.fromfile(f, dtype=_endian2simbole(endian)+"f4", count=nx*ny)), value=undef).reshape(ny, nx)])
          elif isinstance(zidx, (list, tuple, np.ndarray)):
            _idata = []
            for _izidx in zidx:
              f.seek((varid+tidx*loop_block+_izidx)*nx*ny*4, os.SEEK_SET)
              _idata.append(ma.masked_equal(ma.masked_array(np.fromfile(f, dtype=_endian2simbole(endian)+"f4", count=nx*ny)), value=undef).reshape(ny, nx))
            _data.append(_idata)
        elif isinstance(tidx, (list, tuple, np.ndarray)):
          if isinstance(zidx, int):
            for _itidx in tidx:
              f.seek((_itidx*loop_block+varid+zidx)*nx*ny*4, os.SEEK_SET)
              _data.append([ma.masked_equal(ma.masked_array(np.fromfile(f, dtype=_endian2simbole(endian)+"f4", count=nx*ny)), value=undef).reshape(ny, nx)])
          elif isinstance(zidx, (list, tuple, np.ndarray)):
            for _itidx in tidx:
              _idata = []
              for _izidx in zidx:
                f.seek((varid+_itidx*loop_block+_itidx)*nx*ny*4, os.SEEK_SET)
                _idata.append(ma.masked_equal(ma.masked_array(np.fromfile(f, dtype=_endian2simbole(endian)+"f4", count=nx*ny)), value=undef).reshape(ny, nx))
              _data.append(_idata)
            
  _data = ma.masked_array(_data)
  if do_squeese:
    return ma.squeeze(_data)
  else:
    return _data


class Dimension:
  def __init__(self, data, var):
    self.values = data
    self.dim = var

  def __array__(self):
    return self[...]

  def __repr__(self):
    return self.__str__()

  def __getitem__(self, elem):
    return self.values[elem]

  def __str__(self):
    ncdump = [repr(type(self))]
    ncdump.append(f"    variables(dimensions): {self.dim}, ")
    ncdump.append(f"    dimensions(sizes): {len(self.values)}, ")
    ncdump.append(f"    dimensions(data): {self.values}, ")
    return "\n".join(ncdump)

def _endian2simbole(endian):
  if endian.lower() == "big_endian":
    return ">"
  elif endian.lower() == "little_endian":
    return "<"
  elif endian.lower() == "native_endian":
    return "="
  else:
    return ""