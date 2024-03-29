'''
	ODOTS Interface
		command line interface and automatic download forwarder
	
	*Copyright 2019: Lawrence Jones
	* Version 1.0

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
	
	Version	Date	Description
	v1.0	09/2019	Initial Release for Proof of concept.


'''
import os
import sys

import multiprocessing
from multiprocessing import Queue

import time #for pauses in system interface to allow program to actually work 

#hello modules folder!
CWD=os.getcwd()
sys.path.append(CWD)
sys.path.append(CWD+'\\Modules')

import ODOTSFileParser
import SerialUtils

#interface thread (can be upgraded to full gui later)
class HumanInterface():#multiprocessing.Process):
    

    def __init__(self, InputQueue,OutputQueue):
        #multiprocessing.Process.__init__(self)
        self.InputQueue=InputQueue
        self.OutputQueue = OutputQueue
        self.Portlist=[]
        self.SerialVerbose = False
    def run(self):
        self.PrintBootUpScreen()
        self.LoopStart()
        
    def PrintBootUpScreen(self):
        print("+---------------------------------------------------------------+"+\
              "\n|***         Welcome to the ODOTS device interface           ***"+\
              "\n|***************************************************************"+\
              "\n|***  This interface can be used to manage device settings,  ***"+\
              "\n|***  synchronise the devices internal time and read device  ***"+\
              "\n|***  info                                                   ***"+\
              "\n|***************************************************************"+\
              "\n|            Input 'h' for help and usage instruction           "+\
              "\n|---------------------------------------------------------------"+\
              "\n|            EXITING THIS SCREEN WILL DISABLE DOWNLOAD"+\
              "\n+---------------------------------------------------------------+")
    def PrintHelpScreen(self):
        #this one will need to be intercepted
        print("+---------------------------------------------------------------+"+\
              "\n| Help and Usage: "+\
              "\n|  USAGE: >>prompt COMMAND                "+\
              "\n|         >>prompt DATA/ARGUEMENTS (if applicable       "+\
              "\n|  COMMANDS:                                          "+\
              "\n|      'LIST PORTS','l':"+\
              "\n|         Lists available communication ports to listen to an"+\
              "\n|         device on"+\
              "\n|      'CONNECT','x':  RESPONSE '?>' PROVIDE [port number from list]"+\
              "\n|         Initiates connection to communication port"+\
              "\n|      'CLOSEPORT','q':  "+\
              "\n|         Closes any open serial ports used by program"+\
              "\n|      'READ INFO','r':"+\
              "\n|         Instructs interface to read information on device"+\
              "\n|         configs, time and version number to be displayed in"+\
              "\n|         output."+\
              "\n|      'SYNC TIME','t':"+\
              "\n|         Instructs interface to sync device time with system "+\
              "\n|         time, which is assumed to be the base clock for the "+\
              "\n|         race recording system."+\
              "\n|      'SETID','i':  RESPONSE: '?>' PROVIDE: 'ID' (integer)"+\
              "\n|         Sets Device ID (in EEPROM so persistent) to value of "+\
              "\n|         ID"+\
              "\n|      'SET TO STANDARD','s'"+\
              "\n|         Sets Device mode to 'standard', the mode for"+\
              "\n|         checkpoint units. "+\
              "\n|      'SET TO DOWNLOAD','d'"+\
              "\n|         Sets Device mode to 'download', the mode for"+\
              "\n|         download units, DEVICE ID should be set to : 5"+\
              "\n|      'SET TO CLEAR','c'"+\
              "\n|         Sets Device mode to 'standard', the mode for"+\
              "\n|         clear units, DEVICE ID should be set to : 0xdead,"+\
              "\n|         (57,005)"+\
              "\n|      'h'"+\
              "\n|         display this information"+\
              "\n|      'v'"+\
              "\n|         toggle verbose behaviour of Serial interface process"+\
              "\n|         (Default is OFF)"+\
              "\n+---------------------------------------------------------------+")

    def SetDeviceToStandard(self):
        print(" ?> Device configuration will be changed to 'Standard', confirm?")
        Flag = input(" ?> y/n:")
        if Flag.lower() == 'y':
            self.OutputQueue.put(["ChangeStateToStandard"])
            print(" !> Configuration Change Request Sent")
    def SetDeviceToClear(self):
        print(" ?> Device configuration will be changed to 'Clear', confirm?")
        Flag = input(" ?> y/n:")
        if Flag.lower() == 'y':
            print("INterruption : STF is going on")
            self.OutputQueue.put(["ChangeStateToClear"])
            print(" !> Configuration Change Request Sent")
    def SetDeviceToDownload(self):
        print(" ?> Device configuration will be changed to 'Download', confirm?")
        Flag = input(" ?> y/n:")
        if Flag.lower() == 'y':
            self.OutputQueue.put(["ChangeStateToDownload"])
            print(" !> Configuration Change Request Sent")
    def SetDeviceID(self):
        ID = int(input(" ?> NEW DEVICE ID:"))
        print(ID)
        self.OutputQueue.put(["ChangeDeviceID"])
        self.OutputQueue.put([ID])
        print(" !> Device ID Change Request Sent")
    def SyncDeviceTime(self):
        self.OutputQueue.put(["SyncDeviceTime"])
        print(" !> Device time Sync request sent")
    def InvokeHelpScreen(self):
        self.PrintHelpScreen()

        
    def ToggleVerboseSerial(self):
        if self.SerialVerbose:
            self.OutputQueue.put(["NotVerbose"])
            print(" !> Serial Verbose Output disabled")
            self.SerialVerbose = False
        else:
            self.OutputQueue.put(["Verbose"])
            print(" !> Serial Verbose Output Enabled")
            self.SerialVerbose = True
            
    def DumpDeviceInfo(self):
        self.OutputQueue.put(["DumpDeviceInfo"])
        time.sleep(1) #to allow the serial handler to retrieve the list of ports
        print(" !>Retrieving Attached ODOTS Device Info")
        time.sleep(1)
        DeviceInfo = self.InputQueue.get()
        #device info [ID],[FirmareVersion],[HardwareVersion],[Download?],[Clear?],[DeviceTIMEString],[SystemTimeString]

        #this bit is necessary to make the info easy to understand in the interface
        if DeviceInfo[3]:
            Download = "Enabled"
        else:
            Download = "Disabled"
        if DeviceInfo[4]:
            Clear = "Enabled"
        else:
            Clear = "Disabled"

        print( " !> DeviceID: " + str(DeviceInfo[0]) \
               +"\n !> Firmware Version: "+str(DeviceInfo[1])+",    Hardware Version: "+str(DeviceInfo[2])\
               +"\n !> Download: "+Download+",    Clear: "+Clear\
               +"\n !> Battery Charge Remaining: "+str(DeviceInfo[7])+"%"\
               +"\n !> TIME:  \tYr\tM\tD\tHr\tMin\tSec"\
               +"\n !> System:\t"+str(DeviceInfo[6][0])+"\t"+str(DeviceInfo[6][1])+"\t"+str(DeviceInfo[6][2])+"\t"+str(DeviceInfo[6][3])+"\t"+str(DeviceInfo[6][4])+"\t"+str(DeviceInfo[6][5])\
               +"\n !> Device:\t"+str(DeviceInfo[5][0])+"\t"+str(DeviceInfo[5][1])+"\t"+str(DeviceInfo[5][2])+"\t"+str(DeviceInfo[5][3])+"\t"+str(DeviceInfo[5][4])+"\t"+str(DeviceInfo[5][5]))
    def ListAvailablePorts(self):
        self.OutputQueue.put(["ListRequest"])
        time.sleep(0.3) #to allow the serial handler to retrieve the list of ports
        self.PortList = self.InputQueue.get()
        i= 0
        print("Number:  Details")
        for Port in self.PortList:
            print("  "+str(i)+":   "+str(Port))
        print("\n -------------END OF LIST-------------")
              
    def ConnectToPort(self):
        PortNumber = input(" ?> ENTER PORT NUMBER FROM LIST:")
        
        self.OutputQueue.put(["ConnectToPort"])
        self.OutputQueue.put([str(PortNumber)]) #port list is mirrored in serial interface object!
        time.sleep(0.3) #to allow the serial handler to retrieve the list of ports
        Response = self.InputQueue.get()
        print(" !> RESPONSE:"+str(Response))

    def ClosePort(self):
        self.OutputQueue.put(["ClosePort"])
        
        
    def ParseInput(self, RecievedInput):
        #lets get this switchin' goin'
        if RecievedInput == 'h':
            self.InvokeHelpScreen()
        elif (RecievedInput == 'READ INFO') or(RecievedInput == 'r'):
            #yet to be implemented functionality
            self.DumpDeviceInfo()

        elif (RecievedInput == ('SYNC TIME')) or (RecievedInput == 't'):
            self.SyncDeviceTime()

        elif (RecievedInput == ('SETID'))or(RecievedInput == 'i'):
            self.SetDeviceID()

        elif (RecievedInput == ('SET TO STANDARD')) or (RecievedInput == 's'):
            self.SetDeviceToStandard()

        elif (RecievedInput == ('SET TO DOWNLOAD'))or(RecievedInput == 'd'):
            self.SetDeviceToDownload()

        elif (RecievedInput == ('SET TO CLEAR'))or(RecievedInput == 'c'):
            self.SetDeviceToClear()
            
        elif (RecievedInput == ('LIST PORTS'))or(RecievedInput == 'l'):
            self.ListAvailablePorts()
        elif (RecievedInput == ('CONNECT'))or(RecievedInput == 'x'):
            self.ConnectToPort()
        elif (RecievedInput == ('CLOSEPORT'))or(RecievedInput == 'q'):
            self.ClosePort()
        elif (RecievedInput == 'v'):
            self.ToggleVerboseSerial()
        elif RecievedInput == ('EXIT'):
            #this one needs to be reworked
            self.ClosePort()
            time.sleep(0.5)
            sys.exit()
            
        else:
            print(" !> Invalid Command, try inputting 'h' for help")

            
    def LoopStart(self):
        while 1:
            #print('>>')
            InputFromUser = input(">>")#sys.stdin.readline()
            #print(InputFromUser)
            self.ParseInput(InputFromUser)
            #time.sleep(0.05)
            #print("!>ResponseCode: "+str(self.InputQueue.get()))
        

