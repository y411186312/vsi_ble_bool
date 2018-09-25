import wx
import time

from detailMessage import *
from messageLog import *


class Ble_MessagePage(wx.Panel):
	
		
	def __init__(self,parent, windowSize, mainArgObj):
		wx.Panel.__init__(self, parent)
		self._mainArgObj = mainArgObj
		self._cmdList = mainArgObj._cmdTreeObj._mainArgObj._loadSpecObj._getCmdList()
		self._eventList = mainArgObj._cmdTreeObj._mainArgObj._loadSpecObj._getEventList()
		self._retParaList = mainArgObj._cmdTreeObj._mainArgObj._loadSpecObj._getReturnParaList()
		
		
		self.mainPanel = wx.Panel(self, -1)
		panel_up = wx.Panel(self.mainPanel, -1)
		panel_down = wx.Panel(self.mainPanel, -1)
		
		#1. create message log
		logCtrlTitleList = ['Time', 'PacketType', 'Direction', 'PacketHeader', 'Payload']
		logCtrlWeightList = [2, 2, 2, 4, 12]
		self._messageLogObj = Ble_MessageLogListCtrlClass(panel_up, windowSize, logCtrlTitleList, logCtrlWeightList, 'log')
		mainArgObj._messsageLogObj = self._messageLogObj
		
		#2. create para detail
		paraCtrlTitleList = ['Param Name', 'Param Value']
		paraCtrlWeightList = [2, 5]
		self._detailParaObj = Ble_DetailMsgListCtrlClass(panel_down, windowSize, paraCtrlTitleList, paraCtrlWeightList, 'para')
		
		#3. bind action
		self._messageLogObj.getObject().Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnParseMessage2Dic)
		
		#4. layout
		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(panel_up, 1, wx.EXPAND | wx.ALL)
		vbox.Add(panel_down, 1, wx.EXPAND | wx.ALL)
		
		self.mainPanel.SetSizerAndFit(vbox)
		
	def OnParseMessage2Dic(self, event):
		outArrayList = []
		evtObj = event.GetEventObject()
		item = evtObj.GetFocusedItem()
		headerStrList = evtObj.GetItemText(item,3).split(' ')
		payloadStrList = evtObj.GetItemText(item,4).split(' ')
		
		outArrayList = self._mainArgObj._parserObj.getMessagePaserResultByGui(headerStrList, payloadStrList)
		self._detailParaObj.addDetail(outArrayList)
		
	def clearAll(self):
		self._messageLogObj.clearAll()
		self._detailParaObj.clearAll()
		