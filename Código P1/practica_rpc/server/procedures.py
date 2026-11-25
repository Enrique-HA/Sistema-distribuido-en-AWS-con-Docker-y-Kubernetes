from __future__ import annotations
import time


def sumar(a, b):
    return a + b


def multiplicar(a, b):
    return a * b


def potencia(a, b):
    return a ** b


def tarea_lenta(segundos):
    """Útil para comprobar posteriormente la concurrencia."""
    time.sleep(segundos)
    return segundos

def cifrado_cesar(texto, desplazamiento):
    abecedario = "abcdefghijklmnopqrstuvwxyz"
    resultado = ""

    for letra in texto.lower():
        if letra in abecedario:
            posicion = abecedario.index(letra)
            nueva_posicion = (posicion + desplazamiento) % 26
            resultado += abecedario[nueva_posicion]
        else:
            resultado += letra

    return resultado

def factores_primos(n):
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError("n debe ser un entero")

    if n < 2:
        raise ValueError(
            "n debe ser un entero mayor o igual que 2"
        )
    factores = []

    while n % 2 == 0:
        factores.append(2)
        n //= 2

    i = 3
    while i * i <= n:
        while n % i == 0:
            factores.append(i)
            n //= i
        i += 2
         
    if n > 2:
        factores.append(n)    
    return factores