'''class StdInReader(threading.Thread):
    
    def __init__(self,OutputQueue):
        threading.Thread.__init__(self)
        self.OutputQueue = OutputQueue

    def run(self):'''
        

#management thread

class SystemInterface(multiprocessing.Process):
    #manages actually talking to serial device, separated from human interface to allow for downloads to get passes straigth through

    def __init__(self,InputQueue,OutputQueue,Verbose=False):
        
        multiprocessing.Process.__init__(self)

        self.Verbose = Verbose
        self.InputQueue = InputQueue
        self.OutputQueue = OutputQueue
        self.DeviceInterface = SerialUtils.ODOTS_Serial_Interface(FileWritePath = "\\DownloadRecords")#,Verbose=True)
        self.CompetitionInterface = ODOTSFileParser.FileParserTCPWriter(FileReadPath = "\\DownloadRecords")
        self.PortOpenFlag = False

    def run(self):
        self.LoopStart()

    def UpdateDeviceOperationFlags(self,Download=False,Clear = False):
        
        self.DeviceInterface.SetDeviceMode(Download,Clear)

        
    def SyncDeviceTime(self):
        self.DeviceInterface.WriteTime()

        
    def ReadDeviceInfo(self):
        #read device ID
        
        DeviceID = self.DeviceInterface.ReadDeviceID()
        DeviceID = int.from_bytes(DeviceID,'big')
        
        #read device firmware version
        FirmwareVersion = self.DeviceInterface.ReadFirmwareVersion()
        FirmwareVersion = int.from_bytes(FirmwareVersion,'big')
        #read hardware version
        HardwareVersion = self.DeviceInterface.ReadHardwareVersion()
        HardwareVersion = int.from_bytes(HardwareVersion,'big')
        if self.Verbose:
            print(" !> DEBUG ReadID and Versaions")
        #read device operation flags
        DeviceMode = self.DeviceInterface.ReadDeviceMode()
        #read device battery voltage
        BatteryValue = self.DeviceInterface.ReadBatteryVoltage()
        if self.Verbose:
            print(" !> DEBUG Read Battery")
        BatteryCapacity = self.CalculateCapacity(BatteryValue)
        #read System Time
        if self.Verbose:
            print(" !> DEBUG Calculated Capacity")
        SystemTime = self.DeviceInterface.ReadSystemTime()
        #cheaty here, System time waits for next second boundary - calling it after reading the device time would be dodgy
        #read device Time
        DeviceTime = self.DeviceInterface.ReadTime()
        
        
    
        #TODO: This
        ReturnList = [DeviceID,FirmwareVersion,HardwareVersion,DeviceMode[0],DeviceMode[1],DeviceTime,SystemTime,BatteryCapacity]
    
        #self.OutputQueue.put
        self.OutputQueue.put(ReturnList)
    def CalculateCapacity(self, VoltageValue):
        
        Voltage = (VoltageValue[0]/255)*(12.1/2.1)
        Capacity = (Voltage-3.2)*100
        if self.Verbose:
            print("Read Value:"+str(VoltageValue[0]))
            print("Voltage calculated:"+str(Voltage))
            print("Capacity Calculated:"+str(Capacity))
        return Capacity

    def WriteDeviceID(self):
        #request device ID write operation
        
        NewID = self.InputQueue.get()
        
        NewID = int(NewID[0]).to_bytes(2,'big') #turn plain text ID and turn it into bytes form acceptable for serial interface
        
        self.DeviceInterface.WriteDeviceID(NewID)

    def ListPorts(self):
        #request list of available ports and pass off to user interface
        
        PortDetailList = self.DeviceInterface.ListAvailablePorts()
        
        self.OutputQueue.put(PortDetailList)
        

    def ConnectToPort(self):
        
        PortNumber = int((self.InputQueue.get())[0])
        
        #due to persistence in the device interface object opening a port is a two step process
        try:
            self.DeviceInterface.SelectPort(PortNumber)
            self.DeviceInterface.OpenPort()
            self.PortOpenFlag = True
            self.OutputQueue.put("Port Opened, Download Link Intiated")
        except:
            self.OutputQueue.put("Port Did not Open")
        #togge the flag for enabling the download intercepts 
        

    def ClosePort(self):
        self.DeviceInterface.ClosePort()
        self.PortOpenFlag = False

    def ToggleVerboseness(self, Verbose = False):
        self.Verbose = Verbose
        
    def LoopStart(self):

        while 1:
            #check input queue, not blocking
            try:
                Input = []
                Input = self.InputQueue.get(False)
                #print(Input)
                # we will only get here is there was something in the queue
                self.ParseInput(Input)
                #self.OuptutQueue.put(['OK'])
            except:
                #this is going to trigger every time the queue is empty!
                #print(Input)
                pass   
            
            #poll port
            if self.PortOpenFlag == True:
                FileName = self.DeviceInterface.PollInputPortforDownload()
                if FileName != False:
                    self.CompetitionInterface.ProcessRecord(filename=FileName)
            #time.sleep is used to prevent htis thread from using all available processing resources!, 2ms is long enough that the user
            #is unlikely to notice a delay, but the rest of the program does have time to process other things!
            time.sleep(0.02)
                
    def ParseInput(self,Input):
        
        Switch = Input[0]
        if self.Verbose:
            print(" !!>> INTERRUPTION: "+Switch)
        if Switch == "ChangeStateToStandard":
            self.UpdateDeviceOperationFlags()
            
        elif Switch == "ChangeStateToClear":
            self.UpdateDeviceOperationFlags(Clear = True)
            
        elif Switch == "ChangeStateToDownload":
            self.UpdateDeviceOperationFlags(Download = True)

            
        elif Switch == "ChangeDeviceID":
            self.WriteDeviceID()

            
        elif Switch == "SyncDeviceTime":
            self.SyncDeviceTime()

        elif Switch == "DumpDeviceInfo":
            self.ReadDeviceInfo()

        elif Switch == "ListRequest":
            self.ListPorts()

        elif Switch == "ConnectToPort":
            self.ConnectToPort()
        
        elif Switch == "ClosePort":
            self.ClosePort()
            
        elif Switch == "Verbose":
            self.ToggleVerboseness(True)

        elif Switch == "NotVerbose":
            self.ToggleVerboseness(False)
            
        else:
            print("!!>>INTERRUPTION: Invalid command recieved by serial manager")
        
        
