import sys,serial, wx, time

import serial.tools.list_ports
import includes.ble_common_class as comm_cls 

def get_time_stamp():
    ct = time.time()
    local_time = time.localtime(ct)
    data_head = time.strftime("%H:%M:%S", local_time)
    data_secs = (ct - int(ct)) * 1000
    time_stamp = "%s.%03d" % (data_head, data_secs)
    return time_stamp

SAVE_TOOL_BAR_ID=-101
INIT_TOOL_BAR_ID=-102
SEARCH_TOOL_BAR_ID=-103

class Ble_serachCmdComboBox(wx.Frame) :
	def __init__(self, parent, choices, style, mainArgObj):
		self.currentText = ''
		#wx.ComboBox.__init__(self, parent, wx.ID_ANY, value, style=style|wx.CB_DROPDOWN | wx.CB_SORT, choices=choices, **par)
		#wx.Frame.__init__(self, parent, id=-1, title = "no", wx.DefaultPosition, wx.Size(850, 850))
		self._mainArgObj = mainArgObj
		id = -1
		title="no"
		wx.Frame.__init__(self, parent, id, title, 
                          wx.DefaultPosition, wx.Size(850, 850))
		self._comboxObj = wx.ComboBox(parent, style=style|wx.CB_DROPDOWN | wx.CB_SORT, choices=choices)
		self.choices = choices
		self._comboxObj.Bind(wx.EVT_TEXT, self.EvtText)
		#self._comboxObj.Bind(wx.EVT_CHAR, self.EvtChar)
		#self._comboxObj.Bind(wx.EVT_COMBOBOX, self.EvtCombobox) 
		self.ignoreEvtText = False
	def getObject(self):
		return self._comboxObj
	"""
	def EvtCombobox(self, event):
		print "EvtCombobox"
		self.ignoreEvtText = True
		event.Skip()

	def EvtChar(self, event):
		print "EvtChar"
		if event.GetKeyCode() == 8:
			self.ignoreEvtText = True
		event.Skip()
	"""
	def EvtText(self, event):
		currentText = event.GetString()
		if currentText=='':
			self._comboxObj.SetItems(self.choices)
			self._comboxObj.Dismiss()
		if self.ignoreEvtText:
			self.ignoreEvtText = False
			#print "falg1"
			return

		currentText = event.GetString()
		found = False
		choiceTemp = [] #list all string could been matched
		foundStr = ''
		for choice in self.choices :
			if choice.startswith(currentText):
				self.ignoreEvtText = True
				found = True
				foundStr = choice
				choiceTemp.append(choice)
				#break
		#print "len:", len(choiceTemp)
		#if len(choiceTemp) == 1:
		#	print "foundStr:", foundStr
		if found:
			#print "currentText:", currentText
			#print choiceTemp[0]
			self._comboxObj.SetItems(choiceTemp)
			self._comboxObj.Popup()
			self._comboxObj.SetValue(currentText)
			self._comboxObj.SetInsertionPoint(len(currentText))
			self.ignoreEvtText = False
			
		if not found:
			self._comboxObj.Dismiss()
			self._comboxObj.SetInsertionPoint(len(currentText))
			event.Skip()

		if found:
			if self._mainArgObj._cmdTreeObj != None:
				self._mainArgObj._cmdTreeObj.setSpeifiedFocusItem(currentText)
			self.currentText = currentText
			self._mainArgObj._mainPageObj._changeInputPanel(currentText)
	def getCurrentText(self):
		return self.currentText


class Ble_usb(wx.Panel):
		def __init__(self,parent):
			#self._cmdName = argListObj._cmdName
			self._panel = parent
			#panel_info = wx.Panel()
			self.info_text = wx.StaticText(self._panel, wx.ID_ANY, "    USB Port could not be supported", (250, 150), style = wx.ALIGN_LEFT)
			vbox = wx.BoxSizer(wx.HORIZONTAL)
			vbox.Add(self.info_text, 1)
			self._panel.SetSizerAndFit(vbox)
			
			
class Ble_socket(wx.Panel):
		def __init__(self,parent):
			#self._cmdName = argListObj._cmdName
			self._panel = parent
			self.info_text = wx.StaticText(self._panel, wx.ID_ANY, "    Socket could not be supported", (250, 150), style = wx.ALIGN_LEFT)
			vbox = wx.BoxSizer(wx.HORIZONTAL)
			vbox.Add(self.info_text, 1)
			self._panel.SetSizerAndFit(vbox)
			

