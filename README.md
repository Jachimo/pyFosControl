pyFosControl
============

Python interface to Foscam CGI API for HD models

> Jachimo's Python 3.x-only fork!  
> For Python 2.7+ compatibility, see the upstream repository.


Introduction
------------

The Foscam cameras can be controlled via a web interface. There are browser plugins available for Firefox,
Chrome and IE, which are bundled with the camera firmware and can be downloaded using the cameras web interface.

However, these plugins are Windows only. Without them only a few basic configuration options are available (network,
user accounts, firewall, etc.). The bulk of the functionality including the display of the camera pictures,
controlling the ptz movements, motion detection, are not available on a Linux computer.

There is a [SDK](http://foscam.us/forum/cgi-sdk-for-hd-camera-t6045.html#p28979 "SDK for HD cameras") available
describing a CGI interface which seems to make most of these functions available. pyFosControl is intended as an
python interface.


Getting started
---------------

1. Create a new `cam.cfg` file using `cam.cfg.example` as template.
2. Run `camtest.py` from the command line to get some basic information (like model info, firmware and hardware version).


Using the CLI Interface
----------------------

A command-line interface is provided to interact with your camera. 
The `foscam_cli.py` script allows you to execute any SDK command directly.

Basic usage:

```bash
# List all available commands
./foscam_cli.py --list

# Execute a specific command
./foscam_cli.py <command>
```

Examples:

```bash
# Get camera information
./foscam_cli.py getDevInfo

# Take a snapshot
./foscam_cli.py snapPicture

# Move the camera (for PTZ models)
./foscam_cli.py ptzMoveUp

# Configure motion detection
./foscam_cli.py getMotionDetectConfig
```

The CLI will prompt for any required parameters when executing commands. 
You can use Ctrl+C to cancel.


Please note
-----------

* This interface is far from complete.
* It's *mostly* tested on a FI9821W V2.
* The SDK documentation is inaccurate in places.
* The non HD cameras use a different set of CGI commands and are not covered in this implementation.
* The behaviour of the camera changes slightly with each new firmware version. Please include model and firmware version when sending bug reports (run `camtest.py` from the command line).
