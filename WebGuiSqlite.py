import os

import socket

from IPython.display import display, Javascript, HTML, clear_output
import IPython
from datetime import datetime

def popup(line, cell=None):
  _w, _h  = 1200,800
  if cell is None:
    with open(line) as f:
      html = f.read()
  else:
    html = cell
    if type(line) is list:
      _w, _h = line
    elif type(line) is str:
      _wh = line.split(',')
      if len(_wh) == 2:
        _w, _h = [int(x) for x in _wh]  
  wName = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
  _s  = f'\nvar win = window.open("", "{wName}",' 
  _s += '"toolbar=no, location=no, directories=no, status=no, menubar=no, scrollbars=yes, resizable=yes, ' 
  _s += f'width={_w}, height={_h}");'
  _s += f'\nwin.document.write(`\n{html}\n`);'
  display(Javascript(_s))  
  return

IPython.get_ipython().register_magic_function(popup, 'line')
IPython.get_ipython().register_magic_function(popup, 'cell')

def msgBox(title,body,button):
  _JS = '''
    require(
        ["base/js/dialog"], 
        function(dialog) {
            dialog.modal({
                title: '%s',
                body: `%s`,
                buttons: {
                    '%s': {}
                }
            });
        }
    );
    ''' % (title,body,button)
  display(Javascript(_JS))
  return  

# .............................................................................................................................
import ipywidgets as widgets
import io
import pandas as pd

import time
import sqlite3
import os.path
import subprocess
import sys


class WebGuiSqlite:
  def __init__(self):
    self.osname = os.name
    self.subpy = None
    self.xls_uploader = widgets.FileUpload(description="Upload Excel workbook & converting to SQLite-file",
                                           accept='.xls,.xlsx,.xlsm')
  def __call__(self):
    return self.xls_uploader.value[0]
  def xlsupload(self):
    display(self.xls_uploader)

  def xls2sqlite(self,change):
    ioData = io.BytesIO(change.new[0].content.tobytes())
    con = sqlite3.connect(":memory:")
    wb = pd.ExcelFile(ioData)
    for sheet in wb.sheet_names:
      df=pd.read_excel(ioData,sheet_name=sheet)
      df.to_sql(sheet,con, index=False,if_exists="replace")
    con.commit()

    dbPath = os.path.splitext(self.xls_uploader.value[0].name)[0] + '.sqlite'
    db_disk = sqlite3.connect(dbPath)
    con.backup(db_disk)
    con.close()

    from IPython.display import FileLink
    display(FileLink(dbPath))
    msgBox('Workbook uploaded & converted successfully', change.new[0].name, 'continue')

  def kill(self):
    time.sleep(1.5)
    if self.osname == 'posix':
      os.system('pkill -f "python -m http.server"')
    else:
      if type(self.subpy) is subprocess.Popen: self.subpy.kill()    
    time.sleep(0.5)
    
  def runGui(self, opt=0):
    self.kill()
    self.subpy = subprocess.Popen([sys.executable, "-m", "http.server", "-d", "site", "8002"], 
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.5)
    if opt==1:
      script = '''<script>window.location.assign("http://%s:8002/site1/Web-GUI-for-SQLite.html");</script>''' % socket.gethostname()
      popup('', cell=script)
    elif opt==2:  
      script = '''<script>window.location.assign("http://%s:8002/site2/index.html");</script>''' % socket.gethostname()
      popup('1000,700', cell=script)
    self.kill()
# .............................................................................................................................

def applet():
  clear_output()
  from ipywidgets import HBox, Label, Button, Layout
  
  WGS = WebGuiSqlite()
  WGS.xls_uploader.observe(WGS.xls2sqlite, 'value')

  style={'font_weight': 'bold_', 'font_size': '14px'}
  b1 = Button(description="run Web GUI for SQLite", layout=Layout(width='20%', height='30px'), style=style)
  b2 = Button(description="run SQLite Viewer", layout=b1.layout, style=style)
  def on_b1(b):
    WGS.runGui(opt=1)
  def on_b2(b):
    WGS.runGui(opt=2)
    
  b1.on_click(on_b1)
  b2.on_click(on_b2)

  WGS.xls_uploader.layout = Layout(width='50%')
  WGS.xls_uploader.style=style
  
  H=HBox([WGS.xls_uploader, b1, b2])
  display(H)
  
applet()