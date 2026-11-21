import csv
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)

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
        ventana.title("Ecuaciones diferenciales: Euler y RK4")
        ventana.geometry("1150x800")
        ventana.minsize(900, 650)

        self.paso = tk.StringVar()
        self.variable = tk.StringVar()
        self.descripcion = tk.StringVar()

        self.tablas = {}

        self.crear_controles()
        self.crear_pestanas()
        self.cambiar_problema()

    def crear_controles(self):
        controles = ttk.Frame(self.ventana, padding=12)
        controles.pack(fill="x")

        ttk.Label(
            controles,
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
            controles,
            text="Problema:"
        ).grid(row=1, column=0, sticky="w")

        self.selector_problema = ttk.Combobox(
            controles,
            values=[p["nombre"] for p in PROBLEMAS],
            state="readonly",
            width=25
        )
        self.selector_problema.grid(
            row=1, column=1, padx=(5, 20), sticky="w"
        )
        self.selector_problema.current(0)

        ttk.Label(
            controles,
            text="Paso:"
        ).grid(row=1, column=2, sticky="w")

        self.selector_paso = ttk.Combobox(
            controles,
            textvariable=self.paso,
            state="readonly",
            width=10
        )
        self.selector_paso.grid(
            row=1, column=3, padx=(5, 20), sticky="w"
        )

        ttk.Label(
            controles,
            text="Variable:"
        ).grid(row=1, column=4, sticky="w")

        self.selector_variable = ttk.Combobox(
            controles,
            textvariable=self.variable,
            state="readonly",
            width=16
        )
        self.selector_variable.grid(
            row=1, column=5, padx=5, sticky="w"
        )

        ttk.Label(
            controles,
            textvariable=self.descripcion,
            wraplength=1050
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

        self.tab_soluciones = ttk.Frame(notebook)
        self.tab_errores = ttk.Frame(notebook)
        self.tab_convergencia = ttk.Frame(notebook)
        self.tab_datos = ttk.Frame(notebook)

        notebook.add(self.tab_soluciones, text="Soluciones")
        notebook.add(self.tab_errores, text="Errores")
        notebook.add(
            self.tab_convergencia,
            text="Convergencia"
        )
        notebook.add(self.tab_datos, text="Datos")

        ttk.Label(
            self.tab_soluciones,
            text=(
                "Negro: solución exacta. Naranja: Euler. Azul: RK4. "
                "La variable seleccionada se muestra frente al tiempo."
            ),
            padding=8,
            wraplength=1000
        ).pack(fill="x")

        self.texto_error = tk.StringVar()

        ttk.Label(
            self.tab_errores,
            textvariable=self.texto_error,
            padding=8,
            wraplength=1000
        ).pack(fill="x")

        self.texto_convergencia = tk.StringVar()

        ttk.Label(
            self.tab_convergencia,
            textvariable=self.texto_convergencia,
            padding=8,
            wraplength=1000
        ).pack(fill="x")

        self.crear_tabla(
            self.tab_convergencia,
            "convergencia",
            altura=5
        )

        self.fig_soluciones, self.canvas_soluciones = (
            self.crear_grafica(self.tab_soluciones)
        )

        self.fig_errores, self.canvas_errores = (
            self.crear_grafica(self.tab_errores)
        )

        self.fig_convergencia, self.canvas_convergencia = (
            self.crear_grafica(self.tab_convergencia)
        )

        ttk.Label(
            self.tab_datos,
            text=(
                "Valores de la variable seleccionada "
                "en cada instante de la malla."
            ),
            padding=8
        ).pack(fill="x")

        self.crear_tabla(
            self.tab_datos,
            "datos",
            altura=18,
            expandir=True
        )

    def crear_grafica(self, contenedor):
        figura = Figure(figsize=(9, 4), dpi=100)

        canvas = FigureCanvasTkAgg(
            figura,
            master=contenedor
        )

        barra = NavigationToolbar2Tk(
            canvas,
            contenedor,
            pack_toolbar=False
        )
        barra.update()
        barra.pack(side="bottom", fill="x")

        canvas.get_tk_widget().pack(
            fill="both",
            expand=True
        )

        return figura, canvas

    def crear_tabla(
        self,
        contenedor,
        nombre,
        altura,
        expandir=False
    ):
        bloque = ttk.Frame(contenedor, padding=8)
        bloque.pack(fill="both", expand=expandir)

        marco = ttk.Frame(bloque)
        marco.pack(fill="both", expand=True)

        tabla = ttk.Treeview(
            marco,
            show="headings",
            height=altura
        )

        desplazamiento = ttk.Scrollbar(
            marco,
            orient="vertical",
            command=tabla.yview
        )

        tabla.configure(
            yscrollcommand=desplazamiento.set
        )

        desplazamiento.pack(side="right", fill="y")
        tabla.pack(side="left", fill="both", expand=True)

        ttk.Button(
            bloque,
            text="Guardar tabla CSV",
            command=lambda: self.guardar_tabla(nombre)
        ).pack(anchor="e", pady=(6, 0))

        self.tablas[nombre] = {
            "widget": tabla,
            "columnas": [],
            "filas": [],
        }

    def llenar_tabla(self, nombre, columnas, filas):
        datos = self.tablas[nombre]
        tabla = datos["widget"]

        tabla.delete(*tabla.get_children())
        tabla["columns"] = columnas

        for columna in columnas:
            tabla.heading(columna, text=columna)
            tabla.column(
                columna,
                width=170,
                minwidth=100,
                anchor="center"
            )

        for fila in filas:
            valores = []

            for valor in fila:
                if valor is None:
                    valores.append("—")
                elif isinstance(valor, (float, np.floating)):
                    valores.append(f"{valor:.8g}")
                else:
                    valores.append(valor)

            tabla.insert("", "end", values=valores)

        # Guardamos los números originales para exportarlos.
        datos["columnas"] = columnas
        datos["filas"] = filas

    def guardar_tabla(self, nombre):
        datos = self.tablas[nombre]

        ruta = filedialog.asksaveasfilename(
            parent=self.ventana,
            title="Guardar tabla",
            initialfile=f"{nombre}.csv",
            defaultextension=".csv",
            filetypes=[("Archivo CSV", "*.csv")]
        )

        if not ruta:
            return

        try:
            with open(
                ruta,
                "w",
                newline="",
                encoding="utf-8-sig"
            ) as archivo:
                escritor = csv.writer(archivo)
                escritor.writerow(datos["columnas"])
                escritor.writerows(datos["filas"])

            messagebox.showinfo(
                "Tabla guardada",
                "El archivo se guardó correctamente.",
                parent=self.ventana
            )

        except OSError as error:
            messagebox.showerror(
                "No se pudo guardar",
                str(error),
                parent=self.ventana
            )

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
            h = float(self.paso.get())

            self.resultados = ejecutar_problema(
                self.problema,
                h
            )

            self.columna = self.problema["variables"].index(
                self.variable.get()
            )

            texto = (
                f"Intervalo: {self.problema['intervalo']}   |   "
                f"Condiciones iniciales: "
                f"{self.problema['iniciales']}"
            )

            if "v" in self.problema["variables"]:
                texto += "   |   v representa y'."

            self.descripcion.set(texto)

            self.dibujar_soluciones()
            self.dibujar_errores()
            self.mostrar_convergencia()
            self.mostrar_datos()

        except Exception as error:
            messagebox.showerror(
                "No se pudo calcular",
                str(error),
                parent=self.ventana
            )

    def dibujar_soluciones(self):
        figura = self.fig_soluciones
        figura.clear()

        t = self.resultados["t"]
        exacta = self.resultados["exacta"]
        columna = self.columna

        if exacta is None:
            eje = figura.add_subplot(121)
            fase = figura.add_subplot(122)
        else:
            eje = figura.add_subplot(111)

        if exacta is not None:
            eje.plot(
                t,
                exacta[:, columna],
                color="black",
                linewidth=2,
                label="Exacta"
            )

        for metodo in ("euler", "rk4"):
            u = self.resultados[metodo]

            eje.plot(
                t,
                u[:, columna],
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

        eje.set_title(
            f"Solución: {self.variable.get()}"
        )
        eje.set_xlabel("t")
        eje.set_ylabel(self.variable.get())
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

    def dibujar_errores(self):
        figura = self.fig_errores
        figura.clear()
        eje = figura.add_subplot(111)

        exacta = self.resultados["exacta"]

        if exacta is None:
            self.texto_error.set(
                "Para Lotka–Volterra no calculamos un error exacto. "
                "Consultá la pestaña Convergencia."
            )

            eje.text(
                0.5,
                0.5,
                "No hay una solución explícita de referencia.",
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
                "Error absoluto: distancia al valor exacto. "
                "Cuanto más cerca de cero, mejor. "
                "Máximos de la variable seleccionada — "
                + " | ".join(maximos)
            )

            eje.set_title(
                f"Error absoluto: {self.variable.get()}"
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
                "Se usan todos los pasos definidos para el problema. "
                "Error máximo entre todos los tiempos y componentes, "
                "sin normalizarlos. El selector de variable no cambia "
                "esta comparación."
            )

        else:
            columnas = [
                "Paso",
                "Diferencia Euler",
                "Diferencia RK4"
            ]

            texto = (
                "Se comparan aproximaciones con pasos h y h/2 "
                "en tiempos comunes, considerando ambas poblaciones. "
                "Son diferencias entre mallas, no errores exactos. "
                "La última fila no tiene una malla más fina disponible."
            )

        self.texto_convergencia.set(texto)

        filas = [
            (
                fila_euler["h"],
                fila_euler[campo],
                fila_rk4[campo]
            )
            for fila_euler, fila_rk4 in zip(
                resultados["euler"],
                resultados["rk4"]
            )
        ]

        self.llenar_tabla(
            "convergencia",
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
        t = self.resultados["t"]
        exacta = self.resultados["exacta"]
        columna = self.columna

        columnas = ["Tiempo"]
        arreglos = [t]

        if exacta is not None:
            columnas.append("Solución exacta")
            arreglos.append(exacta[:, columna])

        columnas.extend(["Euler", "RK4"])

        arreglos.extend([
            self.resultados["euler"][:, columna],
            self.resultados["rk4"][:, columna]
        ])

        filas = list(zip(*arreglos))

        self.llenar_tabla(
            "datos",
            columnas,
            filas
        )


if __name__ == "__main__":
    ventana = tk.Tk()
    aplicacion = Aplicacion(ventana)
    ventana.mainloop()