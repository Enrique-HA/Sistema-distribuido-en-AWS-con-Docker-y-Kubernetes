"""Prueba de carga para el servidor RPC.

Colocar en la carpeta client/ del proyecto y ejecutar desde la raíz:

    python -m client.load_test --host IP_WORKER --port 30500 \
        --requests 200 --concurrency 20 --carga sumar

Opciones útiles:
    --verbose   imprime una línea por cada petición (estado y tiempo)
"""

from __future__ import annotations

import argparse
import math
import statistics
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

from client.rpc_client import RPCClient, RPCRemoteError

# Tipos de carga: (procedimiento, argumentos)
CARGAS = {
    "sumar": ("sumar", (4, 7)),                       # muy ligera: mide throughput
    "lenta": ("tarea_lenta", (1,)),                   # 1 s de espera: mide concurrencia
    "cpu": ("factores_primos", (1000000000039,)),     # trabajo de CPU
}

# Qué mide cada tipo de carga (se imprime al empezar)
DESCRIPCION_CARGAS = {
    "sumar": (
        "Carga MUY LIGERA: el servidor casi no trabaja en cada petición.\n"
        "   Sirve para medir el THROUGHPUT máximo (cuántas peticiones por segundo\n"
        "   aguanta el servidor/red cuando el cálculo no es el cuello de botella)."
    ),
    "lenta": (
        "Carga de ESPERA: cada petición tarda 1 s sin gastar CPU.\n"
        "   Sirve para medir la CONCURRENCIA: si el servidor atiende varias\n"
        "   peticiones a la vez, el tiempo total será mucho menor que N segundos."
    ),
    "cpu": (
        "Carga de CPU: cada petición factoriza un número grande.\n"
        "   Sirve para ver cómo se comporta el servidor cuando las peticiones\n"
        "   compiten por el procesador."
    ),
}

# Qué significa cada estado de una petición
EXPLICACION_ESTADOS = {
    "ok": "la llamada terminó bien y el servidor devolvió resultado",
    "timeout": "el servidor no respondió a tiempo (saturado, peticiones en cola o --timeout muy bajo)",
    "conexion": "no se pudo conectar o se cortó la conexión (servidor caído, IP/puerto mal, o cola de conexiones llena)",
    "error_remoto": "el servidor respondió con un error (el procedimiento falló en el servidor)",
    "otro": "error inesperado en el cliente (ver detalle)",
}


def una_peticion(host: str, port: int, timeout: float, funcion: str, argumentos: tuple):
    """Hace una llamada RPC y devuelve (estado, segundos, detalle_del_error)."""
    rpc = RPCClient(host, port, timeout=timeout)
    inicio = time.perf_counter()
    detalle = ""
    try:
        rpc.call(funcion, *argumentos)
        estado = "ok"
    except TimeoutError as e:
        estado, detalle = "timeout", str(e)
    except ConnectionError as e:
        estado, detalle = "conexion", str(e)
    except RPCRemoteError as e:
        estado, detalle = "error_remoto", str(e)
    except Exception as e:  # cualquier otra cosa no se pierde en silencio
        estado, detalle = "otro", f"{type(e).__name__}: {e}"
    return estado, time.perf_counter() - inicio, detalle


def percentil(valores: list[float], p: float) -> float:
    ordenados = sorted(valores)
    indice = min(len(ordenados) - 1, int(round(p / 100 * (len(ordenados) - 1))))
    return ordenados[indice]


def ms(segundos: float) -> str:
    return f"{segundos * 1000:.0f} ms"


def imprimir_intro(args, funcion: str, argumentos: tuple) -> None:
    print("=" * 70)
    print(" PRUEBA DE CARGA DEL SERVIDOR RPC")
    print("=" * 70)
    print(f"Destino:      {args.host}:{args.port}")
    print(f"Procedimiento: {funcion}{argumentos}")
    print(f"Tipo de carga: {args.carga}")
    print(f"   {DESCRIPCION_CARGAS[args.carga]}\n")
    print("Qué voy a hacer:")
    print(f"  - Lanzar {args.requests} peticiones RPC en total.")
    print(f"  - Mantener hasta {args.concurrency} peticiones en vuelo a la vez "
          f"(cada una usa un cliente RPC nuevo).")
    print(f"  - Dar por perdida cualquier petición que tarde más de {args.timeout} s.\n")
    print("Enviando peticiones...\n")


