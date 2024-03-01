import json
import unittest

from jinja2 import Environment, BaseLoader


class TestTemplates(unittest.TestCase):

    def test_template(self):

        # Create a dictionary of values
        data = {
            'name': 'Blorkus',
            'weather': 'sunny'
        }

        expected = "Hello Blorkus! Today's weather is sunny."

        # Define the template string
        template_str = "Hello {{ name }}! Today's weather is {{ weather }}."

        # Set up the Jinja2 environment
        env = Environment(loader=BaseLoader)

        # Use the template string as the template
        template = env.from_string(template_str)

        # Render the template with the data dictionary
        output = template.render(data)


        assert expected == output, f"Error: expected does not match output, {output}"
    
if __name__ == "__main__":
    unittest.main()