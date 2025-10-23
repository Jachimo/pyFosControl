from typing import Dict, Any, Optional, List, Callable
import xml.dom.minidom
from ..utils.dictionaries import DictBits, DictChar

class ResultObj:
    """Result object from camera API calls"""
    
    def __init__(self, data: Dict[str, Any]):
        """Initialize result object
        
        Args:
            data: Dictionary of result data
        """
        self.data = data
        self._process_result()

    def _process_result(self) -> None:
        """Process result code and set message"""
        result_messages = {
            0: "Success",
            -1: "CGI request string format error",
            -2: "Username or password error", 
            -3: "Access denied",
            -4: "CGI execute failure",
            -5: "Timeout",
            -6: "Reserve",
            -7: "Unknown error",
            -8: "Reserve",
            None: "Missing result parameter"
        }
        
        msg = result_messages.get(self.result)
        if msg is not None:
            self.set("_result", msg)

    def __getattr__(self, name: str) -> Any:
        """Get attribute value
        
        Special handling for 'result' field to return as integer
        """
        if name == "result":
            try:
                return int(self.data.get(name))
            except (ValueError, TypeError):
                pass
        return self.data.get(name)

    def __str__(self) -> str:
        """String representation"""
        return f"ResultObj: {self.data}"

    def get(self, name: str) -> Optional[Any]:
        """Get value by name"""
        return self.data.get(name)

    def set(self, name: str, value: Any) -> None:
        """Set value by name"""
        self.data[name] = value

    def stringLookupConv(self, value: Any, 
                        converter: DictChar,
                        name: str) -> None:
        """Convert value using DictChar and store result"""
        if value is not None:
            conv = converter.lookup(str(value))
            if conv is not None:
                self.set(name, conv)

    def collectArray(self, getparname: str,
                    setparname: str,
                    convertFunc: Optional[Callable] = None) -> None:
        """Collect numbered parameters into array"""
        res = []
        cnt = 0
        while True:
            p = self.get(f"{getparname}{cnt}")
            if p is None:
                break
            cnt += 1
            if convertFunc is None:
                res.append(p)
            else:
                cp = convertFunc(p)
                if cp is not None:
                    res.append(cp)
        if res:
            self.set(setparname, res)

    def DB_convert2array(self, getparam: str,
                        setparam: str,
                        converter: DictBits) -> None:
        """Convert integer to bit array using DictBits"""
        try:
            val = int(self.get(getparam))
            w = converter.toArray(val)
            self.set(setparam, w)
        except (ValueError, TypeError, KeyError):
            pass

    def collectBinaryArray(self, getparname: str, 
                          setparname: str,
                          length: int) -> None:
        """Collect numbered binary parameters into array
        
        Args:
            getparname: Parameter prefix to get from
            setparname: Parameter name to set result to
            length: Length of binary strings
        """
        res = []
        cnt = 0
        while True:
            p = self.get(f"{getparname}{cnt}")
            if p is None:
                break
            if len(p) != length:
                raise ValueError(f"Binary string length mismatch: {len(p)} != {length}")
            res.append(p)
            cnt += 1
        if res:
            self.set(setparname, res)