class UART_CONFIG_CLASS(object):
	def __init__(self):
		self._port = ''  #False
		self._baudrate = 115200
		self._parity = 'N'
		self._flowctl = 0
		self._stopbits = 1
		self._timeout = 2 #fixed
		


		
	
class Ble_uart(wx.Panel):
	
	def connect(self):
		#print "connect"
		return self.initUart()
	def getUartPort(self):
		return self._uartParaObj._port
		
	def initUart(self):
		"""
		try:
			self._mainArgObj._uartApiObj = serial.Serial()
		except:
			return False
		"""	
		self.getUartConfig()
		self._mainArgObj._uartApiObj.uartConnect(self._uartParaObj)
		"""
		self._mainArgObj._uartApiObj.port = self._uartParaObj._port
		self._mainArgObj._uartApiObj.baudrate = self._uartParaObj._baudrate
		self._mainArgObj._uartApiObj.timeout = self._uartParaObj._timeout
		self._mainArgObj._uartApiObj.stopbits = self._uartParaObj._stopbits
		self._mainArgObj._uartApiObj.parity = self._uartParaObj._parity
		"""
		status = self._mainArgObj._uartApiObj.uartOk()
		self._mainArgObj._portIsConnect = status
		return status
		"""
		#self._mainArgObj._uartApiObj.xonxoff = 0
		try:
			self._mainArgObj._uartApiObj.open()
			print "connect ok"
			print "status:",self._mainArgObj._uartApiObj.isOpen()
			return True
			
		except:
			#print "Error to open uart"
			dlg = wx.MessageDialog(None, "Error to open uart", "Error info", wx.YES_NO | wx.ICON_QUESTION)
			if dlg.ShowModal() == wx.ID_YES:
				self.Close(True)
			dlg.Destroy()
			return False
		"""
	def closeUart(self):
		self._mainArgObj._uartApiObj.close()
			
	def getUartConfig(self):
		#index  = 
		
		self._uartParaObj._port = self.port_choice.GetString(self.port_choice.GetSelection())
		self._uartParaObj._baudrate = int(self.baud_choice.GetString(self.baud_choice.GetSelection()))
		if 'NONE' == self.parity_choice.GetString(self.parity_choice.GetSelection()):
			self._uartParaObj._parity = 'N'
			
		
		if self.flowctl_choice.GetString(self.flowctl_choice.GetSelection()) == 'DISABLE':
			self._uartParaObj._flowctl = 0
		else:
			self._uartParaObj._flowctl = 1
		
		self._uartParaObj._stopbits = int(self.stopbit_choice.GetString(self.stopbit_choice.GetSelection()))
		
		
		
	def __init__(self,parent, mainArgObj):
		#self._cmdName = argListObj._cmdName
		super(Ble_uart, self).__init__(parent, -1)
		self._mainArgObj = mainArgObj
		self._uartParaObj = comm_cls.UART_CONFIG_CLASS()
		self._panel = parent
		self._uartDevList = []
		self._baudList = ['115200', '128000', '230400']
		self._parityList = ['NONE', 'EVEN', 'ODD']
		self._flowCtlList = ['DISABLE', 'ENABLE'] 
		self._stopbitList = ['1', '1.5', '2']
		
		
		#1. get all com port on OS
		port_list = list(serial.tools.list_ports.comports())
		for i in range(len(port_list)):
			self._uartDevList.append(port_list[i].device)
		
		
		
		
		#2. create item
		self.port_choice = wx.Choice(self._panel, size=(150, 20), choices = self._uartDevList)
		self.baud_choice = wx.Choice(self._panel, size=(150, 20), choices = self._baudList)
		self.parity_choice = wx.Choice(self._panel, size = (150, 20), choices = self._parityList)
		self.flowctl_choice = wx.Choice(self._panel, size = (150, 20), choices = self._flowCtlList)
		self.stopbit_choice = wx.Choice(self._panel, size = (150, 20), choices = self._stopbitList)
		
		self.port_choice.SetSelection(0)
		self.baud_choice.SetSelection(0)
		self.parity_choice.SetSelection(0)
		self.flowctl_choice.SetSelection(0)
		self.stopbit_choice.SetSelection(0)
		
		
		self.port_text = wx.StaticText(self._panel, wx.ID_ANY, "Port", (100, 20), style = wx.ALIGN_RIGHT)
		self.baud_text = wx.StaticText(self._panel, wx.ID_ANY, "Baud Rate", (100, 20), style = wx.ALIGN_RIGHT)
		self.parity_text = wx.StaticText(self._panel, wx.ID_ANY, "Parity", (100, 20), style = wx.ALIGN_RIGHT)
		self.flowctl_text = wx.StaticText(self._panel, wx.ID_ANY, "HW Flow Control", (100, 20), style = wx.ALIGN_RIGHT)
		self.stopbit_text = wx.StaticText(self._panel, wx.ID_ANY, "Stopbits", (100, 20), style = wx.ALIGN_RIGHT)
		
		#3. layout
		gbs = wx.GridBagSizer(5, 5)
		gbs.SetVGap(20)
		gbs.Add(self.port_text, (0, 1), (1, 1), wx.ALIGN_RIGHT|wx.EXPAND)
		gbs.Add(self.port_choice, (0, 3), (1, 1), wx.ALIGN_LEFT|wx.EXPAND)
		
		gbs.Add(self.baud_text, (1, 1), (1, 1), wx.ALIGN_RIGHT|wx.EXPAND)
		gbs.Add(self.baud_choice, (1, 3), (1, 1), wx.ALIGN_LEFT|wx.EXPAND)
		
		gbs.Add(self.parity_text, (2, 1), (1, 1), wx.ALIGN_RIGHT|wx.EXPAND)
		gbs.Add(self.parity_choice, (2, 3), (1, 1), wx.ALIGN_LEFT|wx.EXPAND)
		
		gbs.Add(self.flowctl_text, (3, 1), (1, 1), wx.ALIGN_RIGHT|wx.EXPAND)
		gbs.Add(self.flowctl_choice, (3, 3), (1, 1), wx.ALIGN_LEFT|wx.EXPAND)
		
		gbs.Add(self.stopbit_text, (4, 1), (1, 1), wx.ALIGN_RIGHT|wx.EXPAND)
		gbs.Add(self.stopbit_choice, (4, 3), (1, 1), wx.ALIGN_LEFT|wx.EXPAND)
		
		
		
		"""
		fgs.AddMany([
		(self.port_text, 0, wx.ALIGN_RIGHT|wx.EXPAND), (self.port_choice, 0, wx.ALIGN_LEFT|wx.EXPAND),\
		(self.baud_text, 0, wx.ALIGN_RIGHT|wx.EXPAND), (self.baud_choice, 0, wx.ALIGN_LEFT|wx.EXPAND),\
		(self.parity_text, 0, wx.ALIGN_RIGHT|wx.EXPAND), (self.parity_choice, 0, wx.ALIGN_LEFT|wx.EXPAND),\
		(self.flowctl_text, 0, wx.ALIGN_RIGHT|wx.EXPAND), (self.flowctl_choice, 0, wx.ALIGN_LEFT|wx.EXPAND),\
		(self.stopbit_text, 0, wx.ALIGN_RIGHT|wx.EXPAND), (self.stopbit_choice, 0, wx.ALIGN_LEFT|wx.EXPAND)\
					])
		"""
		
		self._panel.SetSizerAndFit(gbs)

