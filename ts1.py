'''
@author: Karun Kanda (kk951)
@author: Shila Basu (sb1825)
'''

import time, random, socket, sys

'''
create_tsdns_table takes in no arguments and returns a dictionary containing the information found in
PROJ2-DNSTS.txt.

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
ts_1_server() takes in no arguments and houses the logic behind the ts_1 server. Upon starting the TS server logic it will create a table which will
hold all the hostnames that is contained for this TS server. This TS server is used to see if the requested hostname matches it.

Purpose: Upon recieving a hostname from the LS server. The TS server will see if there is match within its hostname table. If there is a match within its
table then it will immediately send a response back to the LS server and close the connection. Otherwise the TS server will keep going until the LS server
closes the connection based on its timeout.
'''
def ts_1_server():
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
This is the main method of ts_1.py where ts_1.py is expecting two arguments to start (python ts_1.py) and (the portnumber)
to start successfully.
'''
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Incorrect Usage: python ts_1.py <port number>")
        sys.exit(1)
    ts_1_server()