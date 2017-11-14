#!/usr/bin/env python

"""
EE450 Homework 2
Nicholas Truong
Fall 2017
"""

# You are not required to use any of the code in this stub,
# however you may find it a helpful starting point.

from collections import deque
import time
import socket
import sys
import select

# In general, globals should be sparingly used if at all.
# However, for this simple program it's *ok*.
# You are not required to use these, but you may find them helpful.
our_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
local_input = deque()
network_input = deque()
network_output = deque()
timer1 = 0
timer2 = 0
myID = 0
myPort = 0
messageNumber = 100
recentlySeenPeers = []
knownAddressesDict = {}
messageNumberDict = {} #maps messageNumber to pnum type
pendingMessages = {} #mnum to (message, timesleft, sendingport)
pendingBroadcastMessage = {} #dst to (message, timesleft, sendingport)

#Messages follow format: SRC:###;DST:###;PNUM:#;HCT:#;MNUM:###;VL:xxx;MESG:yyy
def format_message(src, dst, pnum, hct, mnum, vl, mesg):
    global messageNumber
    #increment message number
    
    src = '{0:03d}'.format(src)
    dst = '{0:03d}'.format(dst)
    mnum = '{0:03d}'.format(mnum)
    print "Sending ::: SRC:" + str(src) + ";DST:" +str(dst) + ";PNUM:" + str(pnum) + ";HCT:" + str(hct) + ";MNUM:" + str(mnum) + ";VL:" + vl + ";MESG:" + mesg
    messageNumberDict[str(mnum)] = pnum
    return "SRC:" + str(src) + ";DST:" +str(dst) + ";PNUM:" + str(pnum) + ";HCT:" + str(hct) + ";MNUM:" + str(mnum) + ";VL:" + vl + ";MESG:" + mesg
#remember to check for malformed messages
def parse_message(s):
    list = s.split(";")

    dict = {"SRC": (list[0]).split(":")[1], "DST":(list[1]).split(":")[1], "PNUM":(list[2]).split(":")[1],
            "HCT": (list[3]).split(":")[1], "MNUM": (list[4]).split(":")[1], "VL": (list[5]).split(":")[1],
            "MESG": (list[6]).split(":")[1]
            }

    print list
    return dict


