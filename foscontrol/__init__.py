"""
Python interface to Foscam CGI API for HD models
"""

from foscontrol.camera.base import CamBase
from foscontrol.camera.extended import Cam
from foscontrol.camera.result import ResultObj

__all__ = ["Cam", "CamBase", "ResultObj"]
