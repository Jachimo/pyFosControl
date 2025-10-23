pyFosControl
============

Python interface to Foscam CGI API for HD models

> Jachimo's **Python 3.x-only** fork!
> Now builds using [Poetry](https://python-poetry.org/) instead of `setup.py`.


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


Installation
------------

This project uses Poetry for dependency management. To install:

1. Install Poetry if you haven't already:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Clone the repository:
   ```bash
   git clone https://github.com/Jachimo/pyFosControl.git
   cd pyFosControl
   ```

3. Install dependencies:
   ```bash
   poetry install
   ```

4. Optional: Install with sniffing support:
   ```bash
   poetry install --extras "sniff"
   ```

5. Create a config file:
   ```bash
   cp cam.cfg.example cam.cfg
   # Edit cam.cfg with your camera settings
   ```

Using the CLI Interface
----------------------

A command-line interface is provided to interact with your camera. You can run commands through Poetry:

```bash
# List all available commands
poetry run foscam_cli --list

# Execute a specific command
poetry run foscam_cli <command>
```

Examples:

```bash
# Get camera information
poetry run foscam_cli getDevInfo

# Take a snapshot
poetry run foscam_cli snapPicture

# Move the camera (for PTZ models)
poetry run foscam_cli ptzMoveUp

# Configure motion detection
poetry run foscam_cli getMotionDetectConfig
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


