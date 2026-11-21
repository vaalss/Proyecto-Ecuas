from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from simulacion import ejecutar_problema
from problemas import PROBLEMAS


CARPETA_GRAFICAS = (
    Path(__file__).resolve().parent
    / "resultados"
    / "graficas"
)

COLORES = {
    "euler": "tab:orange",
    "rk4": "tab:blue",
}


def graficar_problema(problema, resultados, h, numero):
    """Grafica cada variable y su error, cuando existe solución exacta."""
    t = resultados["t"]
    exacta = resultados["exacta"]

    cantidad_variables = len(problema["variables"])
    cantidad_columnas = 2 if exacta is not None else 1

    figura, ejes = plt.subplots(
        nrows=cantidad_variables,
        ncols=cantidad_columnas,
        figsize=(
            12 if exacta is not None else 8,
            4 * cantidad_variables
        ),
        squeeze=False
    )

    for columna, variable in enumerate(problema["variables"]):
        eje_solucion = ejes[columna, 0]

        if exacta is not None:
            eje_solucion.plot(
                t,
                exacta[:, columna],
                color="black",
                linewidth=2,
                label="Solución exacta"
            )

        for metodo in ("euler", "rk4"):
            aproximacion = resultados[metodo][:, columna]

            eje_solucion.plot(
                t,
                aproximacion,
                color=COLORES[metodo],
                linestyle="--",
                label=metodo.upper()
            )

            if exacta is not None:
                error = np.abs(
                    aproximacion - exacta[:, columna]
                )

                eje_error = ejes[columna, 1]

                eje_error.plot(
                    t,
                    error,
                    color=COLORES[metodo],
                    label=metodo.upper()
                )

        eje_solucion.set_title(f"Solución: {variable}")
        eje_solucion.set_xlabel("t")
        eje_solucion.set_ylabel(variable)
        eje_solucion.grid(True, alpha=0.3)
        eje_solucion.legend()

        if exacta is not None:
            eje_error = ejes[columna, 1]
            eje_error.set_title(f"Error absoluto: {variable}")
            eje_error.set_xlabel("t")
            eje_error.set_ylabel("Error absoluto")
            eje_error.grid(True, alpha=0.3)
            eje_error.legend()

    figura.suptitle(
        f"{problema['nombre']} | h = {h}",
        fontsize=14
    )

    figura.tight_layout(rect=(0, 0, 1, 0.95))

    ruta = CARPETA_GRAFICAS / f"problema_{numero}.png"

    figura.savefig(ruta, dpi=150)
    plt.close(figura)

    print(f"Guardada: {ruta.name}")


def graficar_plano_fase(resultados, h):
    """Grafica depredadores frente a presas para Lotka–Volterra."""
    figura, eje = plt.subplots(figsize=(8, 6))

    for metodo in ("euler", "rk4"):
        presas = resultados[metodo][:, 0]
        depredadores = resultados[metodo][:, 1]

        eje.plot(
            presas,
            depredadores,
            color=COLORES[metodo],
            label=metodo.upper()
        )

    eje.scatter(
        resultados["euler"][0, 0],
        resultados["euler"][0, 1],
        color="black",
        zorder=5,
        label="Condición inicial"
    )

    eje.set_title(f"Lotka–Volterra: plano de fase | h = {h}")
    eje.set_xlabel("Presas")
    eje.set_ylabel("Depredadores")
    eje.grid(True, alpha=0.3)
    eje.legend()

    figura.tight_layout()

    ruta = CARPETA_GRAFICAS / "lotka_volterra_plano_fase.png"

    figura.savefig(ruta, dpi=150)
    plt.close(figura)

    print(f"Guardada: {ruta.name}")


def main():
    CARPETA_GRAFICAS.mkdir(parents=True, exist_ok=True)

    for numero, problema in enumerate(PROBLEMAS, start=1):
        # Usamos el paso más grande para visualizar las diferencias.
        h = problema["pasos"][0]

        resultados = ejecutar_problema(problema, h)

        graficar_problema(
            problema,
            resultados,
            h,
            numero
        )

        # El único problema sin solución explícita es Lotka–Volterra.
        if problema["exacta"] is None:
            graficar_plano_fase(resultados, h)

    print(f"\nGráficas guardadas en: {CARPETA_GRAFICAS}")


if __name__ == "__main__":
    main()