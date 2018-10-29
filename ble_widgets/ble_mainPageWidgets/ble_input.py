import wx,time
import wx.lib.scrolledpanel as scrolled 


class Ble_getInputClass(wx.Panel):

	def __init__(self,parent, argListObj):
		self._argListObj = argListObj
		self._cmdName = argListObj._name
		self._panel = parent
		self._clear = False
		
		textObjCount = 0
		defaultValListIsValid = False
		
		#1. calc parameter
	
		for i in range(len(argListObj._paraSizeLists)):
			textObjCount += argListObj._paraSizeLists[i]
		
		#print "------name:", argListObj._defaultValueList[]	
		#print "\tlen:", len(argListObj._defaultValueList)
		#print "textObjCount:",textObjCount
		#if argListObj._defaultValueList != None and textObjCount == len(argListObj._defaultValueList) -3:
		#	defaultValListIsValid == True
		#print "defaultValListIsValid:",defaultValListIsValid	
		self.oprCode = argListObj._oprCode
		ocf = self.oprCode & 0x3ff
		ogf = (self.oprCode >> 10) & 0x3f
		
		##########
		"""
		class HCI_SPEC_CLASS(object):
		def __init__(self):
			self._isCmd = False  #False
			self._isEvent = False
			self._classStr = ''
			self._type = 0x01
			self._name = ''
			self._ogf = 0
			self._ocf = 0
			self._eventCode = 0				#for event
			self._subEventCode = 0				#for event
			self._self.oprCode = 0				#for cmd
			self._paraCounts = 0			# 2
			self._paraNameLists = []		# {"name1", "name2"}
			self._paraSizeLists = []		# {4, 2}
			self._paraFixLenFlagLists = []		#1 for fix len, 0 for variety
			self._defaultValueList = None #for cmd
		###########
		"""
		self.inputItemValLen = [[]] * len(argListObj._paraSizeLists)
		titleTextObjArray = [[]] * len(argListObj._paraSizeLists)
		self.countTextObjArray = [[]] * len(argListObj._paraSizeLists)
		valueTextObjArray = [[]] * len(argListObj._paraSizeLists)
		self._valueList = [[]] * len(argListObj._paraSizeLists)
		
		
		offset = 4 #remove 1b type + 2b self.oprCode + 1b len
		for i in range(len(argListObj._paraSizeLists)):
			curArgCnt = argListObj._paraSizeLists[i]
			self._valueList[i] = ''
			if argListObj._defaultValueList != None :
				
				for j in range(curArgCnt):
					self._valueList[i] += "%.2x"%int(argListObj._defaultValueList[offset+curArgCnt - j - 1], 16)
					#self._valueList[i] = argListObj._defaultValueList[offset: offset + 2*curArgCnt]
			else:
				self._valueList[i] = '00'*curArgCnt
				
			offset += curArgCnt
			
		#2. layout
		valueLayoutSizer = wx.GridBagSizer(len(argListObj._paraSizeLists) + 1, 10)
		main_vbox = wx.BoxSizer(wx.VERTICAL)
		title_hbox = wx.BoxSizer(wx.HORIZONTAL)
		cmdName_hbox = wx.BoxSizer(wx.HORIZONTAL)
		
		valueLayoutSizer.SetHGap(1)
		valueLayoutSizer.SetVGap(1)
		
		#3. create title items
		str = "Opcode : %#.4x"%self.oprCode
		self.oprCodeTextObj = wx.StaticText(self._panel, wx.ID_ANY, str[0:len(str)-4]+str[len(str)-4:].upper(), (40, 22))
		str = "OFG : %#.2x"%ogf
		ogfTextObj = wx.StaticText(self._panel, wx.ID_ANY, str[0:len(str)-2]+str[len(str)-2:].upper(), (40,22))
		str = "OCF : %#.3x"%ocf
		ocfTextObj = wx.StaticText(self._panel, wx.ID_ANY, str[0:len(str)-3]+str[len(str)-3:].upper(), (40, 22))
		cmdNameTextObj = wx.StaticText(self._panel, wx.ID_ANY, "CMD : %s"%self._cmdName, (100, 22))
		
		title_hbox.Add(self.oprCodeTextObj, 1)
		title_hbox.AddStretchSpacer()
		title_hbox.Add(ogfTextObj, 1)
		title_hbox.AddStretchSpacer()
		title_hbox.Add(ocfTextObj, 1)
		cmdName_hbox.Add(cmdNameTextObj, 1)
		
		#4. crete input infos
		for i in range(len(argListObj._paraSizeLists)):
			#4.1 add item
			self.inputItemValLen[i] = argListObj._paraSizeLists[i]
			self.countTextObjArray[i] = wx.StaticText(self._panel, wx.ID_ANY, \
												"[%#.3d/%#.3d]"%(argListObj._paraSizeLists[i], argListObj._paraSizeLists[i]), \
												(40, 22))
			
			nameStr = ''
			nameLen = len(argListObj._paraNameLists[i])
			for j in range(64):
				if j < nameLen:
					nameStr += argListObj._paraNameLists[i][j]
				else:
					nameStr += ' '
					
			#titleTextObjArray[i] = wx.StaticText(self._panel, wx.ID_ANY, argListObj._paraNameLists[i], (200, 22))
			titleTextObjArray[i] = wx.StaticText(self._panel, wx.ID_ANY, nameStr, (200, 22))
			
			
			valueTextObjArray[i] = wx.TextCtrl(self._panel, wx.ID_ANY,value=self._valueList[i].upper(), size=(300, 22), style=wx.TE_LEFT)
			
			#4.2 add layout
			valueLayoutSizer.Add(self.countTextObjArray[i], (i+1, 0), (1, 1), wx.EXPAND, border=2)
			valueLayoutSizer.Add(titleTextObjArray[i], (i+1, 2), (1, 2), wx.EXPAND, border=2)
			valueLayoutSizer.Add(valueTextObjArray[i], (i+1, 4), (1, 4), wx.EXPAND, border=2)
			
			#4.3 bind evt
			#valueTextObjArray[i].Bind(wx.EVT_KEY_UP, lambda evt, argIndex=i:self.lower_to_upper(evt, argIndex))
			valueTextObjArray[i].Bind(wx.EVT_TEXT, lambda evt, argIndex=i:self.OnEnter(evt, argIndex))
			
		main_vbox.Add(cmdName_hbox)	
		main_vbox.Add(title_hbox)
		main_vbox.Add(valueLayoutSizer)
		
		#self.hbox.Add(valueLayoutSizer)
		self._panel.SetSizerAndFit(main_vbox)	
		
	def lower_to_upper(self, evt, index):
		eventObj = evt.GetEventObject()
		end_pos = eventObj.GetInsertionPoint()

		if end_pos <=0 :
			return
			
		start_pos = end_pos -1
		eventObj.SetSelection(start_pos,end_pos)
		char_value=eventObj.GetStringSelection()
		
		if 97<=ord(char_value)<=122:
			upper_case = char_value.upper()
			eventObj.Remove(start_pos,end_pos)
			#time.sleep(.5)
			eventObj.WriteText(upper_case)
		else:
			eventObj.SetInsertionPoint(end_pos)
		#self._valueList[index] = content[0:curItemRealLen]
		#self.countTextObjArray[index].SetLabel("[%#.3d/%#.3d]"%(curItemRealLen/2, curItemLen))
		
	def OnEnter(self,evt, index): 
		eventObj = evt.GetEventObject()
		content = eventObj.GetValue()
		curItemLen = self.inputItemValLen[index]
		curItemRealLen = len(content)
		if self._clear == True:
			self._clear = False
			return 
		end_pos = eventObj.GetInsertionPoint()
		if curItemRealLen > curItemLen *2:
			
			content = content[0:end_pos-1].upper() + content[end_pos:curItemLen*2+1].upper()
			self._clear == True
			eventObj.Clear()
			self._clear = True
			eventObj.write(content)
			end_pos -= 1
			
			
		else:
			try: 
				a = int(content[end_pos-1], 16)	
			except:
				content = content[0:end_pos-1].upper() + content[end_pos:curItemRealLen].upper()
				end_pos -= 1
			
			self._clear = True
			eventObj.Clear()
			self._clear = True
			eventObj.write(content.upper())
		curItemRealLen = len(content)
		self._valueList[index] = content[0:curItemRealLen/2*2]
			
		eventObj.SetInsertionPoint(end_pos)
		self.countTextObjArray[index].SetLabel("[%#.3d/%#.3d]"%(curItemRealLen/2, curItemLen))
		
	"""
	def OnEnter(self,evt, index): 
		eventObj = evt.GetEventObject()
		content = eventObj.GetValue()
		curItemLen = self.inputItemValLen[index]
		curItemRealLen = len(content)
		if self._clear == True:
			self._clear = False
			return 
			
		if curItemRealLen > curItemLen*2:
			#too many args
			self._clear = True
			eventObj.Clear()
			self._clear = True
			self.countTextObjArray[index].SetLabel("[%#.3d/%#.3d]"%(curItemLen, curItemLen))
			eventObj.write(content[0:2*curItemLen].upper())
 
		else:
			try: 
				a = int(content[len(content) - 1], 16)
				self._clear = True
				eventObj.Clear()
				self._clear = True
				eventObj.write(content.upper())
				
			except:
				self._clear = True
				eventObj.Clear()
				self._clear = True
				eventObj.write(content[0:len(content)-1].upper())
		self.countTextObjArray[index].SetLabel("[%#.3d/%#.3d]"%(curItemRealLen/2, curItemLen))
		if len(content) > 0:
			self._valueList[index] = eventObj.GetValue()
		print "value:", self._valueList
	"""
	#def _getCmdName
	def _getValue(self):
		oprCodeStr = "%#.4x"% self.oprCode
		
		outList = ['0x01']
		outList.append("%#.2x" % (self.oprCode & 0xff))
		outList.append("%#.2x" % ((self.oprCode  >> 8)& 0xff))
		
		argLen = 0
		for i in range(len(self._argListObj._paraSizeLists)):
			argLen += self._argListObj._paraSizeLists[i]
		outList.append("%#.2x" % argLen)
		
		for i in range(len(self._valueList)):
			itemLen = self._argListObj._paraSizeLists[i]
			isFixed = self._argListObj._paraFixLenFlagLists[i]
			if isFixed == 0:	#variety
				itemLen = len(self._valueList[i])/2
				for j in range(itemLen):
					outList.append('%#.2x' % int(self._valueList[i][2*j:2*j+2], 16))
			else:
				for j in range(itemLen):
					try:
						outList.append('%#.2x' % int(self._valueList[i][2*(itemLen-j-1):2*(itemLen - j-1)+2], 16))
					except:
						return []
		
		#print "len:",((len(outList) ) & 0xff)
		#print "outList:",outList
		#outList[3] = hex(0)
		outList[3] = "%.2x" % ((len(outList) - 4) & 0xff)	
			
			
		return outList
		
	def _getPanel(self):
		return self._getobject()
	
	
	def _getobject(self):
		return self._panel
	
	def _printValue(self):
		print self._valueList
	
	def _getCmdName(self):
		return self._cmdName

