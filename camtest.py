#!/usr/bin/python
# -*- coding: utf-8 -*-

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

    if prot == "https":
        # disable cert checking
        # see also http://tuxpool.blogspot.de/2016/05/accessing-servers-with-self-signed.html
        import ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    else:
        ctx = None

    # connection to the camera
    do = Cam(prot, host, port, user, passwd, context=ctx)

    # display camera info
    res = do.getDevInfo()
    if res.result == 0:  # quick check
        print(f"product name: {res.productName}")
        print(f"firmware version: {res.firmwareVer}")
        print(f"hardware version: {res.hardwareVer}")
    else:
        print(res._result)
