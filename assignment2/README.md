1.) authenticated diffie-hellman  
both parties know each other pk   
send the parts of shared symmetric key over the network in order to establish shared symmetric key  
The key must be digitally signed before being send  
Each party then verifies that the key indeed comes from the other party   
and then uses this key as the one to encrypt messages  
2.) calculations over network  
both parties start sending digitally signed messages over network  
in each turn, first the thrower declares their throw and sends its hashed form to another party  
then the other party sends their throw to the first party  
then the first party sends decryption key to allow first party to see the result of the throw  
then both parties calculate the throw by (a +/* b) mod 6

## Running the code

