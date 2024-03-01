
#Test that we can stream responses to the websocket
#and wait for the next response (text input)
#before continuing to the next node
#or - load the promptflow each request from db
#then re-save allowing for a more 'stateless' approach
#and solves the issue of disconnect / reconnect


#TODO: how to encode the logic where we expect the next input from the user
#then proceed forward until we either get another input, or end the chain

#text input -> ask a queston -> get response, store response, -> proceed to next item