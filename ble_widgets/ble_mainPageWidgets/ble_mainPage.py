import sys,wx,time
import wx.lib.scrolledpanel as scrolled 

import includes.ble_common_class as comm_cls 

from ble_widgets.ble_mainPageWidgets.ble_displayCmdStatus import * 
from ble_widgets.ble_mainPageWidgets.ble_advDevScan import * 
from ble_widgets.ble_mainPageWidgets.ble_input import * 
from ble_widgets.ble_mainPageWidgets.ble_cmdTree import * 

def get_time_stamp():
    ct = time.time()
    local_time = time.localtime(ct)
    data_head = time.strftime("%H:%M:%S", local_time)
    data_secs = (ct - int(ct)) * 1000
    time_stamp = "%s.%03d" % (data_head, data_secs)
    return time_stamp
	
class Ble_CommandMainPage(wx.Panel):
		
	def __init__(self,parent, windowSize, mainArgObj):
		wx.Panel.__init__(self, parent)
		self._historyCmdStrList = []
		self._mainArgObj = mainArgObj
		
		#self._mainArgObj._loadSpecObj._loadPrintDefaultValue()
		#mainPanel = self
		self.mainPanel = wx.Panel(self, -1)
		panel_up_left = wx.Panel(self.mainPanel, -1)
		panel_up_right_adv = wx.Panel(self.mainPanel, -1)
		panel_down_cmd_status = wx.Panel(self.mainPanel, -1)
		
		
		#1. left up cmdlist
		self.cmdTreeObj = Ble_cmdTreeListCtrlClass(panel_up_left, -1, "no", windowSize, mainArgObj)
		mainArgObj._cmdTreeObj = self.cmdTreeObj
		#2. adv panel
		listCtrlTitleList = ['BD Address', 'Conn. Handle', 'ADV Type', 'Addr Type', 'RSSI dBm', 'Role', 'extend adv']
		listCtrlWeightList = [3, 1, 1, 1, 1, 1, 1]
		
		self.advDeviceFrame = Ble_AdvDevScanClass(panel_up_right_adv, windowSize, listCtrlTitleList, listCtrlWeightList, "library-system")
		
		self._mainArgObj._advDeviceListObj = self.advDeviceFrame
		"""
		for i in range(len(list)):
			self.advDeviceFrame.addDevice(list[i])
		"""
		#3. input panel
		self.scroll_up_input_list = []
		self.scroll_input_obj_list = []
		self.curDisplayInputIndex = 0
		cmdArgList = self._mainArgObj._loadSpecObj._getCmdList()
		varHbox = wx.BoxSizer(wx.VERTICAL)
		for i in range(len(cmdArgList)):
			minX = windowSize[0] * 2 / 3
			#panel = wx.ScrolledWindow(mainPanel)
			#panel.SetScrollbars(1, 1, 100, 10)
			panel = scrolled.ScrolledPanel(self.mainPanel, -1, size=(780, 350), style = wx.TAB_TRAVERSAL|wx.SUNKEN_BORDER)
			panel.SetName(cmdArgList[i]._name)
			panel.SetVirtualSize((780, 350))
			panel.SetMaxSize((780, 250))
			panel.SetupScrolling(1)
			guiInputObj = Ble_getInputClass(panel, cmdArgList[i])
			self.scroll_input_obj_list.append(guiInputObj)
			panel.Hide()
			varHbox.Add(panel, 1, wx.EXPAND | wx.ALL)
			self.scroll_up_input_list.append(panel)
		self.scroll_up_input_list[self.curDisplayInputIndex].Show()
		
		self._mainArgObj._cmdInputListObj = self.scroll_input_obj_list
		#4. cmd return parameters
		
		self.returnInfoObj = Ble_cmdReturnInfoClass(panel_down_cmd_status, self._mainArgObj, windowSize)
		mainArgObj._displayStatusObj = self.returnInfoObj
		
		#5. bind function
		self.cmdTreeObj.getObject().Bind(wx.EVT_TREE_SEL_CHANGED, self.OnChangeInputPanelEvent)
		self.returnInfoObj._up_sendCmdButton.Bind(wx.EVT_BUTTON, self.OnSendCmdToUart)
		self.returnInfoObj._up_searchHistoryCombox.Bind(wx.EVT_COMBOBOX, self.OnSelectHistoryCmd)
		self.returnInfoObj._up_filterCheckBox.Bind(wx.EVT_CHECKBOX, self.onFilterChecked)
		
		#6. layout
		
		
		layoutSizer = wx.GridBagSizer(4, 3)
		layoutSizer.Add(panel_up_left, (0, 0), (2, 2), wx.EXPAND | wx.ALL)
		layoutSizer.Add(panel_up_right_adv , (0, 2), (1, 1), wx.EXPAND | wx.ALL)
		layoutSizer.Add(varHbox , (1, 2), (1, 1), wx.EXPAND | wx.ALL)
		layoutSizer.Add(panel_down_cmd_status, (2, 0), (2, 3), wx.EXPAND|wx.ALL)
		
		
		layoutSizer.AddGrowableCol(1, 0)
		self.mainPanel.SetSizerAndFit(layoutSizer)
	
	def _changeInputPanel(self, cmdStr):
		needReplace = False
		proviouePanelIndex = self.curDisplayInputIndex
		for i in range(len(self.scroll_up_input_list)):
			if self.scroll_up_input_list[i].GetName() == cmdStr:
				self.curDisplayInputIndex = i
				#self._mainArgObj._cmdInputCurrentDisplayIndex = i
				needReplace = True
				break
		if needReplace == False:
			return
		
		self.scroll_up_input_list[proviouePanelIndex].Hide()
		self.scroll_up_input_list[self.curDisplayInputIndex].Show()
		self.mainPanel.Layout() #very important
		pass
		
	def OnChangeInputPanelEvent(self, evt): #event from cmdTree
		
		evtObj = evt.GetEventObject()
		if evtObj == None:
			return
		
		cmdStr = evtObj.GetItemText(evtObj.GetFocusedItem())
		self._changeInputPanel(cmdStr)
		pass
	
	def onFilterChecked(self, evt):
		evtObject = evt.GetEventObject()
		self._mainArgObj._mainPageStatusFilter = evtObject.GetValue()
		pass
		
	def OnSelectHistoryCmd(self, evt):
		evtObject = evt.GetEventObject()
		cmdStr = evtObject.GetString(evtObject.GetCurrentSelection())
		self._changeInputPanel(cmdStr)
		pass
		
	def OnSendCmdToUart(self, evt):	
		#1. get data list
		sendDataList = self.scroll_input_obj_list[self.curDisplayInputIndex]._getValue()
		cmdStr = self.scroll_input_obj_list[self.curDisplayInputIndex]._getCmdName()
		
		#2. append history cmd to history cmd list
		hasFoundSameName = False
		for i in range(len(self._historyCmdStrList)):
			if cmdStr == self._historyCmdStrList[i]:
				hasFoundSameName = True
				break
		if hasFoundSameName == False:
			self._historyCmdStrList.append(cmdStr)
			self.returnInfoObj.updateComboxChoice(self._historyCmdStrList)

		#3. send data to message log page
		tempDataObj = comm_cls.HCI_QUEUE_DATA_LIST_CLASS()
		tempDataObj._time = get_time_stamp()
		tempDataObj._dataList = sendDataList
		self._mainArgObj._data_2_parser_queue_lock.acquire()
		self._mainArgObj._recv_2_parser_queue.put(tempDataObj)
		self._mainArgObj._data_2_parser_queue_lock.release()
		
		if self._mainArgObj._uartApiObj.uartOk() == False:
			needInit = False
			dlg = wx.MessageDialog(None, "No port to use, Do you want to init port?", \
			                       'Port init warnning', wx.YES_NO | wx.ICON_QUESTION)
			retCode = dlg.ShowModal()
			if (retCode == wx.ID_YES):
				needInit = True
			dlg.Destroy()
				
			if needInit == True:
				self._mainArgObj._toolBarObj.openInitPort()
				return
		
		#4. send data to uart
		if self._mainArgObj._uartApiObj.uartOk():	
			ret = self._mainArgObj._uartApiObj.uartSend(sendDataList)
			if ret == False:
				dlg = wx.MessageDialog(None, "Failed to send data, please to check port.", \
			                       'ERROR', wx.YES_NO | wx.ICON_ERROR)
				retCode = dlg.ShowModal()
				if (retCode == wx.ID_YES):
					needInit = True
				dlg.Destroy()
		pass	
	pass