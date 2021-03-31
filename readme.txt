Questions
0. Please write down the full names and netids of all your team members.

1. Briefly discuss how you implemented the LS functionality of
   tracking which TS responded to the query and timing out if neither
   TS responded.

The LS functionality implented two dictionary objects to keep track of the routed messages: one to store message queues and the other to keep track of requests.  
The message queue collection used socket objects as keys and stored all inbound data into a message queue class for each readable socket.  It then, dequeued messages for each writable socket to send to its final destination. Upon a client request, LS would store the start time and hostaname into a data collection referenced by the inbound message. LS would then start polling this collection which would bring about one of the follwong outcomes:
    a) If TS1 of TS2 sends a reply, LS would update the client request data strcuture with the reply message and source.  On the next polling iteration, it would then read the reply from this data structure and relay it to the client.
    b) If the client request structure has no reply and the current time is greater than five seconds from the start time, LS sends back "Hostname - Error:HOST NOT FOUND" to the client
    c) If the client request structure has no reply and the current time is less than five seconds from the start time, LS will add the message back to the queue and wait for the next iteration to poll again.

   
2. Are there known issues or functions that aren't working currently in your
   attached code? If so, explain.
   
All fucntions of the project should be working according to the given specifications.
   
3. What problems did you face developing code for this project?

The main problems came when debugging the code and dealing with blocking sockets.  For each issuse encountered, all four processes had to be restarted in order and the TS servers required restarts for each terminal session. There was also an issue when LS read the client socket in a deleyed manner. All the messages piled up in the socket, leading LS to read one large message with the hostanames concatenated together.

4. What did you learn by working on this project?

Using batch scripts were useful in saving time while debugging the code.  Also, implementing a number of print statements to benchmark the execution flow allowed for us to catch errors and debug the code in real-time. Lastly, we learned how the select.select function worked.  After calling it with a list of input and output sockets, it returned a list of all readable and writeable sockets once it was triggered by an event on one of the sockets.
  