#!/usr/bin/env python3

# Slixmpp: The Slick XMPP Library
# Copyright (C) 2010  Nathanael C. Fritz
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.

import logging, time, threading, json, xmltodict
from getpass import getpass
from argparse import ArgumentParser

import asyncio, uuid
import slixmpp

class XmppAccount(slixmpp.ClientXMPP):
    def __init__(self, jid, password, proxy):
        slixmpp.ClientXMPP.__init__(self, jid, password);

        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0004') # Data Forms
        self.register_plugin('xep_0060') # PubSub
        self.register_plugin('xep_0065')
        self.register_plugin('xep_0199') # XMPP Ping

        self.use_proxy = True
        self.proxy_config = {
        'host': "10.0.0.1",
        'port': 1}
        
        self.add_event_handler("session_start", self.start);
        self.add_event_handler("message", self.receive_chat)
        self.connect();
        self.send_presence();
        self.get_roster()
        self.messages = [];
        #self.recipient = recipient
        #self.msg = message
    def send_all_thread(self):
        while True:
            try:
                self.send_presence();
                #self.get_roster()
                for msg in self.messages:
                    if msg["send"]:
                        continue;
                    self.__send_chat__(msg);
                    msg["send"] = True;
            except KeyboardInterrupt:
                break;
            except:
                print("done");
            finally:
                time.sleep(10);
    def send_all(self):
        t = threading.Thread(target=self.send_all_thread);
        t.start();
    async def start(self, event):
        self.send_presence()
        await self.get_roster()
    def __send_chat__(self, msg):
        self.send_presence();
        self.send_message(mto=msg["to"],  mbody=msg["text"], mtype='chat');
    def send_chat(self, to, msg):
        self.messages.append({"id" : str(uuid.uuid4()), "send" : False, "text" : msg, "to" : to});
    def receive_chat(self, msg):
        #<message xml:lang="en" to="nao.importa.web@xmpp.jp" from="aied@xmpp.jp/converse.js-127670175" type="chat" id="3b40c186-5b84-4eb6-9886-6519eee223c2"><active xmlns="http://jabber.org/protocol/chatstates" /><request xmlns="urn:xmpp:receipts" /><origin-id xmlns="urn:xmpp:sid:0" id="3b40c186-5b84-4eb6-9886-6519eee223c2" /><body>ta</body></message>
        from_xmpp = str(msg["from"])[:str(msg["from"]).find("/")];
        if msg['type'] in ('chat', 'normal'):
            self.send_chat(from_xmpp, "Recebido: " + msg["body"] );

def teste_mensagem(x):
    for i in range(10):
        x.send_chat('aied@xmpp.jp', "ANTES DE TUDO: " + str(uuid.uuid4()));
        time.sleep(10);

if __name__ == '__main__':
    x = XmppAccount("nao.importa.web@xmpp.jp", "Foda-sevoce1!", None);
    x.send_all();
    threading.Thread(target=teste_mensagem, args=(x,)).start();
    asyncio.get_event_loop().run_forever()

# if __name__ == '__main__':
#     # Setup the command line arguments.
#     parser = ArgumentParser(description=SendMsgBot.__doc__)

#     # Output verbosity options.
#     parser.add_argument("-q", "--quiet", help="set logging to ERROR",
#                         action="store_const", dest="loglevel",
#                         const=logging.ERROR, default=logging.INFO)
#     parser.add_argument("-d", "--debug", help="set logging to DEBUG",
#                         action="store_const", dest="loglevel",
#                         const=logging.DEBUG, default=logging.INFO)

#     # JID and password options.
#     parser.add_argument("-j", "--jid", dest="jid",
#                         help="JID to use")
#     parser.add_argument("-p", "--password", dest="password",
#                         help="password to use")
#     parser.add_argument("-t", "--to", dest="to",
#                         help="JID to send the message to")
#     parser.add_argument("-m", "--message", dest="message",
#                         help="message to send")

#     args = parser.parse_args()

#     # Setup logging.
#     logging.basicConfig(level=args.loglevel,
#                         format='%(levelname)-8s %(message)s')

#     if args.jid is None:
#         args.jid = input("Username: ")
#     if args.password is None:
#         args.password = getpass("Password: ")
#     if args.to is None:
#         args.to = input("Send To: ")
#     if args.message is None:
#         args.message = input("Message: ")

#     # Setup the EchoBot and register plugins. Note that while plugins may
#     # have interdependencies, the order in which you register them does
#     # not matter.
#     xmpp = SendMsgBot(args.jid, args.password, args.to, args.message)
#     xmpp.register_plugin('xep_0030') # Service Discovery
#     xmpp.register_plugin('xep_0199') # XMPP Ping

#     # Connect to the XMPP server and start processing XMPP stanzas.
#     xmpp.connect()
#     asyncio.get_event_loop().run_until_complete(xmpp.disconnected)