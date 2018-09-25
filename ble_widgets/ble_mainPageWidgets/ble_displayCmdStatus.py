import wx

class Ble_cmdReturnInfoClass(wx.Panel):

	
				

	def updateComboxChoice(self, inChoicesList):
		#print "update......."
		self._up_searchHistoryCombox.Clear()
		for i in range(len(inChoicesList)):
			self._up_searchHistoryCombox.Append(inChoicesList[i])
		
	def __init__(self,parent, mainArgObj, windowSize):
		self._panel = parent
		
		#1. init gui and do some init
		self._up_filterCheckBox = wx.CheckBox(self._panel, label = 'Event Panel Filter')
		self._up_searchHistoryCombox = wx.ComboBox(self._panel, style=wx.CB_DROPDOWN | wx.CB_SORT, choices=[])
		self._up_sendCmdButton = wx.Button(self._panel, label = 'Send Command', size=(100, 26))
		self._down_displayInfoListCtrl = wx.ListCtrl(parent, -1, size=(windowSize[0]-20, 200), style = wx.LC_REPORT | wx.LC_NO_HEADER | wx.LC_AUTOARRANGE)
		
		self._up_filterCheckBox.SetValue(mainArgObj._mainPageStatusFilter)
		
		#2. set _down_displayInfoListCtrl para
		columnTileList = ['x', 'y']
		columnWidthList = [1, 3]
		for i in range(len(columnTileList)):	
			self._down_displayInfoListCtrl.InsertColumn(i, columnTileList[i])
		
		weigths = 0
		for i in range(len(columnWidthList)):
			weigths += columnWidthList[i]
			
		for i in range(len(columnWidthList)):
			value = columnWidthList[i] * windowSize[0] / weigths
			self._down_displayInfoListCtrl.SetColumnWidth(i, value)
		
		#3. layout
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox_down = wx.BoxSizer(wx.HORIZONTAL)
		vbox = wx.BoxSizer(wx.VERTICAL)
		
		hbox.Add(self._up_filterCheckBox, 1, border=5)
		hbox.AddStretchSpacer(1)
		hbox.Add(self._up_searchHistoryCombox, 4, border=5)
		hbox.AddStretchSpacer(1)
		hbox.Add(self._up_sendCmdButton, 1, border=5)
		
		hbox_down.Add(self._down_displayInfoListCtrl, 1, border=5)
		vbox.Add(hbox)
		vbox.Add(hbox_down)
		
		self._panel.SetSizerAndFit(vbox)
	
	def addDetail(self, inArrayList): #inArrayList should be [['x', 'b'], ...]		
		for item in inArrayList:
			index = self._down_displayInfoListCtrl.InsertItem(self._down_displayInfoListCtrl.GetItemCount(), 'x')	
			self._down_displayInfoListCtrl.SetItem (index, 0, item[0])
			self._down_displayInfoListCtrl.SetItem (index, 1, item[1])
			self._down_displayInfoListCtrl.Focus(index)
	"""
	def addDevice(self, valueList):
		if len(valueList) != self._down_displayInfoListCtrl.GetColumnCount():
			return False
		index = self._down_displayInfoListCtrl.InsertItem(self._down_displayInfoListCtrl.GetItemCount(), 'x')	
		for i in range(len(valueList)):
			self._down_displayInfoListCtrl.SetItem (index, i, valueList[i])
			self._down_displayInfoListCtrl.Focus(index)

	"""
	def clearAll(self):
		self._down_displayInfoListCtrl.DeleteAllItems()