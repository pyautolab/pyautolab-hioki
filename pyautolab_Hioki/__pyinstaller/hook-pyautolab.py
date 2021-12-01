from pathlib import Path

import pyautolab_Hioki

hioki_path = Path(pyautolab_Hioki.__file__).parent

datas = []
datas += [(str(hioki_path), "pyautolab_Hioki")]
