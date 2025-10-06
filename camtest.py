#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from configparser import ConfigParser
from foscontrol import Cam

################################
# Don't forget to edit cam.cfg #
# to reflect your setup!        #
################################

if __name__ == "__main__":
    config = ConfigParser()

    # see cam.cfg.example
    config.read(['cam.cfg'])
    prot = config.get('general', 'protocol')
    host = config.get('general', 'host')
    port = config.get('general', 'port')
    user = config.get('general', 'user')
    passwd = config.get('general', 'password')

    if sys.hexversion < 0x03040300:
        # parameter context not available
        ctx = None
    else:
        # disable cert checking
        # see also http://tuxpool.blogspot.de/2016/05/accessing-servers-with-self-signed.html
        import ssl

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

    # connection to the camera
    do = Cam(prot, host, port, user, passwd, context=ctx)

    # display basic camera info
    res = do.getDevInfo()
    if res.result == 0:  # quick check
        print("""product name: %s
serial number: %s
camera name: %s
firmware version: %s
hardware version: %s""" % (res.productName, res.serialNo, res.devName, res.firmwareVer, res.hardwareVer))
    else:
        print(res._result)
