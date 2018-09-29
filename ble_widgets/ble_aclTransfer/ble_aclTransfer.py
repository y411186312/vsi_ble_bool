import wx,threading,time
import includes.ble_common_class as comm_cls 
	
def get_time_stamp():
    ct = time.time()
    local_time = time.localtime(ct)
    data_head = time.strftime("%H:%M:%S", local_time)
    data_secs = (ct - int(ct)) * 1000
    time_stamp = "%s.%03d" % (data_head, data_secs)
    return time_stamp
	
class Ble_processBarGuage(wx.Frame):
	def __init__(self, parent, statusLen, maxRange):
		self._range = maxRange
		wx.Frame.__init__(self, None, -1, 'Gauge Example', size = (600, 300))
		#panel = wx.Panel(parent, -1)
		panel = parent
		#panel.SetBackgroundColour("white")
		#self.gauge = wx.Gauge(panel, -1, 100, (100, 60), (250, 25), style = wx.GA_HORIZONTAL)
		self.gauge = wx.Gauge(panel, -1, statusLen, style = wx.GA_HORIZONTAL)
		self.gauge.SetRange(self._range)
		self.gauge.SetBezelFace(3)
		self.gauge.SetShadowWidth(3)
		self.transferTitleTextObj = wx.StaticText(panel, wx.ID_ANY, 'Data Transfer Status')
		self.transferProcessTextObj = wx.StaticText(panel, wx.ID_ANY, '00%', (50, 30))
		hbox_status = wx.BoxSizer(wx.HORIZONTAL)
		hbox_detail = wx.BoxSizer(wx.HORIZONTAL)
		vbox = wx.BoxSizer(wx.VERTICAL)
		
		#hbox.AddStretchSpacer(1)
		hbox_status.Add(self.transferTitleTextObj, 1)
		hbox_status.AddStretchSpacer(1)
		hbox_status.Add(self.gauge, 8)
		hbox_status.AddStretchSpacer(1)
		hbox_status.Add(self.transferProcessTextObj,1)
		hbox_status.AddStretchSpacer(1)
		
		#######data transfer detail
		self.transferRateTitleObj = wx.StaticText(panel, wx.ID_ANY, 'Transfer Rate:')
		self.transferRateObj = wx.StaticText(panel, wx.ID_ANY, ' 0bps ')
		
		self.transferSizeTitleObj = wx.StaticText(panel, wx.ID_ANY, 'Transfer Size:')
		self.transferSizeObj = wx.StaticText(panel, wx.ID_ANY, ' 0bytes ')
		
		hbox_detail.Add(self.transferRateTitleObj, 1)
		hbox_detail.Add(self.transferRateObj, 1)
		
		hbox_detail.AddStretchSpacer(1)
		hbox_detail.Add(self.transferSizeTitleObj, 1)
		hbox_detail.Add(self.transferSizeObj)
		
		vbox.Add(hbox_status, 2, border=5)
		vbox.AddStretchSpacer(1)
		vbox.Add(hbox_detail, 2, border=5)
		
		panel.SetSizerAndFit(vbox)
	def setTransferRateStr(self, valueStr):
		self.transferRateObj.SetLabel(valueStr + ' bps')
		
	def setTransferSize(self, size):
		self.transferSizeObj.SetLabel(str(size) + ' bytes')
	
	
	def setRange(self, range):
		self.gauge.SetRange(range)
		self._range = range
	
	def setCurrentValue(self, value):
		if value > self._range:
			value = self._range
		percentageStr = "%.2f" % (float(value * 100) / self._range) + "% "
		self.transferProcessTextObj.SetLabel(percentageStr)
		self.gauge.SetValue(value)
		
linkTypeList = ['ACL', 'SCO', 'eSCO']
transferTypeList = ['Sequential', 'Pattern', 'File Transfer', 'Fixed Pattern']
broadcastFlagList = ['No Broadcast', 'Active Slave Broadcast', 'Parked slave Broadcast']
pbFlagList = ['NonAutoFlush', 'AutoFlush', 'Customize']
			