class Ble_portlInitDialog(wx.Dialog): 
	def __init__(self, parent, title, mainArgObj): 
		super(Ble_portlInitDialog, self).__init__(parent, title = title, size = (300, 400)) 
		#mainPanel = wx.Panel(self)
		self._mainArgObj = mainArgObj
		panel = wx.Panel(self, -1)
		self.panel_uart = wx.Panel(panel)
		self.panel_usb = wx.Panel(panel)
		self.panel_socket = wx.Panel(panel)
		self._curDisplayPanel = None
		
		
		#1. select item
		self.uart_rb = wx.RadioButton(panel, -1, 'UART')
		self.usb_rb = wx.RadioButton(panel, -1, 'USB')
		self.socket_rb = wx.RadioButton(panel, -1, 'SOCKET')
		
		#self.uart_rb.SetForegroundColour("#0a74f7")
		
		self.Bind(wx.EVT_RADIOBUTTON, self.modeChange, self.uart_rb)
		self.Bind(wx.EVT_RADIOBUTTON, self.modeChange, self.usb_rb)
		self.Bind(wx.EVT_RADIOBUTTON, self.modeChange, self.socket_rb)
		
		#2. child panel
		self.uartPanelObj = Ble_uart(self.panel_uart, mainArgObj)
		self.usbPanelObj = Ble_usb(self.panel_usb)
		self.socketPanelObj = Ble_socket(self.panel_socket)
		self.content_vbox = wx.BoxSizer(wx.VERTICAL)
		self.content_vbox.Add(self.panel_uart, 1)
		self.content_vbox.Add(self.panel_usb, 1)
		self.content_vbox.Add(self.panel_socket, 1)
		self.panel_uart.Hide()
		self.panel_usb.Hide()
		self.panel_socket.Hide()
		self.panel_uart.Show()
		self.uart_rb.SetValue(True)
		self._curDisplayPanel = self.panel_uart
		
		
		#3. button
		self.ok_bt = wx.Button(panel, -1, 'Ok')
		self.cancel_bt = wx.Button(panel, -1, 'Cancel')
		self.Bind(wx.EVT_BUTTON, self.onClick, self.ok_bt)
		self.Bind(wx.EVT_BUTTON, self.onClick, self.cancel_bt)
		
		
		#4. layout
		
		up_hbox = wx.BoxSizer(wx.HORIZONTAL)	#for select item
		down_hbox = wx.BoxSizer(wx.HORIZONTAL)	#for  ok cancel button
		
		main_vbox = wx.BoxSizer(wx.VERTICAL)	#for main layout
		up_hbox.AddStretchSpacer(1)
		up_hbox.Add(self.usb_rb, 2)
		up_hbox.Add(self.uart_rb, 2)
		up_hbox.Add(self.socket_rb, 2)
		up_hbox.AddStretchSpacer(1)
		
		down_hbox.AddStretchSpacer(1)
		down_hbox.Add(self.ok_bt, 2)
		down_hbox.AddStretchSpacer(2)
		down_hbox.Add(self.cancel_bt, 2)
		down_hbox.AddStretchSpacer(1)
		
		main_vbox.AddStretchSpacer(1)
		main_vbox.Add(up_hbox, 2)
		main_vbox.Add(self.content_vbox, 4)
		main_vbox.AddStretchSpacer(1)
		main_vbox.Add(down_hbox, 2)
		
		panel.SetSizerAndFit(main_vbox)
	
	
	def sendCmdByDefaultValue(self, name):
		inputCnt = len(self._mainArgObj._cmdInputListObj)
		sendDataList = []
		for i in range(inputCnt):
			if name == self._mainArgObj._cmdInputListObj[i]._getCmdName():
				sendDataList = self._mainArgObj._cmdInputListObj[i]._getValue()
				break
				
		tempDataObj = comm_cls.HCI_QUEUE_DATA_LIST_CLASS()
		tempDataObj._time = get_time_stamp()
		tempDataObj._dataList = sendDataList
		self._mainArgObj._data_2_parser_queue_lock.acquire()
		self._mainArgObj._recv_2_parser_queue.put(tempDataObj)
		self._mainArgObj._data_2_parser_queue_lock.release()
		
		
		if self._mainArgObj._uartApiObj.uartOk():
			ret = self._mainArgObj._uartApiObj.uartSend(sendDataList)
			if ret == False:
				dlg = wx.MessageDialog(None, "Failed to send data, please to check port.", \
			                       'ERROR', wx.YES_NO | wx.ICON_ERROR)
				retCode = dlg.ShowModal()
				if (retCode == wx.ID_YES):
					needInit = True
				dlg.Destroy()
	
	def onClick(self, evt):
		evtObj = evt.GetEventObject()
		label = evtObj.GetLabel() 
		if label == "Ok":
			if self._curDisplayPanel == self.panel_uart:
				status = self.uartPanelObj.connect()
				if status == True:
					self._mainArgObj._statusBarObj.setConnectStatus(1)
					self._mainArgObj._statusBarObj.setPort(self.uartPanelObj.getUartPort())
					#print "send cmd...."
					self.sendCmdByDefaultValue('hci_read_bd_addr')
					self.sendCmdByDefaultValue('hci_read_local_version_information')
					self.sendCmdByDefaultValue('hci_le_read_buffer_size')
					
					self.Close()
					
				else:
					self._mainArgObj._statusBarObj.setConnectStatus(0)
					self._mainArgObj._statusBarObj.setPort(self.uartPanelObj.getUartPort())
					
			
		elif label == "Cancel":
			self.Close()
		
	def modeChange(self, evt):
		#print "nothing"
		evtObj = evt.GetEventObject()
		label = evtObj.GetLabel() 
		self._curDisplayPanel.Hide()
			
		if label == "UART":
			self.panel_uart.Show()
			self._curDisplayPanel = self.panel_uart 
		elif label == "USB":
			self.panel_usb.Show()
			self._curDisplayPanel = self.panel_usb
		elif label == "SOCKET":
			self.panel_socket.Show()
			self._curDisplayPanel = self.panel_socket
			

		self.content_vbox.Layout()
		"""
		self.uart_cb =  wx.CheckBox(panel, label = 'UART',pos = (10,10)) 
		self.usb_cb =  wx.CheckBox(panel, label = 'USB',pos = (10,10)) 
		self.sock_cb =  wx.CheckBox(panel, label = 'SOCKET',pos = (10,10))
		
		up_hbox = wx.BoxSizer(wx.HORIZONTAL)
		up_hbox.Add(self.uart_cb, 1)
		up_hbox.Add(self.usb_cb, 1)
		up_hbox.Add(self.sock_cb, 1)
		
		panel.SetSizerAndFit(up_hbox)
		"""
		#self.btn = wx.Button(panel, wx.ID_OK, label = "ok", size = (50,20), pos = (75,50))
			
