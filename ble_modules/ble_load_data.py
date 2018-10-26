import sys,os,time,binascii,json
#sys.path.append(os.getcwd())
import includes.ble_common_class as comm_cls
import ble_modules.ble_cmd_buffer as buf_Cls


#name OGF


event_file_list = [
	"HCI_Events.data"
]
EVENT_DATA_SUFFIX = "_Return_Parameter.data"

packetType = [
	" ",
	"Cmd Packet",
	"ACL Data Packet",
	"Sync Packet",
	"Event Packet"
]


################################################################################## new start ###########
def line_is_empty(line_str):
	if line_str.find("{", 0) < 0:
		return False
	else:
		if line_str.find("}", 1) < 0:
			return False
		else:
			return True

#return [name_x,name_y,name_z],[size_x, size_y,size_z],[1, 1, 1]
def parse_line_cmd_parameter(para_str, count):
	name_list,size_list, fixFlag_List = [], [], []
	err_out = [None, None, None]
	if count <= 0:
		return err_out
	header=tail=0
	for i in range(count):
		#name
		header = para_str.find("\"", tail)
		tail = para_str.find("\"", header + 1)
		if tail < header:
			return err_out
		content = para_str[header+1: tail]
		name = content
		
		#size
		header = para_str.find(",", tail)
		tail = para_str.find(",", header + 1)
		if tail < header:
			return None

		content = para_str[header+1: tail]
		#print "content:",content
		try:
			size = int(content)
		except:
			print "Error %s size." % (name)
			return err_out
		
		#fixLen
		header = para_str.find(",", tail)
		tail = para_str.find(",", header + 1)
		if tail < header:
			return None

		content = para_str[header+1: tail].strip('}')	#skip all tag '}'
		#print "content:",content
		try:
			fixFlag = int(content)
		except:
			print "Error %s size." % (name)
			return err_out
		
		
		name_list.append(name)
		size_list.append(size)
		fixFlag_List.append(fixFlag)
	return [name_list, size_list, fixFlag_List]
	
def parse_line_para(org_str, ogf):
	name = sys._getframe().f_code.co_name
	hci_cmd_obj = comm_cls.HCI_SPEC_CLASS()
	hci_cmd_obj._ogf = ogf
	header=tail=0

	#1. find cmd name
	header = org_str.find("\"", tail)
	tail = org_str.find("\"", header + 1)
	if tail <= header:
		return None
	content = org_str[header+1: tail]
	#print "name:",content
	hci_cmd_obj._name = content.lower()
	#print "cmd:",hci_cmd_obj._cmd
	
	#2. find ocf
	header = org_str.find(",", tail)
	tail = org_str.find(",", header + 1)
	if tail < header:
		return None

	content = org_str[header+1: tail].strip('}')
	#print "content:",content
	try:
		hci_cmd_obj._ocf = int(content, 16)
		#print "ocf:",hci_cmd_obj._ocf
	except:
		print "Error ocf format, cmd:", hci_cmd_obj._name
		return None
	
	hci_cmd_obj._oprCode = (hci_cmd_obj._ocf & 0x3ff) | ((hci_cmd_obj._ogf & 0x3f) << 10)
	
	#3. find paramtere counts
	header = org_str.find(",", tail)
	tail = org_str.find(",", header + 1)
	if tail < header:
		return None
		
	content = org_str[header+1: tail].strip('}')
	try:
		hci_cmd_obj._paraCounts = int(content)
	except:
		print "Error parameters size, cmd:", hci_cmd_obj._name
		return None
	
	if hci_cmd_obj._paraCounts == 0:
		return hci_cmd_obj
	
		
	#4. parse paramteres
	name_list, size_list, fixFlag_list = parse_line_cmd_parameter(org_str[tail:] ,hci_cmd_obj._paraCounts)
	if name_list != None and size_list != None and fixFlag_list != None:
		hci_cmd_obj._paraNameLists = name_list
		hci_cmd_obj._paraSizeLists = size_list
		hci_cmd_obj._paraFixLenFlagLists = fixFlag_list
	else:
		print "Error org_str:",org_str
		return None
	
	return hci_cmd_obj
	
def load_para_from_file(path, ogf):
	cmd_lists_array = []
	try:
		file = open(path)
	except:
		print ("Error to open :", path)
		return None
	lines = file.readlines() #read all lines
	if len(lines) > 0:
		for line in lines:
			if line_is_empty(line) == False:
				continue
			line = line.strip('\n')	# remove the '\n'	
			para_lists = parse_line_para(line, ogf)
			if para_lists == None:
				print "Error on line:", line
				continue
			cmd_lists_array.append(para_lists)
	return cmd_lists_array
	

