
#
# Very Crappy DP832 GUI by Colin O'Flynn
# Crashes under most circumstances, if you do things in the wrong order, etc
#


import sys

from PySide.QtCore import *
from PySide.QtGui import *

try:
	import pyqtgraph as pg
	import pyqtgraph.parametertree.parameterTypes as pTypes
	from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType
except ImportError:
	print "Install pyqtgraph from http://www.pyqtgraph.org"
	raise

from dp832 import DP832

class GraphWidget(QWidget):
	"""
	This GraphWidget holds a pyqtgraph PlotWidget, and adds a toolbar for the user to control it.
	"""		  
	
	def __init__(self):
		pg.setConfigOption('background', 'w')
		pg.setConfigOption('foreground', 'k')

		QWidget.__init__(self)
		layout = QVBoxLayout()

		self.pw = pg.PlotWidget(name="Power Trace View")
		self.pw.setLabel('top', 'Power Trace View')
		self.pw.setLabel('bottom', 'Samples')
		self.pw.setLabel('left', 'Data')
		vb = self.pw.getPlotItem().getViewBox()
		vb.setMouseMode(vb.RectMode)

		layout.addWidget(self.pw)
		
		self.setLayout(layout)

		self.setDefaults()

	def setDefaults(self):
		self.defaultYRange = None

	def VBStateChanged(self, obj):
		"""Called when ViewBox state changes, used to sync X/Y AutoScale buttons"""
		arStatus = self.pw.getPlotItem().getViewBox().autoRangeEnabled()
		
		#X Axis
		if arStatus[0]:
			self.XLockedAction.setChecked(False)
		else:
			self.XLockedAction.setChecked(True)			   
			
		#Y Axis
		if arStatus[1]:
			self.YLockedAction.setChecked(False)
		else:
			self.YLockedAction.setChecked(True) 
			
	def VBXRangeChanged(self, vb, range):
		"""Called when X-Range changed"""
		self.xRangeChanged.emit(range[0], range[1])
		
	def xRange(self):
		"""Returns the X-Range"""
		return self.pw.getPlotItem().getViewBox().viewRange()[0]
			
	def YDefault(self, extraarg=None):
		"""Copy default Y range axis to active view"""
		if self.defaultYRange is not None:
			self.setYRange(self.defaultYRange[0], self.defaultYRange[1])
		  
	def setDefaultYRange(self, lower, upper):
		"""Set default Y-Axis range, for when user clicks default button"""
		self.defaultYRange = [lower, upper]
		  
	def setXRange(self, lower, upper):
		"""Set the X Axis to extend from lower to upper"""
		self.pw.getPlotItem().getViewBox().setXRange(lower, upper)
		
	def setYRange(self, lower, upper):
		"""Set the Y Axis to extend from lower to upper"""
		self.pw.getPlotItem().getViewBox().setYRange(lower, upper)
		  
	def xAutoScale(self, enabled):
		"""Auto-fit X axis to data"""
		vb = self.pw.getPlotItem().getViewBox()
		bounds = vb.childrenBoundingRect(None)
		vb.setXRange(bounds.left(), bounds.right())
		
	def yAutoScale(self, enabled):
		"""Auto-fit Y axis to data"""
		vb = self.pw.getPlotItem().getViewBox()
		bounds = vb.childrenBoundingRect(None)
		vb.setYRange(bounds.top(), bounds.bottom())
		
	def xLocked(self, enabled):
		"""Lock X axis, such it doesn't change with new data"""
		self.pw.getPlotItem().getViewBox().enableAutoRange(pg.ViewBox.XAxis, ~enabled)
		
	def yLocked(self, enabled):
		"""Lock Y axis, such it doesn't change with new data"""
		self.pw.getPlotItem().getViewBox().enableAutoRange(pg.ViewBox.YAxis, ~enabled)
		
	def passTrace(self, trace, startoffset=0, pen='b', clear=True):
		if clear:
			self.pw.clear()			   
		xaxis = range(startoffset, len(trace)+startoffset)
		self.pw.plot(xaxis, trace, pen=pen)

