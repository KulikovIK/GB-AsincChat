import pytest
from socket import *

from ..src.core.message_processor import MessageProcessor
from client import Client


@pytest.fixture
def socket():
    socket = socket(AF_INET, SOCK_STREAM)
    socket.bind(('localhost', 7890))
    yield socket
    socket.close()


@pytest.fixture
def client():
    client = Client(host='localhost', port=7890)
    yield client
    

@pytest.fixture
def responce():
    msg = MessageProcessor.create_presence_message('Guest')
    yield msg


def test_server_connect(socket):
    socket.connect(('localhost', 7890))
    assert socket