def JavaCheck():
    #check if java JRE is installed, which is used for SendPunch.jar
    print("---COMMENCING JAVA CHECK---")
    JavaCheckFileName = 'JavaVersionStore.info'
    os.system("java -version >"+JavaCheckFileName+" 2>&1") #calls java version call



    JavaCheckFile = open(JavaCheckFileName, 'r')
    Line = JavaCheckFile.readline()
    while Line != "":
            try:
                    print(Line,end="")
                    if Line[0:8] == 'operable':#start of second line of printout of error!
                            print(" >> ERROR Java Runtime Environment not detected, please install a version\n"+\
                                  "    of the JRE from \n"+\
                                  "    https://www.oracle.com/technetwork/java/javase/downloads/index.html \n"+\
                                  "    (application developed with JRE 1.8.0). \n"+\
                                  "    \n"+\
                                  "    Java required to interface with Competition management software, if \n"+\
                                  "    this functionality is not required, program can still be used to \n"+\
                                  "    configure ODOTS Units.\n"+\
                                  "    \n"+\
                                  "    Continue using program with limited functionality?\n"+\
                                  "    y/n\n")
                            GoNoGo = input(" >>").lower()
                            if GoNoGo != 'y':
                                    JavaCheckFile.close()
                                    os.remove(JavaCheckFileName)
                                    sys.exit()
                    Line = JavaCheckFile.readline()

            except:
                    break
    print("---    JRE Check End    ---")

if __name__ =='__main__':
    multiprocessing.freeze_support() #adds support for running multiple processes in frozen configuration on windows!
    JavaCheck()
    #Loop
    HtoS = Queue()
    StoH = Queue()
        
    A=HumanInterface(StoH, HtoS)
    B = SystemInterface(HtoS,StoH)

    B.start()
    A.run()
