from typing import Dict, List, Any, Optional

class DictBits:
    """Helper class for bit mappings"""
    def __init__(self, mapping: Dict[int, str]):
        self.dict = mapping
        self.values = list(mapping.values())
        self.items = list(mapping.items())

    def toArray(self, value: int) -> List[str]:
        """Convert integer to array of matching values"""
        res = []
        for k, v in self.items:
            if value & (1 << k):
                res.append(v)
        return res

    def fromArray(self, arr: List[str]) -> int:
        """Convert array of strings to bitmask integer"""
        res = 0
        for k, v in self.items:
            if v in arr:
                res |= (1 << k)
        return res

class DictChar:
    """Helper class for character mappings"""
    def __init__(self, mapping: Dict[str, str]):
        self.dict = mapping
        self.keys = list(mapping.keys())
        self.values = list(mapping.values())
        self.items = list(mapping.items())

    def lookup(self, key: str) -> Optional[str]:
        """Look up value by key"""
        return self.dict.get(key)

    def rlookup(self, value: str) -> Optional[str]:
        """Reverse lookup key by value"""
        for k, v in self.items:
            if v == value:
                return k
        return None

# Constant definitions
BD_alarmAction = DictBits({0: "ring", 1: "mail", 2: "picture", 3: "video"})

DC_WifiEncryption = DictChar({
    "0": "Open Mode", 
    "1": "WEP", 
    "2": "WPA", 
    "3": "WPA2", 
    "4": "WPA/WPA2"
})

DC_WifiAuth = DictChar({
    "0": "Open Mode",
    "1": "Shared key", 
    "2": "Auto mode"
})

DC_motionDetectSensitivity = DictChar({
    "0": "low",
    "1": "normal", 
    "2": "high",
    "3": "lower",
    "4": "lowest"
})

DC_ddnsServer = DictChar({
    "0": "Factory DDNS",
    "1": "Oray",
    "2": "3322",
    "3": "no-ip",
    "4": "dyndns"
})

DC_ptzSpeedList = DictChar({
    "4": 'very slow',
    "3": 'slow',
    "2": 'normal speed',
    "1": 'fast',
    "0": 'very fast'
})

DC_logtype = DictChar({
    "0": "System startup",
    "3": "Login",
    "4": "Logout",
    "5": "User offline"
})

DC_FtpMode = DictChar({
    "0": "PASV",
    "1": "PORT"
})

DC_SmtpTlsMode = DictChar({
    "0": "None",
    "1": "TLS",
    "2": "STARTTLS"
})

DC_timeSource = DictChar({
    "0": "NTP server",
    "1": "manually"
})

DC_timeDateFormat = DictChar({
    "0": "YYYY-MM-DD",
    "1": "DD/MM/YYYY",
    "2": "MM/DD/YYYY"
})

DC_timeFormat = DictChar({
    "0": "12 hours",
    "1": "24 hours"
})

DC_infraLedMode = DictChar({
    "0": "auto",
    "1": "manuel"
})
