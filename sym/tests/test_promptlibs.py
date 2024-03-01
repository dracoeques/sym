import json
import unittest

from sym.modules.promptlibs.core import parse_promptlib_variables, replace_with_var_name

class TestPromptLib(unittest.TestCase):

    def test_promptlib_variables1(self):

        expected = [{
            "variable_name":"variable_name",
            "options":["option1","option2","option3"],
        }]

        text = "This is a test {variable_name|option1,option2,option3} to check the function."

        options = parse_promptlib_variables(text)

        assert expected == options, f"Error: expected does not match response, {options}"
    
    def test_promptlib_variables2(self):

        expected = [{
            "variable_name":"animals",
            "options":["birds","bees","dogs"],
        },
        {
            "variable_name":"plants",
            "options":["herbs","trees","fruits"],
        }]

        text = "This is a test {animals|birds,bees,dogs} to check the {plants|herbs,trees,fruits}  function."

        options = parse_promptlib_variables(text)

        assert expected == options, f"Error: expected does not match response, {options}"


    def test_parse_promptlib_text1(self):
        expected = "This is a test {animals} to check the {plants}  function."

        text = "This is a test {animals|birds,bees,dogs} to check the {plants|herbs,trees,fruits}  function."

        received = replace_with_var_name(text)

        assert expected == received, f"Error: expected does not match response, {received}"
    
    def test_parse_promptlib_text2(self):
        expected = "This is a test {animals} to check the {plants}  function."

        text = "This is a test {animals} to check the {plants}  function."

        received = replace_with_var_name(text)

        assert expected == received, f"Error: expected does not match response, {received}"

if __name__ == "__main__":
    unittest.main()