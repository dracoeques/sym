import unittest
from unittest.mock import Mock
from sym.modules.ode.router import Action
from sym.modules.ode.payload import OdeEnvelope
from sym.modules.ode.dispatcher import OdeDispatcher
from sym.modules.db.models import User, Profile

from sym.modules.ode.payload import OdeSender
from sym.modules.ode.routes import handle_read_me

class TestHandleReadMe(unittest.IsolatedAsyncioTestCase):
    async def test_handle_read_me(self):
        # Mock the necessary objects
        envelope = Mock(spec=OdeEnvelope)
        dispatcher = Mock(spec=OdeDispatcher)
        session = Mock()  # Assuming Session doesn't have any required methods for this test

        # Set up the envelope.sender object
        user = {'first_name': 'John Doe', 'email': 'john@example.com'}
        profile = {'age': 30, 'address': '123 Main St'}
        sender = OdeSender.from_dict({'role': 'user', 'user': user, 'profile': profile})
        envelope.sender = sender

        # Mock the dispatch method to return a specific value
        dispatcher.dispatch.return_value = 'Dispatched'

        # Call the handler
        result = await handle_read_me(envelope, dispatcher, session)

        # Check the result
        self.assertEqual(result, 'Dispatched')
        
        # Check that the dispatch method was called with the correct data
        #TODO: consider how to test this, the payload needs to be accessible to the test
        #dispatcher.dispatch.assert_called_once_with(envelope, user)

if __name__ == '__main__':
    unittest.main()