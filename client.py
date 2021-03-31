'''
@author: Karun Kanda (kk951)
@author: Shila Basu (sb1825)
'''

import time, random, socket, sys, os

f = None

'''
query_hostname_table takes in no arguments and returns a dictionary containing all the hostnames to be
queried held in PROJ2-HNS.txt.

The purpose of this method is to store everything in a dictionary so that when it comes to requesting information
it can pop one element at a time to check with the LS server to check if it can request the information that its looking for.
'''
def query_hostname_table():
    file = open("PROJ2-HNS.txt", "r")
    hostnames_queries = file.read().splitlines()
    file.close()

    for i in range(len(hostnames_queries)):
        hostnames_queries[i] = hostnames_queries[i].lower()
        
    return hostnames_queries

'''
client takes in no arguments and does not return anything because this is where the main logic of the program
is going to be held. Upon start it will create a dictionary containing all the hostnames that need to be queried.
Then looping through all the names it will pop one at a time and send it to the LS server and see where its information lies.

The purpose of this method is to host the knowledge of the client application. One hostname at a time will be popped from the
dictionary of hostnames and sent to the LS server. If the LS server found the requested information it will provide the
client a A flag and all the client will do is stop and print what it recieved.  Otherwise, if the TS servers
did not find its information it will output:
    Hostname - Error:Host not found
Then close the client after all the hostnames have been popped.
'''
def client():
    # initial setup for the client side
    try:
        cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as err:
        print('socket open error: {} \n'.format(err))
        exit()

    port = int(sys.argv[2])
    localhost_addr = socket.gethostbyname(sys.argv[1])

    server_binding = (localhost_addr, port)
    print("Local Address {} and Port Number {}".format(localhost_addr, port))
    cs.connect(server_binding)
    cs.settimeout(10)

    # first task of client is to query the table and send all the queried hostnames to the ls server
    hostnames = query_hostname_table()

    while len(hostnames) != 0:
        queried_hostname = hostnames.pop(0)
        try:
            cs.send(queried_hostname.encode('utf-8'))
            server_message = cs.recv(1024)
            f.write(server_message + "\n")
        except socket.timeout as e:
            print(e)
        else:
            print(server_message.decode("utf-8"))

    f.close()
    cs.close()
    exit()

'''
This is the main method that will expect four arguments from the user to start the application
otherwise it will return an error.
'''
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Incorrect Usage: python client.py <LS hostname> <LS server port number>")
        sys.exit(1)

    if os.path.exists('RESOLVED.txt') == True:
        open('RESOLVED.txt', 'w').close()
        f = open("RESOLVED.txt", "a") # create the file we are going to write to
    else:
        f = open("RESOLVED.txt", "a") # create the file we are going to write to

    client()
