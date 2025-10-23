from typing import Optional, List, Dict, Any, Tuple
from .base import CamBase
from ..utils.dictionaries import (
    DC_WifiEncryption, DC_WifiAuth, DC_motionDetectSensitivity,
    DC_ddnsServer, DC_ptzSpeedList, DC_timeFormat, DC_timeDateFormat,
    DC_infraLedMode, BD_alarmAction
)
from ..utils.arrays import binaryarray2int, array2dict
from .result import ResultObj


class Cam(CamBase):
    """Extended camera interface with additional functionality"""

    def getMotionDetectConfig(self):
        """Get motion detection configuration with decoded information
        
        Returns decoded information:
        _areas: 10x10 active areas in frame -> array of 10 strings
        _schedules: 7 strings of 48 chars, one for each day
        _linkage: array of alarm actions
        """
        res = super().getMotionDetectConfig()
        res.stringLookupConv(res.sensitivity, DC_motionDetectSensitivity, "_sensitivity")
        res.collectBinaryArray("schedule", "_schedules", 48)
        res.collectBinaryArray("area", "_areas", 10)
        res.DB_convert2array("linkage", "_linkage", BD_alarmAction)
        return res

    def setMotionDetectConfig(self, isEnable, linkage, snapInterval, 
                             triggerInterval, sensitivity, schedules, areas):
        return super().setMotionDetectConfig(
            isEnable,
            BD_alarmAction.fromArray(linkage),
            snapInterval,
            triggerInterval,
            DC_motionDetectSensitivity.rlookup(sensitivity),
            binaryarray2int(schedules),
            binaryarray2int(areas)
        )

    def getPTZSpeed(self) -> ResultObj:
        """Get PTZ speed with decoded information"""
        res = super().sendcommand("getPTZSpeed")
        res.stringLookupConv(res.speed, DC_ptzSpeedList, "_speed_desc")
        return res

    def setPTZSpeed(self, speed: str) -> ResultObj:
        """Set PTZ speed using descriptive value"""
        speed_val = DC_ptzSpeedList.rlookup(speed)
        if speed_val is None:
            raise ValueError(f"Invalid speed value. Must be one of: {', '.join(DC_ptzSpeedList.values)}")
        return super().setPTZSpeed(int(speed_val))

    def getDevTimeConfig(self) -> ResultObj:
        """Get device time configuration with decoded values"""
        res = super().sendcommand("getDevTimeConfig")
        res.stringLookupConv(res.timeFormat, DC_timeFormat, "_time_format")
        res.stringLookupConv(res.dateFormat, DC_timeDateFormat, "_date_format")
        return res

    def getMirrorAndFlipSetting(self) -> ResultObj:
        """Get mirror and flip settings with boolean values"""
        return super().sendcommand("getMirrorAndFlipSetting", doBool=["isMirror", "isFlip"])

    def setMirrorAndFlipSetting(self, isMirror: bool, isFlip: bool) -> ResultObj:
        """Set mirror and flip settings"""
        return super().sendcommand("setMirrorAndFlipSetting", {
            "isMirror": isMirror,
            "isFlip": isFlip
        }, doBool=["isMirror", "isFlip"])

    def getInfraLedConfig(self) -> ResultObj:
        """Get infrared LED configuration with decoded mode"""
        res = super().sendcommand("getInfraLedConfig")
        res.stringLookupConv(res.mode, DC_infraLedMode, "_mode_desc")
        return res

    def setInfraLedConfig(self, mode: str) -> ResultObj:
        """Set infrared LED mode using descriptive value"""
        mode_val = DC_infraLedMode.rlookup(mode)
        if mode_val is None:
            raise ValueError(f"Invalid mode value. Must be one of: {', '.join(DC_infraLedMode.values)}")
        return super().sendcommand("setInfraLedConfig", {"mode": mode_val})

    def getWifiConfig(self) -> ResultObj:
        """Get WiFi configuration with decoded values"""
        res = super().sendcommand("getWifiConfig")
        res.stringLookupConv(res.authMode, DC_WifiAuth, "_auth_desc")
        res.stringLookupConv(res.encryptType, DC_WifiEncryption, "_encrypt_desc")
        return res

    def setWifiConfig(self, isEnable: bool, ssid: str, 
                      netType: str, auth: str, encrypt: str,
                      psk: str = None, key1: str = None,
                      key2: str = None, key3: str = None,
                      key4: str = None, keyIndex: int = None) -> ResultObj:
        """Set WiFi configuration using descriptive values"""
        auth_val = DC_WifiAuth.rlookup(auth)
        encrypt_val = DC_WifiEncryption.rlookup(encrypt)
        
        if auth_val is None:
            raise ValueError(f"Invalid auth value. Must be one of: {', '.join(DC_WifiAuth.values)}")
        if encrypt_val is None:
            raise ValueError(f"Invalid encrypt value. Must be one of: {', '.join(DC_WifiEncryption.values)}")
            
        params = {
            "isEnable": isEnable,
            "ssid": ssid,
            "netType": netType,
            "authMode": auth_val,
            "encryptType": encrypt_val
        }
        
        if psk:
            params["psk"] = psk
        if any([key1, key2, key3, key4]):
            if keyIndex not in [1, 2, 3, 4]:
                raise ValueError("keyIndex must be 1-4 when using WEP keys")
            params.update({
                "key1": key1,
                "key2": key2, 
                "key3": key3,
                "key4": key4,
                "keyIndex": keyIndex
            })
            
        return super().sendcommand("setWifiConfig", params)

