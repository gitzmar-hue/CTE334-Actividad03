# CTE334-Actividad03

## 1. Datos del estudiante

- **Nombre:** Gitzy Yissel Andrade Andrade
- **Número de cuenta:** 20161030363
- **Curso:** CTE 334 – Desarrollo de Aplicaciones SIG (UNAH)
- **Profesor:** José David Cáceres

## 2. Descripción y objetivo

Aplicación de escritorio (Tkinter/ttk) para planificar de forma básica un vuelo fotogramétrico con dron. Solicita once datos de cámara, sensor, vuelo y parcela, valida las entradas, aplica las fórmulas de fotogrametría estudiadas y muestra en la misma ventana: RSI, GSD, escala, huella en terreno, base aérea, distancia entre pasadas, intervalo entre fotografías, pasadas, fotografías por pasada, fotografías totales, distancia total y duración estimada.

## 3. Versión de Python y sistema de construcción

- **Python:** 3.12 (entorno Conda `actividad03`). Solo usa la biblioteca estándar (`math`, `tkinter`, `tkinter.messagebox`).
- **Sistema operativo de construcción del .exe:** Windows (PyInstaller no compila de forma cruzada). *(Anote aquí su versión de Windows.)*

## 4. Ejecución y reconstrucción del .exe

Ejecutar el código fuente:

```bash
python Actividad_03.py
```

Reconstruir el ejecutable (en Windows):

```bash
conda create --name actividad03 python=3.12 pyinstaller -y
conda activate actividad03
python -m PyInstaller --onefile --windowed --name PlanificadorVueloFotogrametrico Actividad_03.py
```

El ejecutable queda en `dist\PlanificadorVueloFotogrametrico.exe`.

## 5. Uso de la interfaz

| Control | Función |
|---|---|
| Grupos Cámara, Sensor, Vuelo y Parcela | Once cajas de entrada, cada una con su unidad visible |
| **Calcular** (o Enter) | Valida y calcula; reemplaza el resultado anterior |
| **Limpiar** | Vacía las cajas y el área de resultados |
| **Cargar ejemplo** | Rellena los once valores del caso de referencia |
| Área **Resultados** | `tk.Text` con cada magnitud y su unidad |
| Barra de estado | Confirma cálculo, limpieza o error |

Validaciones: campos vacíos, datos no numéricos (incluye `nan` e `inf`), valores mayores que 0 (focal, dimensiones, altura, velocidad y parcela) y traslapes entre 0 % y menos de 100 %. Cada error indica qué corregir, borra el resultado anterior y no muestra resultados parciales; la aplicación sigue abierta.

## 6. Caso de prueba de referencia

Entradas: focal 3.61 mm; imagen 4000 × 3000 px; sensor 6.3175 × 4.7381 mm; altura 120 m; traslape longitudinal 80 %; transversal 70 %; velocidad 8 m/s; parcela 700 × 250 m.

| Resultado | Valor obtenido | Unidad |
|---|---|---|
| RSI | 0.001579 | mm/píxel |
| GSD | 5.25 | cm/píxel |
| Escala | 1 : 33,241 | — |
| Ancho de imagen en terreno | 210.00 | m |
| Alto de imagen en terreno | 157.50 | m |
| Base aérea | 42.00 | m |
| Distancia entre pasadas | 47.25 | m |
| Intervalo entre fotografías | 5.25 | s |
| Número de pasadas | 5 | — |
| Fotografías por pasada | 18 | — |
| Fotografías por vuelo | 94 | — |
| Distancia total de vuelo | 3,953.72 | m |
| Duración estimada | 8.18 | min |

## 7. Decisiones de diseño

La función `calcular_plan_vuelo(datos)` es pura y no conoce widgets, por lo que las fórmulas se prueban sin abrir la ventana. La interfaz es la clase `PlanificadorApp`; su método `ejecutar_calculo()` sigue el orden leer → convertir → validar → calcular → mostrar. Los datos de entrada se describen una sola vez en `GRUPOS` (variable, etiqueta, unidad, ejemplo y regla), y de ahí salen las cajas, las unidades y las validaciones. Los errores se lanzan como `ErrorDeEntrada` y se muestran en una ventana emergente. Pasadas y fotografías por pasada se muestran con `round()` y el total con `ceil()`; distancia y duración se calculan con los valores teóricos antes de redondear, como pide la guía.

## 8. Limitaciones y advertencia de uso académico

El modelo es una planificación básica: supone terreno plano, vuelo a altura constante, cámara en posición nadir y sin considerar viento, giros del dron ni tiempo de despegue o aterrizaje. Es un trabajo académico y no debe usarse para planificar vuelos reales. El ejecutable no está firmado, por lo que Windows o el antivirus pueden mostrar advertencias; el origen es este repositorio y el código fuente está incluido.
