import ctypes #import ctypes
import tkinter as tk
import CalibGanAdapt as calib

# Constantes de la API de Windows para velocidad del mouse
GET_MOUSE_SPEED = 0x0070
SET_MOUSE_SPEED = 0x0071


"""
    La sensibilidad del mouse en Windows se mide en una escala de 1 a 20
    El codigo obtiene la velocidad actual, la reduce con un factor porcentual dado 
    y luego la aplica de nuevo al sistema operativo
"""
def reducir_sensibilidad(porcentaje):
    # Obtengo la velocidad actual del mouse
    current_speed = ctypes.c_int() # genero dato en C, compatible con Windows
    ctypes.windll.user32.SystemParametersInfoW(GET_MOUSE_SPEED, 0, ctypes.byref(current_speed), 0) # Obtengo la velocidad actual del mouse y almacenarla en current_speed.value

    # Modifico la velocidad segun el porcentaje dado
    if porcentaje < 0:
        new_speed = max(1, int(current_speed.value * (1 - abs(porcentaje)/100)))
    else:
        new_speed = min(20, int(current_speed.value * (1 + porcentaje/100)))
    # new_speed = max(1, 6) # vuelvo la velovidad a 6 por defecto
    
    # Aplicao la nueva velocidad (0x01 actualiza el perfil, 0x02 notifica el cambio)
    ctypes.windll.user32.SystemParametersInfoW(SET_MOUSE_SPEED, 0, new_speed, 0x01 | 0x02)
    
    print(f"Velocidad previa: {current_speed.value}")
    print(f"Nueva velocidad aplicada: {new_speed}")


if __name__ == "__main__":
    app_root = tk.Tk(); app_root.withdraw()
    app = calib.CalibradorCorregido(app_root)
    app_root.deiconify(); app_root.mainloop()

    reducir_sensibilidad(app.porcentaje_final)