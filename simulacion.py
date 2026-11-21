import numpy as np

from metodos import resolver
from problemas import PROBLEMAS


def ejecutar_problema(problema, h):
    """
    Resuelve un problema con Euler y RK4.

    Devuelve los tiempos, las aproximaciones de ambos métodos
    y la solución exacta, si está disponible.
    """
    t, resultado_euler = resolver(
        f=problema["funcion"],
        intervalo=problema["intervalo"],
        condiciones_iniciales=problema["iniciales"],
        h=h,
        metodo="euler"
    )

    _, resultado_rk4 = resolver(
        f=problema["funcion"],
        intervalo=problema["intervalo"],
        condiciones_iniciales=problema["iniciales"],
        h=h,
        metodo="rk4"
    )

    if problema["exacta"] is not None:
        resultado_exacto = problema["exacta"](t)
    else:
        resultado_exacto = None

    return {
        "t": t,
        "euler": resultado_euler,
        "rk4": resultado_rk4,
        "exacta": resultado_exacto,
    }


def mostrar_resultados(problema, resultados, h):
    """Muestra valores finales y errores por variable."""
    t = resultados["t"]
    exacta = resultados["exacta"]

    print("\n" + "=" * 70)
    print(problema["nombre"])
    print(f"Intervalo: {problema['intervalo']}")
    print(f"Paso: {h} | Cantidad de pasos: {len(t) - 1}")
    print(f"\nValores en t = {t[-1]:g}")

    if exacta is not None:
        print(
            f"{'Variable':<15}"
            f"{'Exacta':>16}"
            f"{'Euler':>16}"
            f"{'RK4':>16}"
        )
    else:
        print(
            f"{'Variable':<15}"
            f"{'Euler':>16}"
            f"{'RK4':>16}"
        )

    for columna, variable in enumerate(problema["variables"]):
        valor_euler = resultados["euler"][-1, columna]
        valor_rk4 = resultados["rk4"][-1, columna]

        if exacta is not None:
            valor_exacto = exacta[-1, columna]

            print(
                f"{variable:<15}"
                f"{valor_exacto:16.8f}"
                f"{valor_euler:16.8f}"
                f"{valor_rk4:16.8f}"
            )
        else:
            print(
                f"{variable:<15}"
                f"{valor_euler:16.8f}"
                f"{valor_rk4:16.8f}"
            )

    if exacta is not None:
        print("\nError absoluto máximo en todo el intervalo:")
        print(
            f"{'Variable':<15}"
            f"{'Euler':>16}"
            f"{'RK4':>16}"
        )

        for columna, variable in enumerate(problema["variables"]):
            error_euler = np.max(
                np.abs(
                    resultados["euler"][:, columna]
                    - exacta[:, columna]
                )
            )

            error_rk4 = np.max(
                np.abs(
                    resultados["rk4"][:, columna]
                    - exacta[:, columna]
                )
            )

            print(
                f"{variable:<15}"
                f"{error_euler:16.6e}"
                f"{error_rk4:16.6e}"
            )

    else:
        print("\nNo se calcula error exacto para este problema.")
        print("Su convergencia se evaluará comparando distintos pasos.")

        for metodo in ("euler", "rk4"):
            positivas = np.all(resultados[metodo] > 0)

            print(
                f"{metodo.upper()}: poblaciones positivas "
                f"en todos los puntos = {positivas}"
            )


def main():
    for problema in PROBLEMAS:
        # Por ahora probamos el primer paso de cada problema.
        h = problema["pasos"][0]

        resultados = ejecutar_problema(problema, h)

        mostrar_resultados(problema, resultados, h)


if __name__ == "__main__":
    main()