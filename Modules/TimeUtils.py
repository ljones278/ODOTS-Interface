'''
    Time Utils.py
	
	Manages Time Functionality
	
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
'''


import time

def ReturnCurrentTimeOnSecondEnd():
    Time = time.gmtime() #Get GMT time from computer
    while(Time.tm_sec == time.gmtime().tm_sec):
        pass
    return time.gmtime()

def GetCurrentTime():
    TimeString=[0x00,0x00,0x00,0x00,0x00,0x00]#Year, Month,Day, Hour , Minute, Second
    TimeStruct = ReturnCurrentTimeOnSecondEnd();
    TimeString = [TimeStruct.tm_year%100,TimeStruct.tm_mon,TimeStruct.tm_mday,TimeStruct.tm_hour,TimeStruct.tm_min,TimeStruct.tm_sec]
    return TimeString

