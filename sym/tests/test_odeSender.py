import unittest

from sym.modules.ode.payload import OdeSender

class TestOdeSender(unittest.TestCase):
    def test_from_dict(self):
        data = {
            'role': 'admin',
            'user': {'first_name': 'JohnDoe', 'email': 'john@example.com'},
            'profile': {'id': 30, 'name': '123t'}
        }


        sender = OdeSender.from_dict(data)

        self.assertEqual(sender.role, 'admin')
        self.assertEqual(sender.user.first_name, 'JohnDoe')
        self.assertEqual(sender.user.email, 'john@example.com')
        self.assertEqual(sender.profile.id, 30)
        self.assertEqual(sender.profile.name, '123t')

if __name__ == '__main__':
    unittest.main()