def handle_io():
    # This is likley the only function you'll want to edit.

    global our_socket, local_input, network_input, network_output
    global timer1
    global myID, myPort, messageNumber
    global recentlySeenPeers
    global knownAddressesDict
    global pendingMessages
    global pendingBroadcastMessage

    current_time = time.time()



    # Did you get something from the server?
    #
    # 1) Are you expecting something from the server, but nothing came?  Has
    # it been 3 seconds?  If so, re-send your message by appending it to the
    # left side of the network_output queue and return.  If it hasn't been 3
    # seconds, there's nothing to do but wait a little longer (so return).
    # Remember to print error messages when you need to resend.
    #
    # 2) Are you expecting something from the server, and something came?
    # Does what you received make sense for the protocol?  If not, re-send
    # your message by appending it to the left side of the network_output
    # queue, and return.
    # Remember to print error messages when you don't get what you expect.
    try:
        # Pop will *remove* the message from the FIFO queue, and return it.
        msg_from_server = network_input.pop()
        # Great- we got a message from the server.
        print("Got message %s" % msg_from_server[0])

        #parse the message into a dictionary
        msg = parse_message(msg_from_server[0])

        #error messsage
        if msg["PNUM"] == "0" : 
            print msg["MESG"]

        #initial message from server
        elif msg["PNUM"] == "2" :
            #check matching Message ID
            if int(msg["PNUM"]) == messageNumberDict[msg["MNUM"]] + 1:
                
                myID = ((msg["MESG"].split(","))[0])[-3:]
                myPort = ((msg["MESG"].split(","))[1])[1:]

                print "Succesfully Registered. My ID is: " + myID

        #receiving a message
        #elif msg["PNUM"] == "3" :
         #   print "received a message from somone"
          #  print myID
            #print msg["DST"]
           # if int(msg["DST"]) == int(myID) :
            #    network_output.appendleft(format_message(int(msg["DST"]), int(msg["SRC"]), 4, 1, int(msg["MNUM"]), "", "ACK"))
             #   print "received message from " + msg["SRC"] + ": " + msg["MESG"]

        #Getting registration
        elif msg["PNUM"] == "6" :

            if int(msg["PNUM"]) == messageNumberDict[msg["MNUM"]] + 1:

                recentlySeenPeers = (((msg["MESG"].split("and"))[0]).split(","))
                
                if recentlySeenPeers[0] is not None :
                    recentlySeenPeers[0] = (recentlySeenPeers[0])[-3:]

                print "***************************"
                print "Recently Seen Peers:"

                #if I am in the recently seen peers array, remove
                if myID in recentlySeenPeers :
                    recentlySeenPeers.remove(myID)

                print ','.join(recentlySeenPeers)

                listOfKnownAddressses = ((msg["MESG"].split("and"))[1]).split(",")
                for s in listOfKnownAddressses :
                    knownAddressesDict[s[:3]] = [(s[4:]).split("@")[0], (s[4:]).split("@")[1]] 

                #if I am in the known address dictionary, remove myself
                knownAddressesDict.pop(myID, None)    

                print "Known addresses:"
                for key, value in knownAddressesDict.iteritems() :
                    print key, value[0], value[1]
                print "***************************"





        # Do some things.
        return
    except IndexError:
        # No message from server.
        # Do some things - like check if a timeout has expired.
        pass
    except Exception as e:
        print("Unhandled exception: %s" % e)
        raise

    # Do we have keyboard input?
    #
    # 1) Have we handled our last message ok?  (e.g.  Did we get a response
    # back from the server and did the response make sense?) If we haven't
    # handled our last message ok, we cannot move on to new keyboard input.
    #
    # Send a message by appending it to the left side of the network_output
    # queue a the message onto the network_output queue.  E.g.
    # network_output.appendleft(mesg)
    # (Or change the code if you wish to send some other way)
    #
    # 2) If we're ready to move on, great!  Pop the next keyboard message,
    # check if it follows protocol and if so, keep going.
    # Remember to print error messages if the keyboard input does not follow
    # protocol.
    try:
        input = local_input.pop()
        # Do some things
        print "Recently Seen Peers:"
        print recentlySeenPeers

        input_message = input.split(" ")

        #step 2
        if input == "ids" : 
            network_output.appendleft(format_message(int(myID), 999, 5, 1, messageNumber, "", "get map"))
            messageNumber += 1
        #need to check for special characters in message and under 200 characters   
        
        if input_message[0] == "msg":
            

            string_message = " ".join(input_message[2:])

            #place limitations on messages to send
            string_message = string_message.translate(None, '\'\":;')
            string_message = string_message[:200] #limit to 200 characters

            #if known address, record this message
            if input_message[1] in knownAddressesDict :
                m = messageNumber #must use temp variable m because format_message increments messageNumber


                sending_message = format_message(int(myID), int(input_message[1]), 3, 1, messageNumber, "", string_message)
                messageNumber += 1
                network_output.appendleft(sending_message)
                pendingMessages[str(m)] = [sending_message, 4]

            #if address not known, start forwarding
            else : 
                dictSize = len(knownAddressesDict)
                if (dictSize <= 3) :
                    for key, value in knownAddressesDict.iteritems() :
                        sending_message = format_message(int(myID), int(input_message[1]), 3, 9, messageNumber, str(myID), string_message)

                        our_socket.sendto(sending_message, (value[0], int(value[1])))
                        pendingMessages[messageNumber] = [sending_message, 4]
                    
                    messageNumber += 1

                else : 
                    count = 3
                    for key, value in knownAddressesDict.iteritems() :
                        

                        if count > 0 :  
                            print "initiating forwarding to : " 
                            print value
                            sending_message = format_message(int(myID), int(input_message[1]), 3, 9, messageNumber, str(myID), string_message)
                            
                            count -= 1
                            
                            our_socket.sendto(sending_message, (value[0], int(value[1])))
                            pendingMessages[messageNumber] = [sending_message, 4]
                        
                    messageNumber += 1


        #step 4, serial broadcast
        if input_message[0] == "all" :
            m = messageNumber #must use temp variable m because format_message increments messageNumber

            string_message = " ".join(input_message[1:])

            #place limitations on messages to send
            string_message = string_message.translate(None, '\'\":;')
            string_message = string_message[:200] #limit to 200 characters

            for key in knownAddressesDict : 
                sending_message = format_message(int(myID), int(key), 7, 1, messageNumber, "", string_message)
                network_output.appendleft(sending_message)
                pendingBroadcastMessage[key] = [sending_message, 4]

            messageNumber += 1


        return
    except IndexError:
        # Probably do nothing, but wait.
        pass
    except Exception as e:
        print("Unhandled exception: %s" % e)
        raise
    return

