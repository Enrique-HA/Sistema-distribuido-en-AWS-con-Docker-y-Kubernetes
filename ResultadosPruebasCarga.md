
# Pruebas de carga

Aquí muestro los resultados de las pruebas de carga que he hecho con un archivo código Python. Este código de prueba de cargas ha sido generado por IA, pero la arquitectura que prueba es mía.
El archivo está dentro de la carpeta client, y se ejecuta con:

py -m client.load_test --host (ip de un worker) --port 30500 --requests (num de peticiones) --concurrency 20 --carga (cpu,lenta o sumar)

## 2. Prueba "cpu" con 500 peticiones

C:\Users\Quique\Documents\Uni\Tercero\SistemasDistribuidos\PSD_P2_EnriqueHA\Código P1\practica_rpc> py -m client.load_test --host 35.172.212.72 --port 30500 --requests 500 --concurrency 20 --carga cpu

 PRUEBA DE CARGA DEL SERVIDOR RPC

Destino:      35.172.212.72:30500
Procedimiento: factores_primos(1000000000039,)
Tipo de carga: cpu
   Carga de CPU: cada petición factoriza un número grande.
   Sirve para ver cómo se comporta el servidor cuando las peticiones
   compiten por el procesador.

Qué voy a hacer:
  - Lanzar 500 peticiones RPC en total.
  - Mantener hasta 20 peticiones en vuelo a la vez (cada una usa un cliente RPC nuevo).
  - Dar por perdida cualquier petición que tarde más de 10.0 s.

Enviando peticiones...

[ 50/500 ( 10%)]   5.19 s | ok: 50 | fallos: 0
[100/500 ( 20%)]   9.08 s | ok: 100 | fallos: 0
[150/500 ( 30%)]  13.30 s | ok: 150 | fallos: 0
[200/500 ( 40%)]  17.48 s | ok: 200 | fallos: 0
[250/500 ( 50%)]  21.70 s | ok: 250 | fallos: 0
[300/500 ( 60%)]  25.92 s | ok: 300 | fallos: 0
[350/500 ( 70%)]  30.28 s | ok: 350 | fallos: 0
[400/500 ( 80%)]  34.37 s | ok: 400 | fallos: 0
[450/500 ( 90%)]  38.42 s | ok: 450 | fallos: 0
[500/500 (100%)]  42.27 s | ok: 500 | fallos: 0


 RESULTADOS

Tiempo total:  42.27 s
  -> Lo que tardó en completarse TODA la prueba (de la primera a la última petición).
Throughput:    11.8 peticiones OK/s
  -> Peticiones correctas por segundo. Solo cuentan las que salieron bien.
Tasa de éxito: 500/500 (100.0%)

Desglose por estado:
  ok              500  -> la llamada terminó bien y el servidor devolvió resultado

**Todas las peticiones salieron bien: el servidor aguantó esta carga.**

Latencia (solo peticiones OK) = tiempo que tarda cada petición desde que
el cliente la lanza hasta que recibe la respuesta:
  min     442 ms  -> la petición más rápida (el servidor 'sin esperas')
  media  1671 ms  -> promedio de todas
  p50    1578 ms  -> la mitad de las peticiones tardó menos que esto (caso típico)
  p95    3157 ms  -> el 95% tardó menos que esto; el 5% más lento tardó más
  max    4983 ms  -> la petición más lenta

Lectura: el p95 está cerca del p50, así que los tiempos son bastante homogéneos: no hay una cola importante.


 INTERPRETACIÓN PARA LA CARGA 'cpu'

La petición más rápida tardó 442 ms (aprox. el coste real del cálculo sin competencia).
La media (1671 ms) es más del doble: las peticiones están COMPITIENDO por la CPU o esperando turno. Es normal si hay más peticiones simultáneas que núcleos disponibles.

Prueba terminada.

## Prueba sumar, ahora con 700 peticiones

PS C:\Users\Quique\Documents\Uni\Tercero\SistemasDistribuidos\PSD_P2_EnriqueHA\Código P1\practica_rpc> py -m client.load_test --host 35.172.212.72 --port 30500 --requests 700 --concurrency 20 --carga sumar

 PRUEBA DE CARGA DEL SERVIDOR RPC

Destino:      35.172.212.72:30500
Procedimiento: sumar(4, 7)
Tipo de carga: sumar
   Carga MUY LIGERA: el servidor casi no trabaja en cada petición.
   Sirve para medir el THROUGHPUT máximo (cuántas peticiones por segundo
   aguanta el servidor/red cuando el cálculo no es el cuello de botella).

Qué voy a hacer:
  - Lanzar 700 peticiones RPC en total.
  - Mantener hasta 20 peticiones en vuelo a la vez (cada una usa un cliente RPC nuevo).
  - Dar por perdida cualquier petición que tarde más de 10.0 s.

Enviando peticiones...

[ 70/700 ( 10%)]   0.91 s | ok: 70 | fallos: 0
[140/700 ( 20%)]   1.62 s | ok: 140 | fallos: 0
[210/700 ( 30%)]   2.52 s | ok: 210 | fallos: 0
[280/700 ( 40%)]   3.32 s | ok: 280 | fallos: 0
[350/700 ( 50%)]   4.10 s | ok: 350 | fallos: 0
[420/700 ( 60%)]   4.91 s | ok: 420 | fallos: 0
[490/700 ( 70%)]   5.91 s | ok: 490 | fallos: 0
[560/700 ( 80%)]   6.76 s | ok: 560 | fallos: 0
[630/700 ( 90%)]   7.49 s | ok: 630 | fallos: 0
[700/700 (100%)]   8.33 s | ok: 700 | fallos: 0


 RESULTADOS

