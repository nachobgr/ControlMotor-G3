import sys
import json
import os
import time
import random
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer

class ClinicalDataLogger:
    """Registra métricas consolidadas de diagnóstico motor y velocidad de tipeo."""
    def __init__(self, patient_id):
        self.patient_id = patient_id
        self.metrics = {
            "velocidad_optima_ms": 0,
            "tiempos_reaccion_ms": [], 
            "tr_promedio_ms": 0,
            "errores_impulsividad": 0, 
            "errores_omision": 0,      
            "fallos_fase_validacion": 0,
            "modo_libre_texto_final": "",
            "modo_libre_tiempo_s": 0,
            "modo_libre_cps": 0,
            "modo_libre_wpm": 0
        }
        self.results_dir = os.path.join(os.getcwd(), 'results')
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)

    def export(self):
        if self.metrics["tiempos_reaccion_ms"]:
            promedio = sum(self.metrics["tiempos_reaccion_ms"]) / len(self.metrics["tiempos_reaccion_ms"])
            self.metrics["tr_promedio_ms"] = round(promedio, 2)
            
        filename = f"{self.patient_id}_evaluacion_motora.json"
        filepath = os.path.join(self.results_dir, filename)
        
        data = {
            "paciente_id": self.patient_id,
            "fecha": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "metricas_diagnostico": self.metrics
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Métricas exportadas con éxito a: {filepath}")


class ScanningCalibrationUI(QWidget):
    def __init__(self, patient_id="anon_001", parent=None):
        super().__init__(parent)
        self.logger = ClinicalDataLogger(patient_id)
        
        # Parámetros del sistema
        self.scan_speed_ms = 1500
        self.fase_actual = "SIMBOLOS" 
        
        # Variables de Barrido Fila-Columna
        self.scan_mode = "FILAS" 
        self.current_row = -1
        self.current_col = -1
        self.target_row = -1
        self.target_col = -1
        self.time_highlighted = 0
        
        # Tolerancia Fase 1
        self.errores_consecutivos_fase1 = 0
        
        # Variables Fase Validación
        self.palabra_objetivo = "SOL"
        self.letras_escritas = ""
        self.errores_palabra = 0
        
        # Variables Escritura Libre
        self.texto_libre = ""
        self.tiempo_inicio_libre = 0
        
        self.scan_timer = QTimer(self)
        self.scan_timer.timeout.connect(self.scan_tick)
        
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Evaluación Motora: Barrido Fila-Columna")
        self.resize(900, 750)
        self.setStyleSheet("""
            QWidget { background-color: #D3D3D3; color: #2B2B2B; }
            QLabel.celda {
                border: 3px solid #2B2B2B; font-size: 36px; font-weight: bold;
                qproperty-alignment: AlignCenter; padding: 15px; border-radius: 8px;
            }
            QLabel.celda[highlighted="true"] { 
                background-color: #90CAF9; 
                color: #2B2B2B; 
                border: 4px solid #1976D2; 
            }
            QLabel#info_label { border: none; font-size: 24px; font-weight: bold; padding-bottom: 5px; }
            QLabel#display_texto { background-color: #FFFFFF; border: 2px solid #2B2B2B; font-size: 28px; }
            QLabel#target_card { 
                border: 3px dashed #2B2B2B; background-color: #E0E0E0; font-size: 40px; 
                qproperty-alignment: AlignCenter; border-radius: 8px; 
            }
        """)

        self.layout = QVBoxLayout(self)
        
        self.display_texto = QLabel("")
        self.display_texto.setObjectName("display_texto")
        self.display_texto.hide()
        self.layout.addWidget(self.display_texto)

        self.header_layout = QVBoxLayout()
        self.header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.info_label = QLabel("Presiona ESPACIO para comenzar calibración diagnóstica")
        self.info_label.setObjectName("info_label")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header_layout.addWidget(self.info_label)

        self.target_card = QLabel("")
        self.target_card.setObjectName("target_card")
        self.target_card.setFixedHeight(90)
        self.target_card.setMinimumWidth(120)
        self.target_card.hide() 
        
        card_center_layout = QHBoxLayout()
        card_center_layout.addStretch()
        card_center_layout.addWidget(self.target_card)
        card_center_layout.addStretch()
        self.header_layout.addLayout(card_center_layout)
        
        self.layout.addLayout(self.header_layout)

        self.grid_layout = QGridLayout()
        self.layout.addLayout(self.grid_layout)
        self.grid_cells = [] 
        
        self.construir_matriz_3x3()

    def construir_matriz_3x3(self):
        self.limpiar_grid()
        self.simbolos_datos = [
            ("★", "#D62828"), ("⬤", "#003049"), ("▲", "#2A9D8F"),
            ("■", "#F77F00"), ("♦", "#6A4C93"), ("♥", "#D62828"),
            ("♣", "#003049"), ("♠", "#386641"), ("⬟", "#5E548E")
        ]
        self.letras_validacion = ["S", "A", "M", "O", "R", "L", "E", "T", "C"]

        for i in range(3):
            fila_ui = []
            for j in range(3):
                idx = i * 3 + j
                simbolo, hex_color = self.simbolos_datos[idx]
                cell = QLabel(f"<span style='color:{hex_color}'>{simbolo}</span>") 
                cell.setProperty("class", "celda")
                cell.setProperty("highlighted", False) 
                self.grid_layout.addWidget(cell, i, j)
                fila_ui.append(cell)
            self.grid_cells.append(fila_ui)

    def construir_teclado_libre(self):
        self.limpiar_grid()
        self.fase_actual = "ESCRITURA_LIBRE"
        self.display_texto.show()
        self.target_card.hide()
        self.info_label.setText("MODO LIBRE: Escribe lo que desees. (Presiona ESC para salir y guardar)")
        
        teclado = [
            'Q', 'W', 'E', 'R', 'T', 'Y', 'U',
            'I', 'O', 'P', 'A', 'S', 'D', 'F',
            'G', 'H', 'J', 'K', 'L', 'Z', 'X',
            'C', 'V', 'B', 'N', 'M', '_', '<'
        ]
        
        for i in range(4):
            fila_ui = []
            for j in range(7):
                idx = i * 7 + j
                cell = QLabel(teclado[idx])
                cell.setProperty("class", "celda")
                cell.setProperty("highlighted", False)
                cell.setStyleSheet("font-size: 24px; padding: 8px;")
                self.grid_layout.addWidget(cell, i, j)
                fila_ui.append(cell)
            self.grid_cells.append(fila_ui)
            
        # --- INICIAMOS RELOJ DE ESCRITURA LIBRE ---
        self.tiempo_inicio_libre = time.time()
        
        self.reiniciar_barrido_a_filas()
        self.scan_timer.start(self.scan_speed_ms)

    def limpiar_grid(self):
        for i in reversed(range(self.grid_layout.count())): 
            widget = self.grid_layout.itemAt(i).widget()
            self.grid_layout.removeWidget(widget)
            widget.setParent(None)
        self.grid_cells.clear()

    def set_new_symbol_target(self):
        self.target_row = random.randint(0, len(self.grid_cells) - 1)
        self.target_col = random.randint(0, len(self.grid_cells[0]) - 1)
        
        idx_global = self.target_row * 3 + self.target_col
        simbolo, hex_color = self.simbolos_datos[idx_global]
        
        self.info_label.setText("FASE 1: Encuentra este símbolo")
        self.target_card.setText(f"<span style='color:{hex_color}'>{simbolo}</span>")
        self.target_card.show()

    def set_next_letter_target(self):
        if len(self.letras_escritas) == len(self.palabra_objetivo):
            self.finalizar_calibracion()
            return
            
        letra_buscada = self.palabra_objetivo[len(self.letras_escritas)]
        idx_global = self.letras_validacion.index(letra_buscada)
        self.target_row = idx_global // 3
        self.target_col = idx_global % 3
        
        progreso_visual = self.letras_escritas + " _" * (len(self.palabra_objetivo) - len(self.letras_escritas))
        self.info_label.setText(f"FASE 2: Escribe la palabra\nProgreso: {progreso_visual.strip()}")
        self.target_card.setText(f"<span style='color:#2B2B2B'>{self.palabra_objetivo}</span>")

    def cargar_fase_teclado_validacion(self):
        self.fase_actual = "VALIDACION"
        self.letras_escritas = ""
        self.errores_palabra = 0
        
        for i in range(3):
            for j in range(3):
                idx = i * 3 + j
                self.grid_cells[i][j].setText(self.letras_validacion[idx])
                
        self.set_next_letter_target()

    def start_test(self):
        self.set_new_symbol_target()
        self.reiniciar_barrido_a_filas()
        self.scan_timer.start(self.scan_speed_ms)

    def update_cell_style(self, cell, is_highlighted):
        cell.setProperty("highlighted", is_highlighted)
        cell.style().unpolish(cell)
        cell.style().polish(cell)

    def iluminar_fila_entera(self, row_idx, highlight):
        for col_idx in range(len(self.grid_cells[row_idx])):
            self.update_cell_style(self.grid_cells[row_idx][col_idx], highlight)

    def clear_all_highlights(self):
        for fila in self.grid_cells:
            for celda in fila:
                self.update_cell_style(celda, False)

    def scan_tick(self):
        self.clear_all_highlights()

        if self.scan_mode == "FILAS":
            if self.current_row == self.target_row and self.fase_actual != "ESCRITURA_LIBRE":
                self.logger.metrics["errores_omision"] += 1

            self.current_row = (self.current_row + 1) % len(self.grid_cells)
            self.iluminar_fila_entera(self.current_row, True)
            self.time_highlighted = time.time()
            
        elif self.scan_mode == "COLUMNAS":
            if self.current_col == self.target_col and self.current_row == self.target_row and self.fase_actual != "ESCRITURA_LIBRE":
                self.logger.metrics["errores_omision"] += 1

            self.current_col = (self.current_col + 1) % len(self.grid_cells[self.current_row])
            self.update_cell_style(self.grid_cells[self.current_row][self.current_col], True)
            self.time_highlighted = time.time()

    def handle_switch_press(self):
        if not self.scan_timer.isActive():
            if self.fase_actual == "SIMBOLOS": self.start_test()
            return

        tr_ms = int((time.time() - self.time_highlighted) * 1000)

        if self.scan_mode == "FILAS":
            self.scan_mode = "COLUMNAS"
            self.current_col = -1
            self.clear_all_highlights()
            self.scan_timer.start(self.scan_speed_ms) 
            return

        elif self.scan_mode == "COLUMNAS":
            if self.fase_actual == "ESCRITURA_LIBRE":
                caracter = self.grid_cells[self.current_row][self.current_col].text()
                if caracter == '_': self.texto_libre += " "
                elif caracter == '<': self.texto_libre = self.texto_libre[:-1]
                else: self.texto_libre += caracter
                
                self.display_texto.setText(self.texto_libre)
                self.reiniciar_barrido_a_filas()
                return

            acierto = (self.current_row == self.target_row and self.current_col == self.target_col)

            if acierto:
                self.logger.metrics["tiempos_reaccion_ms"].append(tr_ms)
                
                if self.fase_actual == "SIMBOLOS":
                    self.errores_consecutivos_fase1 = 0
                    self.scan_speed_ms = int(self.scan_speed_ms * 0.90) 
                    self.reiniciar_barrido_a_filas(self.set_new_symbol_target)
                elif self.fase_actual == "VALIDACION":
                    self.letras_escritas += self.palabra_objetivo[len(self.letras_escritas)]
                    self.reiniciar_barrido_a_filas(self.set_next_letter_target)
            else:
                self.logger.metrics["errores_impulsividad"] += 1
                
                if self.fase_actual == "SIMBOLOS":
                    self.errores_consecutivos_fase1 += 1
                    if self.errores_consecutivos_fase1 >= 2:
                        self.scan_speed_ms = int(self.scan_speed_ms * 1.25)
                        self.reiniciar_barrido_a_filas(self.cargar_fase_teclado_validacion)
                    else: 
                        self.scan_speed_ms = int(self.scan_speed_ms * 1.10)
                        self.reiniciar_barrido_a_filas(self.set_new_symbol_target)
                        
                elif self.fase_actual == "VALIDACION":
                    self.errores_palabra += 1
                    self.logger.metrics["fallos_fase_validacion"] += 1
                    if self.errores_palabra > 1:
                        self.scan_speed_ms = int(self.scan_speed_ms * 1.20) 
                        self.letras_escritas = "" 
                        self.errores_palabra = 0
                    self.reiniciar_barrido_a_filas(self.set_next_letter_target)

    def reiniciar_barrido_a_filas(self, funcion_siguiente=None):
        self.clear_all_highlights()
        self.scan_mode = "FILAS"
        self.current_row = -1
        self.current_col = -1
        self.scan_timer.setInterval(self.scan_speed_ms)
        if funcion_siguiente: funcion_siguiente()

    def finalizar_calibracion(self):
        self.scan_timer.stop()
        self.logger.metrics["velocidad_optima_ms"] = self.scan_speed_ms
        self.logger.export() # Guarda primer estado por seguridad
        self.construir_teclado_libre()

    # --- CÁLCULO DE VELOCIDAD FINAL ---
    def guardar_metricas_finales(self):
        """Calcula CPS y WPM antes de cerrar el programa"""
        self.scan_timer.stop()
        if self.fase_actual == "ESCRITURA_LIBRE" and self.tiempo_inicio_libre > 0:
            tiempo_total_s = time.time() - self.tiempo_inicio_libre
            caracteres_finales = len(self.texto_libre)
            
            cps = caracteres_finales / tiempo_total_s if tiempo_total_s > 0 else 0
            wpm = (cps * 60) / 5
            
            self.logger.metrics["modo_libre_texto_final"] = self.texto_libre
            self.logger.metrics["modo_libre_tiempo_s"] = round(tiempo_total_s, 2)
            self.logger.metrics["modo_libre_cps"] = round(cps, 3)
            self.logger.metrics["modo_libre_wpm"] = round(wpm, 2)
            
        self.logger.export()

    # --- CONTROLADORES DE CIERRE DE APLICACIÓN ---
    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Space, Qt.Key.Key_Return):
            self.handle_switch_press()
        elif event.key() == Qt.Key.Key_Escape:
            self.close() # Llama automáticamente a closeEvent
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        """Intercepta el cierre de ventana (por ESC o por la X) para garantizar que se guarde el JSON"""
        self.guardar_metricas_finales()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    modulo = ScanningCalibrationUI(patient_id="paciente_000")
    modulo.show()
    sys.exit(app.exec())