#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import socket
import struct
import sys
import time
from threading import Thread

import FoscDecoder

sys.path.append("..")  # only for pyFosControl in parent directory
import pyFosControl


class ReadThread(Thread):
    """
     We use a persistent tcp connection and blocking read from a socket with a timeout of 1 sec.

     The packets have the following structure:

     int32   command
     char4   "FOSC"
     int32   size
     data block with "size" bytes

     The integers are little endian.
    """

    def __init__(self, socket, name=None):
        self.socket = socket
        super(ReadThread, self).__init__()
        self.endflag = False
        if name is not None:
            self.setName(name)
        self.resync_count = 0
        self.read_sequence = []
        self.decodeerror = []

    def run(self):
        # Mode:
        # 0: awaiting header
        # 1: reading data
        # 2: try to resync
        mode = 0
        remaining = 0
        body = ""

        while not self.endflag:
            try:
                if mode == 0:
                    data = self.socket.recv(12)
                    if len(data) == 0:
                        print("Connection closed by peer")
                        self.endflag = True
                        break

                    cmd, magic, size = struct.unpack("<I4sI", data)
                    if magic != "FOSC":
                        print("**************** resync *************")
                        FoscDecoder.printhex(data)
                        mode = 2
                        self.resync_count += 1
                    else:
                        self.read_sequence.append(cmd)
                        body = ""
                        remaining = size
                        mode = 1
                elif mode == 1:
                    incoming = self.socket.recv(remaining)
                    body += incoming
                    remaining -= len(incoming)
                    print("remaining {}".format( remaining))
                    if remaining == 0:
                        mode = 0
                        self.proc(cmd, size, body)
                else:
                    data = self.socket.recv(2000)  # clear incoming buffer
                    if len(data) == 0:
                        mode = 0
                    else:
                        FoscDecoder.printhex(data)
            except socket.timeout:
                mode = 0
                print(self.name)
            except struct.error:
                print("unpack error")
                FoscDecoder.printhex(data)

    def stopit(self):
        # set endflag in loop
        # which will be noticed after the next command
        # or timeout (i.e. max. 1 sec)
        self.endflag = True

    def proc(self, cmd, size, body):
        """ try to use decoder subroutines
        """

        print("Incoming cmd: %s, size %s" % (cmd, size))

        # Let's check all
        try:
            decoder = FoscDecoder.decoder_call.get(cmd)
            if decoder is None:
                FoscDecoder.printhex(body)
            else:
                decoder(struct.pack("<I4sI", cmd, "FOSC", size) + body)
        except BaseException as e:
            msg = "cmd %s: %s" % (cmd, e.message)
            self.decodeerror.append(msg)
            print("** DECODE ERROR: {}".format(msg))

    def stats(self):
        print("Sequence of incoming packets: {}".format(self.read_sequence))
        if self.resync_count > 0:
            print("Fallen out of sync %s time(s)" % self.resync_count)
        if len(self.decodeerror) > 0:
            print("%s error(s) during decoding:" % len(self.decodeerror))
            for msg in self.decodeerror:
                print(msg)


class TCPHandler(object):
    def __init__(self, host, port, name):
        # timeout in seconds
        timeout = 1
        socket.setdefaulttimeout(timeout)

        self.name = name
        self.ip = host
        self.port = port

        # open a tcp socket
        self.con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.con.connect((self.ip, self.port))

        # create read thread and start it
        self.reader = ReadThread(self.con, name)
        self.reader.start()

    def close(self):
        print("%s: shutdown reader" % self.name)
        self.reader.stopit()
        print("%s: waiting" % self.name)
        self.reader.join()
        print("%s: shutdown complete" % self.name)
        self.reader.stats()
        self.con.close()

    def sendraw(self, data, crconv=False):
        """ Send "raw" text
        :param data:   text to send
        :param crconv: convert LF -> CR LF

        crconv = True, to send HTML-Request (needs CRLF) from a Unix system (have only LF)
        """
        print("send-raw:")
        print(data)
        if crconv:
            data = data.replace("\n", "\r\n")
        self.con.send(data)


