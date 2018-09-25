import sys,wx


class Ble_StatusBar(wx.Frame):
	def __init__(self, parent):
		self._parent = parent
		self._statusBar = wx.StatusBar(parent, -1)
		self._statusBar.SetFieldsCount(3) 
		self._statusBar.SetStatusWidths([-1,-1,-1]) 
		self._statusBar.SetStatusText("Disconnect", 0) 
		self._parent.SetStatusBar(self._statusBar)
		
	def _setStatusContent(self, index, statusStr):
		if index < 0 or index > 2:
			return False
		self._statusBar.SetStatusText(statusStr, index)
		return True
		
	def setConnectStatus(self, status):
		if status == 1:
			self._statusBar.SetStatusText("Connected", 0)
		elif status == 0:
			self._statusBar.SetStatusText("Disconnect", 0)
			
	def setPort(self, inStr):
		self._statusBar.SetStatusText(inStr, 1)
		
	def setBdaddr(self, bdAddrStr):
		self._statusBar.SetStatusText(bdAddrStr, 2)
	