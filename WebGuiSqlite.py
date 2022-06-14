import os

from IPython.display import display, HTML, clear_output
#
display(HTML("<style>.container { width:100% !important; }</style>"))
#clear_output()
print(f"Loading from '{__file__}'")

import socket
def gethostport():
  from notebook import notebookapp
  servers = list(notebookapp.list_running_servers())
  return socket.gethostname(), servers[0]['port']
"http://%s:%d" % gethostport()

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
  clear_output()
  return

IPython.get_ipython().register_magic_function(popup, 'line')
IPython.get_ipython().register_magic_function(popup, 'cell')
