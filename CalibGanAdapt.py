import tkinter as tk
from tkinter import messagebox
import pyautogui
import time
import math

class CalibradorCorregido:
    def __init__(self, root):
        self.root = root
        self.diametro = 120
        self.margen = 30
        self.radio_activacion = 200
        self.color_transparente = "lime green"
        self.color_captura = "#ff9a9a" 
        self.porcentaje_final = 0.0
        
        messagebox.showinfo("CALIBRACION", "Siga los circulos rojos para calibrar la sensibilidad del cursor.\nHaga clic sobre cada círculo para avanzar.")
        
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.config(bg=self.color_transparente)
        self.root.wm_attributes("-transparentcolor", self.color_transparente)

        self.sw, self.sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()

        self.puntos = [
            (self.sw - self.diametro//2 - self.margen, self.diametro//2 + self.margen), # 0: Sup Der
            (self.diametro//2 + self.margen, self.diametro//2 + self.margen),           # 1: Sup Izq
            (self.sw - self.diametro//2 - self.margen, self.sh - self.diametro//2 - self.margen), # 2: Inf Der
            (self.diametro//2 + self.margen, self.sh - self.diametro//2 - self.margen), # 3: Inf Izq
            (self.sw // 2, self.sh // 2)                                               # 4: Centro
        ]
        
        self.indice = 0
        self.datos_tramos = [] 
        self.trayectoria_actual = []
        self.overshoot_actual = False
        self.inicio_tramo = None

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
        
        # Centro del círculo para el radio de activación invisible
        centro_x = wx + self.diametro // 2
        centro_y = wy + self.diametro // 2
        distancia = math.sqrt((mx - centro_x)**2 + (my - centro_y)**2)

        # Solo evaluamos overshoot si el cursor está dentro del radio de 200px
        if distancia <= self.radio_activacion:
            izq, der = wx, wx + self.diametro
            sup, inf = wy, wy + self.diametro

            # Lógica de Overshoot Direccional
            if self.indice == 0: # Sup Der
                if my < sup or mx > der: self.overshoot_actual = True
            elif self.indice == 1: # Sup Izq
                if my < sup or mx < izq: self.overshoot_actual = True
            elif self.indice == 2: # Inf Der
                if my > inf or mx > der: self.overshoot_actual = True
            elif self.indice == 3: # Inf Izq
                if my > inf or mx < izq: self.overshoot_actual = True
            elif self.indice == 4: # Centro: Solo límite superior y derecho
                if my < sup or mx > der: self.overshoot_actual = True

        # Siempre guardamos la trayectoria para el cálculo de error lineal
        self.trayectoria_actual.append((mx, my))
        self.root.after(10, self.verificar_mouse)

    def registrar_clic(self, event):
        ahora = time.time()
        
        # Definimos punto inicial para el cálculo de error lineal
        # Si es el primer punto, tomamos el centro de la pantalla como referencia inicial
        p_ini = self.puntos[self.indice-1] if self.indice > 0 else (self.sw//2, self.sh//2)
        p_fin = self.puntos[self.indice]
        
        err_max = max([self.calcular_error_lineal(p, p_ini, p_fin) for p in self.trayectoria_actual]) if self.trayectoria_actual else 0
        
        # Guardamos datos del tramo actual (incluyendo el punto 0)
        self.datos_tramos.append({
            "tiempo": ahora - self.inicio_tramo, 
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
        avg_t = sum(d['tiempo'] for d in self.datos_tramos) / len(self.datos_tramos)
        avg_err = sum(d['error_camino'] for d in self.datos_tramos) / len(self.datos_tramos)
        total_ov = sum(1 for d in self.datos_tramos if d['overshoot'])
        ref_t = 0.9 
        
        if avg_err < 80 and total_ov < 2:
            self.porcentaje_final = ((avg_t / ref_t) - 1) * 100 if avg_t > ref_t else 0.0
        else:
            # Penalización por falta de precisión u overshoot
            penalizacion = (total_ov * 10) + ((avg_err - 80) / 10)
            self.porcentaje_final = -penalizacion

        print("\n" + "="*50)
        print(f"TIEMPO: {avg_t:.2f}s | ERROR: {avg_err:.1f}px | OV: {total_ov}")
        print(f"AJUSTE SUGERIDO: {self.porcentaje_final:.1f}%")
        print("="*50)