class CamHandler(TCPHandler):
    """ class to send commands to the cam
    """

    def send_command(self, command, data, verbose=True):
        dt = struct.pack("<I4sI", command, "FOSC", len(data)) + data
        print("%s: Sending data" % self.name)
        if verbose:
            FoscDecoder.printhex(dt)
        self.con.send(dt)

    def send_cmd0(self, name, password, uid):
        """
        int32  command
        char4  FOSC
        int32  size
        byte   unknown1 (zero)
        char64 username
        char64 password
        int32  uid
        char28 unknown (zeros)
        """
        print("Sending: Video on")
        data = struct.pack("<x64s64sI28x", name, password, uid)
        self.send_command(0, data)

    def send_cmd1(self, name, password):
        """
        int32  command
        char4  FOSC
        int32  size
        byte   unknown1 (zero)
        char64 username
        char64 password
        """
        print("Sending: close connection")
        data = struct.pack("<x64s64s", name, password)
        self.send_command(1, data)

    def send_cmd2(self, name, password):
        """
        int32  command
        char4  FOSC
        int32  size
        byte   unknown1 (zero)
        char64 username
        char64 password
        char32 unknown (zeros)
        """
        print("Sending: Start audio")
        data = struct.pack("<x64s64s32x", name, password)
        self.send_command(2, data)

    def send_cmd3(self, name, password):
        """
        int32  command
        char4  FOSC
        int32  size
        byte   unknown1 (zero)
        char64 username
        char64 password
        char32 unknown (zeros)
        """
        print("Sending: Mute audio")
        data = struct.pack("<x64s64s32x", name, password)
        self.send_command(3, data)

    def send_cmd4(self, name, password, uid):
        """
        int32  command
        char4  FOSC
        int32  size
        byte   unknown1 (zero)
        char64 username
        char64 password
        int32  uid
        char28 unknown (zeros)
        """
        print("Sending: speaker on")
        data = struct.pack("<x64s64sI28x", name, password, uid)
        self.send_command(4, data)

    def send_cmd5(self, name, password):
        """
        int32  command
        char4  FOSC
        int32  size
        char64 username
        char64 password
        char32 padding (zeros)
        """

        print("Sending: speaker off")
        data = struct.pack("<64s64s32x", name, password)
        self.send_command(5, data)

    def send_cmd6(self, audiodata, chunksize):
        """
        int32  command
        char4  FOSC
        int32  size
        int32  audiodatasize = size-4
               audiodata
        """

        print("Sending audio data to cam")

        # not working correctly!!

        seg = 0
        alen = len(audiodata)
        while True:
            part = audiodata[seg * chunksize: (seg + 1) * chunksize]
            plen = len(part)
            print(seg, plen)
            if plen == 0:
                break
            data = struct.pack("<I", plen) + part
            self.send_command(6, data, verbose=False)
            # time.sleep((0.0 + plen) / 8000)
            seg += 1

    def send_cmd12(self, name, password, uid):
        """
        int32  command
        char4  FOSC
        int32  size
        char64 username
        char64 password
        int32  uid
        char32 padding (zeros)
        """
        print("Sending: Login")
        data = struct.pack("<64s64sI32x", name, password, uid)
        self.send_command(12, data)

    def send_cmd15(self, uid):
        """
        int32 command
        char4 FOSC
        int32 size
        int32 uid
        """
        print("Sending: Login check")
        data = struct.pack("<I", uid)
        self.send_command(15, data)

    def start_serverpush(self):
        """ Start low level protocol

        The low level protocol is started by a HTTP request
        """
        print("Sending: Start serverpush")
        self.sendraw(data="""SERVERPUSH / HTTP/1.1\r\nHost: %s:%s\r\nAccept:*/*\r\nConnection: Close\r\n\r\n\r\n""" % (self.ip, self.port))


