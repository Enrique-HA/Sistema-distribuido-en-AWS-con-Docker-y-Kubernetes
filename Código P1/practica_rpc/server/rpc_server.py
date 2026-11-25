from __future__ import annotations

from typing import Any, Callable


class RPCServer:
    def __init__(self):
        self._procedures: dict[str, Callable[..., Any]] = {}

    def register(self, name: str, function: Callable[..., Any]) -> None:
        if not callable(function):
            raise TypeError("El procedimiento no es ejecutable")
        self._procedures[name] = function

    def dispatch(self, request: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(request, dict):
            return {"status": "error","error": "INVALID_REQUEST","message": "La petición debe ser JSON"}
            
        nombre = request.get("function")
        argumentos = request.get("args")

        if nombre not in self._procedures: #Es decir, no existe o no se ha registrado
            return {"status": "error","error": "PROCEDURE_NOT_FOUND","message":str(nombre)}
        try:
            funcion = self._procedures[nombre]
            resultado = funcion(*argumentos)

            return {"status": "ok","result":resultado}
        except (TypeError, ValueError) as error:
            return {"status": "error","error": "INVALID_ARGUMENTS","message":str(error)}
        except Exception as error:
            return {"status": "error","error": "EXECUTION_ERROR","message":str(error)}

