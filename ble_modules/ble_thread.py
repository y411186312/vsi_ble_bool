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
	
	
#for recv data, divide packet
#output: in-queue a event packet, just one packets 
def thread_recv_data(mainArgObj):
	name = sys._getframe().f_code.co_name
	uartObj = mainArgObj._uartApiObj
	toParserQueue = mainArgObj._recv_2_parser_queue
	ctlObj = mainArgObj._threadCtlObj
	
	remainDataList = []
	#testCount = 0
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
					
					if testCount % 2 == 0:
						helloParserDataObj = comm_cls.HCI_QUEUE_DATA_LIST_CLASS()
						helloParserDataObj._time = get_time_stamp()
						helloParserDataObj._dataList = ['0x4','0x3e','0x13','0x1','0x0','0x1','0x0','0x0',\
						                                '0x0','0xc9','0x2e','0x1f','0xdc','0x8c','0x0c','0x6', \
														'0x0','0x0','0x0','0x0','0x1','0x0' ]
						toParserQueue.put(helloParserDataObj)
					"""
					mainArgObj._data_2_parser_queue_lock.release()
					offset += (curLen + 3)
					continue
				else:
					remainDataList = recvDataList[offset:]
					break
			elif packetType == 0x02:
				try:
					curLen = int(recvDataList[offset + 3], 16) & 0xff
					curLen |= ((int(recvDataList[offset + 4], 16) &0xff) << 8)
				except:
					remainDataList = recvDataList[offset:]
					break
				
				if (offset + curLen + 5) <=  allLen:
					toParserDataObj._dataList = recvDataList[offset:offset + curLen + 3]
					toParserQueue.put(toParserDataObj)
					
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
	while ctlObj._needQuit != True:
		
		try:
			dataRecvList = data_from_queue.get(block=True, timeout=2)
			if isinstance(dataRecvList, comm_cls.HCI_QUEUE_DATA_LIST_CLASS) == True:
				packetType = int(dataRecvList._dataList[0], 16)
				if packetType == 0x4:
					eventCode = int(dataRecvList._dataList[1], 16)
					subEvtCode = int(dataRecvList._dataList[3], 16)
					if eventCode == 0x3e and subEvtCode == 0x02:
						advMsgQueue.put(dataRecvList)
					else:
						nonAdvMsgQueue.put(dataRecvList)
				else:
					nonAdvMsgQueue.put(dataRecvList)
			else:
				print "error to get data from uart recv thread...."
				continue
		
		except:
			if advMsgQueue.qsize() == 0:
				continue
			#else:
			#	print "process adv event................."
		qsize = data_from_queue.qsize()
		for i in range(qsize):
			dataRecvList = data_from_queue.get()
			if isinstance(dataRecvList, comm_cls.HCI_QUEUE_DATA_LIST_CLASS) == True:
				packetType = int(dataRecvList._dataList[0], 16)
				if packetType == 0x4:
					eventCode = int(dataRecvList._dataList[1], 16)
					subEvtCode = int(dataRecvList._dataList[3], 16)
					if eventCode == 0x3e and subEvtCode == 0x02:
						advMsgQueue.put(dataRecvList)
					else:
						nonAdvMsgQueue.put(dataRecvList)
				else:
					nonAdvMsgQueue.put(dataRecvList)
			else:
				print "error to get data from uart recv thread...."
				continue
			
		#print "thread_parse_data falg1"
		#2. process all non-adv
		qsize = nonAdvMsgQueue.qsize()
		for i in range(qsize):
			#print "thread_parse_data falg1.2"
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
				"""	
				if packetType == 1:	###reset
					oprCode = int(temMsgObj._dataList[1], 16) & 0xff
					oprCode |= ((int(temMsgObj._dataList[2], 16) & 0xff) << 8)
					if oprCode == 0x0c03:
						advMsgQueue.queue.clear()
						mainArgObj._advDeviceListObj.clearAllAdv()
						mainArgObj._connectionList = []
						mainArgObj._advDeviceBdaddrList = []
					elif oprCode == 0x1009: #read_bd_addr
						offset = 5
						mainArgObj._bdAddrList = []
						bdStr = ''
						for i in range(6):
							bdStr += "%.2x "%int(temMsgObj._dataList[offset + 6 -i -1], 16)
							mainArgObj._bdAddrList.append(temMsgObj._dataList[offset + 6 -i -1])
						print "mainArgObj:",mainArgObj._bdAddrList
						mainArgObj._statusBarObj.setBdaddr(bdStr)
				"""		
				if packetType == 4 and eventCode == 0xf: #connect status
					statusArrayList = mainArgObj._parserObj.getMessagePaserResult(temMsgObj._dataList)
					#print "statusArrayList:",statusArrayList
					mainArgObj._displayStatusObj.addDetail(statusArrayList)
				
				elif packetType == 4 and eventCode == 0x5: #disconnect status
					#print "enter disconnect...."
					statusArrayList = mainArgObj._parserObj.getMessagePaserResult(temMsgObj._dataList)
					#print "statusArrayList:",statusArrayList
					mainArgObj._displayStatusObj.addDetail(statusArrayList)
					connectHandle = int(temMsgObj._dataList[4], 16) & 0xff
					connectHandle |= ((int(temMsgObj._dataList[5], 16) & 0xff )<< 8)
					connectItem = None
					for i in range(len(mainArgObj._connectionList)):
						#print "_connectionList[%d].handle=%d" % (i, mainArgObj._connectionList[i]._connectHandle)
						if connectHandle == mainArgObj._connectionList[i]._connectHandle:
							#print "remove connect handle..."
							connectItem = mainArgObj._connectionList[i]
							mainArgObj._connectionList.remove(mainArgObj._connectionList[i])
							break
							
					#mainArgObj._connectionList.append(connectItem)
					if connectItem != None:
						mainArgObj._advDeviceListObj.markAdvDevOff(connectItem._bdAddr, connectItem._connectHandle, connectItem._role)
						
				
				elif packetType == 4 and eventCode == 0xe:
					
					#special process
					oprCode = int(temMsgObj._dataList[4], 16) & 0xff
					oprCode |= ((int(temMsgObj._dataList[5], 16) & 0xff) << 8)
					if oprCode == 0x0c03:
						advMsgQueue.queue.clear()
						mainArgObj._advDeviceListObj.clearAllAdv()
						mainArgObj._connectionList = []
						mainArgObj._advDeviceBdaddrList = []
					elif oprCode == 0x1009: #read_bd_addr
						status = int(temMsgObj._dataList[6], 16)
						if status == 0:
						
							offset = 7 #refer to spec doc
							mainArgObj._bdAddrList = []
							bdStr = ''
							for i in range(6):
								bdStr += "%.2x "%int(temMsgObj._dataList[offset + 6 -i -1], 16)
								mainArgObj._bdAddrList.append(temMsgObj._dataList[offset + 6 -i -1])
							#print "mainArgObj:",mainArgObj._bdAddrList
							#print "temMsgObj._dataList:",temMsgObj._dataList
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
					
				#connect or enhanced connect	
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
						#print "add connect device"
		
		#3.	process adv
		if advMsgQueue.qsize() > 0:
			temMsgObj = advMsgQueue.get()
			packetType = int(temMsgObj._dataList[0], 16)
			eventCode = int(temMsgObj._dataList[1], 16)
			messageLogList =  mainArgObj._parserObj.getMessageLog(temMsgObj._time, \
				                                                      temMsgObj._direction, \
																	  temMsgObj._dataList)
			mainArgObj._messsageLogObj.addMessage_new(messageLogList)
			
			if packetType == 4 and mainArgObj._mainPageStatusFilter == False:
				#add parser result to cmd status interface
				statusParserList = mainArgObj._parserObj.getMessagePaserResult(temMsgObj._dataList)
				mainArgObj._displayStatusObj.addDetail(statusParserList)
			
			
			advDevList = mainArgObj._parserObj.getAdvDeviceList(temMsgObj._dataList)
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
			#"""			
		
	print "Thread < %s > quit..." % name
	pass
	
		
