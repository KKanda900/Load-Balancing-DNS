'''
@author: Karun Kanda (kk951)
@author: Shila Basu (sb1825)
'''

import select, socket, sys, time

HOST = ''  # Standard loopback interface address (localhost)
PORT = int(sys.argv[1])  # Port to listen on (non-privileged ports are > 1023)
TS1_HOST = sys.argv[2] # TS1 hostname
TS1_PORT = int(sys.argv[3]) # TS1 port number
TS2_HOST = sys.argv[4] # TS2 hostname
TS2_PORT = int(sys.argv[5]) # TS2 port number
TS_TIMEOUT = 5 # time out for both the TS servers
t_start = -1 # start time for getting the response

'''
ClientRequest class

Description: A class to store the client requests and help enable to send a response within a certain amount of time.
Then give the response back via the LS server socket.
'''
class ClientRequest:
    time_start = -1
    response = ''
    def __init__(self,time,resp):
        self.time_start = time
        self.response = resp
    def __str__(self):
        return "Start Time: " + str(self.time_start) + " Response: " + str(self.response)

'''
MsgQueue class

Description: A class to store the messages the LS server recieves from the TS servers to send back later to the 
client.
'''
class MsgQueue:

    def __init__(self):
        self.queue_list = []

    def put(self, entry):
        self.queue_list.insert(0,entry)

    def get(self):
        return self.queue_list.pop()

    def empty(self):
        return len(self.queue_list) == 0

    def clear(self):
        self.queue_list = []

'''
ls_server takes in no arguments and holds the main logic behind the LS server. Upon starting the main logic of the LS server it creates the LS server socket and 
the two client sockets to connect to the TS servers. Something new about these connections are they are set with timeouts because we don't want to over work the 
connection between the client and the server. 

The purpose of this method is to get the requested response from the TS servers according to who has the information the client needs. The LS server gets the requested
hostname from the client and sends it to the TS_1 server and TS_2 server. Then according to the timeout whoever has the information that information from the recv call 
is stored into a reply type variable which is sent back in the form:
Hostname IP Address A
Then if there is no response from either TS_1 or TS_2 the LS server sends back:
ERROR:Host Not Found
Right at the end of the requesting process.
'''
def ls_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(0)
    server.bind((HOST, PORT))
    server.listen(1)

    ts1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ts1.settimeout(TS_TIMEOUT)
    ts1.connect((TS1_HOST, TS1_PORT))

    ts2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ts2.settimeout(TS_TIMEOUT)
    ts2.connect((TS2_HOST, TS2_PORT))

    client = None
    inputs = [server,ts1,ts2] #List sockets to wait for
    outputs = []
    msg_queues = {}
    msg_queues[ts1] = MsgQueue()
    msg_queues[ts2] = MsgQueue()

    ip_requests = {}

    while inputs:
        readable, writable, exceptional = select.select(
            inputs, outputs, [],TS_TIMEOUT)

        for s in readable:
            if s is server:
                #Connect to client
                client, client_address = s.accept()
                client.setblocking(0)
                inputs.append(client) #Add input for client msgs
                msg_queues[client] = MsgQueue()
                print("Established Connection:",client_address)
            else:
                #Read incoming data
                print()
                print("Receiving Message.....")
                data = s.recv(1024)

                if data:
                    if s is client:
                        #Request for ip has been sent from client
                        #Set ts1 and ts2 sockets for writing
                        outputs.append(ts1)
                        outputs.append(ts2)

                        #Add messages to queue
                        msg_queues[ts1].put(data)
                        msg_queues[ts2].put(data)

                        #Add to request list to keep track of timeouts
                        t_start = time.time()
                        ip_requests[data] = ClientRequest(t_start,b'')

                        print("Client IP Request:", data, ip_requests[data])

                        # Set client socket to keep checking for fulfilled request
                        outputs.append(client)
                        msg_queues[client].put(data)
                    else:
                        #TS1 or TS2 has sent a reply
                        #Parse the data find the domain name
                        data_str = data.decode("UTF-8").strip()
                        b_domain_str = data_str.split()[0].encode('utf-8')
                        t_start = ip_requests[b_domain_str].time_start

                        #update ip_requests to show that it has been fulfilled
                        ip_requests[b_domain_str] = ClientRequest(t_start, data)
                        print("IP Request Fulfilled:",b_domain_str,ip_requests[b_domain_str])
                else:
                    # No data from socket means no connection
                    # Clean up and close the connection
                    print("CONNECTION LOST")
                    if s in outputs:
                        outputs.remove(s)
                    inputs.remove(s)
                    s.close()
                    msg_queues[s].clear()

                #print(ip_requests)

        for s in writable:
            #send data for every socket in writable
            if (not msg_queues[s].empty()):
                next_msg = msg_queues[s].get()
                if s is client:
                    cr = ip_requests[next_msg]
                    # Check to see if ip_requests has been fulfilled
                    #If not, check the timestamp in ip_requests to see if it has timed out
                    #If not, place it back in the queus and try later
                    print(cr.response)
                    if cr.response != b'':
                        s.send(cr.response)
                        print()
                        print("Sending response to client", cr.response)
                    elif (time.time() - cr.time_start) > TS_TIMEOUT:
                        error_msg = next_msg.decode('utf-8') + " - Error:HOST NOT FOUND"
                        s.send(error_msg.encode('utf-8'))
                        del ip_requests[next_msg]
                        print()
                        print("Sending timeout error to client", next_msg + " - Error:HOST NOT FOUND")
                    else:
                        msg_queues[s].put(next_msg)
                else:
                    #Send message to TS1 or TS2
                    s.send(next_msg)
                    print("Sending to TS", next_msg.decode("UTF-8"))
            else:
                #if there are no messages for the socket remove it from the output socket list
                if (s in outputs):
                    outputs.remove(s)

'''
This is the main method of ls.py where ls.py is expecting six arguments to start successfully.
'''
if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Incorrect Usage: python ls.py <ls port number> <ts_1 hostname> <ts_1 port number> <ts_2 hostname> <ts_2 port number>")
        sys.exit(1)
    ls_server()


