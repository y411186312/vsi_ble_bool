import wx

"""
class Ble_localInfoListCtrlClass(wx.Frame):
	def __init__(self, parent, id, title, windowSize, mainArgObj):
		super(Ble_localInfoListCtrlClass, self).__init__(None, -1)
		#gui part
		self._panel = parent
		self.cmdTree = wx.TreeCtrl(self._panel,-1, wx.DefaultPosition, (-1, -1), wx.TR_HAS_BUTTONS)
		self.cmdTreeID = self.cmdTree.GetId()
		self.cmdTree.SetMinSize((windowSize[0]-20, windowSize[1]-20))
		self.treeNode = []
		
		root = self.cmdTree.AddRoot("Local Infos")
		for i in range(len(cmdClsList)):
			self.treeNode[i] = self.cmdTree.AppendItem(root, cmdClsList[i])
		
		for item in cmdsList:
			for i in range(len(cmdClsFileName)):
				if item._classStr == cmdClsFileName[i]:
					self.cmdTree.AppendItem(self.treeNode[i], item._name)
					break
			
		self.cmdTree.Expand(root)
		
		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self.cmdTree)
		self._panel.SetSizerAndFit(vbox)
	
	def addAttr(self, title, value):
		for i in range(len(self.treeNode)):
			
		self.treeNode[i] = self.cmdTree.AppendItem(root, cmdClsList[i])
	
	def setSpeifiedFocusItem(self, str): #to action some info from menubar search cmd
		for i in range(len(self.treeNode)):
			item,cookie = self.cmdTree.GetFirstChild(self.treeNode[i])
			while item.IsOk():
				if self.cmdTree.GetItemText(item) == str:
					self.cmdTree.SetFocusedItem(item)
					return
					
				(item,cookie) = self.cmdTree.GetNextChild(item, cookie)
	def getObject(self):
		return self.cmdTree
"""


class Ble_localInfoListCtrlClass(wx.Frame):
	def __init__(self, parent, windowSize):
		super(Ble_localInfoListCtrlClass, self).__init__(None, -1)
		#gui part
		self._panel = parent
		self.cmdTree = wx.TreeCtrl(self._panel,-1, wx.DefaultPosition, (-1, -1), wx.TR_HAS_BUTTONS)
		self.cmdTreeID = self.cmdTree.GetId()
		self.cmdTree.SetMinSize((windowSize[0]-20, windowSize[1]-20))
		self.treeNode = []
		
		root = self.cmdTree.AddRoot("Local Infos")
		self.cmdTree.Expand(root)
		
		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self.cmdTree)
		self._panel.SetSizerAndFit(vbox)
	
	def addAttr(self, titleStr, value):
		rootItem = self.cmdTree.GetRootItem()
		rootChildCnt = self.cmdTree.GetChildrenCount(rootItem, False)
		if rootChildCnt == 0:
			node = self.cmdTree.AppendItem(rootItem, titleStr)
			self.cmdTree.AppendItem(node, value)
			self.treeNode.append(node) 
		else:
			hasFilled = False
			for dir in self.treeNode:
				existTitle = self.cmdTree.GetItemText(dir)
				if existTitle == titleStr:
					self.cmdTree.AppendItem(dir, value)
					hasFilled = True
					break
			if hasFilled == False:
				node = self.cmdTree.AppendItem(rootItem, titleStr)
				self.cmdTree.AppendItem(node, value)
				self.treeNode.append(node)
				
			
		self.cmdTree.Expand(rootItem)
		
	
	def getObject(self):
		return self.cmdTree
		
class Ble_DeviceInfoPage(wx.Panel):
	def __init__(self, parent, windowSize, mainArgObj):
		wx.Panel.__init__(self, parent)
		mainPanel = wx.Panel(self, -1)
		panel_info = wx.Panel(mainPanel)
		
		
		self.treeObj = Ble_localInfoListCtrlClass(panel_info, (windowSize[0], windowSize[1]))
			
		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(panel_info)	
		
		mainPanel.SetSizerAndFit(vbox)
	def addAttr2Dev(self, titleStr, valueStr):
		self.treeObj.addAttr(titleStr, valueStr)