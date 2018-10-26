import sys,os,time,binascii,json
import includes.ble_common_class as comm_cls
#import ble_load_data as load_func



class Ble_eventParser:
	def getParserResult(self):
		return self._outArrayList
		
	def __init__(self, cmdList, retParaList, eventList):
		self._outPacketType = -1
		self._outArrayList = []
		#eventCode = -1
		self._cmdList = cmdList
		self._evtList = eventList
		self._retParaList = retParaList
		self._curEvent = None
		self._headerList = []
		self._payloadList = []
	
	
	
	def preprocess(self, inStrList):
		headerLen = 4		#for cmd
		type = int(inStrList[0], 16) & 0xff
		self._outPacketType = type
		if type == 1:
			headerLen = 4
		elif type == 2:
			headerLen = 5
			self._outArrayList.append(['Packet Type', 'Event Packet'])
		
		elif type == 4:
			headerLen = 3
			self._outArrayList.append(['Packet Type', 'Event Packet'])
		
		else:	
			print "Error message"
			return False
		self._headerList = inStrList[0:headerLen]
		self._payloadList = inStrList[headerLen:]
		return True
		
	def getMessageLog(self, timeStr, direction, inStrList):
		messageList = []
		typeStr, dirStr, headerStr, payloadStr = '','','',''	
		ret = self.preprocess(inStrList)
		if ret != True:
			print "Error to preprocess"
			return []
		type = self._outPacketType
		headerStr = " ".join(self._headerList)
		payloadStr = " ".join(self._payloadList)
			
		
		if type == 1:
			typeStr = 'Command'
			dirStr = '[TX] --->'
			
			
		elif type == 4:
			typeStr = 'Event'
			dirStr = '[RX] <---'
			
		elif type == 2:
			#print "direction:",direction
			typeStr = 'ACL'
			dirStr = '[TX] --->'
			if direction == 1:
				dirStr = '[RX] <---'
		else:
			typeStr = 'Unknown Type'
			dirStr = '<--->'
			payloadStr = " ".join(inStrList)
			
		
		messageList = [timeStr, typeStr, dirStr, headerStr, payloadStr]
		return messageList
	
	def getMessagePaserResultByGui(self, headerList, payloadList):
		self._outArrayList = [[' ', ' ']]
		inStrList = headerList + payloadList
		return self.getMessagePaserResult(inStrList)
			
	def getMessagePaserResult(self, inStrList):
		self._outArrayList = [[' ', ' ']]
		ret = self.preprocess(inStrList)
		if ret != True:
			print "Error to preprocess"
			return
		
		type = self._outPacketType 	
		if type == 1:
			hasFoundCmd = False
			oprCode = int(self._headerList[1], 16) & 0xff
			oprCode |= ((int(self._headerList[2], 16) & 0xff) << 8)
			self._outArrayList.append(['Packet Type','Command Packet'])
			#print "self._cmdList, len:", len(self._cmdList)
			for cmd in self._cmdList:
				if oprCode == cmd._oprCode:
					hasFoundCmd = True
					break
			if hasFoundCmd == True:
				self._outArrayList.append(['Command Opcode','%#.4x --> %s --> OGF: %#.2x OCF: %#.3x' % (cmd._oprCode, cmd._name, cmd._ogf, cmd._ocf)])
				paraLen = int(self._headerList[3], 16) & 0xff
				self._outArrayList.append(['Parameter Total Length', '%#.2x'%paraLen])
						
				offset = 0
				for i in range(len(cmd._paraSizeLists)):
					if cmd._paraFixLenFlagLists[i] == 0:
						self._outArrayList.append(['%s'%cmd._paraNameLists[i], '%s'%' '.join(self._payloadList[offset:])])
						offset += len(self._payloadList[offset:])
					elif cmd._paraFixLenFlagLists[i] == 1:
						valueStr = ''
						curItemSize = cmd._paraSizeLists[i]
						for j in range(curItemSize):
							valueStr += '%#.2x ' % int(self._payloadList[offset + curItemSize - j -1], 16)
						self._outArrayList.append(['%s'%cmd._paraNameLists[i], '%s'%valueStr])
						offset += curItemSize
					
			else:
				self._outArrayList.append(['Command Opcode','unknown Oprcode %#.4x' % (oprCode)])
			
			
				
			#for i in range(len(_paraSizeLists))
				
		elif type == 2:
			self._outArrayList.append(['Packet Type','ACL Data Packet'])
			connectHandle = int(self._headerList[1], 16)
			connectHandle |= ((int(self._headerList[2], 16) & 0xf) << 8)
			pb_flag = (int(self._headerList[2], 16) >> 4) & 0x3
			bc_flag = (int(self._headerList[2], 16) >> 6) & 0x3
			acl_len = int(self._headerList[3], 16)
			acl_len |= ((int(self._headerList[4], 16) & 0xff) << 8)
			self._outArrayList.append(['Connection Handle', "%#.3x" %connectHandle])
			self._outArrayList.append(['PacketBoundary Flag', "%#.2x" %pb_flag])
			self._outArrayList.append(['BroadCast Flag', "%#.2x" %bc_flag])
			self._outArrayList.append(['Payload_Length', "%#.4x" %acl_len])
			self._outArrayList.append(['Payload_Data', "%s" %' '.join(self._payloadList)])
			
		elif type == 4:
			self.parse_event()	
		else:
			self._outArrayList.append(['Packet Type','Unknown'])
			self._outArrayList.append(['Packet Header', ' '.join(self._headerList)])
			self._outArrayList.append(['Payload', ' '.join(self._payloadList)])
			#self.paraLogObj.addDetail(self._outArrayList)
		#return self._outArrayList	
		
		return self._outArrayList
		
		
	def parse_event(self):
		eventCode = int(self._headerList[1], 16)
		subEvtCode = int(self._payloadList[0], 16)
		#print "subEvtCode:",subEvtCode
		for i in range(len(self._evtList)):	
			#print "i:",i
			if eventCode == self._evtList[i]._eventCode:
				if eventCode == 0x3e:
					if subEvtCode != self._evtList[i]._subEventCode:
						continue
				
				self._curEvent = self._evtList[i]
				#print "self._curEvent.name:",self._curEvent._name
				self._outArrayList.append(['Event', "%#.2x --> %s" %(eventCode, self._evtList[i]._name)])
				break
		
		if eventCode == 0xf:#connect
			self.parser_connect_status_event()
		
		elif  eventCode == 0x5:	 #disconnect
			self.parser_disconnect_status_event()
			
		elif eventCode == 0xe:
			self.parser_command_complete_event()
		elif eventCode == 0x3e:
			#print "subEvtCode:",subEvtCode
			if subEvtCode == 2:
				self.parser_adv_event(subEvtCode)
			elif subEvtCode == 0x1 or subEvtCode == 0xa:
				self.parser_connect_event(subEvtCode)
			elif subEvtCode == 0xd:
				self.parser_extend_adv_event(subEvtCode)
		elif eventCode == 0x13:
			self.parser_num_complete_packet_evnet()
			
	def parser_num_complete_packet_evnet(self):
		#1. len
		totalLen = int(self._headerList[2], 16)
		self._outArrayList.append(['Parameter Total Length', "%#.2x"%totalLen])
		
		offset = 0
		self._curEvent
		varityLen = 0
		for i in range(len(self._curEvent._paraNameLists)):
			curValueStr = ''
			curLen = self._curEvent._paraSizeLists[i]
			if curLen == 1:
				varityLen = int(self._payloadList[offset], 16)
			if self._curEvent._paraFixLenFlagLists[i] == 0:
				curLen = varityLen
			for j in range(curLen):
				curValueStr += "%s " % hex(int(self._payloadList[offset + curLen - 1 - j], 16))
			self._outArrayList.append(['%s' % self._curEvent._paraNameLists[i], "%s"%curValueStr])
			offset += curLen
		#
		#returnObj = None
		
	def parser_connect_status_event(self):
		#1. len
		totalLen = int(self._headerList[2], 16)
		self._outArrayList.append(['Parameter Total Length', "%#.2x"%totalLen])
		returnObj = None
		
		offset = 0
		#2. status
		status = int(self._payloadList[offset], 16)&0xff
		statusStr = 'Success'
		if status != 0x0:
			statusStr = 'Unknown Cmd'
		self._outArrayList.append(['Status', "%#.2x --> %s"%(status, statusStr)])
		offset += 1
		
		#2. num of packets
		num_hci_cmd_packets = int(self._payloadList[offset], 16)&0xff
		self._outArrayList.append(['Num_HCI_Command_Packets Total Length', "%#.2x"%num_hci_cmd_packets])
		offset += 1
		#3. opcode
		oprCode = int(self._payloadList[offset], 16)&0xff
		oprCode |= ((int(self._payloadList[offset + 1], 16)&0xff) << 8)
		ocf = oprCode & 0x3ff
		ogf = (oprCode >> 10) & 0x3f
		
		
		
		for i in range(len(self._retParaList)):
			if self._retParaList[i]._oprCode == oprCode:
				returnObj = self._retParaList[i]
				break
		if returnObj != None:
			self._outArrayList.append(['Command_Opcode', "%#.4x --> %s "%(oprCode, returnObj._name)])
		else:
			self._outArrayList.append(['Command_Opcode', "%#.4x --> Unknown cmd "%(oprCode)])
	def parser_disconnect_status_event(self):
		#1. len
		totalLen = int(self._headerList[2], 16)
		self._outArrayList.append(['Parameter Total Length', "%#.2x"%totalLen])
		returnObj = None
		
		offset = 0
		#2. status
		status = int(self._payloadList[offset], 16)&0xff
		statusStr = 'Success'
		if status != 0x0:
			statusStr = 'Unknown Cmd'
		self._outArrayList.append(['Status', "%#.2x --> %s"%(status, statusStr)])
		offset += 1
		
		#3. connect handle
		connHandle = int(self._payloadList[offset], 16)&0xff
		connHandle |= ((int(self._payloadList[offset + 1], 16)&0xff) << 8)
		self._outArrayList.append(['Connection_Handle', "%#.4x"%connHandle])
		offset += 2
		
		#4. reason
		reason = int(self._payloadList[offset], 16)&0xff
		reasonStr = 'Connection Timeout'
		if reason != 0x08:
			reasonStr = 'unknown reason'
		self._outArrayList.append(['Reason', "%#.4x --> %s"%(reason, reasonStr)])
			
		
			
	def parser_connect_event(self, subEvtCode):
		#print "connect..."
		dataList = self._headerList + self._payloadList
		offset = 3
		subEvtCode = int(dataList[offset], 16)
		try:
			connnect = comm_cls.HCI_CONNECT_EVENT_CLASS()
			connnect._subEventCode = int(dataList[offset], 16)
			offset += 1
			connnect._status = int(dataList[offset], 16)
			offset += 1
			
			connnect._connectHandle = int(dataList[offset], 16) & 0xff
			connnect._connectHandle |= ((int(dataList[offset + 1], 16) & 0x7) << 8)
			offset += 2
			
			connnect._role = int(dataList[offset], 16)
			offset += 1
			
			connnect._peerAddrType = int(dataList[offset], 16)
			offset += 1
			
			for i in range(6):
				connnect._bdAddr.append(dataList[offset + 5 -i]) #from most to least
			offset += 6
			
			if subEvtCode == 0xa:
				for i in range(6):
					connnect._localRpa.append(dataList[offset + 5 -i]) #from most to least
				offset += 6
				
				for i in range(6):
					connnect._peerRpa.append(dataList[offset + 5 -i]) #from most to least
				offset += 6
				
			connnect._connInterval = int(dataList[offset], 16) & 0xff
			connnect._connInterval |= ((int(dataList[offset + 1], 16) & 0xff) << 8)
			offset += 2
			
			connnect._connLatency = int(dataList[offset], 16) & 0xff
			connnect._connLatency |= ((int(dataList[offset + 1], 16) & 0xff) << 8)
			offset += 2
			
			connnect._timeout = int(dataList[offset], 16) & 0xff
			connnect._timeout |= ((int(dataList[offset+1], 16) & 0xff) << 8)
			offset += 2
			
			connnect._masterClkAccuracy = int(dataList[offset], 16)
			offset += 1
			
			
			
		except:
			return None
		
		evtObj = None
		for i in range(len(self._evtList)):
			if self._evtList[i]._subEventCode == 0x1 or self._evtList[i]._subEventCode == 0xa:
				evtObj = self._evtList[i]
				break
		if evtObj == None:
			return None
		self._outArrayList.append(['Parameter Total Length', '%s'%' '.join(self._headerList[2:3])])
		offset = 0
		for i in range(len(evtObj._paraNameLists)):
				valueStr = ''
				curItemSize = evtObj._paraSizeLists[i]
				for j in range(curItemSize):
					valueStr += '%#.2x ' % int(self._payloadList[offset + curItemSize - j -1], 16)
				self._outArrayList.append(['%s'%evtObj._paraNameLists[i], '%s'%valueStr])
				offset += curItemSize
			
			
		
		
		return connnect
		
		"""
		for i in range(len(self._connectionList)):
			if connnect._connectHandle == self._connectionList[i]._connectHandle:
				self._connectionList.remove(self._connectionList[i])
				break	#remove the same handle object, may be update
		self._connectionList.append(connnect)
		"""
	def parser_extend_adv_event(self, subEvtCode):
		#1. len
		#print "Enter extend adv..."
		totalLen = int(self._headerList[2], 16)
		self._outArrayList.append(['Parameter Total Length', "%#.2x"%totalLen])
		offset = 0
		#2. sub
		realLen = 0
		for i in range(len(self._curEvent._paraSizeLists)):
			curItemSize = self._curEvent._paraSizeLists[i]
			if self._curEvent._paraSizeLists[i] == 1:
				realLen = int(self._payloadList[offset], 16)	#for variety len item
			if self._curEvent._paraFixLenFlagLists[i] == 0:
				curItemSize = realLen
			valueStr = ''
			for j in range(curItemSize):
				valueStr += "%#.2x "% int(self._payloadList[offset+curItemSize-j-1], 16)
				
			self._outArrayList.append([self._curEvent._paraNameLists[i], "%s"%valueStr])
			offset += curItemSize
			
		
	def parser_adv_event(self, subEvtCode):
		#print "adv....."
		#1. len
		totalLen = int(self._headerList[2], 16)
		self._outArrayList.append(['Parameter Total Length', "%#.2x"%totalLen])
		
		offset = 0
		#2. sub
		realLen = 0
		for i in range(len(self._curEvent._paraSizeLists)):
			curItemSize = self._curEvent._paraSizeLists[i]
			if self._curEvent._paraSizeLists[i] == 1:
				realLen = int(self._payloadList[offset], 16)	#for variety len item
			if self._curEvent._paraFixLenFlagLists[i] == 0:
				curItemSize = realLen
				
			valueStr = ''
			for j in range(curItemSize):
				valueStr += "%#.2x "% int(self._payloadList[offset+curItemSize-j-1], 16)
				
			self._outArrayList.append([self._curEvent._paraNameLists[i], "%s"%valueStr])
			offset += curItemSize
		
	def parser_command_complete_event(self):
		#1. len
		totalLen = int(self._headerList[2], 16)
		self._outArrayList.append(['Parameter Total Length', "%#.2x"%totalLen])
		returnObj = None
		"""
		offset = 0
		for i in range(self._curEvent._paraNameLists):
			valueStr = '0x'
			curItemSize = self._curEvent._paraSizeLists[i]
			isFixed = self._curEvent._paraFixLenFlagLists[i]	#1 for fix, 0 for variety
			
			for i in range(curItemSize):
				valueStr += "%.2x"%int(self._payloadList[offset+curItemSize-i-1])
				
			#if self._curEvent._paraSizeLists > 1:
				 
		"""
		
		offset = 0
		#2. num of packets
		#print "payload:::",self._payloadList
		num_hci_cmd_packets = int(self._payloadList[offset], 16)&0xff
		self._outArrayList.append(['Num_HCI_Command_Packets Total Length', "%#.2x"%num_hci_cmd_packets])
		offset += 1
		#3. opcode
		oprCode = int(self._payloadList[offset], 16)&0xff
		oprCode |= ((int(self._payloadList[offset + 1], 16)&0xff) << 8)
		ocf = oprCode & 0x3ff
		ogf = (oprCode >> 10) & 0x3f
		
		
		if oprCode == 0:
			self._outArrayList.append(['Command_Opcode', "0x0000 --> No Operation --> OGF 0x00 OCF 0x000"])
			return
		
		#print "oprCode hex:", hex(oprCode)
		for i in range(len(self._retParaList)):
			if self._retParaList[i]._oprCode == oprCode:
				returnObj = self._retParaList[i]
				break
		
		
		#print "returnObj:",returnObj
		#print "returnObj.name:",returnObj._name
		#print "returnObj.oprcode:%x"%returnObj._oprCode
		
		self._outArrayList.append(['Command_Opcode', "%#.4x --> %s --> OGF %#.2x OCF %#.3x" % (oprCode, returnObj._name, ogf, ocf)])
		offset += 2
		#5. return parameters
		
			
		if returnObj == None:
			return
		status = int(self._payloadList[3], 16)&0xff
		
		if status == 0:
			for i in range(len(returnObj._paraSizeLists)):
				curItemSize = returnObj._paraSizeLists[i]
				#print "offset:",offset
				#print "curItemSize:",curItemSize
				valueStr = ''
				for j in range(curItemSize):
					valueStr += "%#.2x "% int(self._payloadList[offset+curItemSize-j-1], 16)
				
				self._outArrayList.append([returnObj._paraNameLists[i], "%s"%valueStr])
				offset += curItemSize
		else:
			self._outArrayList.append(['Status', "%#.2x --> Unknown Command"%status])
	def getAdvDeviceList(self, dataList): #adv or extend adv
		#self._evtList = eventList
		subEventCode = int(dataList[3], 16)
		
		#print "subEventCode:",subEventCode
		
		payloadStrList = dataList[3:]
		advOutList = []
		tempStr = ''
		allLen = len(payloadStrList)
		#print "allLen:",allLen
		
		#if subEventCode == 0xd: #extend adv
			
		#	return
		
		#1. bd addr 
		offset = 4
		if subEventCode == 0xd:
			offset += 1
			
		curLen = 6
		if offset + curLen >= allLen - 1:
			return None
		tempStr = ''	
		for i in range(curLen):
			tempStr += "%#.2x " % int(payloadStrList[offset + curLen - i -1], 16)
		advOutList.append(tempStr)
		
		#2. conn handle
		tempStr = ''
		advOutList.append(tempStr)	#empty
		
		#3. adv type
		if subEventCode == 0xd:
			offset = 2
			advType = int(payloadStrList[offset], 16) & 0xff
			advType |= ((int(payloadStrList[offset+1], 16) & 0xff ) << 8)
			tempStr = "%#.2x " % advType
			advOutList.append(tempStr)
		else:
			offset = 2
			tempStr = "%#.2x " % int(payloadStrList[offset], 16)
			advOutList.append(tempStr)
			
		#4. Addr type
		offset = 3
		if subEventCode == 0xd:
			offset += 1
		
		tempStr = "%#.2x " % int(payloadStrList[offset], 16)
		advOutList.append(tempStr)
		
		#5. RSSI
		offset = allLen - 1
		if subEventCode == 0xd:
			offset = 15
		tempStr = "%d " % int(payloadStrList[offset], 16)
		advOutList.append(tempStr)
		
		#6. Role  empty
		tempStr = ''
		advOutList.append(tempStr)
		
		#7 ext adv
		#"""
		tempStr = '0'
		if subEventCode == 0xd:
			tempStr = '1'
		
		advOutList.append(tempStr)
		#"""
		

		return advOutList
		
		
			
		