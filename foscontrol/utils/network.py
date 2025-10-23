import ssl
import sys
import string
import random
from typing import Callable, Optional, Union, Dict, Any, Tuple
from urllib.parse import urlsplit, urljoin, urlencode, unquote
from urllib.request import urlopen, Request

def create_url_opener(context: Optional[ssl.SSLContext] = None) -> Callable:
    """Create URL opener with optional SSL context.

    The returned opener accepts:
      opener(url_or_request, data=None, context=<SSLContext>)

    If the explicit 'context' argument passed by the caller is None,
    it will fall back to the context provided when the opener was created.
    """
    if sys.hexversion < 0x03040300:
        # older Python: urlopen doesn't accept 'context'
        return lambda url, data=None, **kwargs: urlopen(url, data=data)
    else:
        # newer Python: accept optional 'context' keyword to match callers
        def opener(url: Union[str, Request], data: Optional[bytes] = None,
                   context: Optional[ssl.SSLContext] = None, **kwargs) -> Any:
            ctx = context if context is not None else context  # explicit for clarity
            # fall back to the closure context if caller didn't pass one
            if ctx is None:
                ctx = context  # closure variable (same name) will be used
            return urlopen(url, data=data, context=ctx)
        # Note: closure variable 'context' is captured above
        return opener

def my_urlopen(url: str, data: Optional[bytes] = None, context: Optional[ssl.SSLContext] = None) -> Any:
    """Open URL with optional POST data and SSL context"""
    if sys.hexversion < 0x03040300:
        return urlopen(url, data=data)
    return urlopen(url, data=data, context=context)

def encode_multipart(fields: Dict[str, Any], files: Dict[str, Dict[str, Any]], 
                     boundary: Optional[str] = None) -> Tuple[bytes, Dict[str, str]]:
    """
    Encode form fields and files for multipart/form-data submission
    
    Args:
        fields: Dictionary of form fields
        files: Dictionary of files to upload {name: {filename:, content:}}
        boundary: Optional boundary string
        
    Returns:
        Tuple of (encoded_data, headers)
    """
    _BOUNDARY_CHARS = string.digits + string.ascii_letters

    def escape_quote(s: str) -> str:
        return s.replace('"', '\\"')

    if boundary is None:
        boundary = ''.join(random.choice(_BOUNDARY_CHARS) for i in range(30))

    lines = []

    for name, value in fields.items():
        lines.extend((
            f'--{boundary}',
            f'Content-Disposition: form-data; name="{escape_quote(name)}"',
            '',
            str(value),
        ))

    for name, fileinfo in files.items():
        filename = fileinfo['filename']
        content = fileinfo['content']
        lines.extend((
            f'--{boundary}',
            f'Content-Disposition: form-data; name="{escape_quote(name)}"; '
            f'filename="{escape_quote(filename)}"',
            'Content-Type: application/octet-stream',
            '',
            '',
        ))
        if isinstance(content, str):
            lines[-1] = content
        else:
            lines[-1] = content.decode('utf-8')

    lines.extend((
        f'--{boundary}--',
        '',
    ))

    body = '\r\n'.join(lines)
    
    headers = {
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'Content-Length': str(len(body)),
    }

    return body.encode('utf-8'), headers

def ip2long(ip: str) -> int:
    """Convert an IP string to long"""
    ip_parts = ip.split('.')
    if len(ip_parts) != 4:
        raise ValueError("Invalid IP address format")
    return sum(int(part) << (24 - (8 * i)) for i, part in enumerate(ip_parts))

def long2ip(w: int) -> str:
    """Convert long to IP string"""
    return '.'.join(str((w >> (24 - (8 * i))) & 0xFF) for i in range(4))