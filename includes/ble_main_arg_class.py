import includes.ble_common_class as comm_cls 
import ble_modules.ble_load_data as load_cls
import ble_modules.ble_parser as parser
import ble_modules.ble_uart as uart_cls
import threading,Queue,serial


class MAIN_ARGS_CLASS(object):
	def __init__(self, specFolder, logFoler, bleSubEvtJsonFPath, cmdDefvalueFilePath):
		self._cmdTreeObj = None
		self._toolBarObj = None
		self._mainPageObj = None
		self._messagePageObj = None
		self._deviceInfoPageObj = None
		self._uartApiObj = uart_cls.uartOprClass()
		self._usbApiObj = None
		self._socketApiObj = None
		#thread
		self._uartRecvThreadObj = None
		self._parserThreadObj = None
		self._threadCtlObj = comm_cls.HCI_THREAD_CTL_CLASS()
		self._recv_2_parser_queue =  Queue.Queue()
		self._data_2_parser_queue_lock = threading.Lock()
		self._parserObj = None
		
		
		self._logFolder = logFoler
		self._loadSpecObj = load_cls.Ble_LoadCmdClass(specFolder, bleSubEvtJsonFPath, cmdDefvalueFilePath)
		self._connectionList = []	#HCI_CONNECT_EVENT_CLASS obj list
		self._advDeviceList = []	#HCI_ADV_DEVICE_CLASS obj list
		self._extendAdvDeviceList = []	#HCI_EXTEND_ADV_DEV_CLASS obj list
		self._bdAddrList = []
		self._portIsConnect = False
		#self._parser2AclQueue = Queue.Queue()	#send start time
		#self._recv2ParserQueue = Queue.Queue()	#send time and recv_data
		#self._parser2MainQueue = Queue.Queue()	#send exec results of cmd
		#gui part
		self._cmdInputListObj = None
		#self._cmdInputCurrentDisplayIndex = 0
		self._mainPageStatusFilter = True #open to 
		self._statusBarObj = None
		self._advDeviceBdaddrList = []
		self._advDeviceListObj = None
		self._messsageLogObj = None
		self._displayStatusObj = None
		
		#acl
		self._aclIsDataTxGui = True
		self._aclGuiHasBeenQuited = True
		self._aclRecvHasGotAclHeader = False
		self._aclDataTransferObj = None
		self._aclBufferSize = 0
		self._aclBufferCount = 0
		self._parserToAclCommunicateObj = comm_cls.HCI_PARSER_2_ACL_COMMUNICATE_CLASS()