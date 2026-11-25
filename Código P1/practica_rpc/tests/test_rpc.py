"""Pruebas básicas proporcionadas.

Ejecutar desde la raíz del proyecto:

    python -m unittest discover -s tests
"""

from __future__ import annotations

import socket
import unittest

from common.protocol import send_json, recv_json
from server.rpc_server import RPCServer
from server.procedures import sumar, multiplicar,potencia, cifrado_cesar

class ProtocolTests(unittest.TestCase):
    def test_send_and_receive_json(self):
        left, right = socket.socketpair()

        try:
            expected = {
                "function": "sumar",
                "args": [4, 7],
            }

            send_json(left, expected)
            received = recv_json(right)

            self.assertEqual(received, expected)

        finally:
            left.close()
            right.close()


class StudentTests(unittest.TestCase):
    def setUp(self):
        self.server = RPCServer()
        self.server.register("sumar", sumar)
    def test_rpc_sumar(self):
        request = {"function": "sumar", "args": [4, 7]}
        response = self.server.dispatch(request)
        
        self.assertEqual(response.get("status"), "ok")
        self.assertEqual(response.get("result"), 11)
    def test_rpc_procedure_not_found(self):
        request = {"function": "no_existe", "args": [1, 2]}
        response = self.server.dispatch(request)
        
        self.assertEqual(response.get("status"), "error")
        self.assertEqual(response.get("error"), "PROCEDURE_NOT_FOUND")
    def test_rpc_invalid_arguments(self):
        request = {"function": "sumar", "args": [5]} 
        response = self.server.dispatch(request)
        
        self.assertEqual(response.get("status"), "error")
        self.assertEqual(response.get("error"), "INVALID_ARGUMENTS")   

if __name__ == "__main__":
    unittest.main()
