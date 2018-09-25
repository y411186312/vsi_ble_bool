import wx

class Ble_DetailMsgListCtrlClass(wx.Frame):
	def __init__(self, parent, windowSize, columnTileList, columnWeightList, title):
	
		self._panel = parent
		weights = 0
		for i in range(len(columnWeightList)):
			weights += columnWeightList[i]
		
		
		#1. create ListCtrl
		self._listObj = wx.ListCtrl(self._panel, -1, wx.DefaultPosition, size=(windowSize[0]-10, windowSize[1]/2-80),style = wx.LC_REPORT |wx.LC_AUTOARRANGE)
		
		
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
	def clearAll(self):
		self._listObj.DeleteAllItems()
	
	def addDetail(self, inArrayList): #inArrayList should be [['x', 'b'], ...]
		self._listObj.DeleteAllItems()
		
		for item in inArrayList:
			index = self._listObj.InsertItem(self._listObj.GetItemCount(), 'x')	
			self._listObj.SetItem (index, 0, item[0])
			self._listObj.SetItem (index, 1, item[1])