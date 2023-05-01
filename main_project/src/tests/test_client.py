import unittest
from client import Client, _DESCRIPTOR
from core.get_app_arguments import get_app_arguments


class ClientTest(unittest.TestCase):
    """
    Тесты клиента
    """
    
    
    def setUp(self) -> None:
        self.args = get_app_arguments(_DESCRIPTOR)

    def tearDown(self) -> None:
        pass

    def test_parse_response(self):
        pass

    def test_send_message(self):
        pass


if __name__ == '__main__':
    unittest.main()