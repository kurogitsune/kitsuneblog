# -*- coding: utf-8 -*-

from __future__ import print_function
import sys
#!/usr/bin/env python

try: 
  import simplejson as json
except:
  import json

import itertools
import time
import io
import re

"""
CONFIG
===========
"""

orig_time=1457925161

#SETUP
#Set the deployment time below and comment out the line.
#origin_time = int(time.mktime(time.strptime("28.01.2016 09:16:02", "%d.%m.%Y %H:%M:%S")))

the_delay=40*60 #interval between symbols in seconds

#1 post per week = 1/7 post per day = 1/7/24 per hour = 0.006
#1000 symbols per post => 1000 x 0.006 = 6 symbols per hour = 1 symbol per 10 minutes
#set the_delay=10*60 for 1 post per week.

"""
Kitsune Server
===========

Updates all the users through REDIS and websockets
"""

import os
import logging
import redis
import gevent
from flask import Flask, render_template, url_for

from flask_sockets import Sockets

REDIS_URL = os.environ['REDIS_URL']
REDIS_CHAN = 'chat'

app = Flask(__name__)
app.debug = 'DEBUG' in os.environ

sockets = Sockets(app)
redis = redis.from_url(REDIS_URL)

TAG_RE = re.compile(r'<[^>]+>')

def remove_tags(text):
    return TAG_RE.sub('', text).replace("&nbsp;"," ")

def warning(*objs):
    print("DEBUG INFO: ", *objs, file=sys.stderr)

class ChatBackend(object):
    """Interface for registering and updating WebSocket clients."""

    def __init__(self):
        self.clients = list()
        self.pubsub = redis.pubsub()
        self.pubsub.subscribe(REDIS_CHAN)
        self.data_untilnow=""

    def __iter_data(self):
        for message in self.pubsub.listen():
            data = message.get('data')
            if message['type'] == 'message':
                app.logger.info(u'Sending message: {}'.format(data))
                yield data

    def register(self, client):
        """Register a WebSocket connection for Redis updates."""
        self.clients.append(client)
        out = {'text': self.data_untilnow, 'handle': "a"}
        client.send(json.dumps(out))

    def send(self, client, data):
        """Send given data to the registered client.
        Automatically discards invalid connections."""
        try:
            client.send(data)
        except Exception:
            self.clients.remove(client)

    def run(self):
        """Listens for new messages in Redis, and sends them to clients."""
        for data in self.__iter_data():
            for client in self.clients:
                gevent.spawn(self.send, client, data)

    def start(self):
        """Maintains Redis subscription in the background."""
        gevent.spawn(self.run)
        gevent.spawn(self.generate_messages)
    def generate_messages(self):

        fnum=1
        
        origin_time=orig_time
        if (orig_time==0): origin_time=int(time.time())-6500*the_delay
        
        bytes_read=0

        fname="static/"+str(fnum)+".txt"
        f=io.open(fname, encoding='utf-8')
        currentfile_contents=f.read()
        f.close()
        
        read_data=""
        read_data_stripped=""
        marker=0

        while True:
            
            epoch_time = int(time.time())
            
            bytes_to_read_total=int((epoch_time-origin_time)/the_delay)-bytes_read
            bytes_to_read_now=bytes_to_read_total-len(read_data_stripped)
            
            next_file=0
            if bytes_to_read_now>0:

                counter=0
                
                while len(read_data_stripped)<bytes_to_read_total:
                    
                    
                    bytes_to_read_now=bytes_to_read_total-len(read_data_stripped)
                    
                    if marker+bytes_to_read_now>len(currentfile_contents):
                        read_data = read_data+currentfile_contents[marker:]
                        marker=len(currentfile_contents)
                        
                    else:   
                        read_data = read_data+currentfile_contents[marker:(marker+bytes_to_read_now)]   
                        marker=marker+bytes_to_read_now
                        
                    

                    if read_data.count("<")>read_data.count(">"):
                        missing_tag=currentfile_contents.find(">",marker)
                        read_data=read_data+currentfile_contents[marker:missing_tag+1]
                        marker=missing_tag+1
                        
                    
                    and_location=read_data.rfind("&",len(read_data)-6)

                    if and_location>-1:
                        if read_data[and_location:]+currentfile_contents[marker:marker+(6-len(read_data[and_location:]))]=="&nbsp;":
                            missing_symbols=(6-len(read_data[and_location:]))       
                            read_data=read_data+currentfile_contents[marker:marker+missing_symbols]
                            marker=marker+missing_symbols
                            
                        elif (read_data[and_location:]+currentfile_contents[marker:marker+(4-len(read_data[and_location:]))]=="&lt;") or (read_data[and_location:]+currentfile_contents[marker:marker+(4-len(read_data[and_location:]))]=="&gt;"):
                            missing_symbols=(4-len(read_data[and_location:]))       
                            read_data=read_data+currentfile_contents[marker:marker+missing_symbols]
                            marker=marker+missing_symbols
                        
                    read_data_stripped=remove_tags(read_data)

                    if marker>=len(currentfile_contents):
                        next_file=1
                        break

                    counter=counter+1
            
            if (len(read_data_stripped)<bytes_to_read_total) or (next_file==1):
                
                fname="static/"+str(fnum+1)+".txt"
                warning("next file ")
                try:
                    f=io.open(fname, encoding='utf-8')
                    currentfile_contents=f.read()
                    f.close()
                    marker=0
                    fnum=fnum+1
                except:
                    bytes_read=bytes_read+len(read_data_stripped)
                    out = {'text': read_data, 'handle': "a"}
                    redis.publish(REDIS_CHAN, json.dumps(out))
                    self.data_untilnow=self.data_untilnow+read_data
                    warning(out)
                    read_data_stripped=""
                    read_data=""
                    time.sleep(24*60*60) #wait a day till checking for new posts
                    

            else:
                bytes_read=bytes_read+len(read_data_stripped)
                out = {'text': read_data, 'handle': "a"}
                redis.publish(REDIS_CHAN, json.dumps(out))
                self.data_untilnow=self.data_untilnow+read_data
                warning(out)
                read_data_stripped=""
                read_data=""
                time.sleep(the_delay) 
        
        return

chats = ChatBackend()
chats.start()

@app.route('/')
def hello():
    return render_template('index.html')

@sockets.route('/receive')
def outbox(ws):
    """Sends outgoing chat messages, via `ChatBackend`."""
    chats.register(ws)

    while not ws.closed:
        # Context switch while `ChatBackend.start` is running in the background.
        gevent.sleep(0.1)
