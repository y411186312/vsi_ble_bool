import sys,wx,os
from ble_widgets.ble_aclTransfer.ble_aclTransfer import *

VERSION='0.1.1'
COPYRIGHT='2018-2020'

class Ble_aboutDialogClass(wx.Dialog): 
	def __init__(self, parent, title): 
		super(Ble_aboutDialogClass, self).__init__(parent, title = title, size = (300, 400)) 
		self.panel = wx.Panel(self, -1)
		
		
		img_big = wx.Image("res\\about.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
		staticBmp = wx.StaticBitmap(self.panel, -1, img_big, pos=(200, 20), size=(200, 120), style = wx.ALIGN_CENTER)
		staticBmp.SetBackgroundColour("#a8a8a8")
		
		staticText_company = wx.StaticText(self.panel, wx.ID_ANY, "BlueTooth tool\nVersion: %s\n" % VERSION, style = wx.ALIGN_LEFT)
		staticText_copyright = wx.StaticText(self.panel, wx.ID_ANY, "Copyright (C) %s\nVerisilicon Ltd.\n" % COPYRIGHT, style = wx.ALIGN_LEFT)
		staticText_help = wx.StaticText(self.panel, wx.ID_ANY, "Please contact legendforworking@gmail.com \nfor more information.\n", style = wx.ALIGN_LEFT)
		
		
		self.ok_bt = wx.Button(self.panel, -1, 'Ok')
		self.Bind(wx.EVT_BUTTON, self.onClick, self.ok_bt)
		
		up_hbox = wx.BoxSizer(wx.HORIZONTAL)	#for select item
		content_vbox = wx.BoxSizer(wx.VERTICAL)	#for main layout
		middle_hbox = wx.BoxSizer(wx.HORIZONTAL)
		down_hbox = wx.BoxSizer(wx.HORIZONTAL)
		
		main_vbox = wx.BoxSizer(wx.VERTICAL)	#for main layout
		content_vbox.Add(staticText_company)
		content_vbox.AddStretchSpacer(1)
		content_vbox.Add(staticText_copyright)
		content_vbox.AddStretchSpacer(1)
		content_vbox.Add(staticText_help)
		
		
		up_hbox.AddStretchSpacer(1)
		up_hbox.Add(staticBmp, 2)
		up_hbox.AddStretchSpacer(1)
		
		middle_hbox.AddStretchSpacer(1)
		middle_hbox.Add(content_vbox, 2)
		middle_hbox.AddStretchSpacer(1)
		
		down_hbox.AddStretchSpacer(3)
		down_hbox.Add(self.ok_bt, 1)
		
		main_vbox.Add(up_hbox, 2)
		#main_vbox.AddStretchSpacer(1)
		main_vbox.Add(middle_hbox, 2)
		main_vbox.Add(down_hbox, 2)
		self.panel.SetSizerAndFit(main_vbox)
		
	
	def onClick(self, evt):
		
		self.Close()
		
	

HELP_MANUAL_ID=130
HELP_ABOUT_ID=131

ACTION_CLEAR_LOG_ID=110
ACTION_CLEAR_MESSAGE_LOG_ID=111
ACTION_PORT_INIT_ID=112

class Ble_MenuBar(wx.Frame):
	def __init__(self, winSize, mainArgObj):
		self._windowSize = winSize
		self._mainArgObj = mainArgObj
		self._menuBar = wx.MenuBar()
		self._fileMenu = wx.Menu()
		self._actionsMenu = wx.Menu()
		self._toolsMenu = wx.Menu()
		self._helpMenu = wx.Menu()
		
		#Fill File menu
		self._file_saveLogsItem = self._fileMenu.Append(100, "Save Logs", "Save Logs")
		self._file_loadLogsItem = self._fileMenu.Append(101, "Load Logs", "Load Logs")
		self._file_exitItem = self._fileMenu.Append(102, "Exit", "Quit Applications")
		
		#Fill Actions menu
		self._actions_clearLogsItem = self._actionsMenu.Append(ACTION_CLEAR_LOG_ID, "Clear Logs", "Clear Logs")
		self._actions_clearMessageLogItem = self._actionsMenu.Append(ACTION_CLEAR_MESSAGE_LOG_ID, "Clear Message Log", "Clear Message Log")
		self._actions_portInitItem = self._actionsMenu.Append(ACTION_PORT_INIT_ID, "Port Initialization", "Port Initialization")
		
		#Fill Tools menu
		self._tools_txItem = self._toolsMenu.Append(120, "Tx Data Transfer", "Tx Data Transfer")
		self._tools_rxItem = self._toolsMenu.Append(121, "Rx Data Transfer", "Rx Data Transfer")
		
		#File Help menu
		self._help_userManualItem = self._helpMenu.Append(HELP_MANUAL_ID, "User Manual", "User Manual")
		self._help_aboutItem = self._helpMenu.Append(HELP_ABOUT_ID, "About", "About")
		
		self._menuBar.Append(self._fileMenu,"&File")
		self._menuBar.Append(self._actionsMenu,"&Actions")
		self._menuBar.Append(self._toolsMenu,"&Tools")
		self._menuBar.Append(self._helpMenu,"&Help")
		
		self._helpMenu.Bind(wx.EVT_MENU, self.OnAboutDisplay)
		self._toolsMenu.Bind(wx.EVT_MENU, self.OnAclTrasfer)
		self._actionsMenu.Bind(wx.EVT_MENU, self.OnAboutDisplay)
		
	def OnQuit(self,e):
	
		print "exit"
		sys.exit()
		
	def OnAclTrasfer(self, evt):
	
		id = evt.GetId()
		#print "id:",id
		isSend = True
		if id == 120:
			#print "Tx"
			isSend = True
		elif id == 121:
			isSend = False
			print "Rx"
		else:
			return
		#print "isSend:",isSend
		aclTransferObj = None
		if isSend == True:
			aclTransferObj = Ble_aclTransferClass(None, "Send Data", self._windowSize, self._mainArgObj)
			aclTransferObj.setTxMode()
		else:
			aclTransferObj = Ble_aclTransferClass(None, "Receive Data", self._windowSize, self._mainArgObj)
			aclTransferObj.setRxMode()
		self._mainArgObj._aclDataTransferObj = aclTransferObj
		self._mainArgObj._aclGuiHasBeenQuited = False
		#aclTransferObj.Show()
		if aclTransferObj.ShowModal() == wx.ID_YES:
			self.Close(True)
		aclTransferObj.Destroy()
		self._mainArgObj._aclGuiHasBeenQuited =True
	def OnAboutDisplay(self, evt):
		evtObj = evt.GetEventObject()
		id = evt.GetId()
		print "id:",id
		if id == HELP_ABOUT_ID:
			dlg = Ble_aboutDialogClass(None, "About tool")
			
			if dlg.ShowModal() == wx.ID_YES:
				self.Close(True)
			dlg.Destroy()
		elif id == HELP_MANUAL_ID:
			print "open read me"
			os.system("cmd/c start res\\readme.pdf")
		
		elif id == ACTION_CLEAR_MESSAGE_LOG_ID:
			self._mainArgObj._messagePageObj.clearAll()
		
		elif id == ACTION_CLEAR_LOG_ID:
			self._mainArgObj._displayStatusObj.clearAll()
		
		elif id == ACTION_PORT_INIT_ID:
			self._mainArgObj._toolBarObj.openInitPort()