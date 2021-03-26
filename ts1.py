
'''
@author:
@author: Shila Basu ()
'''

import time
import random
import socket, sys

'''
create_tsdns_table takes in no arguments and returns a dictionary containing the information found in
PROJI-DNSTS.txt.

The purpose of this method is to create a table that the TS server can iterate through to provide the connected
client the information its looking for. Otherwise if the information can't be found it will be give it an
error and send the error string back to the client.
'''

def create_tsdns_table():
    tsdns_table = {}

    file = open("PROJ2-DNSTS1.txt", "r")
    dns_list = file.read().splitlines()
    file.close()


    for dd in dns_list:
        domain = dd.split(' ')[0]
        tsdns_table[domain] = dd

    return tsdns_table

'''
check_hostname_table takes in two arguments queried_hostname and table (the table containing the information
created in the method create_tsdns_table()) and returns a column from the table or an error if the hostname couldn't
be found.

The purpose this table is to check if the given hostname can be found in the TS server otherwise if it can't
be found in the TS table just provide it a Error string that the client will recieve. If a match is found in this server
it will do return a similar result like in RS server returning back:
    Hostname IP Address A
Otherwise if a match can not be found it will return the following error string:
    Hostname - Error:HOST NOT FOUND
Where no matter the results the client will print the respective string back so the user can interpet the
results to their liking.
'''
# def check_hostname_table(queried_hostname, table):
#     for i in range(0, len(table)):
#         if table[i][0].lower() == queried_hostname.lower():
#             return '{} {} {}'.format(table[i][0], table[i][1], table[i][2])
#
#     return '{} - Error:HOST NOT FOUND'.format(queried_hostname)

'''
ts_server takes in no arguments and returns nothing because this is where the main logic of the TS server will lie.
Upon start the TS server will create a table that will be used when the client requests information from the server
upon connecting to it.

The purpose of the method is to house the logic of the TS server. First the table will be created but unlike the RS server
the TS server has a possibility of never being connected to so there is a chance that the TS server will continuely be waiting
for a client to connect to it. Upon connection the given hostname is compared to the table given and provide it the information that
it is looking for otherwise give the client an error message. Like the RS server, the socket used to create the server
will be resusable so in case more clients would like to request information.
'''
def ts_server():
    # initial setup for the server side
    try:
        ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print("[S]: Server socket created")
    except socket.error as err:
        print('socket open error: {}\n'.format(err))
        exit()

    server_binding = ('', int(sys.argv[1]))
    ss.bind(server_binding)
    ss.listen(1)


    host = socket.gethostname()
    localhost_ip = (socket.gethostbyname(host))
    csockid, addr = ss.accept()
    # check if we recieved a connection or not
    print("[S]: Got a connection request from a client at {}".format(addr))

    # setting up the dns table on the TS server side
    table = create_tsdns_table()

    while True:
        # get the input from the client
        b_queried_hostname = csockid.recv(1024)
        queried_hostname = b_queried_hostname.decode('utf-8')

        # next TS should look into its respective table and send what it finds back to the client
        if queried_hostname in table.keys():
            b_dns_entry = table[queried_hostname].encode('utf-8')
            csockid.sendall(b_dns_entry)
            print("Sent: ",b_dns_entry)

    ss.close()
    exit()

'''
This is the main method of ts.py where ts.py is expecting two arguments to start (python ts.py) and (the portnumber)
to start successfully.
'''
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Incorrect Usage: python ts.py <port number>")
        sys.exit(1)
    ts_server()