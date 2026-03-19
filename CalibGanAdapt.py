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
        self.color_fondo = "lime green"
        
        # AGREGADO: Atributo para que el valor sea accesible desde afuera
        self.porcentaje_final = 0.0
        
        # --- Leyenda Inicial ---
        messagebox.showinfo("CALIBRACION", "Siga los circulos rojos para calibrar la sensibilidad del cursor")
        
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.config(bg=self.color_fondo)
        self.root.wm_attributes("-transparentcolor", self.color_fondo)

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

        self.canvas = tk.Canvas(self.root, width=self.diametro, height=self.diametro, bg=self.color_fondo, highlightthickness=0)
        self.canvas.pack()
        self.circulo = self.canvas.create_oval(5, 5, self.diametro-5, self.diametro-5, fill="red", outline="white", width=4)

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
        
        if mx > wx + self.diametro or mx < wx or my > wy + self.diametro or my < wy:
            if mx >= self.sw - 5 or mx <= 5 or my >= self.sh - 5 or my <= 5:
                self.overshoot_actual = True

        if self.indice > 0:
            self.trayectoria_actual.append((mx, my))

        if wx <= mx <= wx + self.diametro and wy <= my <= wy + self.diametro:
            if self.indice > 0:
                p_ini, p_fin = self.puntos[self.indice-1], self.puntos[self.indice]
                err_max = max([self.calcular_error_lineal(p, p_ini, p_fin) for p in self.trayectoria_actual]) if self.trayectoria_actual else 0
                self.datos_tramos.append({"tiempo": time.time() - self.inicio_tramo, "error_camino": err_max, "overshoot": self.overshoot_actual})

            self.indice += 1
            if self.indice < len(self.puntos):
                self.posicionar()
            else:
                self.procesar_logica_final()
                self.root.quit() # Detiene el mainloop
                self.root.destroy() # Cierra la ventana
                return
        self.root.after(10, self.verificar_mouse)

    def procesar_logica_final(self):
        avg_t = sum(d['tiempo'] for d in self.datos_tramos) / len(self.datos_tramos)
        avg_err = sum(d['error_camino'] for d in self.datos_tramos) / len(self.datos_tramos)
        total_ov = sum(1 for d in self.datos_tramos if d['overshoot'])
        
        ref_t = 0.9 
        
        # MODIFICADO: Guardamos en el atributo de clase
        if avg_err < 80 and total_ov < 2:
            if avg_t > ref_t:
                self.porcentaje_final = ((avg_t / ref_t) - 1) * 100
            else:
                self.porcentaje_final = 0.0
        else:
            penalizacion = (total_ov * 10) + ((avg_err - 80) / 10)
            self.porcentaje_final = -penalizacion

        print("\n" + "="*50)
        print(f"TIEMPO: {avg_t:.2f}s | ERROR: {avg_err:.1f}px | OV: {total_ov}")
        print(f"AJUSTE SUGERIDO: {self.porcentaje_final:.1f}%")
        print("="*50)

if __name__ == "__main__":
    app_root = tk.Tk(); app_root.withdraw()
    app = CalibradorCorregido(app_root)
    app_root.deiconify(); app_root.mainloop()

    # Ahora puedes acceder a la variable a través de la instancia 'app'
    print(f"aca quiero imprimir el porcentaje final: {app.porcentaje_final:.2f}%")
