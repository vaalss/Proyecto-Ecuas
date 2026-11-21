import tkinter as tk
from tkinter import ttk, messagebox

import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from simulacion import ejecutar_problema
from convergencia import estudiar_convergencia
from problemas import PROBLEMAS


COLORES = {
    "euler": "tab:orange",
    "rk4": "tab:blue",
}


class Aplicacion:
    def __init__(self, ventana):
        self.ventana = ventana

        ventana.title("Euler y Runge–Kutta de cuarto orden")
        ventana.geometry("1100x780")
        ventana.minsize(900, 650)

        self.descripcion = tk.StringVar()
        self.texto_error = tk.StringVar()
        self.texto_convergencia = tk.StringVar()

        self.crear_controles()
        self.crear_pestanas()

        self.cambiar_problema()

    def crear_controles(self):
        marco = ttk.Frame(self.ventana, padding=12)
        marco.pack(fill="x")

        ttk.Label(
            marco,
            text="Comparación de Euler y RK4",
            font=("Arial", 16, "bold")
        ).grid(
            row=0,
            column=0,
            columnspan=6,
            sticky="w",
            pady=(0, 12)
        )

        ttk.Label(
            marco,
            text="Problema:"
        ).grid(row=1, column=0)

        self.selector_problema = ttk.Combobox(
            marco,
            values=[p["nombre"] for p in PROBLEMAS],
            state="readonly",
            width=24
        )
        self.selector_problema.grid(
            row=1, column=1, padx=(5, 20)
        )
        self.selector_problema.current(0)

        ttk.Label(
            marco,
            text="Paso:"
        ).grid(row=1, column=2)

        self.selector_paso = ttk.Combobox(
            marco,
            state="readonly",
            width=10
        )
        self.selector_paso.grid(
            row=1, column=3, padx=(5, 20)
        )

        ttk.Label(
            marco,
            text="Variable:"
        ).grid(row=1, column=4)

        self.selector_variable = ttk.Combobox(
            marco,
            state="readonly",
            width=16
        )
        self.selector_variable.grid(
            row=1, column=5, padx=5
        )

        ttk.Label(
            marco,
            textvariable=self.descripcion,
            wraplength=1000
        ).grid(
            row=2,
            column=0,
            columnspan=6,
            sticky="w",
            pady=(12, 0)
        )

        self.selector_problema.bind(
            "<<ComboboxSelected>>",
            self.cambiar_problema
        )

        self.selector_paso.bind(
            "<<ComboboxSelected>>",
            self.actualizar
        )

        self.selector_variable.bind(
            "<<ComboboxSelected>>",
            self.actualizar
        )

    def crear_pestanas(self):
        notebook = ttk.Notebook(self.ventana)
        notebook.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=(0, 12)
        )

        soluciones = ttk.Frame(notebook)
        errores = ttk.Frame(notebook)
        convergencia = ttk.Frame(notebook)
        datos = ttk.Frame(notebook)

        notebook.add(soluciones, text="Soluciones")
        notebook.add(errores, text="Errores")
        notebook.add(convergencia, text="Convergencia")
        notebook.add(datos, text="Datos")

        ttk.Label(
            soluciones,
            text=(
                "Negro: solución exacta. "
                "Naranja: Euler. Azul: RK4."
            ),
            padding=8
        ).pack(fill="x")

        ttk.Label(
            errores,
            textvariable=self.texto_error,
            padding=8,
            wraplength=1000
        ).pack(fill="x")

        ttk.Label(
            convergencia,
            textvariable=self.texto_convergencia,
            padding=8,
            wraplength=1000
        ).pack(fill="x")

        self.tabla_convergencia = self.crear_tabla(
            convergencia,
            altura=5,
            expandir=False
        )

        ttk.Label(
            datos,
            text="Valores de la variable seleccionada.",
            padding=8
        ).pack(fill="x")

        self.tabla_datos = self.crear_tabla(
            datos,
            altura=18,
            expandir=True
        )

        self.fig_soluciones, self.canvas_soluciones = (
            self.crear_grafica(soluciones)
        )

        self.fig_errores, self.canvas_errores = (
            self.crear_grafica(errores)
        )

        self.fig_convergencia, self.canvas_convergencia = (
            self.crear_grafica(convergencia)
        )

    def crear_grafica(self, contenedor):
        figura = Figure(figsize=(9, 4), dpi=100)

        canvas = FigureCanvasTkAgg(
            figura,
            master=contenedor
        )

        canvas.get_tk_widget().pack(
            fill="both",
            expand=True
        )

        return figura, canvas

    def crear_tabla(self, contenedor, altura, expandir):
        marco = ttk.Frame(contenedor, padding=8)
        marco.pack(fill="both", expand=expandir)

        tabla = ttk.Treeview(
            marco,
            show="headings",
            height=altura
        )

        barra = ttk.Scrollbar(
            marco,
            orient="vertical",
            command=tabla.yview
        )

        tabla.configure(yscrollcommand=barra.set)

        barra.pack(side="right", fill="y")
        tabla.pack(side="left", fill="both", expand=True)

        return tabla

    def llenar_tabla(self, tabla, columnas, filas):
        tabla.delete(*tabla.get_children())
        tabla["columns"] = columnas

        for columna in columnas:
            tabla.heading(columna, text=columna)
            tabla.column(
                columna,
                width=170,
                anchor="center"
            )

        for fila in filas:
            valores = [
                "—" if valor is None else f"{valor:.8g}"
                for valor in fila
            ]

            tabla.insert("", "end", values=valores)

    def cambiar_problema(self, evento=None):
        indice = self.selector_problema.current()
        self.problema = PROBLEMAS[indice]

        self.selector_paso["values"] = [
            str(h) for h in self.problema["pasos"]
        ]
        self.selector_paso.current(0)

        self.selector_variable["values"] = (
            self.problema["variables"]
        )
        self.selector_variable.current(0)

        self.actualizar()

    def actualizar(self, evento=None):
        try:
            h = float(self.selector_paso.get())
            variable = self.selector_variable.get()

            self.columna = self.problema["variables"].index(
                variable
            )

            self.resultados = ejecutar_problema(
                self.problema,
                h
            )

            texto = (
                f"Intervalo: {self.problema['intervalo']}   |   "
                f"Condiciones iniciales: "
                f"{self.problema['iniciales']}"
            )

            if "v" in self.problema["variables"]:
                texto += "   |   v representa y'."

            self.descripcion.set(texto)

            self.mostrar_soluciones()
            self.mostrar_errores()
            self.mostrar_convergencia()
            self.mostrar_datos()

        except Exception as error:
            messagebox.showerror(
                "No se pudo calcular",
                str(error),
                parent=self.ventana
            )

    def mostrar_soluciones(self):
        figura = self.fig_soluciones
        figura.clear()

        t = self.resultados["t"]
        exacta = self.resultados["exacta"]

        if exacta is None:
            eje = figura.add_subplot(121)
            fase = figura.add_subplot(122)
        else:
            eje = figura.add_subplot(111)

        if exacta is not None:
            eje.plot(
                t,
                exacta[:, self.columna],
                color="black",
                linewidth=2,
                label="Exacta"
            )

        for metodo in ("euler", "rk4"):
            u = self.resultados[metodo]

            eje.plot(
                t,
                u[:, self.columna],
                color=COLORES[metodo],
                linestyle="--",
                label=metodo.upper()
            )

            if exacta is None:
                fase.plot(
                    u[:, 0],
                    u[:, 1],
                    color=COLORES[metodo],
                    label=metodo.upper()
                )

        variable = self.selector_variable.get()

        eje.set_title(f"Solución de {variable}")
        eje.set_xlabel("t")
        eje.set_ylabel(variable)
        eje.grid(True, alpha=0.3)
        eje.legend()

        if exacta is None:
            inicial = self.problema["iniciales"]

            fase.scatter(
                inicial[0],
                inicial[1],
                color="black",
                label="Inicio",
                zorder=5
            )

            fase.set_title("Plano de fase")
            fase.set_xlabel("Presas")
            fase.set_ylabel("Depredadores")
            fase.grid(True, alpha=0.3)
            fase.legend()

        figura.tight_layout()
        self.canvas_soluciones.draw()

    def mostrar_errores(self):
        figura = self.fig_errores
        figura.clear()

        eje = figura.add_subplot(111)
        exacta = self.resultados["exacta"]

        if exacta is None:
            self.texto_error.set(
                "No calculamos un error exacto para Lotka–Volterra. "
                "Consultá la pestaña Convergencia."
            )

            eje.text(
                0.5,
                0.5,
                "Sin solución explícita de referencia.",
                ha="center",
                va="center",
                transform=eje.transAxes
            )
            eje.set_axis_off()

        else:
            maximos = []

            for metodo in ("euler", "rk4"):
                error = np.abs(
                    self.resultados[metodo][:, self.columna]
                    - exacta[:, self.columna]
                )

                maximos.append(
                    f"{metodo.upper()}: {np.max(error):.6e}"
                )

                eje.plot(
                    self.resultados["t"],
                    error,
                    color=COLORES[metodo],
                    label=metodo.upper()
                )

            self.texto_error.set(
                "Cuanto más cerca de cero, mejor. "
                "Error máximo de la variable seleccionada: "
                + " | ".join(maximos)
            )

            eje.set_title(
                f"Error absoluto de "
                f"{self.selector_variable.get()}"
            )
            eje.set_xlabel("t")
            eje.set_ylabel("Error absoluto")
            eje.grid(True, alpha=0.3)
            eje.legend()

        figura.tight_layout()
        self.canvas_errores.draw()

    def mostrar_convergencia(self):
        tiene_exacta = self.problema["exacta"] is not None

        campo = (
            "error_exacto"
            if tiene_exacta
            else "diferencia_mallas"
        )

        resultados = {
            metodo: estudiar_convergencia(
                self.problema,
                metodo
            )
            for metodo in ("euler", "rk4")
        }

        if tiene_exacta:
            columnas = [
                "Paso",
                "Error de Euler",
                "Error de RK4"
            ]

            texto = (
                "Se comparan todos los pasos. El error es el máximo "
                "entre todos los tiempos y componentes, sin normalizar. "
                "Los selectores de paso y variable no cambian esta tabla."
            )

        else:
            columnas = [
                "Paso",
                "Diferencia Euler",
                "Diferencia RK4"
            ]

            texto = (
                "Se comparan pasos h y h/2 en tiempos comunes, "
                "considerando ambas poblaciones. No son errores exactos. "
                "El guion indica que no hay una malla más fina disponible."
            )

        self.texto_convergencia.set(texto)

        filas = [
            (
                euler["h"],
                euler[campo],
                rk4[campo]
            )
            for euler, rk4 in zip(
                resultados["euler"],
                resultados["rk4"]
            )
        ]

        self.llenar_tabla(
            self.tabla_convergencia,
            columnas,
            filas
        )

        figura = self.fig_convergencia
        figura.clear()
        eje = figura.add_subplot(111)

        for metodo in ("euler", "rk4"):
            validos = [
                fila for fila in resultados[metodo]
                if fila[campo] is not None
                and fila[campo] > 0
            ]

            eje.loglog(
                [fila["h"] for fila in validos],
                [fila[campo] for fila in validos],
                marker="o",
                color=COLORES[metodo],
                label=metodo.upper()
            )

        eje.set_title(
            "Los pasos más pequeños están hacia la izquierda"
        )
        eje.set_xlabel("Tamaño del paso")
        eje.set_ylabel(
            "Error máximo"
            if tiene_exacta
            else "Diferencia entre mallas"
        )
        eje.grid(True, which="both", alpha=0.3)
        eje.legend()

        figura.tight_layout()
        self.canvas_convergencia.draw()

    def mostrar_datos(self):
        exacta = self.resultados["exacta"]

        columnas = ["Tiempo"]
        arreglos = [self.resultados["t"]]

        if exacta is not None:
            columnas.append("Solución exacta")
            arreglos.append(exacta[:, self.columna])

        columnas.extend(["Euler", "RK4"])

        arreglos.extend([
            self.resultados["euler"][:, self.columna],
            self.resultados["rk4"][:, self.columna]
        ])

        self.llenar_tabla(
            self.tabla_datos,
            columnas,
            zip(*arreglos)
        )


if __name__ == "__main__":
    ventana = tk.Tk()
    aplicacion = Aplicacion(ventana)
    ventana.mainloop()