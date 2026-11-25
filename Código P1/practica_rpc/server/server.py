from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
import socket

from common.protocol import send_json, recv_json

from server.procedures import sumar,multiplicar,potencia,tarea_lenta,cifrado_cesar,factores_primos
from server.rpc_server import RPCServer

HOST = "0.0.0.0"
PORT = 5000
MAX_WORKERS=4

#Registramos a nuestro rpc las funciones que queremos que el cliente pueda usar
server_rpc=RPCServer()
server_rpc.register("sumar",sumar)
server_rpc.register("multiplicar",multiplicar)
server_rpc.register("potencia",potencia)
server_rpc.register("tarea_lenta",tarea_lenta)
server_rpc.register("cifrado_cesar",cifrado_cesar)
server_rpc.register("factores_primos",factores_primos)

def procesar_peticion(client_socket,address):
    with client_socket:
                print(f"Conexión recibida desde {address}")

                try:
                    request = recv_json(client_socket)
                    print("Mensaje recibido:", request)

                    response = server_rpc.dispatch(request)

                    send_json(client_socket, response)

                except Exception as exc:
                    print(f"Error atendiendo la conexión: {exc}")

def main():
    
    print(f"Servidor escuchando en {HOST}:{PORT}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen()

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as gestor_hilos:

            while True:
                socket_cliente,direccion_cliente=server_socket.accept()
                gestor_hilos.submit(procesar_peticion,socket_cliente,direccion_cliente)
    

if __name__ == "__main__":
    main()
