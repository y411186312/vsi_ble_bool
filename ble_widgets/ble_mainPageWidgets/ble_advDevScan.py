import wx

class Ble_AdvDevScanClass(wx.Frame):
	def __init__(self, parent, windowSize, columnTileList, columnWeightList, title):
	
		self.connectColor = wx.Colour(12, 125, 18, alpha=wx.ALPHA_OPAQUE)
		self._panel = parent
		weights = 0
		for i in range(len(columnWeightList)):
			weights += columnWeightList[i]
		
		curSize = (710, 150)
		#1. create ListCtrl
		self._listObj = wx.ListCtrl(self._panel, -1, wx.DefaultPosition, size=curSize,style = wx.LC_REPORT |wx.LC_AUTOARRANGE)
		
		#self._listObj.SetWindowStyleFlag(wx.BORDER_DEFAULT)
		#2. set column title
		for i in range(len(columnTileList)):	
			self._listObj.InsertColumn(i, columnTileList[i])
		
		#3. set column width
		for i in range(len(columnWeightList)):
			value = (columnWeightList[i] * curSize[0])/weights - 3
			#value = value * 2 / 3 -20
			#print "value:",value
			self._listObj.SetColumnWidth(i, value)
		#self._listObj.SetItemCount(20)
		#up_left_v_vbox = wx.BoxSizer(wx.VERTICAL)
		
		#self._panel.SetMinSize((800, 100))
		self.normalColor = self._listObj.GetTextColour()
		
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self._listObj)
		self._panel.SetSizerAndFit(hbox)	
		
		
	def getObject(self):
		return self._listObj
	
	def clearAllAdv(self):
		self._listObj.DeleteAllItems()
	
	def markAdvDevOff(self, bdAddrStrList, connectHandle, role):
		#print "markAdvDevOff----bdAddrStr:",bdAddrStrList
		#print "markAdvDevOff----connectHandle:",connectHandle
		
		hasFound = False
		allItem = self._listObj.GetItemCount()
		for i in range(allItem):
			bdItemStr = self._listObj.GetItemText(i, 0)
			list = bdItemStr.split(' ')
			#print "inBdAddrStr:",bdItemStr
			for j in range(6):
				if int(list[j], 16) != int(bdAddrStrList[j], 16):
					#print "False:",j
					hasFound = False
					break
				else:
					#print "True:",j
					hasFound = True
			if hasFound == True:
				break
		if hasFound == True:
			#connHandleItem = self._listObj.GetItem(i, 1)
			self._listObj.SetItem(i, 1, '')
			self._listObj.SetItem(i, 5, '')
			self._listObj.SetItemTextColour(i, self.normalColor)
		
	#def recursionMarkAdvDevOn(self, bdAddrStrList, connectHandle, role, addrType):
	#	self._listObj.SetItem(i, 5, roleStr)
	#	self._listObj.SetItemTextColour(i, self.connectColor)
	def addDeviceAndMarkAdvDevOn(self, valueList):
		
		if len(valueList) != self._listObj.GetColumnCount():
			return False
		index = self._listObj.InsertItem(self._listObj.GetItemCount(), 'x')	
		self._lastListIndex = index
		for i in range(len(valueList)):
			self._listObj.SetItem (index, i, valueList[i])
		self._listObj.SetItemTextColour(index, self.connectColor)
	
	
	
	def markAdvDevOn(self, bdAddrStrList, connectHandle, role, addrType):
		#print "markAdvDevOn ----bdAddrStr:",bdAddrStrList
		#print "markAdvDevOn ----connectHandle:",connectHandle
		#hasRecurse = False
		hasFound = False
		allItem = self._listObj.GetItemCount()
		for i in range(allItem):
			bdItemStr = self._listObj.GetItemText(i, 0)
			list = bdItemStr.split(' ')
			#print "inBdAddrStr:",bdItemStr
			for j in range(6):
				if int(list[j], 16) != int(bdAddrStrList[j], 16):
					hasFound = False
					break
				else:
					hasFound = True
			if hasFound == True:
				break
		if hasFound == True:
			#connHandleItem = self._listObj.GetItem(i, 1)
			self._listObj.SetItem(i, 1, hex(connectHandle))
			roleStr = 'Master'
			if role == 1:
				roleStr = 'Slave'
			self._listObj.SetItem(i, 5, roleStr)
			self._listObj.SetItemTextColour(i, self.connectColor)
		else:
			newList = []
			newList.append(' '.join(bdAddrStrList))
			newList.append(hex(connectHandle))
			newList.append('')
			newList.append(hex(addrType))
			newList.append('')
			roleStr = 'Master'
			if role == 1:
				roleStr = 'Slave'
			newList.append(roleStr)
			newList.append(' ')
			
			self.addDeviceAndMarkAdvDevOn(newList)
			
		
	def addDevice(self, valueList):
		if len(valueList) != self._listObj.GetColumnCount():
			return False
		
		allItem = self._listObj.GetItemCount()
		index = 0
		hasFound = False
		for index in range(allItem):
			bdItemStr = self._listObj.GetItemText(index, 0)
			list = bdItemStr.split(' ')
			#print "list:",list
			#print "valueList[0]:",valueList[0].split(' ')
			#print "inBdAddrStr:",bdItemStr
			for j in range(6):
				if int(list[j], 16) != int(valueList[0].split(' ')[j], 16):
					#print "False:",j
					hasFound = False
					break
				else:
					hasFound = True
	
			if hasFound == True:
				break
		
		
		#"""
		#print ""
		#print "index: ",index
		#print "\t\thasFound: ",hasFound
		if len(valueList) != self._listObj.GetColumnCount():
			return False
		if hasFound != True:
			index = self._listObj.InsertItem(self._listObj.GetItemCount(), 'x')	
		#self._lastListIndex = index
		for i in range(len(valueList)):
			self._listObj.SetItem (index, i, valueList[i])
			
		
		
		#"""
		#print "add"	