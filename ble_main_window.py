import wx

from ble_widgets.ble_menubar import *
from ble_widgets.ble_statusbar import *
from ble_widgets.ble_toolbar import *
from ble_widgets.ble_mainPageWidgets.ble_mainPage import *
from ble_widgets.ble_deviceInfoPageWidgets.ble_deviceinfoPage import *
from ble_widgets.ble_messagePageWidgets.ble_messagePage import *



	
		
class MainWindow(wx.Frame):
	def __init__(self, mainArgObj):
		self._mainArgObj = mainArgObj
		super(MainWindow, self).__init__(None, -1)
		self.InitUI()
		self.Centre() 
		self.Show(True)  
	
	def InitUI(self):
		#1. menubar options
		#1.1 Create menubar
		minWinSize = (1100, 700)
		menuBarObj = Ble_MenuBar(self._mainArgObj)	
		self.SetMenuBar(menuBarObj._menuBar)
		#1.2 bind function
		
		self.Bind(wx.EVT_MENU, self.OnExit, menuBarObj._file_exitItem)
		
		#2. toolbar
		
		self.toolBarObj = Ble_ToolBar(self, "res", self._mainArgObj)
		self.ToolBar = self.toolBarObj._toolBar
		self._mainArgObj._toolBarObj = self.toolBarObj
		
		#self.toolBarObj._toolBar.Realize()

		#3. content
		nb = wx.Notebook(self)
		mainPageObj = Ble_CommandMainPage(nb, minWinSize, self._mainArgObj)
		messagePageObj = Ble_MessagePage(nb, minWinSize, self._mainArgObj)
		deviceInfoPageObj = Ble_DeviceInfoPage(nb, minWinSize, self._mainArgObj)
		
		self._mainArgObj._mainPageObj = mainPageObj
		self._mainArgObj._messagePageObj = messagePageObj
		self._mainArgObj._deviceInfoPageObj = deviceInfoPageObj
		
		nb.AddPage(mainPageObj, "Bluetooth HCI Commands")
		nb.AddPage(messagePageObj, "Message Log")
		nb.AddPage(deviceInfoPageObj, "Local Device Info")
		
		#4. Bind 
		#self.Bind(toolBarObj.)
		#self.toolBarObj.getObject().Bind(wx.EVT_TEXT, self.bindMenubar2cmdTree)
		self.Bind(wx.EVT_CLOSE, self.OnExit)
		#Ble_DeviceInfoPage
		#5. status 
		
		statusBarObj = Ble_StatusBar(self)
		statusBarObj.setPort("NO PORT")
		statusBarObj.setBdaddr("00 00 00 00 00 00")
		#self.SetStatusBar(statusBarObj._statusBar)
		self._mainArgObj._statusBarObj = statusBarObj
		
		self.SetSize(minWinSize)
		self.SetMinSize(minWinSize)
		self.SetMaxSize((minWinSize[0], minWinSize[1]+100))
		
		self.icon = wx.Icon("res\\verisilicon.ico", wx.BITMAP_TYPE_ICO)
		self.SetIcon(self.icon) 
		self.SetTitle("Verisilicon ble command tool")
		
	def onCallMainPage(self):
		print ""
	
	def OnExit(self, evt):
		print "exit"
		self.globalClose()
		#self.Close()
		
		sys.exit()
	def globalClose(self):
		print "global_close"
		if self._mainArgObj._uartRecvThreadObj.isAlive() == True or self._mainArgObj._parserThreadObj.isAlive() == True:
			self._mainArgObj._threadCtlObj._needQuit = True
			
		self._mainArgObj._uartApiObj.uartClose()
		
