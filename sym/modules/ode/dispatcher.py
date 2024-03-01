import json
from dataclasses import dataclass
from sym.modules.ode.envelope import OdeEnvelope
 

@dataclass
class OdeDispatcher:

    async def dispatch(self, envelope:OdeEnvelope=None, payload=None):
        pass

    async def send_message(self):
        pass

    async def recieve_message(self):
        pass


@dataclass
class OdeDispatcherWebsocket:

    websocket = None

    async def dispatch(self, envelope, payload=None):
        
        d = envelope.to_dict()
        if payload:
            d["return_payload"] = payload
        print("dispatching message", d)
        _ = await self.send_message(json.dumps(d))

    async def send_message(self, msg):
        print("sending message", msg)
        _ = await self.websocket.send_text(msg)

    #recieve from client -> runner
    async def recieve_message(self, message=None):
        data = await self.websocket.receive_text()
        return data