import sys,json,serial

class UART_CONFIG_CLASS(object):
	def __init__(self):
		self._port = ''  #False
		self._baudrate = 115200
		self._parity = 'N'
		self._flowctl = 0
		self._stopbits = 1
		self._timeout = 2 #fixed

class uartOprClass:

	def __init__(self):
		self._serial_p = serial.Serial()
		
		
	def uartConnect(self, uartParaObj):
		self._serial_p.port = uartParaObj._port
		self._serial_p.baudrate = uartParaObj._baudrate
		self._serial_p.timeout = uartParaObj._timeout
		self._serial_p.stopbits = uartParaObj._stopbits
		self._serial_p.parity = uartParaObj._parity
		try:
			self._serial_p.open()
		except:
			#has been open
			return
	#true ok, false not ok
	def uartOk(self):
		try:
			return self._serial_p.isOpen()
		except:
			#self._serial_p.close()
			#self._serial_p.isOpen()
			return False
			
	def uartClose(self):
		try:
			if self._uart_is_ok() == False:
				self._serial_p.close()
		except:
			#print "do nothing"
			self._serial_p = serial.Serial()
			
	#dataLists shoule be format ['0x1','0x2']
	#return [status]
	def uartSend(self, dataLists):
		sendAssciStr = ''
		if self._serial_p.isOpen() == False:
			print "Uart is not available"
			return False
		try:
			for i in range(len(dataLists)):
				sendAssciStr += chr(int(dataLists[i], 16))
		except:
			print "Error input format."
			return False
			
		try:	
			self._serial_p.write(sendAssciStr)
		except:
			print "Error to write data to uart, please check the data format."
			return False
				
		return True
	
	#return dataLists from uart
	#[dataLists] or None
	def uartRecv(self):
		dataLists = []
		if self._serial_p.isOpen() == False:
			print "Uart is not available"
			return None
		try:
			firstList = self._serial_p.read(1)
		except:
			#print "Serial port is could not be read_1, please be check."
			return None
		if len(firstList) == 0:
			return None
			
		dataLists.append(hex(ord(firstList[0])))
		if self._serial_p == None:
			return None
			
		try:	
			n = self._serial_p.inWaiting()
		except:
			return None
		if n > 0:
			try:
				secondList = self._serial_p.read(n)
			except:
				print "Serial port is could not be read_2, please be check."
				return None
				
			for i in range(len(secondList)):
				dataLists.append(hex(ord(secondList[i])))
		return dataLists

#end_class


"""
		
paraObj = UART_CONFIG_CLASS()
paraObj._port = 'COM4'
uartObj = uartOprClass()
uartObj.uartConnect(paraObj)
uartObj.uartSend(['0x01', '0x03', '0x0c', '0x00'])
datalist = uartObj.uartRecv()
print datalist
"""