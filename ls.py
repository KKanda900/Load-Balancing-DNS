import select, socket, sys
import time


HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = int(sys.argv[1])        # Port to listen on (non-privileged ports are > 1023)
TS1_HOST = sys.argv[2]
TS1_PORT = int(sys.argv[3])
TS2_HOST = sys.argv[4]
TS2_PORT = int(sys.argv[5])
TS_TIMEOUT = 5
t_start = -1

class ClientRequest:
    time_start = -1
    response = ''
    def __init__(self,time,resp):
        self.time_start = time
        self.response = resp
    def __str__(self):
        return "Start Time: " + str(self.time_start) + " Response: " + str(self.response)

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


if __name__ == '__main__':


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

        #print(time.perf_counter())


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
                        #print("Reading TS:", data)

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
                    print("CONNECTIN LOST")
                    if s in outputs:
                        outputs.remove(s)
                    inputs.remove(s)
                    s.close()
                    msg_queues[s].clear()

                #print(ip_requests)

        for s in writable:
            #send data for every socket in writable
            if (not msg_queues[s].empty()):
                #print(msg_queues[s].queue_list)
                next_msg = msg_queues[s].get()



                if s is client:

                    cr = ip_requests[next_msg]
                    #print("Writeable Client Request",cr)
                    # Check to see if ip_requests has been fulfilled
                    #If not, check the timestamp in ip_requests to see if it has timed out
                    #If not, place it back in the queus and try later
                    if cr.response != b'':
                        #print("Response for:", next_msg)
                        s.send(cr.response)
                        print()
                        print("Sending response to client", cr.response)
                    elif (time.time() - cr.time_start) > TS_TIMEOUT:
                        #print("Time out:", next_msg)
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


