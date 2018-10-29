import sys,os,wx,threading
import ble_main_window as mainWindowCls
import includes.ble_main_arg_class as main_cls
import ble_modules.ble_parser as parser_cls
import ble_modules.ble_thread as thread_cls


#from includes.ble_common_class import *
#from ble_widgets.ble_mainPage import *


"""

def func_timer():
	print "hello"
	global timer
	timer = threading.Timer(5, func_timer)
	timer.start()
	
"""	


SPEC_FOLDER="configs\\spec"
LOG_FOLDER="temp\\logs"
BLE_SUBEVENT_JSON_PATH="configs\\LE_subevent_code.json"
CMD_DEFAULT_VALUE_FILE_PATH="configs\\btc_command_history.ini"

def global_init():
	#print "global_init"
	sys.path.append(os.getcwd())
	#sys.path.append(os.getcwd() + '\\mainPage')
	#print "path:", os.getcwd() + '\\mainPage'
def base_init(mainArgObj):
	#print "base_init"
	mainArgObj._parserObj = parser_cls.Ble_eventParser(mainArgObj._loadSpecObj._getCmdList(), \
													   mainArgObj._loadSpecObj._getReturnParaList(), \
													   mainArgObj._loadSpecObj._getEventList())
	
	mainArgObj._uartRecvThreadObj = threading.Thread(target = thread_cls.thread_recv_data, args = (mainArgObj,))
	mainArgObj._parserThreadObj = threading.Thread(target = thread_cls.thread_parse_data, args = (mainArgObj,))
	
	
	mainArgObj._uartRecvThreadObj.start()
	mainArgObj._parserThreadObj.start()
	#mainArgObj._loadSpecObj._printCmdParaList()
	
def main(argv):
	#global timer
	#timer = threading.Timer(5, func_timer)
	#timer.start()
	global_init()
	
	mainArgObj = main_cls.MAIN_ARGS_CLASS(SPEC_FOLDER, LOG_FOLDER, BLE_SUBEVENT_JSON_PATH, CMD_DEFAULT_VALUE_FILE_PATH)
	base_init(mainArgObj)
	
	
   	ex = wx.App()
	#mainWindowCls.MainWindow(None)
	mainWindowCls.MainWindow(mainArgObj)
	ex.MainLoop()
	global_close(mainArgObj)
	#timer.cancel()


if __name__ == "__main__":
    main(sys.argv)	#main(sys.argv[1:]) means point??? skip app name