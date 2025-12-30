# PyInstaller runtime hook for tkinterdnd2
# This helps tkinterdnd2 find its TkDND libraries when bundled in a single exe

import os
import sys

# When running from a PyInstaller bundle, set the TkDND library path
if hasattr(sys, '_MEIPASS'):
    # The tkinterdnd2 package is extracted to _MEIPASS/tkinterdnd2
    tkdnd_path = os.path.join(sys._MEIPASS, 'tkinterdnd2')
    if os.path.exists(tkdnd_path):
        # Set environment variable that tkinterdnd2 uses to find TkDND
        os.environ['TKDND_LIBRARY'] = tkdnd_path
