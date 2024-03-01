import logging
from dataclasses import dataclass
from typing import Any

from sym.modules.ode.envelope import OdeEnvelope,OdePayload, OdeSender
from sym.modules.ode.persistence import OdePersistence
from sym.modules.ode.dispatcher import OdeDispatcher


from sym.modules.auth.core import authenticate_ws_user, InvalidAuth
from sym.modules.auth.profile import validate_user_profile

from sym.modules.ode.routes import action_route_registry, Action


@dataclass
class OpportunityDiscoveryEngineInterface:

    persistence: OdePersistence = None
    dispatcher: OdeDispatcher = None

    async def run(self, rawstr:str = None, session: Any = None):
        """ Main function, run the request"""

        #parse input
        ode_envelope = OdeEnvelope().from_str(rawstr)

        #run auth
        try:
            u = authenticate_ws_user(session, ode_envelope)
            sender = OdeSender()
            sender.name = u.username
            sender.role = "user"
            if ode_envelope.profile_id:
                p = validate_user_profile(session, u.id, ode_envelope.sender.profile.id)
                if p is None:
                    err = f"Invalid profile: {ode_envelope.profile_id} for user id: {u.id}"
                    _ = await self.invalid_auth_response(ode_envelope, err)
                    return err
                sender.profile = p
            ode_envelope.sender = sender
        except InvalidAuth as ia:
            _ = await self.invalid_auth_response(ode_envelope, ia)
            return ia
        except Exception as e:
            raise e

        #run access control logic
        #... todo

        #route to function using decorator pattern
        action = ode_envelope.action
        route = ode_envelope.route  
        action_enum = getattr(Action, action, None)

    
        
        
        for (registered_action, registered_pattern), handler in action_route_registry.items():
            print(action_enum, registered_action, registered_pattern)
            if action_enum == registered_action and registered_pattern:
                match = registered_pattern.match(route)
                if match:
                    # Extract parameters from the route
                    params = match.groupdict()
                    # Apply basic type conversion based on the type annotations
                    # Note: For simplicity, we're assuming the handler functions are annotated with the correct types
                    for param, value in params.items():
                        # Determine the expected type from the handler function annotations
                        # Default to str if no annotation is found
                        expected_type = handler.__annotations__.get(param, str)
                        # Convert the parameter to the expected type
                        params[param] = expected_type(value)
                    err = await handler(ode_envelope, self.dispatcher, session, **params)
                    if err:
                        return self.error_response(ode_envelope, err)
            else:
                # TODO: Handle unknown action/route combination
                print("No handler for action:", action, action_enum, "and route:", route)
                #logging.error("No handler for action:", action, action_enum, "and route:", route)

        # handler = action_route_registry.get((action_enum, route))
        # if handler:
        #     err = await handler(envelope=ode_envelope, dispatcher=self.dispatcher)
        #     if err:
        #         return self.error_response(ode_envelope, err)
        # else:
        #     # TODO: Handle unknown action/route combination
        #     logging.error("No handler for action:", action, action_enum, "and route:", route)



    


    def build_envelope(self, 
            action:str=None,
            route:str=None,

            authtoken:str=None,

            #ui routing
            thread_id:int=None,
            thread_column:int=None,
            thread_item_id:int=None,

            #payload convenience
            payload:OdePayload=None,
            payload_type:str=None,
            key:str=None,
            value:str=None,


            #sender convenience
            sender:OdeSender=None,
            sender_name: str = None,
            sender_role: str = None,
            sender_profile: dict[str:Any] = None,
        ):
        """ convenience function, will build an envelope

        """
        e = OdeEnvelope()

        e.action = action
        e.route = route
        
        #handle payload build
        e.payload_type = payload_type
        if payload:
            e.payload = payload
        else:
            payload = OdePayload(key=key, value=value)
            e.payload = payload
        
        e.thread_id = thread_id
        e.thread_column = thread_column
        e.thread_item_id = thread_item_id

        #optional auth (likely empty
        # )
        e.authtoken = authtoken

        #Sender logic
        if sender:
            e.sender = sender
        else:
            sender = OdeSender()
            sender.name = sender_name
            sender.role = sender_role
            sender.profile = sender_profile

            e.sender = sender
        
        return e


    async def invalid_auth_response(self, ode_envelope, ia):

        e = self.build_envelope(
            sender_name="system",
            sender_role="system",
            payload_type="error",
            key="auth_error",
            value=str(ia),


        )

        print("invalid auth response", e.to_dict())
        _ = await self.dispatcher.dispatch(e)

    async def error_response(self, ode_envelope, msg):
        e = self.build_envelope(
            sender_name="system",
            sender_role="system",
            payload_type="error",
            key="error",
            value=msg,
        )
        _ = await self.dispatcher.dispatch(e)