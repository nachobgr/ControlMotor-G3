import json
import os
import time

# --------- Agregar en ficheros para exportar el json ---------
""""
import ExportJson as export

#ID_PACIENTE = "BR_PACIENTE_001"  # ID para el archivo JSON de barrido ritmico
#ID_PACIENTE = "AS_PACIENTE_001"  # ID para el archivo JSON de arrastre sostenido
#ID_PACIENTE = "GA_PACIENTE_001"  # ID para el archivo JSON de ganacia adaptativa

# Diccionario
resultados_finales = {
    "variable_1": valor_1,
    "variable_2": valor_2,
    "variable_n": valor_n
}

# Llamar a la clase para exportar json
logger = export.ClinicalDataLogger(ID_PACIENTE)
logger.exportar_datos(resultados_finales)

"""
class ClinicalDataLogger:
    """Gestor flexible para exportar métricas personalizadas a formato JSON."""
    def __init__(self, patient_id):
        self.patient_id = patient_id
        # Definimos la ruta de la carpeta 'results' en el directorio actual
        self.results_dir = os.path.join(os.getcwd(), 'results')
        
        # Si la carpeta no existe, la crea automáticamente
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)

    def exportar_datos(self, diccionario_metricas):
        """
        Recibe un diccionario con las variables que el usuario elija 
        y las guarda en un archivo JSON con marca de tiempo.
        """
        nombre_archivo = f"{self.patient_id}_evaluacion_{int(time.time())}.json"
        ruta_completa = os.path.join(self.results_dir, nombre_archivo)
        
        # Estructura final del documento
        data_final = {
            "paciente_id": self.patient_id,
            "fecha_registro": time.strftime("%Y-%m-%d %H:%M:%S"),
            "datos_sesion": diccionario_metricas
        }
        
        try:
            with open(ruta_completa, 'w', encoding='utf-8') as f:
                json.dump(data_final, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error al exportar el archivo: {e}")
