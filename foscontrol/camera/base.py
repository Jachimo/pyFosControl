from typing import List, Optional, Dict, Any, Tuple
import ssl
from urllib.parse import urlencode, urljoin
from urllib.request import Request 
from ..utils.network import create_url_opener, my_urlopen, encode_multipart
from ..utils.dictionaries import DictBits, DictChar
from .result import ResultObj

class CamBase:
    """Base interface to camera with core functionality"""

    def __init__(self, 
                 prot: str,
                 host: str, 
                 port: int,
                 user: str,
                 password: str,
                 context: Optional[ssl.SSLContext] = None):
        """Initialize camera connection
        
        Args:
            prot: Protocol ("http" or "https")
            host: Hostname
            port: Port number
            user: Username
            password: Password
            context: SSL context for HTTPS
        """
        self.base = f"{prot}://{host}:{port}/cgi-bin/CGIProxy.fcgi"
        self.user = user
        self.password = password
        self.context = context
        self.url_opener = create_url_opener(context)

    def sendcommand(self, cmd: str, 
                    param: Optional[Dict[str, Any]] = None,
                    raw: bool = False,
                    doBool: Optional[List[str]] = None,
                    headers: Optional[Dict[str, str]] = None,
                    data: Optional[bytes] = None) -> ResultObj:
        """Send command to camera and return result"""
        if param is None:
            param = {}
            
        param.update({
            'cmd': cmd,
            'usr': self.user,
            'pwd': self.password
        })
        
        if data is None:
            url = f"{self.base}?{urlencode(param)}"
            data = self.url_opener(url, context=self.context).read()
        else:
            url = self.base
            req = Request(url, data=data, headers=headers)
            data = self.url_opener(req, context=self.context).read()

        if raw:
            return data

        from xml.dom.minidom import parseString
        dom = parseString(data)
        
        d = {}
        for node in dom.getElementsByTagName('*'):
            if node.firstChild and node.firstChild.nodeType == node.TEXT_NODE:
                d[node.tagName] = node.firstChild.data

        if doBool:
            for k in doBool:
                if k in d:
                    d[k] = d[k] == "1"
                    
        return ResultObj(d)

    def getMotionDetectConfig(self):
        return self.sendcommand("getMotionDetectConfig", doBool=["isEnable"])

    def setMotionDetectConfig(self, isEnable, linkage, snapInterval, 
                             triggerInterval, sensitivity, schedules, areas):
        param = {
            "isEnable": isEnable,
            "linkage": linkage,
            "snapInterval": snapInterval,
            "triggerInterval": triggerInterval,
            "sensitivity": sensitivity
        }
        for day in range(7):
            param[f"schedule{day}"] = schedules[day]
        for row in range(10):
            param[f"area{row}"] = areas[row]

        return self.sendcommand("setMotionDetectConfig", param=param, doBool=["isEnable"])

    def getDevInfo(self) -> ResultObj:
        """Get device information"""
        return self.sendcommand("getDevInfo")

    def getDevState(self) -> ResultObj:
        """Get device state"""
        return self.sendcommand("getDevState")

    def snapPicture(self) -> bytes:
        """Take a snapshot"""
        return self.sendcommand("snapPicture", raw=True)

    def snapPicture2(self) -> bytes:
        """Take a snapshot (alternative method)"""
        return self.sendcommand("snapPicture2", raw=True)

    def getVideoStreamParam(self) -> ResultObj:
        """Get video stream parameters"""
        return self.sendcommand("getVideoStreamParam")

    def getMirrorAndFlipSetting(self) -> ResultObj:
        """Get mirror and flip settings"""
        return self.sendcommand("getMirrorAndFlipSetting")

    def setPTZSpeed(self, speed: int) -> ResultObj:
        """Set PTZ movement speed (0-4)"""
        return self.sendcommand("setPTZSpeed", {"speed": speed})

    def ptzReset(self) -> ResultObj:
        """Reset PTZ to home position"""
        return self.sendcommand("ptzReset")

    def ptzMoveUp(self) -> ResultObj:
        """Move camera up"""
        return self.sendcommand("ptzMoveUp")

    def ptzMoveDown(self) -> ResultObj:
        """Move camera down"""
        return self.sendcommand("ptzMoveDown")

    def ptzMoveLeft(self) -> ResultObj:
        """Move camera left"""
        return self.sendcommand("ptzMoveLeft")

    def ptzMoveRight(self) -> ResultObj:
        """Move camera right"""
        return self.sendcommand("ptzMoveRight")

    def ptzStopRun(self) -> ResultObj:
        """Stop PTZ movement"""
        return self.sendcommand("ptzStopRun")

    def getRecordList(self, recordPath: str) -> ResultObj:
        """Get list of recordings"""
        return self.sendcommand("getRecordList", {"recordPath": recordPath})

    def getIPInfo(self) -> ResultObj:
        """Get IP configuration"""
        return self.sendcommand("getIPInfo")

    def setIPInfo(self, isDHCP: bool, ip: str, gate: str, mask: str, dns1: str, dns2: str) -> ResultObj:
        """Set IP configuration"""
        param = {
            "isDHCP": isDHCP,
            "ip": ip,
            "gate": gate,
            "mask": mask,
            "dns1": dns1,
            "dns2": dns2
        }
        return self.sendcommand("setIPInfo", param=param)

    def reboot(self) -> ResultObj:
        """Reboot camera"""
        return self.sendcommand("reboot")

    def restore(self) -> ResultObj:
        """Restore factory settings"""
        return self.sendcommand("restore")
