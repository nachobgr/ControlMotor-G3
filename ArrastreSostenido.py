import sys
import json
import time
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QRect, QPoint
from PyQt6.QtGui import QPainter, QColor, QFont, QPen

class ArrastreSostenido(QWidget):

    CORNER_SIZE = 100
    DRAG_SIZE = 80
    CORNER_MARGIN = 20

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prueba de Arrastre Sostenido")
        screen = QApplication.primaryScreen().availableGeometry()
        self.WINDOW_W = screen.width()
        self.WINDOW_H = screen.height()

        m = self.CORNER_MARGIN
        s = self.CORNER_SIZE
        w, h = self.WINDOW_W, self.WINDOW_H

        # Distribucion en 3 filas: 1,2,3 / 4,5 / 6,7,8
        top_y = m
        middle_y = (h - s) // 2
        bottom_y = h - m - s

        left_x = m
        center_x = (w - s) // 2
        right_x = w - m - s

        self.corners = {
            1: QRect(left_x, top_y, s, s),
            2: QRect(center_x, top_y, s, s),
            3: QRect(right_x, top_y, s, s),
            4: QRect(left_x, middle_y, s, s),
            5: QRect(right_x, middle_y, s, s),
            6: QRect(left_x, bottom_y, s, s),
            7: QRect(center_x, bottom_y, s, s),
            8: QRect(right_x, bottom_y, s, s),
        }

        self.current_number = 1
        self._reset_drag_to_center()
        self.dragging = False
        self.drag_offset = QPoint()
        self.completed = False
        self.results = []
        self.trial_start = None

    def _reset_drag_to_center(self):
        ds = self.DRAG_SIZE
        self.drag_rect = QRect(
            (self.WINDOW_W - ds) // 2,
            (self.WINDOW_H - ds) // 2,
            ds, ds
        )

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
                bg, border = QColor(200, 220, 255), QColor(50, 100, 200)
            else:
                bg, border = QColor(200, 200, 210), QColor(100, 100, 130)

            painter.fillRect(rect, bg)
            painter.setPen(QPen(border, 3))
            painter.drawRect(rect)
            painter.setPen(QColor(30, 30, 30))
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(num))

        if self.completed:
            font_big = QFont("Arial", 28, QFont.Weight.Bold)
            painter.setFont(font_big)
            msg_rect = QRect((self.WINDOW_W - 500) // 2, (self.WINDOW_H - 160) // 2, 500, 160)
            painter.fillRect(msg_rect, QColor(220, 255, 220))
            painter.setPen(QPen(QColor(30, 130, 60), 2))
            painter.drawRect(msg_rect)
            painter.setPen(QColor(30, 130, 60))
            painter.drawText(msg_rect, Qt.AlignmentFlag.AlignCenter, "¡Prueba completada!")
        else:
            painter.fillRect(self.drag_rect, QColor(255, 190, 40))
            painter.setPen(QPen(QColor(180, 100, 0), 3))
            painter.drawRect(self.drag_rect)
            painter.setPen(QColor(50, 30, 0))
            font = QFont("Arial", 22, QFont.Weight.Bold)
            painter.setFont(font)
            painter.drawText(self.drag_rect, Qt.AlignmentFlag.AlignCenter, str(self.current_number))

            font_small = QFont("Arial", 11)
            painter.setFont(font_small)
            painter.setPen(QColor(80, 80, 80))
            instr = f"Arrastra el cuadrado {self.current_number} hasta la esquina {self.current_number}"
            painter.drawText(
                QRect(0, self.WINDOW_H - 35, self.WINDOW_W, 30),
                Qt.AlignmentFlag.AlignCenter, instr
            )

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and not self.completed:
            if self.drag_rect.contains(event.pos()):
                self.dragging = True
                self.drag_offset = event.pos() - self.drag_rect.topLeft()
                if self.trial_start is None:
                    self.trial_start = time.time()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.drag_rect.moveTopLeft(event.pos() - self.drag_offset)
            self.update()

    def mouseReleaseEvent(self, event):
        if not self.dragging:
            return
        self.dragging = False

        target = self.corners[self.current_number]
        duration = round(time.time() - (self.trial_start or time.time()), 3)

        if self.drag_rect.intersects(target):
            self.results.append({
                "cuadrado": self.current_number,
                "duracion_seg": duration,
                "exitoso": True,
            })
            self.current_number += 1
            if self.current_number > 8:
                self.completed = True
                self._save_results()
            else:
                self._reset_drag_to_center()
                self.trial_start = time.time()
        else:
            self._reset_drag_to_center()

        self.update()

    def _save_results(self):
        import os
        data = {
            "fecha": datetime.now().isoformat(),
            "prueba": "ArrastreSostenido",
            "resultados": self.results,
        }
        os.makedirs("results", exist_ok=True)
        filename = f"results/arrastre_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ArrastreSostenido()
    window.showMaximized()
    sys.exit(app.exec())