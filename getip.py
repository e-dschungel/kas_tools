#!/usr/bin/env python
#script to print the current IP if executed on a KAS server

import socket
import kas

kas = kas.KAS()
if kas.is_local():
    print socket.gethostbyname(socket.gethostname())
else:
    print "Not on a KAS server!"
    exit(1)