Tiempo total:  8.35 s
  -> Lo que tardó en completarse TODA la prueba (de la primera a la última petición).
Throughput:    83.9 peticiones OK/s
  -> Peticiones correctas por segundo. Solo cuentan las que salieron bien.
Tasa de éxito: 700/700 (100.0%)

Desglose por estado:
  ok              700  -> la llamada terminó bien y el servidor devolvió resultado

**Todas las peticiones salieron bien: el servidor aguantó esta carga.**

Latencia (solo peticiones OK) = tiempo que tarda cada petición desde que
el cliente la lanza hasta que recibe la respuesta:
  min     208 ms  -> la petición más rápida (el servidor 'sin esperas')
  media   234 ms  -> promedio de todas
  p50     226 ms  -> la mitad de las peticiones tardó menos que esto (caso típico)
  p95     261 ms  -> el 95% tardó menos que esto; el 5% más lento tardó más
  max     591 ms  -> la petición más lenta

Lectura: el p95 está cerca del p50, así que los tiempos son bastante homogéneos: no hay una cola importante.


 INTERPRETACIÓN PARA LA CARGA 'sumar'

El servidor sostuvo ~84 peticiones simples por segundo con 20 clientes simultáneos.
Como el cálculo es trivial, este valor refleja el coste de red + gestión de conexiones (cada petición crea un cliente nuevo).
Prueba a subir --concurrency: si el throughput deja de crecer o aparecen timeouts/errores de conexión, has encontrado el límite del servidor.

Prueba terminada.

## Prueba lenta, ahora con 1000 peticiones

 C:\Users\Quique\Documents\Uni\Tercero\SistemasDistribuidos\PSD_P2_EnriqueHA\Código P1\practica_rpc> py -m client.load_test --host 35.172.212.72 --port 30500 --requests 1000 --concurrency 20 --carga lenta

 PRUEBA DE CARGA DEL SERVIDOR RPC

Destino:      35.172.212.72:30500
Procedimiento: tarea_lenta(1,)
Tipo de carga: lenta
   Carga de ESPERA: cada petición tarda 1 s sin gastar CPU.
   Sirve para medir la CONCURRENCIA: si el servidor atiende varias
   peticiones a la vez, el tiempo total será mucho menor que N segundos.

Qué voy a hacer:
  - Lanzar 1000 peticiones RPC en total.
  - Mantener hasta 20 peticiones en vuelo a la vez (cada una usa un cliente RPC nuevo).
  - Dar por perdida cualquier petición que tarde más de 10.0 s.

Enviando peticiones...

[ 100/1000 ( 10%)]   8.00 s | ok: 100 | fallos: 0
[ 200/1000 ( 20%)]  15.23 s | ok: 200 | fallos: 0
[ 300/1000 ( 30%)]  22.34 s | ok: 300 | fallos: 0
[ 400/1000 ( 40%)]  29.09 s | ok: 400 | fallos: 0
[ 500/1000 ( 50%)]  36.04 s | ok: 500 | fallos: 0
[ 600/1000 ( 60%)]  43.35 s | ok: 600 | fallos: 0
[ 700/1000 ( 70%)]  49.80 s | ok: 700 | fallos: 0
[ 800/1000 ( 80%)]  56.53 s | ok: 800 | fallos: 0
[ 900/1000 ( 90%)]  63.63 s | ok: 900 | fallos: 0
[1000/1000 (100%)]  71.23 s | ok: 1000 | fallos: 0


 RESULTADOS

Tiempo total:  71.24 s
  -> Lo que tardó en completarse TODA la prueba (de la primera a la última petición).
Throughput:    14.0 peticiones OK/s
  -> Peticiones correctas por segundo. Solo cuentan las que salieron bien.
Tasa de éxito: 1000/1000 (100.0%)

Desglose por estado:
  ok             1000  -> la llamada terminó bien y el servidor devolvió resultado

**Todas las peticiones salieron bien: el servidor aguantó esta carga.**

Latencia (solo peticiones OK) = tiempo que tarda cada petición desde que
el cliente la lanza hasta que recibe la respuesta:
  min    1208 ms  -> la petición más rápida (el servidor 'sin esperas')
  media  1408 ms  -> promedio de todas
  p50    1239 ms  -> la mitad de las peticiones tardó menos que esto (caso típico)
  p95    2014 ms  -> el 95% tardó menos que esto; el 5% más lento tardó más
  max    3838 ms  -> la petición más lenta

Lectura: el p95 está cerca del p50, así que los tiempos son bastante homogéneos: no hay una cola importante.


 INTERPRETACIÓN PARA LA CARGA 'lenta'

Cada tarea espera 1 s. Con 1000 peticiones y 20 a la vez:
  - Si el servidor atiende en paralelo, lo ideal sería ~50 s (50 tandas de 1 s).
  - Si atendiera de una en una, tardaría ~1000 s.
  - Ha tardado 71.24 s.
Conclusión: el servidor ATIENDE EN PARALELO sin problemas.

Prueba terminada.