#cmd file to OGF 
g_cmdFileToOgfArray = [
	["LinkControlCommands.data", 0x1],
	["Link_Policy_Commands.data", 0x2],
	["Controller_Baseband_Commands.data", 0x3],
	["Informational_Parameters_Commands.data", 0x4],
	["Status_Parameters_Commands.data", 0x05],
	["Testing_Commands.data", 0x6],
	["Vendor_Commands.data", 0x3f],
	["LE_Commands.data", 0x8],
]

"""
g_paraFileToOgfArray = [
	["LinkControlCommands.data", 0x1],
	["Link_Policy_Commands.data", 0x2],
	["Controller_Baseband_Commands.data", 0x3],
	["Informational_Parameters_Commands.data", 0x4],
	["Status_Parameters_Commands.data", 0x05],
	["Testing_Commands.data", 0x6],
	["Vendor_Commands.data", 0x3f],
	["LE_Commands.data", 0x8],
]
"""
class Ble_LoadCmdClass: 
	def __init__(self, cmdSpecFolder, bleSubEventCodeJsonFilePath, cmdDefaultFilePath):
		self._cmdsList = []
		self._returnParaList = []
		self._eventsList = []
		#self._cmdBufferDefault_dic = {}
		
		self._subEventJsonObj = None
		self._cmdSpecFolder = cmdSpecFolder
		self._subEvtJsonFilePath = bleSubEventCodeJsonFilePath
		self._cmdDefaultFilePath = cmdDefaultFilePath
		self._cmdBufClsObj = None	
		self._loadInit()
		#self._defaultValueComment = ''
		
	def _loadInit(self):
		self._loadSubEventCode()
		self._cmdBufClsObj = buf_Cls.cmdBufferOprClass(self._cmdDefaultFilePath)
		self._load_spec_parameters()
	
	def _loadClose(self):
		self._cmdBufClsObj._cmd_buf_close()
	
	def _loadAddDefault(self, name, value_list): #for add default value
		return	self._cmdBufClsObj. _cmd_buf_add(name, value_list)
		
		
	def _loadSubEventCode(self):
	
		try:
			f = open(self._subEvtJsonFilePath)
			self._subEventJsonObj = json.load(f)
		except:
			print "error............"
			return
	
	def _getCmdList(self):
		return self._cmdsList
	
	def _getEventList(self):
		return self._eventsList
		
	def _getReturnParaList(self):
		return self._returnParaList
	
	def _printCmdParaList(self):
		for i in range(len(self._cmdsList)):
			print "name: %s, oprcode:%x" % (self._cmdsList[i]._name, self._cmdsList[i]._oprCode)
	
	def _printReturnParaList(self):
		for i in range(len(self._returnParaList)):
			print "name: %s, oprcode:%x" % (self._returnParaList[i]._name, self._returnParaList[i]._oprCode)
	
	def	_loadClose(self):
		buf_Cls
		
		
	def _load_spec_parameters(self):
		try:
			fileList = os.listdir(self._cmdSpecFolder)
		except:
			return
			
		for file in fileList:
			
			ogf=0
			isCmd = False
			isEvent = False
			if event_file_list[0] == file:
				#parse event list
				#print "find event file............"
				isEvent = True
				
				
			for item in g_cmdFileToOgfArray:
				if item[0] == file:
					isCmd = True
					ogf = item[1]
					break
				else:
					compareStr = item[0].split('.')[0]
					if compareStr == file[0:len(compareStr)]:
						ogf = item[1]
						break
			fullPath = self._cmdSpecFolder + "\\" + file
			curFileParaList = load_para_from_file(fullPath, ogf)
				
			if curFileParaList == None:
				print "Error format on file:", file
				continue
				
				
			for para in curFileParaList:
				para._classStr = file
				if isCmd == False and isEvent == False:
					para._isCmd = False
					self._returnParaList.append(para)
				else:
					if isEvent == True:
						#use the same function to parse event, so need to re-srite value
						para._isEvent = True
						para._eventCode = para._ocf
						para._ocf = 0
						if self._subEventJsonObj != None:
							#print "para._name:",para._name
							#print "self._subEventJsonObj[para._name]:",self._subEventJsonObj[para._name]
							#print "::::::::::",para._name
							if self._subEventJsonObj.get(para._name) != None:
								para._subEventCode = int(self._subEventJsonObj[para._name], 16)
								#print "get subevent code [%s]....:%d"%(para._name, para._subEventCode)
						self._eventsList.append(para)
					else:
						para._isCmd = True
						#add default value
						if self._cmdBufClsObj != None:
							para._defaultValueList = self._cmdBufClsObj._cmd_buf_get_list(para._name)
						self._cmdsList.append(para)
	def _loadPrintDefaultValue(self):
		if self._cmdBufClsObj != None:
			self._cmdBufClsObj._cmd_buf_print_all()
		for item in self._cmdsList:
			print "name: %s, default value: %s" % (item._name, item._defaultValueList)

