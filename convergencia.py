import csv
from pathlib import Path

import numpy as np

from metodos import resolver
from problemas import PROBLEMAS


def estudiar_convergencia(problema, metodo):
    """Resuelve un problema con cada paso y compara los resultados."""
    pasos = problema["pasos"]
    soluciones = []
    errores = []

    for h in pasos:
        t, u = resolver(
            f=problema["funcion"],
            intervalo=problema["intervalo"],
            condiciones_iniciales=problema["iniciales"],
            h=h,
            metodo=metodo
        )

        soluciones.append(u)

        if problema["exacta"] is not None:
            exacta = problema["exacta"](t)

            # Máximo entre todos los tiempos y todas las variables.
            error = np.max(np.abs(u - exacta))
            errores.append(float(error))

    filas = []

    for i, h in enumerate(pasos):
        error_exacto = None
        diferencia = None
        orden = None

        if problema["exacta"] is not None:
            error_exacto = errores[i]

            # Comparamos el error con el del siguiente paso, h/2.
            if i + 1 < len(pasos):
                if errores[i] > 0 and errores[i + 1] > 0:
                    orden = np.log2(
                        errores[i] / errores[i + 1]
                    )

        else:
            # No hay solución explícita: comparamos mallas.
            if i + 1 < len(pasos):
                gruesa = soluciones[i]

                # Cada dos puntos de la malla fina coincide
                # uno con la malla gruesa.
                fina = soluciones[i + 1][::2]

                diferencia = float(
                    np.max(np.abs(gruesa - fina))
                )

                # Para estimar el orden necesitamos tres mallas:
                # h, h/2 y h/4, comparadas en los mismos tiempos.
                if i + 2 < len(pasos):
                    mas_fina = soluciones[i + 2][::4]

                    diferencia_siguiente = float(
                        np.max(np.abs(fina - mas_fina))
                    )

                    if diferencia > 0 and diferencia_siguiente > 0:
                        orden = np.log2(
                            diferencia / diferencia_siguiente
                        )

        filas.append({
            "problema": problema["nombre"],
            "metodo": metodo,
            "h": h,
            "error_exacto": error_exacto,
            "diferencia_mallas": diferencia,
            "orden_observado": (
                float(orden) if orden is not None else None
            ),
        })

    return filas


def formatear(valor):
    """Un guion indica que no hay un valor aplicable."""
    if valor is None:
        return "-"

    return f"{valor:.6e}"


def mostrar_tabla(problema, metodo, filas):
    print("\n" + "=" * 70)
    print(f"{problema['nombre']} | {metodo.upper()}")

    if problema["exacta"] is not None:
        etiqueta = "Error máximo"
        campo = "error_exacto"
    else:
        etiqueta = "Diferencia mallas"
        campo = "diferencia_mallas"

    print(
        f"{'h':>10}"
        f"{etiqueta:>24}"
        f"{'Orden observado':>22}"
    )

    for fila in filas:
        print(
            f"{fila['h']:10.4f}"
            f"{formatear(fila[campo]):>24}"
            f"{formatear(fila['orden_observado']):>22}"
        )


def guardar_tabla(filas):
    carpeta = Path(__file__).resolve().parent / "resultados"
    carpeta.mkdir(exist_ok=True)

    ruta = carpeta / "convergencia.csv"

    columnas = [
        "problema",
        "metodo",
        "h",
        "error_exacto",
        "diferencia_mallas",
        "orden_observado",
    ]

    with ruta.open(
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as archivo:
        escritor = csv.DictWriter(
            archivo,
            fieldnames=columnas
        )

        escritor.writeheader()
        escritor.writerows(filas)

    print(f"\nTabla guardada en: {ruta}")


def main():
    todas_las_filas = []

    for problema in PROBLEMAS:
        for metodo in ("euler", "rk4"):
            filas = estudiar_convergencia(problema, metodo)

            mostrar_tabla(problema, metodo, filas)

            todas_las_filas.extend(filas)

    guardar_tabla(todas_las_filas)


if __name__ == "__main__":
    main()