class Ble_aclTransferClass(wx.Dialog):
	def __init__(self, parent, title, windowSize, mainArgObj):
		super(Ble_aclTransferClass, self).__init__(parent, title=title, size = (500, 400))
		#parent, title = title, size = (300, 400)
		
		self._sendAclThreadObj = None
		self.treadCloseFlag = False
		self._aclSpecialStartTime = 0
		self._mainArgObj = mainArgObj
		#0. get handle data
		handleList = []
		for i in range(len(mainArgObj._connectionList)):
			handleList.append(hex(mainArgObj._connectionList[i]._connectHandle))
		
		
		#1. data part
		connectHandleList = handleList
		
		#2. panel
			
		mainPanel = wx.Panel(self, -1)
		
		panel_input = wx.Panel(mainPanel, -1)
		panel_transStatus = wx.Panel(mainPanel, -1)
		panel_button = wx.Panel(mainPanel, -1)
		
		#2.1 input part
		linkType_staticText = wx.StaticText(panel_input, wx.ID_ANY, 'Link Type', (80, 30))
		self.linkType_choice = wx.Choice(panel_input, size=(120, 30), choices = linkTypeList)
		self.linkType_choice.SetSelection(0)
		
		transferType_staticText = wx.StaticText(panel_input, wx.ID_ANY, 'Transfer Type', (80, 30))
		self.transferType_choice = wx.Choice(panel_input, size=(120, 30), choices = transferTypeList)
		self.transferType_choice.SetSelection(0)
		
		packetSize_staticText = wx.StaticText(panel_input, wx.ID_ANY, 'Packet Size', (80, 30))
		self.packetSize_text = wx.TextCtrl(panel_input, wx.ID_ANY, '27', size =(120, 25), style = wx.TE_LEFT)
		 
		numberOfTrails_staticText = wx.StaticText(panel_input, wx.ID_ANY, 'Number of Trails', (80, 30))
		self.numberOfTrails_text = wx.TextCtrl(panel_input, wx.ID_ANY, '1', size =(120, 25), style = wx.TE_LEFT)
		
		connHandle_staticText = wx.StaticText(panel_input, wx.ID_ANY, 'Connection Handle', (80, 30))
		self.connHandle_combox = wx.ComboBox(panel_input, size =(120, 30), style=wx.CB_DROPDOWN | wx.CB_SORT, choices=connectHandleList)
		if len(connectHandleList)>0:
			self.connHandle_combox.SetSelection(0)
		
		bcFlag_staticText = wx.StaticText(panel_input, wx.ID_ANY, 'Broadcast Flag', (80, 30))
		self.bcFlag_choice = wx.Choice(panel_input, size=(120, 30), choices = broadcastFlagList)
		self.bcFlag_choice.SetSelection(0)
		
		
		pbFlag_staticText = wx.StaticText(panel_input, wx.ID_ANY, 'PB Flag', (80, 30))
		self.pbFlag_choice = wx.Choice(panel_input, size=(120, 30), choices = pbFlagList)
		self.pbFlag_choice.SetSelection(0)
		
		
		
		input_gbs = wx.GridBagSizer(4, 4)
		input_gbs.Add(linkType_staticText, (0, 0), (1, 1), wx.ALIGN_LEFT) 
		input_gbs.Add(self.linkType_choice, (0, 1), (1, 1), wx.ALIGN_LEFT) 
		
		input_gbs.Add(transferType_staticText, (0, 2), (1, 1), wx.ALIGN_LEFT) 
		input_gbs.Add(self.transferType_choice, (0, 3), (1, 1), wx.ALIGN_LEFT) 
		
		input_gbs.Add(packetSize_staticText, (1, 0), (1, 1), wx.ALIGN_LEFT) 
		input_gbs.Add(self.packetSize_text, (1, 1), (1, 1), wx.ALIGN_LEFT) 
		
		input_gbs.Add(numberOfTrails_staticText, (1, 2), (1, 1), wx.ALIGN_LEFT) 
		input_gbs.Add(self.numberOfTrails_text, (1, 3), (1, 1), wx.ALIGN_LEFT) 
		
		input_gbs.Add(connHandle_staticText, (2, 0), (1, 1), wx.ALIGN_LEFT) 
		input_gbs.Add(self.connHandle_combox, (2, 1), (1, 1), wx.ALIGN_LEFT) 
		
		input_gbs.Add(bcFlag_staticText, (2, 2), (1, 1), wx.ALIGN_LEFT) 
		input_gbs.Add(self.bcFlag_choice, (2, 3), (1, 1), wx.ALIGN_LEFT) 
		
		input_gbs.Add(pbFlag_staticText, (3, 0), (1, 1), wx.ALIGN_LEFT) 
		input_gbs.Add(self.pbFlag_choice, (3, 1), (1, 1), wx.ALIGN_LEFT) 
		panel_input.SetSizerAndFit(input_gbs)
		
		#3. data transfer
		#windowSize
		self.dataTransferStatusObj = Ble_processBarGuage(panel_transStatus,windowSize[1] -15, 300)
		
		#4. button
		self._startTxButton = wx.Button(panel_button, label = 'Start Transfer', size = (100, 30))
		self._cancelTxButton = wx.Button(panel_button, label = 'Cancel Transfer', size = (100, 30))
		self._closeButton = wx.Button(panel_button, label = 'Close', size = (100, 30))
		hbox_button = wx.BoxSizer(wx.HORIZONTAL)
		
		hbox_button.AddStretchSpacer(1)
		hbox_button.Add(self._startTxButton, 2)
		hbox_button.AddStretchSpacer(1)
		hbox_button.Add(self._cancelTxButton, 2)
		hbox_button.AddStretchSpacer(1)
		hbox_button.Add(self._closeButton, 2)
		hbox_button.AddStretchSpacer(1)
		self._startTxButton.Bind(wx.EVT_BUTTON, self.sendAclData)
		self._closeButton.Bind(wx.EVT_BUTTON, self.closeGui)
		self._cancelTxButton.Bind(wx.EVT_BUTTON, self.cancelTransfer)
		
		panel_button.SetSizerAndFit(hbox_button)
		
		#5. main layout
		main_vbox = wx.BoxSizer(wx.VERTICAL)
		main_vbox.Add(panel_input)
		main_vbox.AddStretchSpacer(1)
		main_vbox.Add(panel_transStatus, 2)
		main_vbox.AddStretchSpacer(1)
		main_vbox.Add(panel_button, 2)
		
		mainPanel.SetSize((400, 600))
		mainPanel.SetSizerAndFit(main_vbox)
	
	def setRange(self, range):
		self.dataTransferStatusObj.setRange(range)
		self._aclSpecialStartTime = 0
	def setTransferRateStr(self, rateStr):
		self.dataTransferStatusObj.setTransferRateStr(rateStr)
	def setTransferSize(self, transferSize):
		self.dataTransferStatusObj.setTransferSize(transferSize)
	
	def setCurrentValue(self, packetCnt):
		#print "setCurrentValue::::"
		self.dataTransferStatusObj.setCurrentValue(packetCnt)
		
		
	def setSpecialAclRecv(self, transferSize, timeData):
		if self._aclSpecialStartTime == 0:
			self._aclSpecialStartTime = timeData
			return
			
		timeInterval = timeData - self._aclSpecialStartTime
		rateStr = "%.2f" % (transferSize * 8 /float(timeData - self._aclSpecialStartTime))
		self.setTransferRateStr(rateStr)
		self.setTransferSize(transferSize)
		
			
	def cancelTransfer(self, evt):
		self._mainArgObj._aclRecvHasGotAclHeader = False
		self.treadCloseFlag = True
		self.restoreBeforeSendStatus()
		
	def closeGui(self, evt):
		self._mainArgObj._aclGuiHasBeenQuited = True
		self._mainArgObj._aclRecvHasGotAclHeader = False
		self.treadCloseFlag = True
		if self._sendAclThreadObj != None:
			self._sendAclThreadObj.join()
		self.Close()
		
	def setTxMode(self):
		self._startTxButton.Enable()
		self._cancelTxButton.Disable()
		self._closeButton.Enable()
		
	
	def setRxMode(self):
		self._startTxButton.Disable()
		self._cancelTxButton.Disable()
		self._closeButton.Enable()
	
	def displayErrorDlg(self, typeStr, shouldStr):
		dlg = wx.MessageDialog(None, "[%s] should be [%s], Yes for input again"%(typeStr, shouldStr), "Error input", wx.YES_NO | wx.ICON_QUESTION)
		if dlg.ShowModal() == wx.ID_NO:
			self.Close(True)
		dlg.Destroy()
		return True
	
	def getInput(self):
		threadRunObj = comm_cls.HCI_ACL_THREAD_RUN_CLASS()
		#1. link type
		index = self.linkType_choice.GetSelection()
		content = self.linkType_choice.GetString(index) 
		if content != 'ACL':
			self.displayErrorDlg('Link Type', 'ACL')
			return None
		
		#2. transfer type
		index = self.transferType_choice.GetSelection()
		content = self.transferType_choice.GetString(index) 
		if content != 'Sequential':
			self.displayErrorDlg('Transfer Type', 'Sequential')
			return None
		#3. packetSize
		content = self.packetSize_text.GetLineText(0)
		try:
			threadRunObj._packetSize = packetSize = int(content)
			if threadRunObj._packetSize <= 0 or threadRunObj._packetSize > 27:
				self.displayErrorDlg('Packet Size', 'dex digital (0, 27]')
				return None
		except:
			self.displayErrorDlg('Packet Size', 'dex digital (0, 27]')
			return None
			
		#4. packet cnt
		content = self.numberOfTrails_text.GetLineText(0)
		try:
			threadRunObj._packetNum = packetSize = int(content)
			if threadRunObj._packetNum <= 0:
				self.displayErrorDlg('Number of Trails ', 'dex digital integer > 0')
				return None
		except:
			self.displayErrorDlg('Number of Trails ', 'dex digital integer > 0')
			return None
			
		#5. connect handle
		content = self.connHandle_combox.GetValue()
		try:
			threadRunObj._connectHandle = int(content, 16)
			if threadRunObj._connectHandle < 0 or threadRunObj._connectHandle > 0xfff:
				self.displayErrorDlg('Connection Handle ', 'hex digital (0, 0xfff)')
		except:
			self.displayErrorDlg('Connection Handle ', 'hex digital (0, 0xfff)')
			return None
		
		#6. bc flag
		index = self.bcFlag_choice.GetSelection()
		content = self.bcFlag_choice.GetString(index) 
		if content == broadcastFlagList[0]:
			threadRunObj._bcFlag = 0x0
		elif content == broadcastFlagList[1]:
			threadRunObj._bcFlag = 0x1
		else:
			self.displayErrorDlg('Connection Handle ', '<%s> <%s>' % (broadcastFlagList[0], broadcastFlagList[1]))
			return None
		#7. pb flag
		index = self.pbFlag_choice.GetSelection()
		content = self.pbFlag_choice.GetString(index) 
		if content == pbFlagList[0]: #non
			threadRunObj._pbFlag = 0x0
		elif content == pbFlagList[1]: #auto
			threadRunObj._pbFlag = 0x3
		else:
			self.displayErrorDlg('Connection Handle ', '<%s> <%s>' % (pbFlagList[0], pbFlagList[1]))
			return None
		return threadRunObj
		
	def setSendingStatus(self):
		self.linkType_choice.Disable()
		self.transferType_choice.Disable()
		self.packetSize_text.Disable()
		self.numberOfTrails_text.Disable()
		self.connHandle_combox.Disable()
		self.bcFlag_choice.Disable()
		self.pbFlag_choice.Disable()
		self._startTxButton.Disable()
		
		self._cancelTxButton.Enable()
		pass
		
	def restoreBeforeSendStatus(self):
		self.linkType_choice.Enable()
		self.transferType_choice.Enable()
		self.packetSize_text.Enable()
		self.numberOfTrails_text.Enable()
		self.connHandle_combox.Enable()
		self.bcFlag_choice.Enable()
		self.pbFlag_choice.Enable()
		self._startTxButton.Enable()
		
		self._cancelTxButton.Disable()
		pass
		
	def sendAclData(self, evt):
		
		self.treadCloseFlag = False
		#1. get input
		threadRunObj = self.getInput()
		if threadRunObj == None:
			return
		threadRunObj._allDataLen = threadRunObj._packetSize * threadRunObj._packetNum
		#2. make header
		threadRunObj._headerStrList.append(hex(2)) #ACL
		header_temp = threadRunObj._connectHandle & 0xfff
		header_temp |= (threadRunObj._pbFlag & 0x3) << 12
		header_temp |= (threadRunObj._bcFlag & 0x3) << 14
		
		threadRunObj._headerStrList.append(hex(header_temp & 0xff)) 		#
		threadRunObj._headerStrList.append(hex((header_temp >> 8)& 0xff)) #
		
		threadRunObj._headerStrList.append(hex(threadRunObj._packetSize & 0xff))
		threadRunObj._headerStrList.append(hex((threadRunObj._packetSize >> 8) & 0xff))
		#3. make first packet
		threadRunObj._firstPacketList = threadRunObj._headerStrList[0:3]
		threadRunObj._firstPacketList.append(hex(7 & 0xff))
		threadRunObj._firstPacketList.append(hex((7 >> 8) & 0xff))	#len
		
		#1B 2B packet_size 4B packet_cnt
		
		threadRunObj._firstPacketList.append(hex(0))
		
		threadRunObj._firstPacketList.append(hex(threadRunObj._packetSize & 0xff))
		threadRunObj._firstPacketList.append(hex((threadRunObj._packetSize >> 8) & 0xff))
		
		threadRunObj._firstPacketList.append(hex((threadRunObj._packetNum >> 0) & 0xff))
		threadRunObj._firstPacketList.append(hex((threadRunObj._packetNum >> 8) & 0xff))
		threadRunObj._firstPacketList.append(hex((threadRunObj._packetNum >> 16) & 0xff))
		threadRunObj._firstPacketList.append(hex((threadRunObj._packetNum >> 24) & 0xff))
		
		self.setSendingStatus()
		#4. start thread
		self._sendAclThreadObj = threading.Thread(target = self.thread_acl_send, args = (threadRunObj,))

		self._sendAclThreadObj.start()
		pass
		
	def thread_acl_send(self, aclSendArgObj):
		hasBeenSendPacketCnt = 0
		#self._mainArgObj._parserToAclCommunicateObj = self._mainArgObj._parserToAclCommunicateObj
		uartObj = self._mainArgObj._uartApiObj
		#print "self._mainArgObj._parserToAclCommunicateObj._aclBufferCount:",self._mainArgObj._parserToAclCommunicateObj._aclBufferCount
		curCouldSendCnt = self._mainArgObj._parserToAclCommunicateObj._aclBufferCount
	
		if curCouldSendCnt > aclSendArgObj._packetNum:
			curCouldSendCnt = aclSendArgObj._packetNum
		
		#do some clean work
		hasFoundHandle = False
		self._mainArgObj._parserToAclCommunicateObj._lock.acquire()
		for i in range(len(self._mainArgObj._parserToAclCommunicateObj._connectHandlesList)):
			if aclSendArgObj._connectHandle == self._mainArgObj._parserToAclCommunicateObj._connectHandlesList[i]:
				self._mainArgObj._parserToAclCommunicateObj._connectHandlesCompleteLists[i] = 0
				break
		self._mainArgObj._parserToAclCommunicateObj._completeNum = 0	
		self._mainArgObj._parserToAclCommunicateObj._lock.release()
		
		#send first packet include size and other infos
		curCouldSendCnt -=1
		tempDataObj = comm_cls.HCI_QUEUE_DATA_LIST_CLASS()
		tempDataObj._time = get_time_stamp()
		tempDataObj._dataList = aclSendArgObj._firstPacketList
		self._mainArgObj._data_2_parser_queue_lock.acquire()
		self._mainArgObj._recv_2_parser_queue.put(tempDataObj)
		self._mainArgObj._data_2_parser_queue_lock.release()
		
		uartObj.uartSend(tempDataObj._dataList)
		
		
		#do setting
		self.setRange(aclSendArgObj._packetNum)
		dataValue = 0
		transferSize = 0
		startTime = time.clock()
		#print "curCouldSendCnt:",curCouldSendCnt
		while hasBeenSendPacketCnt < aclSendArgObj._packetNum and self.treadCloseFlag == False:
			#1. send data
			#print "send....."
			
			self._mainArgObj._parserToAclCommunicateObj._lock.acquire()
			self._mainArgObj._parserToAclCommunicateObj._ack = False
			self._mainArgObj._parserToAclCommunicateObj._lock.release()
			if curCouldSendCnt > aclSendArgObj._packetNum - hasBeenSendPacketCnt:
				curCouldSendCnt = aclSendArgObj._packetNum - hasBeenSendPacketCnt
			#print "curCouldSendCnt:",curCouldSendCnt
			
			for i in range(curCouldSendCnt):
				#1.1 fill data
				curPayloadList = []
				for j in range(aclSendArgObj._packetSize):
					if dataValue >= 255:
						dataValue = 0
					curPayloadList.append(hex(dataValue))
					dataValue += 1
				#1.2 uart send data
				tempDataObj = comm_cls.HCI_QUEUE_DATA_LIST_CLASS()
				tempDataObj._time = get_time_stamp()
				tempDataObj._dataList = aclSendArgObj._headerStrList + curPayloadList
				self._mainArgObj._data_2_parser_queue_lock.acquire()
				self._mainArgObj._recv_2_parser_queue.put(tempDataObj)
				self._mainArgObj._data_2_parser_queue_lock.release()
				
				uartObj.uartSend(tempDataObj._dataList)
				hasBeenSendPacketCnt += 1
				transferSize += aclSendArgObj._packetSize
			curCouldSendCnt = 0
			#set gauge
			self.setCurrentValue(hasBeenSendPacketCnt)
			#set rate
			currentTime = time.clock()
			rateStr = "%.2f" % (transferSize * 8 /float(currentTime - startTime))
			self.setTransferRateStr(rateStr)
			self.setTransferSize(transferSize)
			
			#2. wait ack and update curCouldSendCnt
			while self.treadCloseFlag == False:
				self._mainArgObj._parserToAclCommunicateObj._lock.acquire()
				if self._mainArgObj._parserToAclCommunicateObj._ack == True:
					curCouldSendCnt = self._mainArgObj._parserToAclCommunicateObj._completeNum
					self._mainArgObj._parserToAclCommunicateObj._completeNum = 0	
					self._mainArgObj._parserToAclCommunicateObj._lock.release()
					break
				self._mainArgObj._parserToAclCommunicateObj._lock.release()
			
		print "thread_acl_send quit"
		self.restoreBeforeSendStatus()
		pass
		
	def thread_acl_recv(self):
		print "thread_acl_recv"
	

		