"""
    La sensibilidad del mouse en Windows se mide en una escala de 1 a 20
    El codigo obtiene la velocidad actual, la reduce con un factor porcentual dado 
    y luego la aplica de nuevo al sistema operativo. Esto lo hace mediante una calibracion
    donde el usuario debe hacer clic en 5 puntos específicos de la pantalla (esquinas y centro) 
    siguiendo un círculo rojo.
"""
ID_PACIENTE = "GA_PACIENTE_001"  # ID para el archivo JSON

import ctypes
import tkinter as tk
from tkinter import messagebox
import pyautogui
import time
import math
import ExportJson as export

class CalibradorCorregido:
    def __init__(self, root):
        self.root = root
        self.diametro = 120
        self.margen = 30
        self.radio_activacion = 200
        self.color_transparente = "lime green"
        self.color_captura = "#ff9a9a" 
        self.porcentaje_final = 0.0
        
        # Variables para el diccionario final
        self.avg_v = 0  # Velocidad promedio (px/s)
        self.avg_err = 0
        self.total_ov = 0
        
        messagebox.showinfo("CALIBRACION", "Siga los circulos rojos.\nSe calculará su velocidad promedio de desplazamiento.")
        
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.config(bg=self.color_transparente)
        self.root.wm_attributes("-transparentcolor", self.color_transparente)

        self.sw, self.sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()

        self.puntos = [
            (self.sw - self.diametro//2 - self.margen, self.diametro//2 + self.margen),
            (self.diametro//2 + self.margen, self.diametro//2 + self.margen),
            (self.sw - self.diametro//2 - self.margen, self.sh - self.diametro//2 - self.margen),
            (self.diametro//2 + self.margen, self.sh - self.diametro//2 - self.margen),
            (self.sw // 2, self.sh // 2)
        ]
        
        self.indice = 0
        self.datos_tramos = [] 
        self.trayectoria_actual = []
        self.overshoot_actual = False
        self.inicio_tramo = None
        self.pos_inicial_mouse = None # Para calcular distancia recorrida

        self.canvas = tk.Canvas(self.root, width=self.diametro, height=self.diametro, bg=self.color_transparente, highlightthickness=0)
        self.canvas.pack()
        self.fondo_click = self.canvas.create_oval(5, 5, self.diametro-5, self.diametro-5, fill=self.color_captura, outline="white", width=4)
        self.circulo = self.canvas.create_oval(5, 5, self.diametro-5, self.diametro-5, fill="red", outline="white", width=4)

        self.canvas.bind("<Button-1>", self.registrar_clic)

        self.posicionar()
        self.parpadear()
        self.verificar_mouse()

    def posicionar(self):
        cx, cy = self.puntos[self.indice]
        self.root.geometry(f"{self.diametro}x{self.diametro}+{cx - self.diametro//2}+{cy - self.diametro//2}")
        self.overshoot_actual = False
        self.trayectoria_actual = []
        self.inicio_tramo = time.time()
        # Registramos dónde está el mouse al aparecer el nuevo círculo
        self.pos_inicial_mouse = pyautogui.position()

    def parpadear(self):
        estado = 'hidden' if self.canvas.itemcget(self.circulo, 'state') == 'normal' else 'normal'
        self.canvas.itemconfigure(self.circulo, state=estado)
        self.root.after(350, self.parpadear)

    def calcular_error_lineal(self, p_actual, p_ini, p_fin):
        x0, y0 = p_actual
        x1, y1 = p_ini
        x2, y2 = p_fin
        num = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
        den = math.sqrt((y2 - y1)**2 + (x2 - x1)**2)
        return num / den if den != 0 else 0

    def verificar_mouse(self):
        mx, my = pyautogui.position()
        wx, wy = self.root.winfo_x(), self.root.winfo_y()
        centro_x, centro_y = wx + self.diametro // 2, wy + self.diametro // 2
        distancia = math.sqrt((mx - centro_x)**2 + (my - centro_y)**2)

        if distancia <= self.radio_activacion:
            izq, der, sup, inf = wx, wx + self.diametro, wy, wy + self.diametro
            if self.indice == 0 and (my < sup or mx > der): self.overshoot_actual = True
            elif self.indice == 1 and (my < sup or mx < izq): self.overshoot_actual = True
            elif self.indice == 2 and (my > inf or mx > der): self.overshoot_actual = True
            elif self.indice == 3 and (my > inf or mx < izq): self.overshoot_actual = True
            elif self.indice == 4 and (my < sup or mx > der): self.overshoot_actual = True

        self.trayectoria_actual.append((mx, my))
        self.root.after(10, self.verificar_mouse)

    def registrar_clic(self, event):
        ahora = time.time()
        mx, my = pyautogui.position()
        
        # 1. Distancia recorrida en este tramo (del punto anterior al clic actual)
        ix, iy = self.pos_inicial_mouse
        distancia_tramo = math.sqrt((mx - ix)**2 + (my - iy)**2)
        
        # 2. Tiempo transcurrido
        tiempo_tramo = ahora - self.inicio_tramo
        
        # 3. Velocidad del tramo (evitando división por cero)
        velocidad_tramo = distancia_tramo / tiempo_tramo if tiempo_tramo > 0 else 0
        
        p_ini = self.puntos[self.indice-1] if self.indice > 0 else (self.sw//2, self.sh//2)
        p_fin = self.puntos[self.indice]
        err_max = max([self.calcular_error_lineal(p, p_ini, p_fin) for p in self.trayectoria_actual]) if self.trayectoria_actual else 0
        
        self.datos_tramos.append({
            "velocidad": velocidad_tramo, 
            "error_camino": err_max, 
            "overshoot": self.overshoot_actual
        })

        self.indice += 1
        if self.indice < len(self.puntos):
            self.posicionar()
        else:
            self.procesar_logica_final()
            self.root.quit()
            self.root.destroy()

    def procesar_logica_final(self):
        # Promedio de las velocidades de cada tramo
        self.avg_v = sum(d['velocidad'] for d in self.datos_tramos) / len(self.datos_tramos)
        self.avg_err = sum(d['error_camino'] for d in self.datos_tramos) / len(self.datos_tramos)
        self.total_ov = sum(1 for d in self.datos_tramos if d['overshoot'])
        
        # Lógica de ajuste basada en velocidad (ejemplo: referencia de 800 px/s)
        ref_v = 800 
        if self.avg_err < 80 and self.total_ov < 2:
            # Si la velocidad es menor a la referencia, se sugiere aumentar sensibilidad
            self.porcentaje_final = ((ref_v / self.avg_v) - 1) * 100 if self.avg_v < ref_v else 0.0
        else:
            penalizacion = (self.total_ov * 10) + ((self.avg_err - 80) / 10)
            self.porcentaje_final = -penalizacion

# ---------- MODIFICACION DE SENSIBILIDAD ----------

GET_MOUSE_SPEED = 0x0070
SET_MOUSE_SPEED = 0x0071

def aplicar_ajuste_sensibilidad(porcentaje):
    current_speed = ctypes.c_int()
    ctypes.windll.user32.SystemParametersInfoW(GET_MOUSE_SPEED, 0, ctypes.byref(current_speed), 0)
    vel_previa = current_speed.value

    if porcentaje < 0:
        new_speed = max(1, int(vel_previa * (1 - abs(porcentaje)/100)))
    else:
        new_speed = min(20, int(vel_previa * (1 + porcentaje/100)))
    
    ctypes.windll.user32.SystemParametersInfoW(SET_MOUSE_SPEED, 0, new_speed, 0x01 | 0x02)
    return vel_previa, new_speed

if __name__ == "__main__":
    app_root = tk.Tk(); app_root.withdraw()
    calibrador = CalibradorCorregido(app_root)
    app_root.deiconify(); app_root.mainloop()

    # Obtenemos las sensibilidades al aplicar el ajuste
    s_previa, s_actual = aplicar_ajuste_sensibilidad(calibrador.porcentaje_final)

    # Diccionario para exportar json
    resultados_finales = {
        "velocidad_promedio_px_s": round(calibrador.avg_v, 2),
        "error_camino_px": round(calibrador.avg_err, 1),
        "overshoots_totales": calibrador.total_ov,
        "ajuste_sugerido_porcentual": round(calibrador.porcentaje_final, 1),
        "sensibilidad_previa": s_previa,
        "sensibilidad_actual": s_actual
    }

    # Llamar a la clase para exportar json
    logger = export.ClinicalDataLogger(ID_PACIENTE)
    logger.exportar_datos(resultados_finales)