import os

from IPython.display import display, HTML, clear_output
#print(f"Loading from '{__file__}'")
display(f"Loading from '{__file__}'")
display(HTML("<style>.container { width:100% !important; }</style>"))

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
  #clear_output()
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

import sqlite3
import os.path


class WebGuiSqlite:
  def __init__(self):
    self.xls_uploader = widgets.FileUpload(description="Upload Excel workbook", accept='.xls,.xlsx,.xlsm')
  def __call__(self):
    return self.xls_uploader.value[0]
  def xlsupload(self):
    display(self.xls_uploader)

  def xls2sqlite(self):
    if len(self.xls_uploader.value) == 0:
      msgBox("converting Excel-file to SQLite-file","Excel-file not loaded","ERROR!")
      return
    ioData = io.BytesIO(self.xls_uploader.value[0].content.tobytes())

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

  def runGui(self, opt=0):
    os.system('pkill -f "python -m http.server"')
    os.system('python -m http.server -d "site" 8002 > /dev/null 2>&1 &')
    #print(os.system('ps -ef | grep "python -m http.server" | grep -v grep'))
    
    if opt==1:
      script = '''<script>window.location.assign("http://%s:8002/site1/Web-GUI-for-SQLite.html");</script>''' % socket.gethostname()
      popup('', cell=script)
      return
    elif opt==2:  
      script = '''<script>window.location.assign("http://%s:8002/site2/index.html");</script>''' % socket.gethostname()
      popup('1000,700', cell=script)
      return
    
    os.system('pkill -f "python -m http.server"')
    os.system('ps -ef | grep "python -m http.server" | grep -v grep')
# .............................................................................................................................
#WGS = None

def applet():
  clear_output()
  from ipywidgets import HBox, Label, Button, Layout
  #global WGS
  
  WGS = WebGuiSqlite()
  
  style={'font_weight': 'bold_', 'font_size': '14px'}
  b1 = Button(description="run Web GUI for SQLite", layout=Layout(width='20%', height='30px'), style=style)
  b2 = Button(description="run SQLite Viewer", layout=b1.layout, style=style)
  b3 = Button(description="converting Excel-file to SQLite-file", layout=b1.layout, style=style)
  b4 = Button(description="reset", layout=b1.layout, style=style)
  def on_b1(b):
    WGS.runGui(opt=1)
  def on_b2(b):
    WGS.runGui(opt=2)
  def on_b3(b):
    WGS.xls2sqlite()
  def on_b4(b):
    applet()
    
  b1.on_click(on_b1)
  b2.on_click(on_b2)
  b3.on_click(on_b3)
  b4.on_click(on_b4)

  WGS.xls_uploader.layout=b1.layout
  WGS.xls_uploader.style=style
  
  H=HBox([b1, b2, WGS.xls_uploader,b3,b4])
  display(H)
  
applet()