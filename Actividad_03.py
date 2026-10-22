"""
CTE-334 - Desarrollo de Aplicaciones SIG
Actividad 03 - Planificacion de un vuelo fotogrametrico con dron
Autor: Gitzy Yissel Andrade Andrade
Numero de cuenta: 20161030363

La logica matematica (calcular_plan_vuelo) esta separada de la interfaz
(clase PlanificadorApp), de modo que las formulas se pueden probar sin
abrir ninguna ventana.
"""

import math
import tkinter as tk
from tkinter import messagebox, ttk


# ---------------------------------------------------------------------------
# Definicion de los datos de entrada
# ---------------------------------------------------------------------------

class Campo:
    """Describe un dato de entrada: variable, etiqueta, unidad, ejemplo y
    la regla que debe cumplir ('positivo' o 'traslape')."""

    def __init__(self, variable, etiqueta, unidad, ejemplo, regla):
        self.variable = variable
        self.etiqueta = etiqueta
        self.unidad = unidad
        self.ejemplo = ejemplo
        self.regla = regla


GRUPOS = {
    "Cámara": [
        Campo("focal", "Distancia focal", "mm", "3.61", "positivo"),
        Campo("ancho_imagen_px", "Ancho de imagen", "píxeles", "4000", "positivo"),
        Campo("alto_imagen_px", "Alto de imagen", "píxeles", "3000", "positivo"),
    ],
    "Sensor": [
        Campo("ancho_sensor_mm", "Ancho del sensor", "mm", "6.3175", "positivo"),
        Campo("alto_sensor_mm", "Alto del sensor", "mm", "4.7381", "positivo"),
    ],
    "Vuelo": [
        Campo("altura_vuelo_m", "Altura de vuelo", "m", "120", "positivo"),
        Campo("traslape_longitudinal", "Traslape longitudinal", "%", "80", "traslape"),
        Campo("traslape_transversal", "Traslape transversal", "%", "70", "traslape"),
        Campo("velocidad_m_s", "Velocidad", "m/s", "8", "positivo"),
    ],
    "Parcela": [
        Campo("largo_parcela_m", "Largo", "m", "700", "positivo"),
        Campo("ancho_parcela_m", "Ancho", "m", "250", "positivo"),
    ],
}

TODOS_LOS_CAMPOS = [c for lista in GRUPOS.values() for c in lista]


class ErrorDeEntrada(Exception):
    """Error de validacion con un titulo y un mensaje que indica que corregir."""

    def __init__(self, titulo, mensaje):
        super().__init__(mensaje)
        self.titulo = titulo
        self.mensaje = mensaje


# ---------------------------------------------------------------------------
# Logica (sin widgets)
# ---------------------------------------------------------------------------

def convertir_a_numero(campo, texto):
    """Convierte el texto de un campo a float o lanza ErrorDeEntrada."""
    texto = texto.strip()
    if not texto:
        raise ErrorDeEntrada(
            "Campo vacío",
            f"El campo «{campo.etiqueta}» está vacío. Escriba un valor en {campo.unidad}.")
    try:
        valor = float(texto.replace(",", "."))
    except ValueError:
        raise ErrorDeEntrada(
            "Dato no numérico",
            f"«{campo.etiqueta}» no es un número ({texto}). Use dígitos y punto decimal, "
            "por ejemplo 3.61.") from None
    if not math.isfinite(valor):
        raise ErrorDeEntrada(
            "Dato no numérico", f"«{campo.etiqueta}» debe ser un número finito.")
    return valor


def comprobar_rango(campo, valor):
    """Verifica la regla del campo o lanza ErrorDeEntrada."""
    if campo.regla == "positivo" and valor <= 0:
        raise ErrorDeEntrada(
            "Valor fuera de rango",
            f"«{campo.etiqueta}» debe ser mayor que 0 ({campo.unidad}).")
    if campo.regla == "traslape" and not 0 <= valor < 100:
        raise ErrorDeEntrada(
            "Valor fuera de rango",
            f"«{campo.etiqueta}» debe ser de 0 % hasta menos de 100 %.")


def calcular_plan_vuelo(datos):
    """Recibe un diccionario con los once datos y devuelve un diccionario
    con los resultados. Distancia y duracion usan valores teoricos; solo
    pasadas, fotos por pasada y fotos totales se redondean."""
    rsi = datos["ancho_sensor_mm"] / datos["ancho_imagen_px"]           # mm/px
    gsd = datos["altura_vuelo_m"] * 100 / datos["focal"] * rsi          # cm/px
    escala = datos["altura_vuelo_m"] / (datos["focal"] / 1000)          # 1:E

    huella_x = datos["ancho_sensor_mm"] * escala / 1000                 # m
    huella_y = datos["alto_sensor_mm"] * escala / 1000                  # m
    base = huella_x * (1 - datos["traslape_longitudinal"] / 100)        # m
    sep = huella_y * (1 - datos["traslape_transversal"] / 100)          # m

    intervalo = base / datos["velocidad_m_s"]                           # s
    n_pasadas = datos["ancho_parcela_m"] / sep
    n_fotos_pasada = datos["largo_parcela_m"] / base + 1
    n_fotos = n_pasadas * n_fotos_pasada
    dist_total = n_pasadas * datos["largo_parcela_m"] + datos["ancho_parcela_m"]
    minutos = n_fotos * intervalo / 60

    return {
        "RSI": (f"{rsi:.6f}", "mm/píxel"),
        "GSD": (f"{gsd:.2f}", "cm/píxel"),
        "Escala": (f"1 : {escala:,.0f}", ""),
        "Ancho de imagen en terreno": (f"{huella_x:,.2f}", "m"),
        "Alto de imagen en terreno": (f"{huella_y:,.2f}", "m"),
        "Base aérea": (f"{base:,.2f}", "m"),
        "Distancia entre pasadas": (f"{sep:,.2f}", "m"),
        "Intervalo entre fotografías": (f"{intervalo:.2f}", "s"),
        "Número de pasadas": (str(round(n_pasadas)), ""),
        "Fotografías por pasada": (str(round(n_fotos_pasada)), ""),
        "Fotografías por vuelo": (str(math.ceil(n_fotos)), ""),
        "Distancia total de vuelo": (f"{dist_total:,.2f}", "m"),
        "Duración estimada": (f"{minutos:.2f}", "min"),
    }


