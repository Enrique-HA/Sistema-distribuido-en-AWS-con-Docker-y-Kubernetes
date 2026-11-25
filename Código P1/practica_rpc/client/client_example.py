from __future__ import annotations

import socket
from client.rpc_client import RPCClient,RPCRemoteError

HOST = "35.172.212.72"
PORT = 30500


def main():
    
    rpc = RPCClient(HOST, PORT)
    try:
        print("¿4+7)",rpc.call("sumar", 4, 7))
        print("¿3*5?",rpc.call("multiplicar", 3, 5))
        print("Tarea lenta...",rpc.call("tarea_lenta", 2))
        print("Cifrando Hola Mundo:",rpc.call("cifrado_cesar","Hola Mundo",3))
        print("¿Factores de 66?",rpc.call("factores_primos",66))
    except RPCRemoteError as error:
        print(f"Error remoto: {error}")
    except (TimeoutError, ConnectionError) as error:
        print(f"Error de comunicación: {error}")
    
if __name__ == "__main__":
    main()
