import os,threading,time,sys,Queue
import ble_modules.ble_parser as parser
import includes.ble_common_class as comm_cls

def get_time_stamp():
    ct = time.time()
    local_time = time.localtime(ct)
    data_head = time.strftime("%H:%M:%S", local_time)
    data_secs = (ct - int(ct)) * 1000
    time_stamp = "%s.%03d" % (data_head, data_secs)
    return time_stamp
	
def isAclHeader(dataList):
	packetType = int(dataList[0], 16)
	curPayLoadList = dataList[5:]
	
	if len(dataList) != 12 or packetType != 2:
		return False
	
	matchCondtion = 0
	shouldBeValue = int(curPayLoadList[0], 16)
	for i in range(len(curPayLoadList)):
		curValue = int(curPayLoadList[i], 16)
		if curValue == shouldBeValue:
			matchCondtion += 1
		if shouldBeValue >= 0xff:
			shouldBeValue = 0
		else:
			shouldBeValue += 1
	if matchCondtion == 7:
		return False
	else:
	
		return True
	
#for recv data, divide packet
#output: in-queue a event packet, just one packets 
def thread_recv_data(mainArgObj):
	name = sys._getframe().f_code.co_name
	uartObj = mainArgObj._uartApiObj
	toParserQueue = mainArgObj._recv_2_parser_queue
	ctlObj = mainArgObj._threadCtlObj
	
	remainDataList = []
	testCount = 0
	while ctlObj._needQuit != True:
		
		if uartObj.uartOk() != True:
			time.sleep(1)
			continue
		
					
		recvDataList = uartObj.uartRecv()
		if recvDataList == None:	#no data been read
			continue
		else:
			recvDataList = remainDataList + recvDataList
			remainDataList = []
		#check packet is insanity, get remainDataList
		allLen = len(recvDataList)
		offset = 0
		while offset < allLen:
			packetType = int(recvDataList[offset], 16)
			
			toParserDataObj = comm_cls.HCI_QUEUE_DATA_LIST_CLASS()
			toParserDataObj._time = get_time_stamp()
			toParserDataObj._direction = 1
			
			if packetType == 0x04:
				
				try:
					curLen = int(recvDataList[offset + 2], 16)
				except:
					remainDataList = recvDataList[offset:]
					break
					
				if (offset + curLen + 3) <=  allLen:
					toParserDataObj._dataList = recvDataList[offset:offset + curLen + 3]
					#print "put queue"
					mainArgObj._data_2_parser_queue_lock.acquire()
					toParserQueue.put(toParserDataObj)
					"""
					testCount += 1
					
					if testCount % 5 == 0:
						helloParserDataObj = comm_cls.HCI_QUEUE_DATA_LIST_CLASS()
						helloParserDataObj._time = get_time_stamp()
						#helloParserDataObj._dataList = ['0x4','0x3e','0x13','0x1','0x0','0x1','0x0','0x0',\
						#                                '0x0','0xc9','0x2e','0x1f','0xdc','0x8c','0x0c','0x6', \
						#								'0x0','0x0','0x0','0x0','0x1','0x0' ]
						helloParserDataObj._dataList = ['0x4', '0x3e', '0x1a', '0xd', '0x1', '0x22', '0x0', '0x0', '0x0', '0x0', '0x0', '0x0', '0x0', '0x0', '0x0', '0x0', '0x0', '0x0', '0x9c', '0x0', '0x0', '0x0', '0x0', '0x0', '0x0', '0x0', '0x0', '0x0', '0x0']
						toParserQueue.put(helloParserDataObj)
						#print "send extend adv...."
					"""
					mainArgObj._data_2_parser_queue_lock.release()
					offset += (curLen + 3)
					continue
				else:
					remainDataList = recvDataList[offset:]
					break
			elif packetType == 0x02:
				#print "recvDataList:",recvDataList
				try:
					curLen = int(recvDataList[offset + 3], 16) & 0xff
					curLen |= ((int(recvDataList[offset + 4], 16) &0xff) << 8)
				except:
					remainDataList = recvDataList[offset:]
					break
				
				if (offset + curLen + 5) <=  allLen:
					toParserDataObj._dataList = recvDataList[offset:offset + curLen + 5]
					#print "put......"
					mainArgObj._data_2_parser_queue_lock.acquire()
					toParserQueue.put(toParserDataObj)
					mainArgObj._data_2_parser_queue_lock.release()
					offset += (curLen + 5)
					continue
				else:
					remainDataList = recvDataList[offset:]
					break
			else:
				break
	print "Thread < %s > quit..." % name
	pass

		
