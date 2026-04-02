import tkinter as tk
from tkinter import messagebox, simpledialog
import ArrastreSostenido as AS
import BarridoRitmico as BR
import GananciaAdaptativa as GA

class MenuEvaluacion:
    def __init__(self, root):
        self.root = root
        self.root.title("Interfaz de Evaluación Motriz - G3")
        self.root.geometry("450x400")
        self.root.resizable(True, True)
        
        self.id_paciente = ""
        
        self.frame_principal = tk.Frame(root, padx=20, pady=20)
        self.frame_principal.pack(expand=True, fill="both")

        tk.Label(self.frame_principal, text="SISTEMA DE CONTROL MOTOR", font=("Helvetica", 16, "bold")).pack(pady=10)
        tk.Label(self.frame_principal, text="Seleccione la prueba a realizar:", font=("Helvetica", 12)).pack(pady=5)

        self.crear_boton("Arrastre Sostenido", self.ejecutar_as)
        self.crear_boton("Barrido Rítmico", self.ejecutar_br)
        self.crear_boton("Ganancia Adaptativa", self.ejecutar_ga)

        self.lbl_paciente = tk.Label(self.frame_principal, text="Paciente: No ingresado", fg="red", font=("Helvetica", 10, "italic"))
        self.lbl_paciente.pack(side="bottom", pady=20)

        self.root.after(100, self.solicitar_nombre)

    def crear_boton(self, texto, comando):
        btn = tk.Button(self.frame_principal, text=texto, font=("Helvetica", 11), width=30, height=2, command=comando)
        btn.pack(pady=10)

    def solicitar_nombre(self):
        nombre = simpledialog.askstring("Identificación", "Ingrese el nombre del paciente:", parent=self.root)
        if nombre and nombre.strip():
            self.id_paciente = nombre.strip()
            self.lbl_paciente.config(text=f"Paciente actual: {self.id_paciente}", fg="darkgreen")
        else:
            messagebox.showwarning("Atención", "El nombre del paciente es obligatorio.")
            self.solicitar_nombre()

    def confirmar_usuario(self):
        """
        Verifica el usuario. Si es 'No', pide el nuevo nombre y 
        devuelve True para que la ejecución continúe.
        """
        respuesta = messagebox.askyesno("Validación de Usuario", f"¿El usuario evaluado es {self.id_paciente}?")
        if not respuesta:
            self.solicitar_nombre()
            # Una vez actualizado el nombre, retornamos True para que la función llamadora prosiga
        return True

    def ejecutar_as(self):
        if self.confirmar_usuario():
            self.root.withdraw()
            try:
                AS.ejecutar_prueba_arrastre(self.id_paciente)
            except Exception as e:
                messagebox.showerror("Error", f"Error en Arrastre Sostenido: {e}")
            self.root.deiconify()

    def ejecutar_br(self):
        if self.confirmar_usuario():
            self.root.withdraw()
            try:
                BR.ejecutar_prueba_barrido(self.id_paciente)
            except Exception as e:
                messagebox.showerror("Error", f"Error en Barrido Rítmico: {e}")
            self.root.deiconify()

    def ejecutar_ga(self):
        if self.confirmar_usuario():
            self.root.withdraw()
            try:
                GA.ejecutar_prueba_ganancia(self.id_paciente)
            except Exception as e:
                messagebox.showerror("Error", f"Error en Ganancia Adaptativa: {e}")
            self.root.deiconify()

if __name__ == "__main__":
    root = tk.Tk()
    app = MenuEvaluacion(root)
    root.mainloop()