import numpy as np


# Ecuaciones de primer orden

def primer_orden_1(t, u):
    y = u[0]
    return np.array([t - y])


def exacta_primer_orden_1(t):
    y = t - 1 + 2 * np.exp(-t)
    return np.column_stack((y,))


def primer_orden_2(t, u):
    y = u[0]
    return np.array([y * np.cos(t)])


def exacta_primer_orden_2(t):
    y = np.exp(np.sin(t))
    return np.column_stack((y,))


# Ecuaciones de segundo orden
# Definimos v = y'.
# Entonces el estado es u = [y, v].

def segundo_orden_1(t, u):
    y, v = u

    dy = v
    dv = -4 * y

    return np.array([dy, dv])


def exacta_segundo_orden_1(t):
    y = np.cos(2 * t)
    v = -2 * np.sin(2 * t)

    return np.column_stack((y, v))


def segundo_orden_2(t, u):
    y, v = u

    dy = v
    dv = np.sin(t) - 3 * v - 2 * y

    return np.array([dy, dv])


def exacta_segundo_orden_2(t):
    y = (
        1.5 * np.exp(-t)
        - 1.2 * np.exp(-2 * t)
        + 0.1 * np.sin(t)
        - 0.3 * np.cos(t)
    )

    v = (
        -1.5 * np.exp(-t)
        + 2.4 * np.exp(-2 * t)
        + 0.1 * np.cos(t)
        + 0.3 * np.sin(t)
    )

    return np.column_stack((y, v))


# Sistemas lineales

def sistema_lineal_1(t, u):
    x, y = u

    dx = 3 * x - 2 * y
    dy = 2 * x - 2 * y

    return np.array([dx, dy])


def exacta_sistema_lineal_1(t):
    x = (4 * np.exp(2 * t) - np.exp(-t)) / 3
    y = 2 * (np.exp(2 * t) - np.exp(-t)) / 3

    return np.column_stack((x, y))


def sistema_lineal_2(t, u):
    x, y = u

    dx = 3 * x + 2 * y
    dy = 2 * x + 3 * y

    return np.array([dx, dy])


def exacta_sistema_lineal_2(t):
    x = (np.exp(5 * t) + np.exp(t)) / 2
    y = (np.exp(5 * t) - np.exp(t)) / 2

    return np.column_stack((x, y))


# Sistema no lineal: Lotka–Volterra

def lotka_volterra(t, u):
    presas, depredadores = u

    dx = 0.5 * presas - 0.02 * presas * depredadores
    dy = 0.01 * presas * depredadores - 0.3 * depredadores

    return np.array([dx, dy])


# Catálogo de problemas
# Cada diccionario reúne lo necesario para ejecutar un caso.

PROBLEMAS = [
    {
        "nombre": "Primer orden 1",
        "funcion": primer_orden_1,
        "exacta": exacta_primer_orden_1,
        "variables": ["y"],
        "iniciales": [1],
        "intervalo": (0, 5),
        "pasos": [0.1, 0.05, 0.025, 0.0125],
    },
    {
        "nombre": "Primer orden 2",
        "funcion": primer_orden_2,
        "exacta": exacta_primer_orden_2,
        "variables": ["y"],
        "iniciales": [1],
        "intervalo": (0, 5),
        "pasos": [0.1, 0.05, 0.025, 0.0125],
    },
    {
        "nombre": "Segundo orden 1",
        "funcion": segundo_orden_1,
        "exacta": exacta_segundo_orden_1,
        "variables": ["y", "v"],
        "iniciales": [1, 0],
        "intervalo": (0, 5),
        "pasos": [0.1, 0.05, 0.025, 0.0125],
    },
    {
        "nombre": "Segundo orden 2",
        "funcion": segundo_orden_2,
        "exacta": exacta_segundo_orden_2,
        "variables": ["y", "v"],
        "iniciales": [0, 1],
        "intervalo": (0, 5),
        "pasos": [0.1, 0.05, 0.025, 0.0125],
    },
    {
        "nombre": "Sistema lineal 1",
        "funcion": sistema_lineal_1,
        "exacta": exacta_sistema_lineal_1,
        "variables": ["x", "y"],
        "iniciales": [1, 0],
        "intervalo": (0, 1),
        "pasos": [0.1, 0.05, 0.025, 0.0125],
    },
    {
        "nombre": "Sistema lineal 2",
        "funcion": sistema_lineal_2,
        "exacta": exacta_sistema_lineal_2,
        "variables": ["x", "y"],
        "iniciales": [1, 0],
        "intervalo": (0, 1),
        "pasos": [0.1, 0.05, 0.025, 0.0125],
    },
    {
        "nombre": "Lotka–Volterra",
        "funcion": lotka_volterra,
        "exacta": None,
        "variables": ["presas", "depredadores"],
        "iniciales": [40, 9],
        "intervalo": (0, 40),
        "pasos": [0.2, 0.1, 0.05, 0.025],
    },
]