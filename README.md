dp832-gui
=========

Rigol DP832 GUI. This is a simple graphing GUI for the Rigol DP832 connected via VISA (tested over USB although other IO connections should work).

To use this you'll need to install:

 * Ultra Sigma from Rigol [OPTIONAL: Can also just copy/paste the address from the DP832 display]
 * Python 2.7 with PySide, suggested to just install WinPython (see http://winpython.sourceforge.net/)
 * PyQtGraph, see http://www.pyqtgraph.org/
 * pyvisa, use easy_install
 
Once your system is running, just run dpgui.py via your installed Python. Supply the address string (open Ultra Sigma, make sure it finds your Power Supply, and copy-paste address string from that, OR just look in the 'utilities' menu). Will look something like USB0::0x1AB1::0x0E11::DP8XXXXXXXX::INSTR

If the address copied from the DP832 display doesn't work, install Ultra Sigma to confirm it is detected there. If Ultra Sigma didn't see the power supply something else is up...

Bugs
=======

 * Can only set number of windows before connecting
 * Doesn't validate instrument state before doing anything, so crashes are likely. Check python output for reasons.
 
Notes
========

While connected remotely you CANNOT control the power supply from the front panel. You can turn outputs on/off seems to be about it. So setup your required voltages etc first then hit connect. If you want to change anything just disconnect, modify settings on the panel, and connect again. You don't need to restart the dp832gui application.
