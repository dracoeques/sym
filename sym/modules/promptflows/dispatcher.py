import json, logging
from dataclasses import dataclass

from sym.modules.promptflows.envelope import PromptFlowEnvelope

@dataclass
class MessageDispatcher:
    
    async def send_message(self):
        pass

    async def recieve_message(self):
        pass


@dataclass
class MessageDispatcherSimulated:
    """ Simulates message dispatching"""

    last_envelope_sent = None
    last_message_sent = None

    last_envelope_recieved = None
    last_message_recieved = None

    #send from runner -> client
    async def send_message(self, envelope:PromptFlowEnvelope=None):
        self.last_envelope_sent = envelope
        message = envelope.to_dict()
        print(f"Sending: {message}")
        self.last_message_sent = message
        return message

    #recieve from client -> runner
    async def recieve_message(self, message=None):
        envelope_json = json.loads(message)
        envelope = PromptFlowEnvelope().from_dict(envelope_json)
        self.last_envelope_recieved = envelope
        self.last_message_recieved = message
        return envelope


@dataclass
class MessageDispatcherWebsocket:
    """ Streams messages to and from a websocket"""

    websocket = None


    #send from runner -> client
    async def send_message(self, envelope:PromptFlowEnvelope=None):
        message = envelope.to_dict()
        message_str = json.dumps(message)
        #print(message_str)
        await self.websocket.send_text(message_str)

    #recieve from client -> runner
    async def recieve_message(self, message=None):
        data = await self.websocket.receive_text()
        envelope_json = json.loads(data)
        envelope = PromptFlowEnvelope().from_dict(envelope_json)
        return envelope
