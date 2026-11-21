import numpy as np


def resolver(f, intervalo, condiciones_iniciales, h, metodo):
    """
    Resuelve un problema de valor inicial:
        u' = f(t, u)

    Parámetros:
        f: función que calcula las derivadas.
        intervalo: tiempo inicial y final, por ejemplo (0, 5).
        condiciones_iniciales: lista con los valores iniciales.
        h: tamaño del paso.
        metodo: "euler" o "rk4".

    Devuelve:
        t: arreglo con los tiempos.
        u: matriz con las aproximaciones en cada tiempo.
    """
    if metodo not in ("euler", "rk4"):
        raise ValueError("El método debe ser 'euler' o 'rk4'.")

    inicio, fin = intervalo

    if not all(np.isfinite(valor) for valor in (inicio, fin, h)):
        raise ValueError("El intervalo y el paso deben ser finitos.")

    if h <= 0 or fin <= inicio:
        raise ValueError("El paso debe ser positivo y el final mayor al inicio.")

    cantidad_pasos = (fin - inicio) / h
    n = round(cantidad_pasos)

    if n < 1 or not np.isclose(
        cantidad_pasos, n, rtol=1e-12, atol=1e-10
    ):
        raise ValueError("El paso debe dividir exactamente el intervalo.")

    iniciales = np.asarray(condiciones_iniciales, dtype=float)

    if (
        iniciales.ndim != 1
        or iniciales.size == 0
        or not np.all(np.isfinite(iniciales))
    ):
        raise ValueError("Las condiciones iniciales deben ser una lista finita.")

    t = np.linspace(inicio, fin, n + 1)

    # Cada fila corresponde a un tiempo.
    # Cada columna corresponde a una variable.
    u = np.zeros((n + 1, len(iniciales)))
    u[0] = iniciales

    def evaluar(t_actual, u_actual):
        derivadas = np.asarray(f(t_actual, u_actual), dtype=float)

        if derivadas.shape != iniciales.shape:
            raise ValueError(
                "Debe haber una derivada por cada variable del problema."
            )

        if not np.all(np.isfinite(derivadas)):
            raise ValueError("Se obtuvo una derivada no finita.")

        return derivadas

    for i in range(n):
        t_actual = t[i]
        u_actual = u[i]

        if metodo == "euler":
            pendiente = evaluar(t_actual, u_actual)
            u[i + 1] = u_actual + h * pendiente

        else:
            k1 = evaluar(t_actual, u_actual)

            k2 = evaluar(
                t_actual + h / 2,
                u_actual + h * k1 / 2
            )

            k3 = evaluar(
                t_actual + h / 2,
                u_actual + h * k2 / 2
            )

            k4 = evaluar(
                t_actual + h,
                u_actual + h * k3
            )

            u[i + 1] = u_actual + h * (
                k1 + 2 * k2 + 2 * k3 + k4
            ) / 6

        if not np.all(np.isfinite(u[i + 1])):
            raise FloatingPointError(
                "La aproximación dejó de ser finita. Revisá el tamaño del paso."
            )

    return t, u