#parser packet from recv thread, put to main thread to display cmd result, socket send to display event.
def thread_parse_data(mainArgObj):
	data_from_queue = mainArgObj._recv_2_parser_queue
	ctlObj = mainArgObj._threadCtlObj
	name = sys._getframe().f_code.co_name
	advMsgQueue = Queue.Queue()
	nonAdvMsgQueue = Queue.Queue()
	recvCalcAclObj =  comm_cls.HCI_ACL_THREAD_RUN_CLASS()
	
	
	while ctlObj._needQuit != True:
		hasNonAdvQueue = False
		#"""
		try:
			dataRecvList = data_from_queue.get(block=True, timeout=2)
			#print "subEvtCode::::", int(dataRecvList._dataList[3], 16)
			if isinstance(dataRecvList, comm_cls.HCI_QUEUE_DATA_LIST_CLASS) == True:
				packetType = int(dataRecvList._dataList[0], 16)
				if packetType == 0x4:
					eventCode = int(dataRecvList._dataList[1], 16)
					subEvtCode = int(dataRecvList._dataList[3], 16)
					#print "subEvtCode:",subEvtCode
					if eventCode == 0x3e and (subEvtCode == 0x02 or subEvtCode == 0xd): #adv or extend adv
						advMsgQueue.put(dataRecvList)
					else:
						nonAdvMsgQueue.put(dataRecvList)
						hasNonAdvQueue = True
				else:
					nonAdvMsgQueue.put(dataRecvList)
					hasNonAdvQueue = True
			else:
				print "error to get data from uart recv thread...."
				continue
		
		except:
			if advMsgQueue.qsize() == 0:
				continue
			#else:
			#	print "process adv event................."
		"""
		qsize = data_from_queue.qsize()
		for i in range(qsize):
			dataRecvList = data_from_queue.get()
			if isinstance(dataRecvList, comm_cls.HCI_QUEUE_DATA_LIST_CLASS) == True:
				packetType = int(dataRecvList._dataList[0], 16)
				if packetType == 0x4:
					eventCode = int(dataRecvList._dataList[1], 16)
					subEvtCode = int(dataRecvList._dataList[3], 16)
					if eventCode == 0x3e and (subEvtCode == 0x02 or subEvtCode == 0xd):
						advMsgQueue.put(dataRecvList)
					else:
						nonAdvMsgQueue.put(dataRecvList)
				else:
					nonAdvMsgQueue.put(dataRecvList)
			else:
				print "error to get data from uart recv thread...."
				continue
		"""
		#2. process all non-adv
		qsize = nonAdvMsgQueue.qsize()
		for i in range(qsize):
			temMsgObj = nonAdvMsgQueue.get()
			packetType = int(temMsgObj._dataList[0], 16)
			eventCode = int(temMsgObj._dataList[1], 16)
			if mainArgObj._parserObj != None:
				#2.1 add message log
				messageLogList =  mainArgObj._parserObj.getMessageLog(temMsgObj._time, \
				                                                      temMsgObj._direction, \
																	  temMsgObj._dataList)
				mainArgObj._messsageLogObj.addMessage_new(messageLogList)
				if packetType == 4 and mainArgObj._mainPageStatusFilter == False:
					#add parser result to cmd status interface
					statusParserList = mainArgObj._parserObj.getMessagePaserResult(temMsgObj._dataList)
					mainArgObj._displayStatusObj.addDetail(statusParserList)
					
				#2.2 add cmd status to display
				subEvtCode = int(dataRecvList._dataList[3], 16)
					
				if packetType == 4 and eventCode == 0xf: #connect status
					statusArrayList = mainArgObj._parserObj.getMessagePaserResult(temMsgObj._dataList)
					mainArgObj._displayStatusObj.addDetail(statusArrayList)
				
				elif packetType == 4 and eventCode == 0x5: #disconnect status
					statusArrayList = mainArgObj._parserObj.getMessagePaserResult(temMsgObj._dataList)
					mainArgObj._displayStatusObj.addDetail(statusArrayList)
					connectHandle = int(temMsgObj._dataList[4], 16) & 0xff
					connectHandle |= ((int(temMsgObj._dataList[5], 16) & 0xff )<< 8)
					connectItem = None
					for i in range(len(mainArgObj._connectionList)):
						if connectHandle == mainArgObj._connectionList[i]._connectHandle:
							connectItem = mainArgObj._connectionList[i]
							mainArgObj._connectionList.remove(mainArgObj._connectionList[i])
							break
							
					if connectItem != None:
						mainArgObj._advDeviceListObj.markAdvDevOff(connectItem._bdAddr, connectItem._connectHandle, connectItem._role)
				elif packetType == 4 and eventCode == 0x13: #acl ack. Number_of_Complete_Packets
					payloadLen = int(temMsgObj._dataList[2], 16) & 0xff
					numOfHandle = int(temMsgObj._dataList[3], 16) & 0xff
					handleOffset = 4
					allCompleteNum = 0
					numOfCompleteOffset = handleOffset + numOfHandle *2
					numOfCompleteList = [0]*numOfHandle
					handleList = [0]*numOfHandle
					#foundExistHandleFlagList = [False] *numOfHandle
					for i in range(numOfHandle):
						handleList[i] = int(temMsgObj._dataList[handleOffset + i *2], 16) & 0xff
						handleList[i] |= ((int(temMsgObj._dataList[handleOffset + i *2 + 1], 16) & 0xf) << 8)
						
						numOfCompleteList[i] = int(temMsgObj._dataList[numOfCompleteOffset + i *2], 16) & 0xff
						numOfCompleteList[i] |= ((int(temMsgObj._dataList[numOfCompleteOffset + i *2 + 1], 16) & 0xf) << 8)
						
						
					mainArgObj._parserToAclCommunicateObj._lock.acquire()
					hasFoundConnectHandle = False
					for i in range(numOfHandle):
						#print "numOfCompleteList[%d]:%d" % (i, numOfCompleteList[i])
						for j in range(len(mainArgObj._parserToAclCommunicateObj._connectHandlesList)):
							if mainArgObj._parserToAclCommunicateObj._connectHandlesList[j] == handleList[i]:
								mainArgObj._parserToAclCommunicateObj._connectHandlesCompleteLists[j] += numOfCompleteList[i]
								hasFoundConnectHandle = True
								break
						if hasFoundConnectHandle == False:
							mainArgObj._parserToAclCommunicateObj._connectHandlesList.append(handleList[i])
							mainArgObj._parserToAclCommunicateObj._connectHandlesCompleteLists.append(numOfCompleteList[i])
						mainArgObj._parserToAclCommunicateObj._ack = True
						mainArgObj._parserToAclCommunicateObj._completeNum += numOfCompleteList[i]
						
					mainArgObj._parserToAclCommunicateObj._lock.release()
						
				elif packetType == 4 and eventCode == 0xe: #cmd status
					
					#special process
					oprCode = int(temMsgObj._dataList[4], 16) & 0xff
					oprCode |= ((int(temMsgObj._dataList[5], 16) & 0xff) << 8)
					if oprCode == 0x0c03:
						advMsgQueue.queue.clear()
						mainArgObj._advDeviceListObj.clearAllAdv()
						mainArgObj._connectionList = []
						mainArgObj._advDeviceBdaddrList = []
					elif oprCode == 0x2002: #read_le_buffer_size
						mainArgObj._parserToAclCommunicateObj._aclBufferSize
						mainArgObj._parserToAclCommunicateObj._aclBufferSize = int(temMsgObj._dataList[7], 16) & 0xff
						mainArgObj._parserToAclCommunicateObj._aclBufferSize |= (int(temMsgObj._dataList[8], 16) & 0xff )<< 8 
						mainArgObj._parserToAclCommunicateObj._aclBufferCount = int(temMsgObj._dataList[9], 16) & 0xff
						
					elif oprCode == 0x1009: #read_bd_addr
						status = int(temMsgObj._dataList[6], 16)
						if status == 0:
						
							offset = 7 #refer to spec doc
							mainArgObj._bdAddrList = []
							bdStr = ''
							for i in range(6):
								bdStr += "%.2x "%int(temMsgObj._dataList[offset + 6 -i -1], 16)
								mainArgObj._bdAddrList.append(temMsgObj._dataList[offset + 6 -i -1])
							mainArgObj._statusBarObj.setBdaddr(bdStr)
						
							mainArgObj._deviceInfoPageObj.addAttr2Dev('BdAddr', bdStr)
					elif oprCode == 0x1001:	#local version
						status = int(temMsgObj._dataList[6], 16)
						if status == 0:
							hciVersion = int(temMsgObj._dataList[7], 16)
							hciRevision = int(temMsgObj._dataList[8], 16) & 0xff
							hciRevision |= ((int(temMsgObj._dataList[9], 16) & 0xff) << 8)
							lmpVersion = int(temMsgObj._dataList[10], 16)
							
							manufactureCode = int(temMsgObj._dataList[11], 16) & 0xff
							manufactureCode |= ((int(temMsgObj._dataList[12], 16) & 0xff) << 8)
							
							lmpRevision = int(temMsgObj._dataList[13], 16) & 0xff
							lmpRevision |= ((int(temMsgObj._dataList[14], 16) & 0xff) << 8)
							
							hciVersionName = 'Bluetooth HCI Specification '
							if hciVersion == 0x6:
								hciVersionName += "4.0"
							elif hciVersion == 0x8:
								hciVersionName += "4.2"
							elif hciVersion > 0x8:
								hciVersionName += "4.2+"
								
							mainArgObj._deviceInfoPageObj.addAttr2Dev('Version Info', 'HCI Version --> %s' % hciVersionName)
							mainArgObj._deviceInfoPageObj.addAttr2Dev('Version Info', 'HCI Reversion --> %#.4x' % hciRevision)
							
							lmpVersionName = 'Bluetooth LMP '
							if lmpVersion == 0x6:
								lmpVersionName += "4.0"
							elif lmpVersion == 0x8:
								lmpVersionName += "4.2"
							elif lmpVersion > 0x8:
								lmpVersionName += "4.2+"
								
							mainArgObj._deviceInfoPageObj.addAttr2Dev('Version Info', 'LMP Version --> %s' % lmpVersionName)
							
							mainArgObj._deviceInfoPageObj.addAttr2Dev('Version Info', 'Manufatocture Code --> %#.4x' % manufactureCode)
					#normal process
					statusArrayList = mainArgObj._parserObj.getMessagePaserResult(temMsgObj._dataList)
					mainArgObj._displayStatusObj.addDetail(statusArrayList)
					
				elif packetType == 4 and eventCode == 0x3e and (subEvtCode == 0x1 or subEvtCode == 0x0a):
					#print "get connect............"
					#connect handle
					connectItem = mainArgObj._parserObj.parser_connect_event(temMsgObj._dataList)
					if connectItem != None:
						for i in range(len(mainArgObj._connectionList)):
							if connectItem._connectHandle == mainArgObj._connectionList[i]._connectHandle:
								mainArgObj._connectionList.remove(mainArgObj._connectionList[i])
								break	#remove the same handle object, may be update
						mainArgObj._connectionList.append(connectItem)
						mainArgObj._advDeviceListObj.markAdvDevOn(connectItem._bdAddr, connectItem._connectHandle, connectItem._role, connectItem._peerAddrType)
						
				elif packetType == 2 and temMsgObj._direction == 1 and mainArgObj._aclDataTransferObj != None and mainArgObj._aclGuiHasBeenQuited == False and mainArgObj._aclIsDataTxGui == False: #recv acl
					if isAclHeader(temMsgObj._dataList) == True: #first time, should set range
						
						payLoadList = temMsgObj._dataList[5:]
						recvCalcAclObj._packetSize = ((int(payLoadList[1], 16) & 0xff) << 0)
						recvCalcAclObj._packetSize |= ((int(payLoadList[2], 16) & 0xff) << 8)
						
						recvCalcAclObj._packetNum = ((int(payLoadList[3], 16) & 0xff) << 0)
						recvCalcAclObj._packetNum |= ((int(payLoadList[4], 16) & 0xff) << 8)
						recvCalcAclObj._packetNum |= ((int(payLoadList[5], 16) & 0xff) << 16)
						recvCalcAclObj._packetNum |= ((int(payLoadList[6], 16) & 0xff) << 24)
						
						recvCalcAclObj._curRecvPacketCnt = 0
						recvCalcAclObj._curRecvLen = 0
						recvCalcAclObj._allDataLen = recvCalcAclObj._packetNum * recvCalcAclObj._packetSize
						recvCalcAclObj._startTime =  time.clock()
						recvCalcAclObj._curValueIsValued = True
						mainArgObj._aclRecvHasGotAclHeader = True
						mainArgObj._aclDataTransferObj.setRange(recvCalcAclObj._packetNum)
					else:
						if mainArgObj._aclRecvHasGotAclHeader == True:
							recvCalcAclObj._curRecvPacketCnt += 1
							
							#set gauge
							mainArgObj._aclDataTransferObj.setCurrentValue(recvCalcAclObj._curRecvPacketCnt)
							#set rate
							transferSize = recvCalcAclObj._packetSize * recvCalcAclObj._curRecvPacketCnt #byte
							currentTime = time.clock()
							rateStr = "%.2f" % (transferSize *8/float(currentTime - recvCalcAclObj._startTime))
							mainArgObj._aclDataTransferObj.setTransferRateStr(rateStr)
							mainArgObj._aclDataTransferObj.setTransferSize(transferSize)
							if recvCalcAclObj._curRecvPacketCnt == recvCalcAclObj._packetNum:
								recvCalcAclObj._curRecvPacketCnt = 0
								recvCalcAclObj._curRecvLen = 0	
								recvCalcAclObj._allDataLen = 0
								recvCalcAclObj._packetNum = 0
								recvCalcAclObj._packetSize = 0
								recvCalcAclObj._curValueIsValued = False
								mainArgObj._aclRecvHasGotAclHeader = False
						else:
							curLen = ((int(temMsgObj._dataList[3], 16) & 0xff )<< 0)
							curLen |= ((int(temMsgObj._dataList[4], 16) & 0xff )<< 0)
							recvCalcAclObj._allDataLen += curLen
							mainArgObj._aclDataTransferObj.setSpecialAclRecv(recvCalcAclObj._allDataLen, time.clock())	
							
		#3.	process adv
		advQueueSize = 0
		if hasNonAdvQueue == False and advMsgQueue.qsize() > 0: #if no non-adv then process all adv event
			
			advQueueSize = advMsgQueue.qsize()
		elif advMsgQueue.qsize() > 0:
			advQueueSize = 1
		
		for i in range(advQueueSize):		
			temMsgObj = advMsgQueue.get()
			packetType = int(temMsgObj._dataList[0], 16)
			eventCode = int(temMsgObj._dataList[1], 16)
			subEventCode = int(temMsgObj._dataList[3], 16)
			#print "subEventCode:",subEventCode
			messageLogList =  mainArgObj._parserObj.getMessageLog(temMsgObj._time, \
				                                                      temMsgObj._direction, \
																	  temMsgObj._dataList)
			mainArgObj._messsageLogObj.addMessage_new(messageLogList)
			
			if packetType == 4 and mainArgObj._mainPageStatusFilter == False:
				#add parser result to cmd status interface
				statusParserList = mainArgObj._parserObj.getMessagePaserResult(temMsgObj._dataList)
				mainArgObj._displayStatusObj.addDetail(statusParserList)
			
			#if subEventCode == 0x1:
			advDevList = mainArgObj._parserObj.getAdvDeviceList(temMsgObj._dataList)
			#elif subEventCode == 0x1:
			if advDevList != None:
				
				hasBeenAdded = False
				
				for i in range(len(mainArgObj._advDeviceBdaddrList)):
					#print "advDevList[0]:",advDevList
					if advDevList[0] == mainArgObj._advDeviceBdaddrList[i]:
						#print "found the same thing."
						mainArgObj._advDeviceBdaddrList[i] = advDevList[0]
						mainArgObj._advDeviceBdaddrList.remove(mainArgObj._advDeviceBdaddrList[i])
						#hasBeenAdded = True
						break
						
				#if hasBeenAdded == False:
				#add or update adv list
				mainArgObj._advDeviceListObj.addDevice(advDevList)
				mainArgObj._advDeviceBdaddrList.append(advDevList[0])
						
		
	print "Thread < %s > quit..." % name
	pass
	
		