"""
class Ble_getInputClass(wx.Panel):

	def __init__(self,parent, argListObj):
		self._cmdName = argListObj._cmdName
		self._panel = parent
		self._clear = False
		
		#panel_up = wx.Panel(self._panel)
		
		#panel_down = wx.ScrolledWindow(self._panel)
		#panel_down.SetScrollbars(1, 1, 100, 10)
			
			
		#panel_down = wx.Panel(self._panel)
		textObjCount = 0
		index = 0
		maxArgLen = 0
		
		#1. calc parameter
		for i in range(len(argListObj._paraSizeLists)):
			if argListObj._paraSizeLists[i] > maxArgLen:
				
				maxArgLen = argListObj._paraSizeLists[i]
		
		
		for i in range(len(argListObj._paraSizeLists)):
			textObjCount += argListObj._paraSizeLists[i]
		
		self.oprCode = argListObj._self.oprCode
		ocf = self.oprCode & 0x3ff
		ogf = (self.oprCode >> 10) & 0x3f
		
		
		
		titleTextObjArray = [[]] * len(argListObj._paraSizeLists)
		valueTextObjArray = [[]] * textObjCount
		self._valueList = [[00]] * textObjCount
		
		
		if len(argListObj._defaultValue) == textObjCount * 2:
			for i in range(textObjCount):
				self._valueList[i] = argListObj._defaultValue[i*2: i*2+2]
		
		#2. layout
		valueLayoutSizer = wx.GridBagSizer(len(argListObj._paraSizeLists) + 1, maxArgLen * 3 / 2)
		main_vbox = wx.BoxSizer(wx.VERTICAL)
		title_hbox = wx.BoxSizer(wx.HORIZONTAL)
		
		valueLayoutSizer.SetHGap(1)
		valueLayoutSizer.SetVGap(1)
		
		#3. create title items
		str = "Opcode : %#.4x"%self.oprCode
		self.oprCodeTextObj = wx.StaticText(self._panel, wx.ID_ANY, str[0:len(str)-4]+str[len(str)-4:].upper(), (40, 22))
		str = "OFG : %#.2x"%ogf
		ogfTextObj = wx.StaticText(self._panel, wx.ID_ANY, str[0:len(str)-2]+str[len(str)-2:].upper(), (40,22))
		str = "OCF : %#.3x"%ocf
		ocfTextObj = wx.StaticText(self._panel, wx.ID_ANY, str[0:len(str)-3]+str[len(str)-3:].upper(), (40, 22))
		cmdNameTextObj = wx.StaticText(self._panel, wx.ID_ANY, "CMD : %s"%self._cmdName, (100, 22))
		
		title_hbox.Add(self.oprCodeTextObj, 1)
		title_hbox.Add(ogfTextObj, 1)
		title_hbox.Add(ocfTextObj, 1)
		title_hbox.Add(cmdNameTextObj, 1)
		
		#4. crete input infos
		for i in range(len(argListObj._paraSizeLists)):
			titleTextObjArray[i] = wx.StaticText(self._panel, wx.ID_ANY, argListObj._paraNameLists[i], (60, 22))
			valueLayoutSizer.Add(titleTextObjArray[i], (i+1, 0), (1, maxArgLen/2), wx.EXPAND|wx.ALL, border=2)
				
			max = argListObj._paraSizeLists[i]
			for j in range(argListObj._paraSizeLists[i]):
				currentValueIndex = (index-j) + (max - j -1)
				print "textObjCount:",textObjCount
				print "len:",len( argListObj._defaultValue)
				if textObjCount*2 == len( argListObj._defaultValue):
					defaultValue = argListObj._defaultValue[2 * currentValueIndex:2*currentValueIndex+2]
				else:
					defaultValue = '00'
				#valueTextObjArray[index] = wx.TextCtrl(self._panel, wx.ID_ANY,value=defaultValue.upper(),size=(26, 26), style=wx.TE_LEFT)
				valueTextObjArray[index] = wx.TextCtrl(self._panel, wx.ID_ANY,value=defaultValue.upper(),size=(26, 22), style=wx.TE_CENTER)
				valueTextObjArray[index].Bind(wx.EVT_TEXT, lambda evt, argIndex=currentValueIndex:self.OnEnter(evt, argIndex))  
				#valueTextObjArray[index].SetFont(font)
				#valueLayoutSizer.Add(valueTextObjArray[index], (i+1, j+8), (1, 1), wx.EXPAND | wx.ALL, border=2)
				valueLayoutSizer.Add(valueTextObjArray[index], (i+1, j+maxArgLen/2), (1, 1), wx.EXPAND, border=2)
				index += 1
		
		main_vbox.Add(title_hbox)
		main_vbox.Add(valueLayoutSizer)
		
		#self.hbox.Add(valueLayoutSizer)
		self._panel.SetSizerAndFit(main_vbox)		
		
	def OnEnter(self,evt, index): 
		if self._clear == True:
			self._clear = False
			return 
		eventObj = evt.GetEventObject()
		defaultValue = self._valueList[index]
		
		content = eventObj.GetValue()
		if len(content) > 2:
			print "value:",content[0:2]
			self._clear = True
			
			eventObj.Clear()
			self._clear = True
			eventObj.write(content[0:2].upper())
		else:
			try: 
				a = int(content[len(content) - 1], 16)
				self._clear = True
				eventObj.Clear()
				self._clear = True
				eventObj.write(content.upper())
				
			except:
				self._clear = True
				eventObj.Clear()
				self._clear = True
				eventObj.write(defaultValue[0:len(content)-1].upper())
		content = eventObj.GetValue()
			
		if len(content) > 0:
			self._valueList[index] = content
		print "value:", self._valueList
		
	def _getPanel(self):
		return self._getobject()
	
	
	def _getobject(self):
		return self._panel
	
	def _printValue(self):
		print self._valueList
	
	def _getCmdName(self):
		return self._cmdName
"""