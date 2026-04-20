"""
Widget de animación del tornillo usando QPainter.

IMPORTANTE: Este widget NO usa matplotlib para animación.
Solo usa QPainter para representar el movimiento helicoidal
del tornillo, cumpliendo con la restricción técnica.
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath
import math


class AnimationWidget(QWidget):
    """Widget de animación del tornillo usando QPainter."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._angulo = 0.0
        self._desplazamiento = 0.0
        self._paso = 0.002
        self._radio = 0.05
        
        self._color_tornillo = QColor("#0078D4")
        self._color_rosca = QColor("#FF6B00")
        self._color_fondo = QColor("#FFFFFF")
        self._color_flecha = QColor("#28A745")
        self._color_texto = QColor("#333333")
    
    @property
    def angulo(self) -> float:
        return self._angulo
    
    @angulo.setter
    def angulo(self, value: float):
        self._angulo = value
        self.update()
    
    @property
    def desplazamiento(self) -> float:
        return self._desplazamiento
    
    @desplazamiento.setter
    def desplazamiento(self, value: float):
        self._desplazamiento = value
        self.update()
    
    def set_parameters(self, angulo: float, desplazamiento: float, paso: float = 0.002, radio: float = 0.05):
        self._angulo = angulo
        self._desplazamiento = desplazamiento
        self._paso = paso
        self._radio = radio
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = self.width()
        h = self.height()
        cx = w // 2
        cy = h // 2
        
        painter.fillRect(self.rect(), self._color_fondo)
        
        self._dibujar_tornillo(painter, cx, cy)
        self._dibujar_rosca(painter, cx, cy)
        self._dibujar_flecha_direccion(painter, cx, cy)
        self._dibujar_info(painter, cx, cy)
    
    def _dibujar_tornillo(self, painter, cx, cy):
        pen = QPen(self._color_tornillo)
        pen.setWidth(3)
        painter.setPen(pen)
        
        cuerpo_ancho = 40
        cuerpo_alto = min(200, self.height() - 100)
        
        # Escalamiento visual: Limitamos el desplazamiento para que no se salga del widget
        # Usamos una escala que permite ver el movimiento pero mantiene el objeto centrado
        y_max_visual = cuerpo_alto // 2
        y_offset = int(self._desplazamiento * 50) # Escala 1:50 para mayor estabilidad visual
        
        # Clamp para seguridad visual
        y_offset = max(-y_max_visual, min(y_max_visual, y_offset))
        
        rect = QRectF(
            float(cx - cuerpo_ancho // 2),
            float(cy - cuerpo_alto // 2 + y_offset),
            float(cuerpo_ancho),
            float(cuerpo_alto)
        )
        
        painter.setBrush(QBrush(QColor("#E8E8E8")))
        painter.drawRect(rect)
        
        pen.setWidth(1)
        painter.setPen(pen)
        for i in range(5):
            y_line = cy - cuerpo_alto // 2 + y_offset + i * cuerpo_alto // 5
            painter.drawLine(
                cx - cuerpo_ancho // 2, y_line,
                cx + cuerpo_ancho // 2, y_line
            )
    
    def _dibujar_rosca(self, painter, cx, cy):
        pen = QPen(self._color_rosca)
        pen.setWidth(2)
        painter.setPen(pen)
        
        num_vueltas = 6
        paso_visual = 20
        
        escala = 50
        y_base = cy - 80 + max(-50, min(50, int(self._desplazamiento * escala)))
        
        for vuelta in range(num_vueltas):
            path = QPainterPath()
            
            inicio = y_base + vuelta * paso_visual
            
            if inicio < cy - 100 or inicio > cy + 100:
                continue
            
            for i in range(21):
                theta = (i / 20) * 2 * math.pi + self._angulo + vuelta * 2 * math.pi
                
                x = float(cx + 35 * math.cos(theta))
                y = float(inicio + i * (paso_visual / 20) - 10)
                
                if i == 0:
                    path.moveTo(x, y)
                else:
                    path.lineTo(x, y)
            
            painter.drawPath(path)
        
        painter.drawLine(cx + 35, cy - 70, cx + 35, cy + 70)
    
    def _dibujar_flecha_direccion(self, painter, cx, cy):
        pen = QPen(self._color_flecha)
        pen.setWidth(3)
        painter.setPen(pen)
        
        escala = 50
        y_inicio = cy + 90
        y_fin = cy + 110 + max(-20, min(20, int(self._desplazamiento * escala / 2)))
        
        painter.drawLine(cx, y_inicio, cx, y_fin)
        painter.drawLine(cx - 8, y_fin - 8, cx, y_fin)
        painter.drawLine(cx + 8, y_fin - 8, cx, y_fin)
    
    def _dibujar_info(self, painter, cx, cy):
        pen = QPen(self._color_texto)
        pen.setWidth(1)
        painter.setPen(pen)
        
        painter.setFont(self.font())
        
        angulo_deg = math.degrees(self._angulo) % 360
        
        info = [
            f"Angulo: {angulo_deg:.1f}",
            f"Delta x: {self._desplazamiento:.4f} m",
            f"Paso: {self._paso:.4f} m",
            f"VM: {(2 * math.pi * self._radio) / self._paso:.2f}x"
        ]
        
        y_start = 15
        for i, texto in enumerate(info):
            painter.drawText(10, y_start + i * 18, texto)