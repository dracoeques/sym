from sym.modules.ode.interface import OpportunityDiscoveryEngineInterface
from sym.modules.ode.persistence import OdePersistence
from sym.modules.ode.dispatcher import OdeDispatcherWebsocket

import logging
logging.basicConfig(level=logging.INFO)


async def ode_websocket_run(session, websocket, rawmsg=None):
    """ Default run using a websocket and a DB session"""
    

    await websocket.accept()

    dispatcher = OdeDispatcherWebsocket()
    dispatcher.websocket = websocket

    persistence = OdePersistence()
    persistence.session = session

    #load and initialize an ode interface
    ode_interface = OpportunityDiscoveryEngineInterface(persistence=persistence, dispatcher=dispatcher)

    while True:
        rawstr = await websocket.receive_text()
        print("Received message:", rawstr)
        response = await ode_interface.run(rawstr=rawstr, session=session)
        
        #addtional logging or error handling here
        #logging.info("ODE response:", response)
        print("ODE response:", response)