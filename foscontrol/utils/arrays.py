# src/pyFosControl/foscontrol/utils/arrays.py

from typing import List, Any, Callable, Dict, Optional

def array2dict(source: List[Any], keyprefix: str, 
               convertFunc: Optional[Callable[[Any], Any]] = None) -> Dict[str, Any]:
    """Convert an array to dict
    
    Args:
        source: Source array
        keyprefix: Key prefix used in the dict
        convertFunc: Optional function to convert values
        
    Returns:
        Dictionary with numbered keys
    """
    res = {}
    for i, s in enumerate(source):
        if convertFunc is not None:
            s = convertFunc(s)
        res[f"{keyprefix}{i}"] = s
    return res

def arrayTransform(source: List[Any], 
                   convertFunc: Callable[[Any], Any]) -> List[Any]:
    """Transform array elements using conversion function
    
    Args:
        source: Source array
        convertFunc: Function to convert each element
        
    Returns:
        Transformed array
    """
    return [convertFunc(x) for x in source]

def binaryarray2int(source: List[str]) -> List[int]:
    """Convert array with binary strings to integers
    
    Args:
        source: Array of binary strings
        
    Returns:
        Array of integers
    """
    return arrayTransform(source, lambda x: int(x, 2))