def formatear_resultados(resultados):
    """Convierte el diccionario de resultados en texto alineado."""
    ancho = max(len(nombre) for nombre in resultados)
    lineas = ["PLAN DE VUELO FOTOGRAMÉTRICO", "=" * (ancho + 22)]
    for nombre, (valor, unidad) in resultados.items():
        lineas.append(f"{nombre:<{ancho}}  {valor:>12} {unidad}".rstrip())
    return "\n".join(lineas)


# ---------------------------------------------------------------------------
# Interfaz
# ---------------------------------------------------------------------------

class PlanificadorApp:
    """Ventana principal del planificador."""

    def __init__(self, raiz):
        self.raiz = raiz
        self.entradas = {}
        self.estado = tk.StringVar(value="Listo. Ingrese los datos o cargue el ejemplo.")
        raiz.title("Planificador de vuelo fotogramétrico - CTE 334")
        raiz.resizable(False, False)
        self._crear_formulario()
        self._crear_acciones()
        self._crear_resultados()
        raiz.bind("<Return>", lambda _e: self.ejecutar_calculo())
        self.entradas["focal"].focus_set()

    # -- construccion -------------------------------------------------------

    def _crear_formulario(self):
        cuerpo = ttk.Frame(self.raiz, padding=(12, 12, 12, 0))
        cuerpo.grid(row=0, column=0, sticky="nsew")
        posiciones = {"Cámara": (0, 0), "Sensor": (1, 0), "Vuelo": (0, 1), "Parcela": (1, 1)}
        for titulo, campos in GRUPOS.items():
            fila, col = posiciones[titulo]
            marco = ttk.LabelFrame(cuerpo, text=titulo, padding=8)
            marco.grid(row=fila, column=col, padx=6, pady=4, sticky="nsew")
            for i, campo in enumerate(campos):
                ttk.Label(marco, text=campo.etiqueta).grid(row=i, column=0, sticky="w", pady=3)
                caja = ttk.Entry(marco, width=11, justify="right")
                caja.grid(row=i, column=1, padx=6, pady=3)
                ttk.Label(marco, text=campo.unidad, width=8).grid(row=i, column=2, sticky="w")
                self.entradas[campo.variable] = caja

    def _crear_acciones(self):
        barra = ttk.Frame(self.raiz, padding=8)
        barra.grid(row=1, column=0)
        ttk.Button(barra, text="Calcular", command=self.ejecutar_calculo).grid(row=0, column=0, padx=5)
        ttk.Button(barra, text="Limpiar", command=self.limpiar).grid(row=0, column=1, padx=5)
        ttk.Button(barra, text="Cargar ejemplo", command=self.cargar_ejemplo).grid(row=0, column=2, padx=5)

    def _crear_resultados(self):
        marco = ttk.LabelFrame(self.raiz, text="Resultados", padding=8)
        marco.grid(row=2, column=0, padx=18, sticky="nsew")
        self.salida = tk.Text(marco, width=58, height=16, state="disabled",
                              font="TkFixedFont", bg="#f4f4f4", relief="flat")
        self.salida.grid(row=0, column=0)
        ttk.Label(self.raiz, textvariable=self.estado, relief="sunken", anchor="w",
                  padding=4).grid(row=3, column=0, sticky="ew", padx=18, pady=10)

    # -- acciones -----------------------------------------------------------

    def _escribir_salida(self, texto):
        self.salida.config(state="normal")
        self.salida.delete("1.0", tk.END)
        self.salida.insert("1.0", texto)
        self.salida.config(state="disabled")

    def ejecutar_calculo(self):
        """Leer -> convertir -> validar -> calcular -> mostrar."""
        self._escribir_salida("")  # los resultados anteriores se limpian siempre
        try:
            datos = {}
            for campo in TODOS_LOS_CAMPOS:
                datos[campo.variable] = convertir_a_numero(
                    campo, self.entradas[campo.variable].get())
            for campo in TODOS_LOS_CAMPOS:
                comprobar_rango(campo, datos[campo.variable])
        except ErrorDeEntrada as error:
            self.estado.set("Error en los datos: no se realizó el cálculo.")
            messagebox.showerror(error.titulo, error.mensaje)
            return
        self._escribir_salida(formatear_resultados(calcular_plan_vuelo(datos)))
        self.estado.set("Cálculo realizado correctamente.")

    def limpiar(self):
        for caja in self.entradas.values():
            caja.delete(0, tk.END)
        self._escribir_salida("")
        self.estado.set("Formulario limpiado.")
        self.entradas["focal"].focus_set()

    def cargar_ejemplo(self):
        for campo in TODOS_LOS_CAMPOS:
            caja = self.entradas[campo.variable]
            caja.delete(0, tk.END)
            caja.insert(0, campo.ejemplo)
        self._escribir_salida("")
        self.estado.set("Ejemplo cargado. Presione Calcular.")


def main():
    raiz = tk.Tk()
    PlanificadorApp(raiz)
    raiz.mainloop()


if __name__ == "__main__":
    main()
