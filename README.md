
# 🧠 OpenRehab ACV — Área 2: Control Motor y Acceso (Hemiparesia)
### Ingeniería en Rehabilitación · Ciclo 2026 · Grupo 3
## Ignacio Bergara, Aguzin Lautaro y Leonel Pastor 
 
> Plataforma de evaluación motora para pacientes con hemiparesia. Incluye tres módulos funcionales de diagnóstico clínico que registran métricas objetivas y las exportan en formato JSON.
 
---
 
## 📋 Índice
 
- [Descripción general](#descripción-general)
- [Módulos incluidos](#módulos-incluidos)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Requisitos del sistema](#requisitos-del-sistema)
- [▶️ Ejecución rápida (archivo .exe)](#️-ejecución-rápida-archivo-exe)
- [🛠️ Modo desarrollador (desde el código fuente)](#️-modo-desarrollador-desde-el-código-fuente)
- [Formato de salida JSON](#formato-de-salida-json)
- [Prompts utilizados](#prompts-utilizados)
- [Créditos](#créditos)
 
---
 
## Descripción general
 
Este proyecto forma parte de la asignatura **Ingeniería en Rehabilitación** y fue desarrollado por el **Grupo 3**. Su objetivo es proporcionar herramientas de evaluación motora clínica para pacientes con hemiparesia, midiendo con precisión variables como tiempos de reacción, errores, trayectorias y fatiga muscular.
 
El sistema cuenta con una **interfaz de menú principal** desde la cual se accede a los tres módulos de prueba. Cada módulo genera un archivo `.json` en la carpeta `/results` con los datos de la sesión.
 
---
 
## Módulos incluidos
 
### 1. 🖱️ Arrastre Sostenido (`ArrastreSostenido.py`)
 
Evalúa el **control motor fino** y la **fatiga muscular** mediante una tarea de arrastrar y soltar (drag & drop).
 
- El paciente debe arrastrar un símbolo central hacia 8 destinos ubicados en distintas posiciones de la pantalla.
- Cada destino tiene un tamaño diferente, lo que permite aplicar la **Ley de Fitts** para calcular la dificultad del movimiento.
- Se registran duración real, duración de control (Fitts), distancia recorrida, intentos fallidos y resultado por cada destino.
 
**Métricas exportadas:**
| Variable | Descripción |
|---|---|
| `destino` | Número de destino (1–8) |
| `duracion_ms` | Tiempo real del movimiento en ms |
| `duracion_control_ms` | Tiempo esperado según Ley de Fitts |
| `ancho_destino_px` | Ancho del objetivo en píxeles |
| `distancia_inicial_px` | Distancia desde el centro al destino |
| `exitoso` | Si el arrastre fue completado correctamente |
| `intentos_fallidos` | Total de intentos no exitosos |
 
---
 
### 2. ⌨️ Barrido Rítmico (`BarridoRitmico.py`)
 
Sistema de **selección por pulsador único** para pacientes con movilidad mínima (scanning fila-columna).
 
El módulo consta de tres fases progresivas:
 
1. **Fase Símbolos:** El paciente debe seleccionar un símbolo objetivo en una grilla 3×3 usando únicamente la barra espaciadora. La velocidad de barrido se adapta automáticamente según el desempeño.
2. **Fase Validación:** El paciente deletrea la palabra "SOL" seleccionando letras en la grilla.
3. **Modo Libre:** Teclado de 28 teclas para escritura libre, con métricas de velocidad de tipeo.
 
**Métricas exportadas:**
| Variable | Descripción |
|---|---|
| `velocidad_optima_ms` | Intervalo de barrido final calibrado |
| `tiempos_reaccion_ms` | Lista de todos los tiempos de reacción |
| `tr_promedio_ms` | Promedio de tiempos de reacción |
| `errores_impulsividad` | Selecciones incorrectas (pulsación anticipada) |
| `errores_omision` | Objetivos que pasaron sin ser seleccionados |
| `fallos_fase_validacion` | Errores durante la fase de escritura guiada |
| `modo_libre_texto_final` | Texto escrito libremente por el paciente |
| `modo_libre_tiempo_s` | Duración de la sesión libre en segundos |
| `modo_libre_cps` | Caracteres por segundo |
| `modo_libre_wpm` | Palabras por minuto equivalentes |
 
---
 
### 3. 🖱️ Ganancia Adaptativa (`GananciaAdaptativa.py`)
 
Módulo que **ajusta automáticamente la sensibilidad del mouse** del sistema operativo para pacientes con rango de movimiento (ROM) limitado.
 
- Guía al paciente a través de 5 puntos en la pantalla (esquinas y centro), siguiendo círculos rojos parpadeantes.
- Calcula velocidad promedio de desplazamiento, error de trayectoria y eventos de overshoot.
- Aplica un ajuste porcentual a la sensibilidad del sistema Windows (escala 1–20).
- Solicita confirmación antes de guardar los cambios.
 
> ⚠️ **Nota:** Este módulo solo funciona en **Windows** ya que modifica parámetros del sistema operativo mediante `ctypes`.
 
**Métricas exportadas:**
| Variable | Descripción |
|---|---|
| `velocidad_promedio_px_s` | Velocidad media de desplazamiento del cursor |
| `error_camino_px` | Desviación promedio respecto a la trayectoria ideal |
| `overshoots_totales` | Cantidad de veces que se superó el objetivo |
| `ajuste_sugerido_porcentual` | Porcentaje de ajuste calculado |
| `sensibilidad_previa` | Sensibilidad del mouse antes del ajuste |
| `sensibilidad_actual` | Sensibilidad del mouse después del ajuste |
 

---
 
## Requisitos del sistema
 
- **Sistema operativo:** Windows 10/11 (requerido para Ganancia Adaptativa; los otros módulos funcionan en cualquier OS)
- **Python:** 3.10 o superior
 
---
 
## ▶️ Ejecución rápida (archivo .exe)
 
> Para usuarios sin entorno de desarrollo. No requiere instalación de Python ni dependencias.
 
### Pasos:
 
1. Descargar el archivo `OpenRehab_G3.exe` desde la sección [**Releases**](https://github.com/tu-org/openrehab-g3/releases/latest) del repositorio.
2. Hacer **doble clic** en el ejecutable.
3. Si Windows muestra una advertencia de seguridad, hacer clic en **"Más información" → "Ejecutar de todas formas"**.
4. Se abrirá el menú principal. Ingresar el nombre del paciente cuando se solicite.
5. Seleccionar la prueba a realizar desde el menú.
 
> 📁 Los resultados se guardarán automáticamente en la carpeta `results/` ubicada en el mismo directorio que el `.exe`.
 
---
 
## 🛠️ Modo desarrollador (desde el código fuente)
 
### 1. Clonar el repositorio
 
```bash
git clone https://github.com/tu-org/openrehab-g3.git
cd openrehab-g3
```
 
### 2. Crear un entorno virtual (recomendado)
 
```bash
# Windows
python -m venv venv
venv\Scripts\activate
 
# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```
 
### 3. Instalar dependencias
 
```bash
pip install -r requirements.txt
```
 
**Contenido de `requirements.txt`:**
```
PyQt6>=6.5.0
pyautogui>=0.9.54
```
 
> `tkinter` y `ctypes` ya vienen incluidos con la instalación estándar de Python.
 
### 4. Ejecutar la aplicación
 
```bash
python Menu.py
```
 
### 5. Ejecutar un módulo de forma independiente (opcional)
 
Cada módulo puede ejecutarse de forma autónoma para pruebas:
 
```bash
# Arrastre Sostenido
python ArrastreSostenido.py
 
# Barrido Rítmico
python BarridoRitmico.py
 
# Ganancia Adaptativa (solo Windows)
python GananciaAdaptativa.py
```
 
> Al ejecutarlos directamente, el ID de paciente se definirá con el valor por defecto especificado dentro de cada archivo. Para producción, siempre usar `Menu.py`.
 
---
 
## Formato de salida JSON
 
Todos los módulos utilizan la clase `ClinicalDataLogger` de `ExportJson.py` para generar archivos con la siguiente estructura:
 
```json
{
    "paciente_id": "Juan Perez",
    "fecha_registro": "2026-04-05 14:32:10",
    "datos_sesion": {
        "variable_1": "valor_1",
        "variable_2": "valor_2",
        "...": "..."
    }
}
```
 
Los archivos se nombran automáticamente con el formato:
 
```
{ID_PACIENTE}_{YYYYMMDD}_{HHMMSS}.json
```
 
Y se guardan en subcarpetas dentro de `results/`:
 
```
results/
├── ArrastreSostenido/
├── BarridoRitmico/
└── GananciaAdaptativa/
```
 
## Créditos
 
Desarrollado por el **Grupo 3** para la cátedra de Ingeniería en Rehabilitación — Primer cuatrimestre de 2026. ECyT-UNSAM.
 
Integrantes: 

- **Ignacio Bergara**
- **Lautaro Aguzin**
- **Leonel Pastor**