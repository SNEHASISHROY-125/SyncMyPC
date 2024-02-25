import unittest
from unittest.mock import patch
import server
import client

class TestServer(unittest.TestCase):
    def test_start_server(self):
        # Test server start
        with patch('server.socket.socket') as mock_socket:
            server.start_server()
            mock_socket.assert_called_once_with(server.socket.AF_INET, server.socket.SOCK_STREAM)
            # Add more assertions if needed

class TestClient(unittest.TestCase):
    def test_client(self):
        # Test client function
        with patch('client.socket.socket') as mock_socket:
            # Mock server IP and port
            server_ip = '127.0.0.1'
            server_port = 8080

            # Mock server response
            mock_socket.return_value.recv.return_value.decode.return_value = '{"Qport": [25250, 25300]}'

            # Call client function
            client.client()

            # Add assertions to test the behavior of the client function
            mock_socket.assert_called_with(client.socket.AF_INET, client.socket.SOCK_STREAM)
            # Add more assertions if needed

if __name__ == '__main__':
    unittest.main()