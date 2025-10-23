#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import inspect
import argparse
from configparser import ConfigParser
import ssl
from ..camera.extended import Cam

def get_method_params(method):
    """Get parameters for a method excluding self"""
    params = inspect.signature(method).parameters
    return [(name, param.default) for name, param in params.items() if name != 'self']

def prompt_for_param(param_name, default_value):
    """Prompt user for parameter value"""
    if default_value is inspect.Parameter.empty:
        prompt = f"Enter {param_name}: "
    else:
        prompt = f"Enter {param_name} (default={default_value}): "
    
    value = input(prompt)
    if not value and default_value is not inspect.Parameter.empty:
        return default_value
    
    # Handle boolean values
    if value.lower() in ['true', 'yes', 'y', '1']:
        return True
    if value.lower() in ['false', 'no', 'n', '0']:
        return False
    
    # Try to convert to int if possible
    try:
        return int(value)
    except ValueError:
        return value

def get_camera_instance():
    """Get camera instance using config file"""
    config = ConfigParser()
    config.read(['cam.cfg'])
    
    try:
        prot = config.get('general', 'protocol')
        host = config.get('general', 'host')
        port = config.get('general', 'port')
        user = config.get('general', 'user')
        passwd = config.get('general', 'password')
    except Exception as e:
        print("Error reading cam.cfg file:", e)
        print("Please ensure cam.cfg exists with [general] section containing:")
        print("protocol, host, port, user, password")
        sys.exit(1)

    # Setup SSL context for HTTPS
    if prot == "https":
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    else:
        ctx = None

    return Cam(prot, host, port, user, passwd, context=ctx)

def list_commands():
    """List all available camera commands"""
    methods = []
    for name, method in inspect.getmembers(Cam, predicate=inspect.isfunction):
        if not name.startswith('_'):
            methods.append(name)
    return sorted(methods)

def main():
    parser = argparse.ArgumentParser(description='Foscam HD Camera CLI Controller')
    parser.add_argument('command', nargs='?', help='Command to execute')
    parser.add_argument('--list', action='store_true', help='List all available commands')
    
    args = parser.parse_args()

    if args.list:
        print("Available commands:")
        for cmd in list_commands():
            print(f"  {cmd}")
        return

    if not args.command:
        parser.print_help()
        return

    cam = get_camera_instance()
    
    try:
        method = getattr(cam, args.command)
    except AttributeError:
        print(f"Unknown command: {args.command}")
        print("Use --list to see available commands")
        return

    # Get method parameters and prompt for values
    params = get_method_params(method)
    kwargs = {}
    
    if params:
        print(f"\nEntering parameters for {args.command}:")
        for param_name, default_value in params:
            kwargs[param_name] = prompt_for_param(param_name, default_value)

    try:
        result = method(**kwargs)
        print("\nResult:")
        print(result)
    except Exception as e:
        print(f"Error executing command: {e}")

if __name__ == "__main__":
    main()