# convenience functions for the test program
# saves some typing

def delay(secs):
    return time.sleep, (secs,)


def start_serverpush():
    global spush
    return spush.start_serverpush, ()


def do_login():
    global spush
    global username, password, uid
    return spush.send_cmd12, (username, password, uid)


def do_login_check():
    global spush
    global uid
    return spush.send_cmd15, (uid,)


def do_logoff():
    global username, password
    return spush.send_cmd1, (username, password)


def do_audio_start():
    global spush
    global username, password
    return spush.send_cmd2, (username, password)


def do_audio_stop():
    global spush
    global username, password
    return spush.send_cmd3, (username, password)


def do_speaker_on():
    global spush
    global username, password, uid
    return spush.send_cmd4, (username, password, uid)


def do_speaker_off():
    global spush
    global username, password
    return spush.send_cmd5, (username, password)


def do_video_start():
    global spush
    global username, password, uid
    return spush.send_cmd0, (username, password, uid)


##############################
# convenience functions to CGI

def do_cgi_logIn(name, uid):
    global cgictrl

    def subfkt(pname, puid):
        print(cgictrl.logIn(pname, groupId=puid))

    return subfkt, (name, uid)


def do_cgi_logOut(name, uid):
    global cgictrl

    def subfkt(pname, puid):
        print(cgictrl.logOut(pname, groupId=puid))

    return subfkt, (name, uid)


def do_cgi_add_preset(name):
    global cgictrl

    def subfkt(pname):
        print(cgictrl.ptzAddPresetPoint(pname))

    return subfkt, (name,)


def do_cgi_del_preset(name):
    global cgictrl

    def subfkt(pname):
        print(cgictrl.ptzDeletePresetPoint(pname))

    return subfkt, (name,)


def do_cgi_del_cruise(name):
    global cgictrl

    def subfkt(pname):
        print(cgictrl.ptzDelCruiseMap(pname))

    return subfkt, (name,)


# change according to your environment
camera_ip = "192.168.0.102"
camera_port = 88
username = "testadmin"
password = "testpassword"
uid = int(time.time())  # unix time stamp as random unique identifier

# handle to CGI interface
cgictrl = pyFosControl.cam("http", camera_ip, camera_port, username, password)
cgictrl.setConsoleDump(True)

# Audio data to send to camera (cmd6), only partially successful yet
# playme = open("music8000s.raw","rb").read()

# Dump incoming audio into file
# FoscDecoder.openAudioDumpFile("/tmp/audio2.raw")

# Set-up the connection and the listener thread
try:
    spush = CamHandler(camera_ip, camera_port, "spush-Handler")
except socket.timeout:
    print("Connection failed")
    sys.exit(1)

try:
    testprogram = [
        do_cgi_logIn(username, uid),
        start_serverpush(),
        do_login(),
        do_login_check(),
        delay(1),
        # do_cgi_del_preset("punk8"),
        do_cgi_del_cruise("crusie5"),
        delay(1),
        do_cgi_logOut(username, uid),
        delay(1),
        do_logoff()
    ]

    """
        do_video_start(),
        do_audio_start(),
        delay(5),
        do_audio_stop(),
        delay(2),
        do_video_start(),
        do_audio_start(),
        delay(5),
        do_audio_stop(),
        do_speaker_on(),
        delay(2),
        do_speaker_off(),
        delay(2),
    """

    """
        ( spush.send_cmd6,  (playme, 960)),                # send audio data to cam
    """

    for cmd in testprogram:
        func = cmd[0]
        par = cmd[1]
        func(*par)
        # time.sleep(0.5)
finally:
    # Always shut the thread down
    spush.close()

# Display the UID used
print("\n** uid: 0x%08x (%s)" % (uid, uid))
FoscDecoder.closeAudioDumpFile()
FoscDecoder.datacomp.stats()