class Ble_ToolBar(wx.Frame):
	
		
	def __init__(self, parent, resFolder, mainArgObj):
		super(Ble_ToolBar, self).__init__(None, -1)
		self._mainArgObj = mainArgObj
		self._parent = parent
		self._toolBar = wx.ToolBar(self._parent, style=wx.TB_DEFAULT_STYLE)
		self._parent.ToolBar = self._toolBar
		
		#1. left items
		self._saveLogToolBar = self._toolBar.AddTool(SAVE_TOOL_BAR_ID, "Save", wx.Bitmap(resFolder + "\\save.png"), "Save Logs")
		self._toolBar.AddSeparator()
		self._initPortToolBar = self._toolBar.AddTool(INIT_TOOL_BAR_ID, "Init", wx.Bitmap(resFolder + "\\init.png"), "Port Initialization")
		
		#right item
		#choices = ['hci_read_bd_addr', 'hci_le_read_white_list_size', 'hci_flush', 'hci_read_local_name', 'hci_reset', #'hci_le_read_buffer_size', 'hci_le_set_scan_enable']
		cmdChoices = []
		cmdsList = self._mainArgObj._loadSpecObj._getCmdList()
		for item in cmdsList:
			cmdChoices.append(item._name)
			
		self._serachCmdObj = Ble_serachCmdComboBox(self._toolBar, cmdChoices, wx.CB_DROPDOWN, mainArgObj)
		self._serachButton = wx.Button(self._toolBar, -1, "SEARCH")
		self._serachText = wx.StaticText(self._toolBar, wx.ID_ANY, "Search a Command", (100, 30))
		
		
		self._toolBar.AddStretchableSpace()
		self._serachCombox = self._toolBar.AddControl(self._serachText, label="Search")
		self._serachCombox = self._toolBar.AddControl(self._serachCmdObj.getObject(), label="Search")
		self._serachButton = self._toolBar.AddControl(self._serachButton, label="Search")
		
		#bind
		self._toolBar.Bind(wx.EVT_TOOL, self.OnInitPort)
		
		
		
		
		self._toolBar.Realize()
		
	def openInitPort(self):
		if self._mainArgObj._portIsConnect == True:
			#print "need to close...."
			dlg = wx.MessageDialog(None, "Do you want to close current port?", \
			                       'Port init warnning', wx.YES_NO | wx.ICON_QUESTION)
			retCode = dlg.ShowModal()
			if (retCode == wx.ID_YES):
				#print "yes"
				self._mainArgObj._uartApiObj.uartClose()
				self._mainArgObj._statusBarObj.setConnectStatus(0)
				curDlg = Ble_portlInitDialog(None, "Port Initialization", self._mainArgObj)				
				if curDlg.ShowModal() == wx.ID_YES:
					self.Close(True)
				curDlg.Destroy()
			#else:
			#	print "no"
				#close()
			dlg.Destroy()	
		else:
			dlg = Ble_portlInitDialog(None, "Port Initialization", self._mainArgObj)
				
			if dlg.ShowModal() == wx.ID_YES:
				self.Close(True)
			dlg.Destroy()
				
	def OnInitPort(self, evt):
		id = evt.GetId()
		object = evt.GetEventObject()
		
		if INIT_TOOL_BAR_ID == id:
			#print "init port ID:", id
			self.openInitPort()
			#"""
			"""
			dlg = Ble_portlInitDialog(None, "Port Initialization", self._mainArgObj)
			
			if dlg.ShowModal() == wx.ID_YES:
				self.Close(True)
			dlg.Destroy()
			"""
		elif SAVE_TOOL_BAR_ID == id:
			print "save log ID:", id
	
	def _getObject(self):
		return self._toolBar
	def _getComboText(self):
		return self._serachCmdObj.getCurrentText()
		
	def OnSave(self, evt):
		#print "save...."
		print "GetID:", evt.GetId()
		
	def _setStatusContent(self, index, statusStr):
		if index < 0 or index > 2:
			return False
		self._statusBar.SetStatusText(statusStr, index)
		return True