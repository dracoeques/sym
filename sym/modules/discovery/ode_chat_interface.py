import json
from dataclasses import dataclass, asdict

from sym.modules.auth.core import authenticate_ws_user
from sym.modules.auth.profile import get_default_profile

from sym.modules.discovery.core import chat_with_media_item

@dataclass
class ODE_Payload():
    authtoken: str = None
    sender: str = None
    action: str = None
    payload: dict = None 
    error: str = None

    def to_dict(self):
        return asdict(self)

    def from_dict(self, payload):
        return ODE_Payload(**payload)


@dataclass
class ODE_Chat():
    
    ws = None
    session = None
    rawmsg: str = None
    envelope: ODE_Payload = None
    user = None

    async def init(self):
        """ Initialize and prepare class """

        #parse rawmessage -> ODE_Payload
        #TODO: handle json exceptions
        d = json.loads(self.rawmsg)
        self.envelope = ODE_Payload.from_dict(d)


    async def run(self):
        """ Main function, routes actions -> subroutines"""
        if self.envelope.action == "media_item_prompt":
            self.media_item_prompt()
        else:
            err_payload = ODE_Payload(error=f"Action: {self.envelope.action} is undefined")
            self.send(err_payload)

    async def send(self, ode_payload):
        ode_payload.sender = "system"
        d = ode_payload.to_dict()
        await self.ws.send_text(json.dumps(d))

    async def authenticate(self):
        #TODO: handle exceptions
        self.user = authenticate_ws_user(self.session, self.envelope)
        self.profile = get_default_profile(self.session, self.user.id)
    
    async def media_item_prompt(self):
        """ Chat with a media item"""
        payload = self.envelope.payload
        if "id_media_item" in payload:
            id_media_item = payload["id_media_item"]
        else:
            #TODO: throw error
            pass

        if "message" in self.envelope.payload:
            prompt = self.envelope.payload["message"]
        else:
            pass

        #TODO: stream responses async
        text = chat_with_media_item(
                prompt=prompt,
                item_id=id_media_item,
                session=self.session,
                id_profile=self.profile.id,
        )
        
        #send this over the websocket
        payload = ODE_Payload()
        payload.action = "media_item_prompt_response"
        payload.payload = {
            "id_media_item":id_media_item,
            "prompt":prompt,
            "response":text,
        }
        self.send(payload)