class DP832GUI(QMainWindow):
 
	def __init__(self):
		super(DP832GUI, self).__init__()
		wid = QWidget()
		layout = QVBoxLayout()
		self.drawDone = False

		settings = QSettings()

		constr = settings.value('constring')
		if constr is None: constr = "USB0::0x1AB1::0x0E11::DPXXXXXXXXXXX::INSTR"

		self.constr = QLineEdit(constr)
		self.conpb = QPushButton("Connect")
		self.conpb.clicked.connect(self.tryConnect)

		self.dispb = QPushButton("Disconnect")
		self.dispb.clicked.connect(self.dis)

		self.cbNumDisplays = QSpinBox()
		self.cbNumDisplays.setMinimum(1)
		self.cbNumDisplays.setMaximum(3)		

		layoutcon = QHBoxLayout()
		layoutcon.addWidget(QLabel("Connect String:"))
		layoutcon.addWidget(self.constr)
		layoutcon.addWidget(self.conpb)
		layoutcon.addWidget(self.dispb)
		layoutcon.addWidget(self.cbNumDisplays)
		layout.addLayout(layoutcon)

		self.graphlist = []
		self.graphsettings = []
		self.vdata = []
		self.idata = []
		self.pdata = []


		wid.setLayout(layout)

		self.setCentralWidget(wid)
		self.setWindowTitle("DP832 GUI")

	def addGraphs(self, numgraphs):

		self.numchannels = numgraphs
		layout = self.centralWidget().layout()

		for i in range(0,self.numchannels):
			self.graphsettings.append({"channel":"CH%d"%(i+1), "points":1024})
			self.graphlist.append(GraphWidget())
			self.vdata.append([0]*self.graphsettings[-1]["points"])
			self.idata.append([0]*self.graphsettings[-1]["points"])
			self.pdata.append([0]*self.graphsettings[-1]["points"])
			gb = QGroupBox()
			lgb = QVBoxLayout()
			lgb.addWidget(self.graphlist[-1])

			sbPoints = QSpinBox()
			sbPoints.setMinimum(1)
			sbPoints.setMaximum(500000)
			sbPoints.setValue(self.graphsettings[-1]["points"])
			sbPoints.valueChanged.connect(lambda x: self.setPoints(i, x))

			self.cbChannel = QComboBox()
			self.cbChannel.addItem("CH1")
			self.cbChannel.addItem("CH2")
			self.cbChannel.addItem("CH3")
			self.cbChannel.setCurrentIndex(i)
			self.cbChannel.currentIndexChanged.connect(lambda x :self.setChannel(i, "CH%d"%(x+1)))
			
			lsettings = QHBoxLayout()
			lsettings.addWidget(QLabel("Points"))
			lsettings.addWidget(sbPoints)
			lsettings.addWidget(QLabel("Channel"))
			lsettings.addWidget(self.cbChannel)

			plotV = QPushButton("V")
			plotV.setCheckable(True)
			plotV.setChecked(True)
			plotI = QPushButton("I")
			plotI.setCheckable(True)
			plotP = QPushButton("P")
			plotP.setCheckable(True)

			self.onButton = QPushButton("ON")
			self.onButton.setCheckable(True)
			self.onButton.clicked.connect(self.tryOn)

			self.pauseButton = QPushButton("Pause")
			self.pauseButton.setCheckable(True)
			self.pauseButton.clicked.connect(self.tryPause)

			
			self.graphsettings[-1]["venabled"] = plotV
			self.graphsettings[-1]["ienabled"] = plotI
			self.graphsettings[-1]["penabled"] = plotP

			lsettings.addWidget(plotV)
			lsettings.addWidget(plotI)
			lsettings.addWidget(plotP)
			lsettings.addWidget(self.onButton)
			lsettings.addWidget(self.pauseButton)
			
			lsettings.addStretch()

			lgb.addLayout(lsettings)
			
			gb.setLayout(lgb)

			layout.addWidget(gb)

	def tryOn(self):
		if self.onButton.isChecked() == True:
			self.inst.writing(":OUTP "+self.cbChannel.currentText()+",ON")
		else:
			self.inst.writing(":OUTP "+self.cbChannel.currentText()+",OFF")
			
	def tryPause(self):
		if self.pauseButton.isChecked() == True:
			self.readtimer.stop()
		else:
			self.readtimer.start()
			
	def dis(self):
		self.readtimer.stop()
		self.inst.dis()

	def tryConnect(self):

		if self.drawDone == False:
			self.addGraphs(self.cbNumDisplays.value())
			self.cbNumDisplays.setEnabled(False)
			self.resize(800,600)
			self.drawDone = True
		
		constr = self.constr.text()
		QSettings().setValue('constring', constr)

		self.inst = DP832()
		self.inst.conn(constr)		  

		self.readtimer = QTimer()
		self.readtimer.setInterval(250)
		self.readtimer.timeout.connect(self.updateReadings)
		self.readtimer.start()
		
	def setChannel(self, graphnum, channelstr):
		self.graphsettings[graphnum]["channel"] = channelstr

	def setPoints(self, graphnum, points):
		self.graphsettings[graphnum]["points"] = points

	def updateReadings(self):
		for i, gs in enumerate(self.graphsettings):
			readings = self.inst.readings(gs["channel"])
			self.vdata[i].append(readings["v"])
			self.idata[i].append(readings["i"])
			self.pdata[i].append(readings["p"])

			while len(self.vdata[i]) > gs["points"]:
				self.vdata[i].pop(0)

			while len(self.idata[i]) > gs["points"]:
				self.idata[i].pop(0)

			while len(self.pdata[i]) > gs["points"]:
				self.pdata[i].pop(0)

		self.redrawGraphs()

	def redrawGraphs(self):
		for i,g in enumerate(self.graphlist):

			clear = True
			
			if self.graphsettings[i]["venabled"].isChecked():
				g.passTrace(self.vdata[i], pen='b')
				clear = False

			if self.graphsettings[i]["ienabled"].isChecked():  
				g.passTrace(self.idata[i], pen='r', clear=clear)

			if self.graphsettings[i]["penabled"].isChecked():  
				g.passTrace(self.pdata[i], pen='k', clear=clear)

def makeApplication():
	# Create the Qt Application
	app = QApplication(sys.argv)
	app.setOrganizationName("GhettoFab Productions")
	app.setApplicationName("DP832 GUI")
	return app
  
if __name__ == '__main__':
	app = makeApplication()
	
	# Create and show the form
	window = DP832GUI()
	window.show()
   
	# Run the main Qt loop
	sys.exit(app.exec_())
