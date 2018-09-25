import wx

class Ble_MessageLogListCtrlClass(wx.Frame):
	def __init__(self, parent, windowSize, columnTileList, columnWeightList, title):
		wx.Panel.__init__(self, parent)
		self._panel = parent
		weights = 0
		for i in range(len(columnWeightList)):
			weights += columnWeightList[i]
		
		
		#1. create ListCtrl
		self._listObj = wx.ListCtrl(self._panel, -1, wx.DefaultPosition, size=(windowSize[0]-10, windowSize[1]/2-50),style = wx.LC_REPORT |wx.LC_AUTOARRANGE)
		
		
		#2. set column title
		for i in range(len(columnTileList)):	
			self._listObj.InsertColumn(i, columnTileList[i])
		
		#3. set column width
		for i in range(len(columnWeightList)):
			value = (columnWeightList[i] * windowSize[0])/weights
			self._listObj.SetColumnWidth(i, value)
	
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self._listObj)
		self._panel.SetSizerAndFit(hbox)	
		
		
	def getObject(self):
		return self._listObj
	#def getCurFocusedMessage(self):
		
		
	def addMessage(self, dataMsgObj):
		inList = []
		dataList = dataMsgObj._dataList
		
		timeStr, typeStr, dirStr, headerStr, payloadStr = dataMsgObj._time,'','','',''
		
		type = int(dataList[0], 16)
		if type == 1:
			typeStr = 'Command'
			dirStr = '[TX] --->'
			headerStr = " ".join(dataList[:4])
			payloadStr = " ".join(dataList[4:])
			
			
		elif type == 4:
			typeStr = 'Event'
			dirStr = '[RX] <---'
			headerStr = " ".join(dataList[:3])
			payloadStr = " ".join(dataList[3:])
			
		elif type == 2:
			typeStr = 'ACL'
			dirStr = '[TX] --->'
			if dataMsgObj._direction == 1:
				dirStr = '[RX] --->'
			
			headerStr = " ".join(dataList[:5])
			payloadStr = " ".join(dataList[5:])
		else:
			payloadStr = " ".join(dataList)
			
		if dataMsgObj._direction == 0:
			inList.append('[Tx] --->')
		elif dataMsgObj._direction == 1:
			inList.append('[Tx] --->')
		else:
			inList.append('<--->')
			
		inList = [timeStr, typeStr, dirStr, headerStr, payloadStr]
		
		index = self._listObj.InsertItem(self._listObj.GetItemCount(), 'x')	
		for i in range(len(inList)):
			self._listObj.SetItem (index, i, inList[i])
		
	def addMessage_new(self, arrayList):
		#self._listObj.DeleteAllItems()
		index = self._listObj.InsertItem(self._listObj.GetItemCount(), 'x')	
		for i in range(len(arrayList)):
			self._listObj.SetItem (index, i, arrayList[i])
		self._listObj.Focus(index)
	def clearAll(self):
		self._listObj.DeleteAllItems()
		

