import sys
import json
import time
import math
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QRect, QPoint
from PyQt6.QtGui import QPainter, QColor, QFont, QPen
import ExportJson as export

class ArrastreSostenido(QWidget):

    CORNER_SIZES = {
        1: 60,
        2: 140,
        3: 95,
        4: 180,
        5: 70,
        6: 100,
        7: 50,
        8: 165,
    }
    DRAG_SIZE = 50
    CORNER_MARGIN = 20
    CORNER_SQUARES = {1, 3, 6, 8}

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prueba de Arrastre Sostenido")
        screen = QApplication.primaryScreen().availableGeometry()
        self.WINDOW_W = screen.width()
        self.WINDOW_H = screen.height()

        m = self.CORNER_MARGIN
        w, h = self.WINDOW_W, self.WINDOW_H
        sizes = self.CORNER_SIZES

        # Distribucion en 3 filas: 1,2,3 / 4,5 / 6,7,8
        top_row_h = max(sizes[1], sizes[2], sizes[3])
        middle_row_h = max(sizes[4], sizes[5])
        bottom_row_h = max(sizes[6], sizes[7], sizes[8])

        top_y = m
        middle_y = (h - middle_row_h) // 2
        bottom_y = h - m - bottom_row_h - 35

        def left_rect(size, row_y, row_h):
            return QRect(m, row_y + (row_h - size) // 2, size, size)

        def center_rect(size, row_y, row_h):
            return QRect((w - size) // 2, row_y + (row_h - size) // 2, size, size)

        def right_rect(size, row_y, row_h):
            return QRect(w - m - size, row_y + (row_h - size) // 2, size, size)

        self.corners = {
            1: left_rect(sizes[1], top_y, top_row_h),
            2: center_rect(sizes[2], top_y, top_row_h),
            3: right_rect(sizes[3], top_y, top_row_h),
            4: left_rect(sizes[4], middle_y, middle_row_h),
            5: right_rect(sizes[5], middle_y, middle_row_h),
            6: left_rect(sizes[6], bottom_y, bottom_row_h),
            7: center_rect(sizes[7], bottom_y, bottom_row_h),
            8: right_rect(sizes[8], bottom_y, bottom_row_h),
        }

        self.simbolos = [
            ("★", "#D62828"), ("⬤", "#003049"), ("▲", "#2A9D8F"),
            ("■", "#F77F00"), ("♦", "#6A4C93"), ("♥", "#D62828"),
            ("♣", "#003049"), ("♠", "#386641"),
        ]

        self.current_number = 1
        self._reset_drag_to_center()
        drag_center = self.drag_rect.center()
        self.initial_distances = {
            num: round(math.hypot(
                drag_center.x() - rect.center().x(),
                drag_center.y() - rect.center().y()
            ), 2)
            for num, rect in self.corners.items()
        }
        self.started = False
        self.dragging = False
        self.drag_offset = QPoint()
        self.completed = False
        self.results = []
        self.failed_attempts = 0
        self.trial_start = None

    def _reset_drag_to_center(self):
        ds = self.DRAG_SIZE
        self.drag_rect = QRect(
            (self.WINDOW_W - ds) // 2,
            (self.WINDOW_H - ds) // 2,
            ds, ds
        )

    def _reset_test(self):
        self.current_number = 1
        self.started = False
        self.completed = False
        self.results = []
        self.failed_attempts = 0
        self.trial_start = None
        self._reset_drag_to_center()
        self.update()

    def _draw_direction_arrow(self, painter, start_point, end_point, target_rect):
        dx = end_point.x() - start_point.x()
        dy = end_point.y() - start_point.y()
        length = math.hypot(dx, dy)
        if length < 1:
            return

        ux = dx / length
        uy = dy / length

        start_offset = self.DRAG_SIZE // 2 + 8
        end_offset = min(target_rect.width(), target_rect.height()) // 2 + 8
        line_start = QPoint(
            int(start_point.x() + ux * start_offset),
            int(start_point.y() + uy * start_offset),
        )
        line_end = QPoint(
            int(end_point.x() - ux * end_offset),
            int(end_point.y() - uy * end_offset),
        )

        painter.setPen(QPen(QColor(200, 100, 200), 4))
        painter.drawLine(line_start, line_end)

        angle = math.atan2(line_end.y() - line_start.y(), line_end.x() - line_start.x())
        head_len = 16
        spread = math.pi / 7

        left_head = QPoint(
            int(line_end.x() - head_len * math.cos(angle - spread)),
            int(line_end.y() - head_len * math.sin(angle - spread)),
        )
        right_head = QPoint(
            int(line_end.x() - head_len * math.cos(angle + spread)),
            int(line_end.y() - head_len * math.sin(angle + spread)),
        )

        painter.setPen(QPen(QColor(200, 100, 200), 4))
        painter.drawLine(line_end, left_head)
        painter.drawLine(line_end, right_head)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(240, 240, 245))

        font = QFont("Arial", 22, QFont.Weight.Bold)
        painter.setFont(font)

        for num, rect in self.corners.items():
            if num < self.current_number:
                bg, border = QColor(80, 190, 100), QColor(30, 130, 60)
            elif num == self.current_number:
                bg, border = QColor(200, 220, 255), QColor(200, 100, 200)
            else:
                bg, border = QColor(200, 200, 210), QColor(100, 100, 130)

            painter.fillRect(rect, bg)
            painter.setPen(QPen(border, 3))
            painter.drawRect(rect)
            simbolo, color_simbolo = self.simbolos[num - 1]
            painter.setPen(QColor(color_simbolo))
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, simbolo)

        if not self.started:
            title_rect = QRect((self.WINDOW_W - 820) // 2, (self.WINDOW_H - 230) // 2, 820, 230)
            painter.fillRect(title_rect, QColor(220, 255, 220))
            painter.setPen(QPen(QColor(30, 130, 60), 2))
            painter.drawRect(title_rect)

            painter.setPen(QColor(30, 130, 60))
            font_big = QFont("Arial", 28, QFont.Weight.Bold)
            painter.setFont(font_big)
            painter.drawText(
                QRect(title_rect.x(), title_rect.y() + 25, title_rect.width(), 70),
                Qt.AlignmentFlag.AlignCenter,
                "Prueba de arrastre sostenido"
            )

            painter.setPen(QColor(30, 90, 50))
            font_small = QFont("Arial", 14)
            painter.setFont(font_small)
            painter.drawText(
                QRect(title_rect.x() + 20, title_rect.y() + 105, title_rect.width() - 40, 45),
                Qt.AlignmentFlag.AlignCenter,
                "Arrastre cada icono hasta su respectiva ubicacion en la pantalla"
            )
            painter.drawText(
                QRect(title_rect.x() + 20, title_rect.y() + 155, title_rect.width() - 40, 35),
                Qt.AlignmentFlag.AlignCenter,
                "Oprima barra de espacio o haga click para comenzar"
            )
            return

        if self.completed:
            font_big = QFont("Arial", 28, QFont.Weight.Bold)
            painter.setFont(font_big)
            msg_rect = QRect((self.WINDOW_W - 500) // 2, (self.WINDOW_H - 160) // 2, 500, 160)
            painter.fillRect(msg_rect, QColor(220, 255, 220))
            painter.setPen(QPen(QColor(30, 130, 60), 2))
            painter.drawRect(msg_rect)
            painter.setPen(QColor(30, 130, 60))
            painter.drawText(msg_rect, Qt.AlignmentFlag.AlignCenter, "¡Prueba completada!")

            font_small = QFont("Arial", 12)
            painter.setFont(font_small)
            painter.setPen(QColor(30, 90, 50))
            end_msg_rect = QRect((self.WINDOW_W - 900) // 2, msg_rect.bottom() + 15, 900, 40)
            painter.drawText(
                end_msg_rect,
                Qt.AlignmentFlag.AlignCenter,
                "Oprima Esc para terminar la prueba o la barra de espacio para repetirla"
            )
        else:
            target_rect = self.corners[self.current_number]
            self._draw_direction_arrow(
                painter,
                self.drag_rect.center(),
                target_rect.center(),
                target_rect,
            )

            painter.fillRect(self.drag_rect, QColor(255, 190, 40))
            painter.setPen(QPen(QColor(180, 100, 0), 3))
            painter.drawRect(self.drag_rect)
            simbolo_actual, color_actual = self.simbolos[self.current_number - 1]
            painter.setPen(QColor(color_actual))
            font = QFont("Arial", 22, QFont.Weight.Bold)
            painter.setFont(font)
            painter.drawText(self.drag_rect, Qt.AlignmentFlag.AlignCenter, simbolo_actual)

            font_small = QFont("Arial", 11)
            painter.setFont(font_small)
            painter.setPen(QColor(80, 80, 80))
            painter.drawText(
                QRect(0, self.WINDOW_H - 35, self.WINDOW_W, 30),
                Qt.AlignmentFlag.AlignCenter,
                "Arrastra el símbolo hasta su casilla correspondiente"
            )

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and not self.started:
            self.started = True
            self.trial_start = None
            self.update()
            return

        if event.button() == Qt.MouseButton.LeftButton and not self.completed:
            if self.drag_rect.contains(event.pos()):
                self.dragging = True
                self.drag_offset = event.pos() - self.drag_rect.topLeft()
                if self.trial_start is None:
                    self.trial_start = time.perf_counter()

    def mouseMoveEvent(self, event):
        if not self.started:
            return

        if self.dragging:
            self.drag_rect.moveTopLeft(event.pos() - self.drag_offset)
            self.update()

    def mouseReleaseEvent(self, event):
        if not self.started:
            return

        if not self.dragging:
            return
        self.dragging = False

        target = self.corners[self.current_number]
        size = self.CORNER_SIZES[self.current_number]
        ancho = round(size * math.sqrt(2), 2) if self.current_number in self.CORNER_SQUARES else size

        if self.drag_rect.intersects(target):
            if self.trial_start is None:
                self.trial_start = time.perf_counter()
            duration_ms = round(
                (time.perf_counter() - self.trial_start) * 1000
            )
            distancia = self.initial_distances[self.current_number]
            duracion_control_ms = round(135 + 249 * math.log2(distancia / ancho + 1), 2)
            self.results.append({
                "destino": self.current_number,
                "duracion_ms": duration_ms,
                "duracion_control_ms": duracion_control_ms,
                "ancho_destino_px": ancho,
                "distancia_inicial_px": distancia,
                "exitoso": True,
            })
            self.current_number += 1
            if self.current_number > 8:
                self.completed = True
                self._save_results()
            else:
                self._reset_drag_to_center()
                self.trial_start = None
        else:
            self.failed_attempts += 1
            self.trial_start = None
            self._reset_drag_to_center()

        self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
            return

        if not self.started and event.key() == Qt.Key.Key_Space:
            self.started = True
            self.trial_start = None
            self.update()
            return

        if self.completed and event.key() == Qt.Key.Key_Space:
            self._reset_test()
            return

        super().keyPressEvent(event)

    def _save_results(self):
        resultados_finales = {
            "fecha": datetime.now().isoformat(),
            "prueba": "ArrastreSostenido",
            "total_intentos": len(self.results) + self.failed_attempts,
            "intentos_fallidos": self.failed_attempts,
            "resultados": self.results,
        }

        # Llamar a la clase para exportar json
        logger = export.ClinicalDataLogger("ID_PACIENTE")
        logger.exportar_datos(resultados_finales)
        """
        import os
        data = {
            "fecha": datetime.now().isoformat(),
            "prueba": "ArrastreSostenido",
            "total_intentos": len(self.results) + self.failed_attempts,
            "intentos_fallidos": self.failed_attempts,
            "resultados": self.results,
        }
        os.makedirs("results", exist_ok=True)
        filename = f"results/arrastre_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)"""


def ejecutar_prueba_arrastre(ID_PACIENTE):
    app = QApplication(sys.argv)
    window = ArrastreSostenido()
    window.showMaximized()
    sys.exit(app.exec())