def imprimir_resumen_general(estados: Counter, total_peticiones: int, total: float) -> None:
    ok = estados["ok"]
    fallos = total_peticiones - ok
    print("\n" + "=" * 70)
    print(" RESULTADOS")
    print("=" * 70)
    print(f"Tiempo total:  {total:.2f} s")
    print("  -> Lo que tardó en completarse TODA la prueba (de la primera a la última petición).")
    print(f"Throughput:    {ok / total:.1f} peticiones OK/s")
    print("  -> Peticiones correctas por segundo. Solo cuentan las que salieron bien.")
    print(f"Tasa de éxito: {ok}/{total_peticiones} ({ok / total_peticiones * 100:.1f}%)")

    print("\nDesglose por estado:")
    for estado, cantidad in estados.most_common():
        print(f"  {estado:<13} {cantidad:>5}  -> {EXPLICACION_ESTADOS.get(estado, '')}")

    if fallos == 0:
        print("\nTodas las peticiones salieron bien: el servidor aguantó esta carga.")
    else:
        print(f"\nATENCIÓN: {fallos} peticiones fallaron. Los números de latencia de abajo "
              "solo incluyen las que salieron bien, así que pueden verse mejor de lo real.")


def imprimir_latencias(latencias: list[float]) -> None:
    print("\nLatencia (solo peticiones OK) = tiempo que tarda cada petición desde que")
    print("el cliente la lanza hasta que recibe la respuesta:")
    minimo = min(latencias)
    media = statistics.mean(latencias)
    p50 = percentil(latencias, 50)
    p95 = percentil(latencias, 95)
    maximo = max(latencias)
    print(f"  min   {ms(minimo):>8}  -> la petición más rápida (el servidor 'sin esperas')")
    print(f"  media {ms(media):>8}  -> promedio de todas")
    print(f"  p50   {ms(p50):>8}  -> la mitad de las peticiones tardó menos que esto (caso típico)")
    print(f"  p95   {ms(p95):>8}  -> el 95% tardó menos que esto; el 5% más lento tardó más")
    print(f"  max   {ms(maximo):>8}  -> la petición más lenta")

    # Lectura orientativa de la forma de la distribución
    if len(latencias) >= 5:
        if p95 > 3 * p50:
            print("\nLectura: el p95 es mucho mayor que el p50. Algunas peticiones esperan "
                  "bastante más que el resto (probablemente hacen cola en el servidor).")
        else:
            print("\nLectura: el p95 está cerca del p50, así que los tiempos son bastante "
                  "homogéneos: no hay una cola importante.")


def interpretar_por_carga(args, estados: Counter, latencias: list[float], total: float) -> None:
    ok = estados["ok"]
    print("\n" + "-" * 70)
    print(f" INTERPRETACIÓN PARA LA CARGA '{args.carga}'")
    print("-" * 70)

    if ok == 0:
        print("Ninguna petición terminó bien, no hay datos para interpretar. Revisa que el "
              "servidor esté levantado y que --host y --port sean correctos.")
        return

    if args.carga == "sumar":
        print(f"El servidor sostuvo ~{ok / total:.0f} peticiones simples por segundo con "
              f"{args.concurrency} clientes simultáneos.")
        print("Como el cálculo es trivial, este valor refleja el coste de red + gestión de "
              "conexiones (cada petición crea un cliente nuevo).")
        print("Prueba a subir --concurrency: si el throughput deja de crecer o aparecen "
              "timeouts/errores de conexión, has encontrado el límite del servidor.")

    elif args.carga == "lenta":
        if ok != args.requests:
            print("Hubo fallos, así que la comparación de tiempos no es fiable. Soluciona "
                  "los errores (o sube --timeout) y repite.")
            return
        tandas = math.ceil(args.requests / args.concurrency)
        ideal = tandas * 1.0               # cada tarea espera 1 s
        secuencial = args.requests * 1.0
        print(f"Cada tarea espera 1 s. Con {args.requests} peticiones y {args.concurrency} "
              f"a la vez:")
        print(f"  - Si el servidor atiende en paralelo, lo ideal sería ~{ideal:.0f} s "
              f"({tandas} tandas de 1 s).")
        print(f"  - Si atendiera de una en una, tardaría ~{secuencial:.0f} s.")
        print(f"  - Ha tardado {total:.2f} s.")
        if total <= ideal * 1.5:
            print("Conclusión: el servidor ATIENDE EN PARALELO sin problemas.")
        elif total >= secuencial * 0.7:
            print("Conclusión: el servidor funciona casi SECUENCIALMENTE (una petición tras "
                  "otra). Revisa si usa hilos/procesos para atender clientes.")
        else:
            print("Conclusión: PARALELISMO PARCIAL. Atiende varias a la vez, pero con un "
                  "límite menor que la concurrencia pedida (p. ej. un pool de hilos pequeño).")

    elif args.carga == "cpu":
        minimo = min(latencias)
        media = statistics.mean(latencias)
        print(f"La petición más rápida tardó {ms(minimo)} (aprox. el coste real del cálculo "
              f"sin competencia).")
        if media > 2 * minimo:
            print(f"La media ({ms(media)}) es más del doble: las peticiones están "
                  "COMPITIENDO por la CPU o esperando turno. Es normal si hay más "
                  "peticiones simultáneas que núcleos disponibles.")
        else:
            print(f"La media ({ms(media)}) es parecida al mínimo: el servidor reparte bien "
                  "el trabajo y casi no hay contención de CPU con esta concurrencia.")