def run_loop():
    global our_socket, local_input, network_input, network_output
    global timer1, timer2
    global pendingMessages
    global pendingBroadcastMessage
    global messageNumber 

    watch_for_write = []
    watch_for_read = [sys.stdin, our_socket]

     #step 1 format_message(000, 999, 1, 1, messageNumber, "", "register")
    network_output.appendleft(format_message(000, 999, 1, 1, messageNumber, "", "register"))
    messageNumber += 1

    while True:
        try:

            #sending acks
            current_time = time.time()
            #pendingMessages maps a messageNumber to tuple (message, and number Acks Left)
            # if ((current_time - timer1 >= 2) and (pendingMessages)) or ((current_time - timer2 >= 2) and pendingBroadcastMessage): 
            #     if pendingMessages : 
            #         for key, value in pendingMessages.items() :
            #             timer1 = time.time()
            #             #resend message
            #             #decrement messages left to send
            #             msg_to_send = value[0]
            #             msg = parse_message(msg_to_send)

            #             if value[1] == 0 :
                            
            #                 print "ERROR: Gave up sending to " + msg["DST"]
            #                 del pendingMessages[key]

            #             elif value[1] == -1 :
            #                 del pendingMessages[key]

            #             else : 
            #                 print "num acks left = " + str(value[1])
            #                 print "resending message " + msg_to_send

            #                 sendingPort = knownAddressesDict[msg["DST"]]
            #                 value[1] -= 1
            #                 our_socket.sendto(msg_to_send, (sendingPort[0], int(sendingPort[1])))

            #     if pendingBroadcastMessage : 
            #         for key, value in pendingBroadcastMessage.items() :
            #             timer2 = time.time()
            #             #resend message
            #             #decrement messages left to send
            #             msg_to_send = value[0]
            #             msg = parse_message(msg_to_send)

            #             if value[1] == 0 :
                            
            #                 print "ERROR: Gave up sending to " + key
            #                 del pendingBroadcastMessage[key]

            #             elif value[1] == -1 :
            #                 del pendingBroadcastMessage[key]

            #             else : 
            #                 print "num acks left = " + str(value[1])
            #                 print "resending message " + msg_to_send

            #                 sendingPort = knownAddressesDict[str(key)]
            #                 value[1] -= 1
            #                 our_socket.sendto(msg_to_send, (sendingPort[0], int(sendingPort[1])))

            # Use select to wait for input from either stdin (0) or our
            # socket (i.e.  network input).  Select returns when one of the
            # watched items has input, or has outgoing buffer space or has
            # an error.
            if len(network_output) > 0:
                watch_for_write = [our_socket]
            else:
                watch_for_write = []
            input_ready, output_ready, except_ready = select.select(watch_for_read, watch_for_write, watch_for_read, 3)    
            
            for item in input_ready:
                if item == sys.stdin:
                    data = sys.stdin.readline().strip()
                    if len(data) > 0:
                        print("Received local input: %s" % data)
                        local_input.appendleft(str(data)) 
                    else:
                        pass
                if item == our_socket:
                    data = our_socket.recvfrom(1024)

                    

                    if len(data[0]) > 0:
                        print("Received from network: %s" % data[0])

                        msg = parse_message(data[0])

                        #if receive a message, send ack
                        if msg["PNUM"] == "3" :
                            print "received a message from somone"
                            print myID
                            print msg["DST"]
                            #If I am destination, send ack
                            if int(msg["DST"]) == int(myID) :
                                our_socket.sendto(format_message(int(msg["DST"]), int(msg["SRC"]), 4, 1, int(msg["MNUM"]), "", "ACK"), data[1])
                                messageNumber += 1
                                print "Received message from " + msg["SRC"] + ": " + msg["MESG"]
                                print "sending ack"

                            #step 5 forwarding    
                            else :

                                if int(msg["HCT"]) > 0 :
                                    vl = msg["VL"].split(",")
                                    #if I'm already in the list
                                    if str(myID) in vl :
                                        print "************"
                                        print "Dropped message from " + msg["SRC"] + " to " + msg["DST"] + " - peer revisited"
                                        print "MESG: " + msg["MESG"]

                                    else : 

                                        dictSize = len(knownAddressesDict)
                                        if (dictSize <= 3) :
                                            for key, value in knownAddressesDict.iteritems() :
                                                print "forwarding to " + key
                                                print "sending port is "
                                                print value

                                               
                                                our_socket.sendto(format_message(int(msg["SRC"]), int(msg["DST"]), int(msg["PNUM"]), int(msg["HCT"])-1, int(msg["MNUM"]), msg["VL"] + "," + str(myID), msg["MSG"]), (value[0], int(value[1])))
                                                #pendingMessages[msg["MNUM"]] = [value[1], 4]
                                        else : 
                                            count = 3
                                            for key, value in knownAddressesDict.iteritems() :
                                                if count > 0 :
                                                    print "forwarding to " + key
                                                    print "sending port is "
                                                    print value
                                                    our_socket.sendto(format_message(int(msg["SRC"]), int(msg["DST"]), int(msg["PNUM"]), int(msg["HCT"])-1, int(msg["MNUM"]), msg["VL"] + "," + str(myID), msg["MSG"]), (value[0], int(value[1])))
                                                    count -= 1
                                                    #pendingMessages[msg["MNUM"]] = [value[1], 4]
                                else :
                                    print "************"
                                    print "Dropped message from " + msg["SRC"] + " to " + msg["DST"] + " - hop count exceeded"
                                    print "MESG: " + msg["MESG"]
                                


                        #if receive an ack, remove the message from pendingMessages
                        elif msg["PNUM"] == "4" :

                            if int(msg["PNUM"]) == messageNumberDict[msg["MNUM"]] + 1:

                                print "received ack, will stop resending now"
                                if msg["MNUM"] in pendingMessages :  
                                    print "mnum is " + msg["MNUM"]
                                    message = parse_message((pendingMessages[msg["MNUM"]])[0])
                                    print message["DST"]
                                    if int(msg["DST"]) == int(message["SRC"]) and int(msg["SRC"]) == int(message["DST"]) :
                                        print "removing from pendingMessages"
                                        del pendingMessages[msg["MNUM"]]


                        #if receive a broadcast, send ack
                        elif msg["PNUM"] == "7" :
                            print "received a broadcast from somone"
                            print myID
                            print msg["DST"]
                            #If I am destination, send ack
                            if int(msg["DST"]) == int(myID) :
                                our_socket.sendto(format_message(int(msg["DST"]), int(msg["SRC"]), 8, 1, int(msg["MNUM"]), "", "ACK"), data[1])
                                messageNumber += 1
                                print "*********************"
                                print "SRC:" + msg["SRC"] + " broadcasted:" + msg["MESG"]
                                print "sending ack"

                        #if receive an ack
                        # elif msg["PNUM"] == "8" :

                        #                 if int(msg["PNUM"]) == messageNumberDict[msg["MNUM"]] + 1:

                        #     if msg["SRC"] in pendingBroadcastMessage : 
                        #         message = parse_message((pendingBroadcastMessage[msg["SRC"]])[0])
                        #         if int(msg["DST"]) == int(myID) and int(msg["SRC"]) == int(message["DST"]) and msg["MNUM"] == message["MNUM"]:
                        #             print "ugh"
                        #             del pendingMessages[(msg["SRC"])] 

                        #add network messages to input
                        else :
                            print "hi" + data[0]
                            network_input.appendleft(data)
                    else:
                        our_socket.close()
                        return
            
            # Though the amount of data you are writing to the socket will
            # not overload the outgoing buffer...it is good practice to
            # only write to sockets when you know their outgoing buffer
            # is not full.
            for item in output_ready:
                if item == our_socket:
                    try:
                        msg_to_send = network_output.pop()
                        print msg_to_send
                        # Normally you want to check the return value of
                        # send() to make sure you were able to send all the
                        # bytes.  Our messages are so short, we don't bother
                        # doing that here."SRC:000;DST:999;PNUM:1;HCT:1;MNUM:100;VL:;MESG:register"

                        msg = parse_message(msg_to_send)
                        #if sending to the server
                        if msg["DST"] == "999" : 
                            our_socket.sendto(msg_to_send, ('steel.isi.edu', 63682))

                        elif 1 <= int(msg["DST"]) <= 998:
                            if msg["DST"] in knownAddressesDict : 
                                sendingPort = knownAddressesDict[msg["DST"]]
                                print sendingPort
                                our_socket.sendto(msg_to_send, (sendingPort[0], int(sendingPort[1])))

                            else :
                                print "not in dictionary"
                        else :
                            print "Invalid Destination"
                    except IndexError:
                        pass
                   
                    except Exception as e:
                       print("Unhandled send exception: %s" % e)
            
            for item in except_ready:
                if item == our_socket:
                    our_socket.close()
                    return
        
        # Catch ^C to cancel and end program.
        except KeyboardInterrupt:
            our_socket.close()
            return
        #except Exception as e:
            print("Unhandled exception 0: %s" % e)
            return
        handle_io()

def connect_to_server():
    global our_socket
    # steel.isi.edu:63682,
    #server_address = ('steel.isi.edu', 63682)
    #our_socket.connect(server_address)

   
    return

if __name__ == "__main__":
    connect_to_server()
    run_loop()

     
