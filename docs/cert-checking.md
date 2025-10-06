Certificate Checking
--------------------

> This note was moved from the original `README.md` file, as it is no longer an issue with modern (>3.5) Python versions.

Since version 2.7.9 Python is checking certificates used in https connections.

This works fine with most sites on the internet because their certificates are signed by major
certificate authorities and Python has the means to verify their signatures.

However, most cameras use self-signed certificates which will fail this check and throw an exception. 

The certificate checking is controlled by the parameter `context.` See `camtest.py` for an example.
This [blog entry](http://tuxpool.blogspot.de/2016/05/accessing-servers-with-self-signed.html) shows how to create a context that fits your camera.

Unfortunately the `context` parameter was first added in Python 3.4.3. Between Python 2.7.9 and 3.4.3 
you either have to refrain from using https with self-signed certs or you have to tweak your system 
(i.e. install the camera certificate yourself in the system, change the host file, etc) so that the check is 
successful without using `context`.    
