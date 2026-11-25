from __future__ import annotations

import socket
from typing import Any

from common.protocol import send_json, recv_json

class RPCRemoteError(Exception):pass
class RPCClient:
    def __init__(self, host: str, port: int, timeout: float = 5.0):
        self.host = host
        self.port = port
        self.timeout = timeout

    def call(self, function: str, *args: Any) -> Any:

        #Se crea la petición RPC.
        peticion = {"function":function,"args":list(args)}
  
        try:
            with socket.create_connection((self.host,self.port),timeout = self.timeout) as socket_cliente:
                #Enviar la petición.
                send_json(socket_cliente,peticion)
      
                respuesta = recv_json(socket_cliente)

                if not isinstance(respuesta, dict):
                    raise ValueError("Respuesta del servidor no válida")

                if respuesta.get("status")=="ok":
                    return respuesta.get("result")

                raise RPCRemoteError(f"{respuesta.get('error')}: {respuesta.get('message')}") 

        except TimeoutError as error:
            raise TimeoutError(
                f"Tiempo de espera agotado después de {self.timeout} segundos"
            ) from error

        except OSError as error:
            raise ConnectionError(
                f"No se pudo comunicar con {self.host}:{self.port}"
            ) from error