def imprimir_errores(detalles: list[tuple[str, str]]) -> None:
    """Muestra un ejemplo del mensaje de cada tipo de error para facilitar el diagnóstico."""
    ejemplos: dict[str, str] = {}
    for estado, detalle in detalles:
        if estado != "ok" and detalle and estado not in ejemplos:
            ejemplos[estado] = detalle
    if ejemplos:
        print("\nEjemplo de mensaje de error por tipo:")
        for estado, detalle in ejemplos.items():
            print(f"  {estado}: {detalle}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prueba de carga del servidor RPC")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=30500)
    parser.add_argument("--requests", type=int, default=200, help="peticiones totales")
    parser.add_argument("--concurrency", type=int, default=20, help="clientes simultáneos")
    parser.add_argument("--carga", choices=CARGAS, default="sumar")
    parser.add_argument("--timeout", type=float, default=10.0, help="timeout por petición (s)")
    parser.add_argument("--verbose", action="store_true",
                        help="imprime una línea por cada petición terminada")
    args = parser.parse_args()

    funcion, argumentos = CARGAS[args.carga]
    imprimir_intro(args, funcion, argumentos)

    # Se imprime el progreso cada ~10% (o cada petición si hay pocas)
    paso_progreso = max(1, args.requests // 10)
    resultados: list[tuple[str, float, str]] = []
    contador = Counter()

    inicio = time.perf_counter()
    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futuros = [
            pool.submit(una_peticion, args.host, args.port, args.timeout, funcion, argumentos)
            for _ in range(args.requests)
        ]
        # as_completed entrega cada resultado según va terminando, así se puede
        # mostrar el avance en tiempo real desde el hilo principal.
        for hechas, futuro in enumerate(as_completed(futuros), start=1):
            estado, segundos, detalle = futuro.result()
            resultados.append((estado, segundos, detalle))
            contador[estado] += 1

            if args.verbose:
                extra = f" ({detalle})" if detalle else ""
                print(f"  petición {hechas:>4}: {estado:<13} {ms(segundos):>8}{extra}")

            if hechas % paso_progreso == 0 or hechas == args.requests:
                transcurrido = time.perf_counter() - inicio
                fallos = hechas - contador["ok"]
                print(f"[{hechas:>{len(str(args.requests))}}/{args.requests} "
                      f"({hechas / args.requests * 100:3.0f}%)] "
                      f"{transcurrido:6.2f} s | ok: {contador['ok']} | fallos: {fallos}")
    total = time.perf_counter() - inicio

    estados = Counter(estado for estado, _, _ in resultados)
    latencias_ok = [t for estado, t, _ in resultados if estado == "ok"]

    imprimir_resumen_general(estados, args.requests, total)
    imprimir_errores([(estado, detalle) for estado, _, detalle in resultados])
    if latencias_ok:
        imprimir_latencias(latencias_ok)
    interpretar_por_carga(args, estados, latencias_ok, total)
    print("\nPrueba terminada.")


if __name__ == "__main__":
    main()
