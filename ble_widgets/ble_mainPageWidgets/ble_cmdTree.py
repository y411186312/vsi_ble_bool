import wx



"""
dict = {
'a1':['b', 'c', 'd'],
'a2':['b1', 'c1'],
'a3':['b2']

}
"""
class Ble_cmdTreeListCtrlClass(wx.Frame):
	def __init__(self, parent, id, title, windowSize, mainArgObj):
		super(Ble_cmdTreeListCtrlClass, self).__init__(None, -1)
		
		self._mainArgObj = mainArgObj
		cmdsList = self._mainArgObj._loadSpecObj._getCmdList()
		cmdClsList = ['Link Control Commands', \
		              'Controller & Baseband Commands', \
					  'Informational Parameters Commands', \
					  'Status Parameters Commands', \
					  'Testing Commands', \
					  'LE Commands', \
					  'Vendor Commands'\
					 ]
					  
		cmdClsFileName = ['LinkControlCommands.data', \
						  'Controller_Baseband_Commands.data', \
						  'Informational_Parameters_Commands.data', \
						  'Status_Parameters_Commands.data', \
						  'Testing_Commands.data', \
		                  'LE_Commands.data', \
						  'Vendor_Commands.data', \
						 ]
		
		#cmdClsList cmdClsFileName should be keep in touch with
		minX = windowSize[0] * 1 / 3
		minY = windowSize[1] * 5 / 8
		self.treeNode = [[]] * len(cmdClsList)
	
		#gui part
		self._panel = parent
		self.cmdTree = wx.TreeCtrl(self._panel,-1, wx.DefaultPosition, (-1, -1), wx.TR_HAS_BUTTONS)
		self.cmdTreeID = self.cmdTree.GetId()
		self.cmdTree.SetMinSize((minX, minY))
		
		root = self.cmdTree.AddRoot("cmd")
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
	
	#"""
	def setSpeifiedFocusItem(self, str): #to action some info from menubar search cmd
		for i in range(len(self.treeNode)):
			item,cookie = self.cmdTree.GetFirstChild(self.treeNode[i])
			while item.IsOk():
				if self.cmdTree.GetItemText(item) == str:
					self.cmdTree.SetFocusedItem(item)
					return
					
				(item,cookie) = self.cmdTree.GetNextChild(item, cookie)
	#"""
	def getObject(self):
		return self.cmdTree
		
	