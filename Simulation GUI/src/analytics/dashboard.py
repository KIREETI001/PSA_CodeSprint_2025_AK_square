"""
Live Analytics Dashboard
Real-time monitoring dashboard for PSA Terminal Simulation
Enhanced Dark Theme: Deep blue/purple gradient with high contrast
"""
import sys
import csv
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QFrame, QScrollArea, QGridLayout, 
                             QMessageBox, QProgressBar, QSizePolicy)
from PyQt5.QtCore import QTimer, Qt, QPropertyAnimation, QEasingCurve, QPoint, QRectF
from PyQt5.QtGui import QFont, QPalette, QColor, QLinearGradient, QPainter, QPen, QBrush
from PyQt5.QtChart import (QChart, QChartView, QLineSeries, QBarSeries, QBarSet, 
                           QValueAxis, QBarCategoryAxis, QPieSeries, QPieSlice)
import pandas as pd


class VisualProgressBar(QWidget):
    """Custom visual progress bar with gradient and label"""
    
    def __init__(self, label="", max_value=100, color_start="#00D9FF", color_end="#667EEA", parent=None):
        super().__init__(parent)
        self.label = label
        self.value = 0
        self.max_value = max_value
        self.color_start = QColor(color_start)
        self.color_end = QColor(color_end)
        self.setMinimumHeight(50)
    
    def setValue(self, value):
        self.value = min(value, self.max_value)
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        # Draw background
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#1A1D2E"))
        painter.drawRoundedRect(0, 15, width, 25, 12, 12)
        
        # Draw progress
        if self.value > 0:
            progress_width = int((self.value / self.max_value) * width)
            gradient = QLinearGradient(0, 0, progress_width, 0)
            gradient.setColorAt(0, self.color_start)
            gradient.setColorAt(1, self.color_end)
            painter.setBrush(gradient)
            painter.drawRoundedRect(0, 15, progress_width, 25, 12, 12)
        
        # Draw label and value
        painter.setPen(QColor("#FFFFFF"))
        font = QFont("Segoe UI", 12, QFont.Bold)
        painter.setFont(font)
        painter.drawText(0, 0, width, 15, Qt.AlignLeft, self.label)
        
        # Draw percentage
        pct_text = f"{int(self.value)}/{self.max_value}"
        if self.max_value == 100:
            pct_text = f"{int(self.value)}%"
        painter.drawText(0, 15, width, 25, Qt.AlignCenter, pct_text)


class MiniBarChart(QWidget):
    """Compact bar chart widget for dashboard"""
    
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.title = title
        self.data = []  # List of (label, value, color) tuples
        self.setMinimumSize(300, 200)
    
    def setData(self, data):
        """Set data as list of (label, value, color) tuples"""
        self.data = data
        self.update()
    
    def paintEvent(self, event):
        if not self.data:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        # Draw title
        painter.setPen(QColor("#00D9FF"))
        font = QFont("Segoe UI", 14, QFont.Bold)
        painter.setFont(font)
        painter.drawText(0, 0, width, 30, Qt.AlignCenter, self.title)
        
        # Calculate bar dimensions
        bar_area_height = height - 50
        bar_width = width / len(self.data) * 0.7
        spacing = width / len(self.data)
        max_value = max([v for _, v, _ in self.data]) if self.data else 1
        
        # Draw bars
        for i, (label, value, color) in enumerate(self.data):
            x = i * spacing + (spacing - bar_width) / 2
            bar_height = (value / max_value) * bar_area_height
            y = height - bar_height - 20
            
            # Draw bar with gradient
            gradient = QLinearGradient(x, y, x, y + bar_height)
            color_obj = QColor(color)
            gradient.setColorAt(0, color_obj.lighter(120))
            gradient.setColorAt(1, color_obj)
            
            painter.setPen(Qt.NoPen)
            painter.setBrush(gradient)
            painter.drawRoundedRect(int(x), int(y), int(bar_width), int(bar_height), 5, 5)
            
            # Draw value on top
            painter.setPen(QColor("#FFFFFF"))
            font = QFont("Segoe UI", 11, QFont.Bold)
            painter.setFont(font)
            painter.drawText(int(x), int(y) - 15, int(bar_width), 15, Qt.AlignCenter, str(int(value)))
            
            # Draw label
            font = QFont("Segoe UI", 9)
            painter.setFont(font)
            painter.drawText(int(x), height - 15, int(bar_width), 15, Qt.AlignCenter, label)


class CongestionAlert(QWidget):
    """Popup alert widget for congestion warnings"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(400, 150)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Alert frame
        self.alert_frame = QFrame()
        self.alert_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #E74C3C, stop:1 #C0392B);
                border-radius: 15px;
                border: 3px solid #FF6B9D;
                padding: 15px;
            }
        """)
        
        alert_layout = QVBoxLayout()
        self.alert_frame.setLayout(alert_layout)
        
        # Title
        title = QLabel("⚠️ CONGESTION ALERT ⚠️")
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 20px;
                font-weight: bold;
                background: transparent;
            }
        """)
        title.setAlignment(Qt.AlignCenter)
        alert_layout.addWidget(title)
        
        # Message
        self.message_label = QLabel("")
        self.message_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                background: transparent;
                padding: 10px;
            }
        """)
        self.message_label.setWordWrap(True)
        self.message_label.setAlignment(Qt.AlignCenter)
        alert_layout.addWidget(self.message_label)
        
        layout.addWidget(self.alert_frame)
        
        # Auto-hide timer
        self.hide_timer = QTimer()
        self.hide_timer.timeout.connect(self.hide)
        
    def show_alert(self, message, duration=5000):
        """Show alert with message for specified duration (ms)"""
        self.message_label.setText(message)
        
        # Position at top-right of parent or screen
        if self.parent():
            parent_geo = self.parent().geometry()
            x = parent_geo.right() - self.width() - 20
            y = parent_geo.top() + 100
        else:
            screen = QApplication.desktop().screenGeometry()
            x = screen.width() - self.width() - 20
            y = 100
        
        self.move(x, y)
        self.show()
        self.raise_()
        
        # Auto-hide after duration
        self.hide_timer.start(duration)


class HorizontalBarChart(QWidget):
    """Horizontal bar chart for yard statistics"""
    
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.title = title
        self.data = []  # List of (label, value, color) tuples
        self.max_value = 100
        self.setMinimumHeight(400)
        
    def set_data(self, data, max_value=None):
        """Set data as list of (label, value, color) tuples"""
        self.data = data
        if max_value:
            self.max_value = max_value
        else:
            self.max_value = max([v for _, v, _ in data]) if data else 100
        self.update()
    
    def paintEvent(self, event):
        if not self.data:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Title
        painter.setPen(QColor("#00D9FF"))
        font = QFont("Segoe UI", 16, QFont.Bold)
        painter.setFont(font)
        painter.drawText(10, 25, self.title)
        
        # Draw bars
        bar_height = 25
        spacing = 10
        start_y = 50
        label_width = 80
        bar_start_x = label_width + 10
        max_bar_width = self.width() - bar_start_x - 100
        
        font = QFont("Segoe UI", 12)
        painter.setFont(font)
        
        for i, (label, value, color) in enumerate(self.data):
            y = start_y + i * (bar_height + spacing)
            
            # Draw label
            painter.setPen(QColor("#FFFFFF"))
            painter.drawText(5, y + bar_height - 5, label)
            
            # Draw bar background
            painter.setPen(QPen(QColor("#1A1D2E"), 1))
            painter.setBrush(QBrush(QColor("#1A1D2E")))
            painter.drawRect(bar_start_x, y, max_bar_width, bar_height)
            
            # Draw bar value
            bar_width = int((value / self.max_value) * max_bar_width)
            gradient = QLinearGradient(bar_start_x, y, bar_start_x + bar_width, y)
            gradient.setColorAt(0, QColor(color).lighter(130))
            gradient.setColorAt(1, QColor(color))
            
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(gradient))
            painter.drawRect(bar_start_x, y, bar_width, bar_height)
            
            # Draw value text
            painter.setPen(QColor("#FFFFFF"))
            value_text = str(int(value))
            painter.drawText(bar_start_x + bar_width + 10, y + bar_height - 5, value_text)


class StackedBarChart(QWidget):
    """Stacked horizontal bar chart for yard DI/LO counts with constraint line"""
    
    def __init__(self, title="", max_di_constraint=700, parent=None):
        super().__init__(parent)
        self.title = title
        self.data = []  # List of (label, di_count, lo_count) tuples
        self.max_di_constraint = max_di_constraint
        self.setMinimumHeight(650)
        
    def set_data(self, data):
        """Set data as list of (label, di_count, lo_count) tuples"""
        self.data = data
        self.update()
    
    def paintEvent(self, event):
        if not self.data:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Title
        painter.setPen(QColor("#00D9FF"))
        font = QFont("Segoe UI", 16, QFont.Bold)
        painter.setFont(font)
        painter.drawText(10, 25, self.title)
        
        # Draw legend
        legend_y = 30
        font = QFont("Segoe UI", 12)
        painter.setFont(font)
        
        # DI legend
        painter.setBrush(QBrush(QColor("#E74C3C")))
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.width() - 300, legend_y, 20, 15)
        painter.setPen(QColor("#FFFFFF"))
        painter.drawText(self.width() - 275, legend_y + 12, "DI Jobs (Red)")
        
        # LO legend
        painter.setBrush(QBrush(QColor("#F39C12")))
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.width() - 140, legend_y, 20, 15)
        painter.setPen(QColor("#FFFFFF"))
        painter.drawText(self.width() - 115, legend_y + 12, "LO Jobs (Yellow)")
        
        # Draw bars
        bar_height = 30
        spacing = 7
        start_y = 60
        label_width = 50
        bar_start_x = label_width + 10
        max_bar_width = self.width() - bar_start_x - 150
        
        # Find max total for scaling
        max_total = max([di + lo for _, di, lo in self.data]) if self.data else 1000
        max_scale = max(max_total, self.max_di_constraint * 1.5)  # Scale to show constraint
        
        font = QFont("Segoe UI", 11)
        painter.setFont(font)
        
        # Draw constraint line
        constraint_x = bar_start_x + int((self.max_di_constraint / max_scale) * max_bar_width)
        painter.setPen(QPen(QColor("#FF6B9D"), 2, Qt.DashLine))
        painter.drawLine(constraint_x, start_y - 10, constraint_x, start_y + len(self.data) * (bar_height + spacing) + 10)
        
        # Draw constraint label
        painter.setPen(QColor("#FF6B9D"))
        font_bold = QFont("Segoe UI", 10, QFont.Bold)
        painter.setFont(font_bold)
        painter.drawText(constraint_x - 80, start_y - 15, f"Max DI: {self.max_di_constraint}")
        
        font = QFont("Segoe UI", 11)
        painter.setFont(font)
        
        for i, (label, di_count, lo_count) in enumerate(self.data):
            y = start_y + i * (bar_height + spacing)
            
            # Draw yard label
            painter.setPen(QColor("#FFFFFF"))
            painter.drawText(5, y + bar_height - 8, label)
            
            # Draw bar background
            painter.setPen(QPen(QColor("#1A1D2E"), 1))
            painter.setBrush(QBrush(QColor("#1A1D2E")))
            painter.drawRect(bar_start_x, y, max_bar_width, bar_height)
            
            # Draw DI portion (red)
            if di_count > 0:
                di_width = int((di_count / max_scale) * max_bar_width)
                gradient = QLinearGradient(bar_start_x, y, bar_start_x + di_width, y)
                gradient.setColorAt(0, QColor("#E74C3C").lighter(120))
                gradient.setColorAt(1, QColor("#E74C3C"))
                
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(gradient))
                painter.drawRect(bar_start_x, y, di_width, bar_height)
                
                # Check if over constraint
                if di_count > self.max_di_constraint:
                    # Draw warning indicator
                    painter.setPen(QPen(QColor("#FF0000"), 2))
                    painter.drawRect(bar_start_x, y, di_width, bar_height)
            
            # Draw LO portion (yellow) - stacked after DI
            if lo_count > 0:
                di_width = int((di_count / max_scale) * max_bar_width)
                lo_width = int((lo_count / max_scale) * max_bar_width)
                gradient = QLinearGradient(bar_start_x + di_width, y, bar_start_x + di_width + lo_width, y)
                gradient.setColorAt(0, QColor("#F39C12").lighter(120))
                gradient.setColorAt(1, QColor("#F39C12"))
                
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(gradient))
                painter.drawRect(bar_start_x + di_width, y, lo_width, bar_height)
            
            # Draw total and DI/LO counts
            painter.setPen(QColor("#FFFFFF"))
            font_small = QFont("Segoe UI", 10)
            painter.setFont(font_small)
            
            total = di_count + lo_count
            di_width = int((di_count / max_scale) * max_bar_width)
            lo_width = int((lo_count / max_scale) * max_bar_width)
            
            # Total on the right
            painter.drawText(bar_start_x + di_width + lo_width + 10, y + bar_height - 8, str(int(total)))
            
            # DI count in red section if wide enough
            if di_width > 40:
                painter.setPen(QColor("#FFFFFF"))
                painter.drawText(bar_start_x + 5, y + bar_height - 8, str(int(di_count)))
            
            # LO count in yellow section if wide enough  
            if lo_width > 40:
                painter.setPen(QColor("#FFFFFF"))
                painter.drawText(bar_start_x + di_width + 5, y + bar_height - 8, str(int(lo_count)))


class PieChartWidget(QWidget):
    """Custom pie chart widget"""
    
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.title = title
        self.segments = []  # List of (label, value, color) tuples
        self.setMinimumSize(300, 350)
        
    def set_data(self, segments):
        """Set data as list of (label, value, color) tuples"""
        self.segments = segments
        self.update()
    
    def paintEvent(self, event):
        if not self.segments:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Title
        painter.setPen(QColor("#00D9FF"))
        font = QFont("Segoe UI", 16, QFont.Bold)
        painter.setFont(font)
        painter.drawText(0, 25, self.width(), 30, Qt.AlignCenter, self.title)
        
        # Calculate total
        total = sum([v for _, v, _ in self.segments])
        if total == 0:
            return
        
        # Draw pie chart
        center_x, center_y = self.width() // 2, 180
        radius = 80
        
        start_angle = 0
        for label, value, color in self.segments:
            span_angle = int((value / total) * 360 * 16)
            
            gradient = QLinearGradient(center_x - radius, center_y, center_x + radius, center_y)
            gradient.setColorAt(0, QColor(color).lighter(120))
            gradient.setColorAt(1, QColor(color))
            
            painter.setPen(QPen(QColor("#0A0E27"), 2))
            painter.setBrush(QBrush(gradient))
            painter.drawPie(center_x - radius, center_y - radius, radius * 2, radius * 2, 
                           start_angle, span_angle)
            
            start_angle += span_angle
        
        # Draw legend
        legend_y = 280
        font = QFont("Segoe UI", 12)
        painter.setFont(font)
        
        for i, (label, value, color) in enumerate(self.segments):
            y = legend_y + i * 30
            
            # Color box
            painter.setBrush(QBrush(QColor(color)))
            painter.setPen(Qt.NoPen)
            painter.drawRect(20, y, 20, 20)
            
            # Label and percentage
            percentage = (value / total) * 100
            painter.setPen(QColor("#FFFFFF"))
            text = f"{label}: {int(value)} ({percentage:.1f}%)"
            painter.drawText(50, y + 16, text)


class ProgressBar(QWidget):
    """Custom horizontal progress bar"""
    
    def __init__(self, label="", max_value=100, color="#2ECC71", parent=None):
        super().__init__(parent)
        self.label = label
        self.value = 0
        self.max_value = max_value
        self.color = QColor(color)
        self.counter_text = ""  # Custom counter text to display
        self.setMinimumHeight(60)
        
    def set_value(self, value, counter_text=""):
        """Set value and optional counter text"""
        self.value = min(value, self.max_value)
        self.counter_text = counter_text
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Label
        painter.setPen(QColor("#FFFFFF"))
        font = QFont("Segoe UI", 14, QFont.Bold)
        painter.setFont(font)
        painter.drawText(10, 25, self.label)
        
        # Background bar
        bar_y = 35
        bar_height = 20
        painter.setPen(QPen(QColor("#1A1D2E"), 1))
        painter.setBrush(QBrush(QColor("#1A1D2E")))
        painter.drawRoundedRect(10, bar_y, self.width() - 20, bar_height, 10, 10)
        
        # Progress bar
        if self.value > 0:
            progress_width = int(((self.value / self.max_value) * (self.width() - 20)))
            gradient = QLinearGradient(10, bar_y, 10 + progress_width, bar_y)
            gradient.setColorAt(0, self.color.lighter(130))
            gradient.setColorAt(1, self.color)
            
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(gradient))
            painter.drawRoundedRect(10, bar_y, progress_width, bar_height, 10, 10)
            
            # Counter text in the middle of the filled bar
            if self.counter_text:
                painter.setPen(QColor("#FFFFFF"))
                font = QFont("Segoe UI", 11, QFont.Bold)
                painter.setFont(font)
                # Position text in the center of the filled portion
                text_x = 10 + (progress_width // 2) - 20  # Approximate center
                painter.drawText(text_x, bar_y + 15, self.counter_text)


class CircularProgressWidget(QWidget):
    """Circular progress indicator with enhanced styling"""
    
    def __init__(self, value=0, max_value=100, title="", color_start="#00D9FF", color_end="#667EEA"):
        super().__init__()
        self.value = value
        self.max_value = max_value
        self.title = title
        self.color_start = QColor(color_start)
        self.color_end = QColor(color_end)
        self.setMinimumSize(150, 200)  # Minimum size for responsive layout
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Allow horizontal expansion
    
    def setValue(self, value):
        self.value = min(value, self.max_value)
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw background circle (darker)
        center_x, center_y = 90, 90
        radius = 70
        painter.setPen(QPen(QColor("#1A1D2E"), 10))
        painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)
        
        # Draw progress arc with gradient
        gradient = QLinearGradient(center_x - radius, center_y, center_x + radius, center_y)
        gradient.setColorAt(0, self.color_start)
        gradient.setColorAt(1, self.color_end)
        
        pen = QPen(gradient, 12)  # Thicker for better visibility
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        
        span_angle = int((self.value / self.max_value) * 360 * 16)
        painter.drawArc(center_x - radius, center_y - radius, radius * 2, radius * 2, 
                       90 * 16, -span_angle)
        
        # Draw value text (larger, bolder, white)
        painter.setPen(QColor("#FFFFFF"))
        font = QFont("Segoe UI", 36, QFont.Bold)
        painter.setFont(font)
        value_text = f"{int(self.value)}"
        if self.max_value > 1000:
            value_text = f"{int(self.value/1000)}k" if self.value >= 1000 else str(int(self.value))
        painter.drawText(20, 60, 140, 60, Qt.AlignCenter, value_text)
        
        # Draw title (larger, cyan color)
        font = QFont("Segoe UI", 12, QFont.Normal)
        painter.setFont(font)
        painter.setPen(QColor("#00D9FF"))
        painter.drawText(0, 170, 180, 50, Qt.AlignCenter | Qt.TextWordWrap, self.title)


class DashboardCard(QFrame):
    """Enhanced card widget with dark theme"""
    
    def __init__(self, title, icon="", title_color="#00D9FF"):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0F3460, stop:1 #16213E);
                border-radius: 15px;
                border: 2px solid #1A1D2E;
                padding: 10px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Title with icon
        title_label = QLabel(f"{icon} {title}")
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {title_color};
                font-size: 14px;
                font-weight: bold;
                padding: 8px;
                background: transparent;
            }}
        """)
        layout.addWidget(title_label)
        
        # Content area
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(10)
        layout.addLayout(self.content_layout)
        
        self.setLayout(layout)
    
    def addContent(self, widget):
        self.content_layout.addWidget(widget)


class PSADashboard(QMainWindow):
    """Main dashboard window with enhanced dark theme"""
    
    def __init__(self, data_folder: Path):
        super().__init__()
        self.data_folder = data_folder
        self.setWindowTitle("🚢 PSA TERMINAL LIVE ANALYTICS")
        self.setGeometry(50, 50, 1800, 1100)
        self.setMinimumSize(1200, 800)  # Set minimum window size for responsive layout
        
        # Enhanced dark theme - Elegant deep navy gradient
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0A1929, stop:0.4 #132F4C, stop:0.7 #1A3A52, stop:1 #0A1929);
            }
            QLabel {
                color: #FFFFFF;
                font-size: 14px;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)
        
        # Setup UI
        self.setup_ui()
        
        # Create congestion alert popup
        self.congestion_alert = CongestionAlert(self)
        self.last_alert_count = 0  # Track alerts to avoid duplicates
        
        # Setup update timer (refresh every 2 seconds)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_dashboard)
        self.timer.start(2000)
    
    def setup_ui(self):
        """Setup dashboard UI with enhanced styling"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        central_widget.setLayout(main_layout)
        
        # Header with gradient background
        header = QLabel("🚢 PSA TERMINAL LIVE ANALYTICS")
        header.setStyleSheet("""
            QLabel {
                font-size: 36px;
                font-weight: bold;
                color: #00D9FF;
                padding: 25px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0, 217, 255, 0.1), 
                    stop:0.5 rgba(102, 126, 234, 0.1), 
                    stop:1 rgba(0, 217, 255, 0.1));
                border-radius: 15px;
                border: 2px solid #00D9FF;
            }
        """)
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)
        
        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_layout.setSpacing(30)
        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
        
        # Row 1 - HT Timelines (full width)
        self.timeline_card = DashboardCard("🚛 HT TIMELINES", "", "#00D9FF")
        self.timeline_card.setMinimumWidth(300)
        self.timeline_label = QLabel("Loading...")
        self.timeline_label.setStyleSheet("""
            color: #FFFFFF; 
            padding: 10px; 
            font-size: 14px;
            line-height: 1.6;
        """)
        self.timeline_label.setWordWrap(True)
        self.timeline_card.addContent(self.timeline_label)
        scroll_layout.addWidget(self.timeline_card)
        
        # Row 2 - Yard Jobs Card (Full width with stacked bar chart - original layout)
        self.yard_card = DashboardCard("📦 YARD JOB COUNTERS - LIVE STATUS (DI/LO Split)", "", "#2ECC71")
        
        # Create container for summary stats + stacked bar chart
        yard_container = QWidget()
        yard_layout = QHBoxLayout(yard_container)
        yard_layout.setContentsMargins(10, 10, 10, 10)
        
        # Left side: Summary stats only (no pie chart)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_widget.setMinimumWidth(250)
        left_widget.setMaximumWidth(350)  # Set range instead of fixed width
        
        self.yard_label = QLabel("Loading...")
        self.yard_label.setStyleSheet("""
            color: #FFFFFF; 
            padding: 15px; 
            font-size: 16px;
            line-height: 1.8;
        """)
        self.yard_label.setWordWrap(True)
        left_layout.addWidget(self.yard_label)
        left_layout.addStretch()
        
        yard_layout.addWidget(left_widget, stretch=1)  # Add stretch factor for responsiveness
        
        # Right side: Stacked bar chart showing all 16 yards with DI (red) and LO (yellow) split
        self.yard_stacked_chart = StackedBarChart("All Yards - DI/LO Job Distribution", max_di_constraint=700)
        yard_layout.addWidget(self.yard_stacked_chart, stretch=4)  # Larger stretch for chart
        
        self.yard_card.addContent(yard_container)
        scroll_layout.addWidget(self.yard_card)
        
        # Row 3 - Emissions and Route Optimization cards (side by side)
        row3_layout = QHBoxLayout()
        row3_layout.setSpacing(2)
        row3_layout.setContentsMargins(0, 0, 0, 0)
        
        # Emissions Card - Purple (Responsive)
        self.emissions_card = DashboardCard("💨 EMISSIONS TRACKER", "", "#9B59B6")
        self.emissions_card.setMinimumWidth(300)
        
        # Container for emissions stats
        emissions_container = QWidget()
        emissions_layout = QVBoxLayout(emissions_container)
        
        self.emissions_label = QLabel("Loading...")
        self.emissions_label.setStyleSheet("""
            color: #FFFFFF; 
            padding: 10px; 
            font-size: 14px;
            line-height: 1.6;
        """)
        self.emissions_label.setWordWrap(True)
        emissions_layout.addWidget(self.emissions_label)
        
        # Add two horizontal progress bars - one for DI, one for LO (both deplete to zero)
        self.di_progress = ProgressBar("DI Jobs Remaining", 100, "#F39C12")
        self.di_progress.setMinimumHeight(50)
        emissions_layout.addWidget(self.di_progress)
        
        self.lo_progress = ProgressBar("LO Jobs Remaining", 100, "#2ECC71")
        self.lo_progress.setMinimumHeight(50)
        emissions_layout.addWidget(self.lo_progress)
        
        emissions_layout.addStretch()
        
        self.emissions_card.addContent(emissions_container)
        row3_layout.addWidget(self.emissions_card, stretch=1)  # Add to row3
        
        # Route Optimization Card - Blue (Compact)
        self.route_card = DashboardCard("�️ ROUTE OPTIMIZATION", "", "#3498DB")
        self.route_card.setMinimumWidth(300)  # Set minimum instead of maximum
        
        # Container for route stats + progress bars
        route_container = QWidget()
        route_layout = QVBoxLayout(route_container)
        
        self.route_label = QLabel("Loading...")
        self.route_label.setStyleSheet("""
            color: #FFFFFF; 
            padding: 10px; 
            font-size: 14px;
            line-height: 1.6;
        """)
        self.route_label.setWordWrap(True)
        route_layout.addWidget(self.route_label)
        
        # Add progress bars for efficiency metrics (responsive)
        self.efficiency_bar = ProgressBar("Avg Efficiency", 100, "#2ECC71")
        self.efficiency_bar.setMinimumHeight(40)
        self.optimal_bar = ProgressBar("Optimal Routes", 100, "#00D9FF")
        self.optimal_bar.setMinimumHeight(40)
        route_layout.addWidget(self.efficiency_bar)
        route_layout.addWidget(self.optimal_bar)
        route_layout.addStretch()  # Add stretch to fill vertical space
        
        self.route_card.addContent(route_container)
        row3_layout.addWidget(self.route_card, stretch=1)  # Add to row3
        
        scroll_layout.addLayout(row3_layout)  # Add row3 to main layout

    def update_dashboard(self):
        """Update dashboard with latest data"""
        try:
            self.update_timeline_data()
            self.update_emissions_data()
            self.update_yard_data()
            self.update_congestion_data()
            self.update_route_data()
        except Exception as e:
            print(f"Dashboard update error: {e}")
    
    def update_timeline_data(self):
        """Update HT timeline information with enhanced styling"""
        timeline_file = self.data_folder / "ht_timelines.csv"
        if not timeline_file.exists():
            self.timeline_label.setText("<span style='color: #F39C12; font-size: 16px;'>No data available yet...</span>")
            return
        
        try:
            df = pd.read_csv(timeline_file)
            active_jobs = len(df[df['status'] == 'pending'].groupby('job_seq'))
            completed_jobs = len(df[df['status'] == 'completed'].groupby('job_seq'))
            total_jobs = len(df.groupby('job_seq'))
            
            text = f"""
            <div style='line-height: 1.6; padding: 5px;'>
                <p style='margin: 5px 0;'><span style='color: #00D9FF; font-size: 13px; font-weight: bold;'>● Active:</span> 
                   <span style='color: #FFFFFF; font-size: 15px; font-weight: bold;'>{active_jobs}</span></p>
                <p style='margin: 5px 0;'><span style='color: #2ECC71; font-size: 13px; font-weight: bold;'>● Completed:</span> 
                   <span style='color: #FFFFFF; font-size: 15px; font-weight: bold;'>{completed_jobs}</span></p>
                <p style='margin: 5px 0;'><span style='color: #F39C12; font-size: 13px; font-weight: bold;'>● Tracked:</span> 
                   <span style='color: #FFFFFF; font-size: 15px; font-weight: bold;'>{total_jobs}</span></p>
            </div>
            """
            self.timeline_label.setText(text)
            
            # Update progress indicator (removed - circular progress widgets removed from UI)
            # self.progress_total.setValue(completed_jobs)
            
        except Exception as e:
            self.timeline_label.setText(f"<span style='color: #E74C3C;'>Error: {e}</span>")
    
    def update_emissions_data(self):
        """Update emissions information with separate DI/LO depleting progress bars"""
        emissions_file = self.data_folder / "emissions.csv"
        timeline_file = self.data_folder / "ht_timelines.csv"
        
        if not emissions_file.exists():
            self.emissions_label.setText("<span style='color: #F39C12; font-size: 16px;'>No data available yet...</span>")
            self.di_progress.set_value(100)  # Full bar when no data
            self.lo_progress.set_value(100)  # Full bar when no data
            return
        
        try:
            df = pd.read_csv(emissions_file)
            if not df.empty:
                total_emissions = df['cumulative_emissions'].max()
                
                # Get DI and LO emissions
                di_emissions = df[df['job_type'] == 'DI']['emissions_kg'].sum()
                lo_emissions = df[df['job_type'] == 'LO']['emissions_kg'].sum()
                
                di_pct = (di_emissions/max(total_emissions,1)*100)
                lo_pct = (lo_emissions/max(total_emissions,1)*100)
                
                # Calculate DI and LO job completion percentages separately
                di_remaining_pct = 100  # Default to full
                lo_remaining_pct = 100  # Default to full
                di_remaining_count = 0
                lo_remaining_count = 0
                
                if timeline_file.exists():
                    timeline_df = pd.read_csv(timeline_file)
                    if not timeline_df.empty:
                        # DI jobs progress
                        di_completed = len(timeline_df[(timeline_df['status'] == 'completed') & (timeline_df['job_type'] == 'DI')].groupby('job_seq'))
                        di_total = len(timeline_df[timeline_df['job_type'] == 'DI'].groupby('job_seq'))
                        if di_total > 0:
                            di_remaining_count = di_total - di_completed
                            di_remaining_pct = (di_remaining_count / di_total) * 100
                        
                        # LO jobs progress
                        lo_completed = len(timeline_df[(timeline_df['status'] == 'completed') & (timeline_df['job_type'] == 'LO')].groupby('job_seq'))
                        lo_total = len(timeline_df[timeline_df['job_type'] == 'LO'].groupby('job_seq'))
                        if lo_total > 0:
                            lo_remaining_count = lo_total - lo_completed
                            lo_remaining_pct = (lo_remaining_count / lo_total) * 100
                
                text = f"""
                <div style='line-height: 1.5; padding: 5px;'>
                    <p style='margin: 5px 0;'><span style='color: #E74C3C; font-size: 14px; font-weight: bold;'>Total Emissions:</span> 
                       <span style='color: #FFFFFF; font-size: 16px; font-weight: bold;'>{total_emissions:.1f} kg</span></p>
                    <p style='margin: 2px 0 8px 10px;'><span style='color: #9B59B6; font-size: 11px;'>≈ {total_emissions/1000:.2f} tons</span></p>
                    
                    <p style='margin: 5px 0;'><span style='color: #F39C12; font-size: 12px; font-weight: bold;'>● DI:</span> 
                       <span style='color: #FFFFFF; font-size: 14px;'>{di_emissions:.1f} kg</span> 
                       <span style='color: #F39C12; font-size: 11px;'>({di_pct:.1f}%)</span></p>
                    <p style='margin: 5px 0;'><span style='color: #2ECC71; font-size: 12px; font-weight: bold;'>● LO:</span> 
                       <span style='color: #FFFFFF; font-size: 14px;'>{lo_emissions:.1f} kg</span> 
                       <span style='color: #2ECC71; font-size: 11px;'>({lo_pct:.1f}%)</span></p>
                </div>
                """
                self.emissions_label.setText(text)
                
                # Update separate depleting progress bars for DI and LO with job counts
                self.di_progress.set_value(di_remaining_pct, f"{di_remaining_count} jobs")
                self.lo_progress.set_value(lo_remaining_pct, f"{lo_remaining_count} jobs")
                
                # Update progress (removed - circular progress widgets removed from UI)
                # self.progress_emissions.setValue(min((total_emissions / 1000) * 10, 100))
        except Exception as e:
            self.emissions_label.setText(f"<span style='color: #E74C3C;'>Error: {e}</span>")
    
    def update_yard_data(self):
        """Update yard job counter information with stacked bar chart"""
        yard_file = self.data_folder / "yard_job_counts.csv"
        if not yard_file.exists():
            self.yard_label.setText("<span style='color: #F39C12; font-size: 18px;'>⏳ Waiting for job completions...</span>")
            return
        
        try:
            df = pd.read_csv(yard_file)
            if df.empty:
                self.yard_label.setText("<span style='color: #F39C12; font-size: 18px;'>⏳ No completed jobs yet...</span>")
                return
                
            # Get totals by yard
            yard_totals = df.groupby('yard_name').agg({
                'yard_total': 'max',
                'yard_di_count': 'max',
                'yard_lo_count': 'max'
            }).sort_values('yard_total', ascending=False)
            
            total_di = int(yard_totals['yard_di_count'].sum())
            total_lo = int(yard_totals['yard_lo_count'].sum())
            total_jobs = total_di + total_lo
            
            if total_jobs == 0:
                self.yard_label.setText("<span style='color: #F39C12; font-size: 18px;'>⏳ No completed jobs yet...</span>")
                return
            
            di_pct = (total_di/max(total_jobs,1)*100)
            lo_pct = (total_lo/max(total_jobs,1)*100)
            
            # Count yards violating DI constraint
            over_limit = len(yard_totals[yard_totals['yard_di_count'] > 700])
            
            # Update summary text
            text = f"""
            <div style='line-height: 1.5; padding: 5px;'>
                <p style='margin: 5px 0;'><span style='color: #2ECC71; font-size: 14px; font-weight: bold;'>Total:</span> 
                   <span style='color: #FFFFFF; font-size: 18px; font-weight: bold;'>{total_jobs}</span></p>
                
                <p style='margin: 8px 0 5px 0;'><span style='color: #E74C3C; font-size: 12px; font-weight: bold;'>● DI:</span> 
                   <span style='color: #FFFFFF; font-size: 14px;'>{total_di}</span> 
                   <span style='color: #E74C3C; font-size: 10px;'>({di_pct:.1f}%)</span></p>
                
                <p style='margin: 5px 0;'><span style='color: #F39C12; font-size: 12px; font-weight: bold;'>● LO:</span> 
                   <span style='color: #FFFFFF; font-size: 14px;'>{total_lo}</span> 
                   <span style='color: #F39C12; font-size: 10px;'>({lo_pct:.1f}%)</span></p>
                
                <p style='margin: 10px 0 5px 0;'><span style='color: #00D9FF; font-size: 11px;'>Yards:</span> 
                   <span style='color: #FFFFFF; font-size: 13px;'>{len(yard_totals)}</span></p>
            """
            
            if over_limit > 0:
                text += f"""
                <p style='margin: 8px 0;'><span style='color: #FF6B9D; font-size: 11px; font-weight: bold;'>⚠ Over limit:</span> 
                   <span style='color: #FFFFFF; font-size: 12px;'>{over_limit} yards</span></p>
                """
            
            text += "</div>"
            self.yard_label.setText(text)
            
            # Prepare stacked bar data for all yards (ensure all 16 yards are shown)
            all_yards = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'D1', 'D2', 
                        'E1', 'E2', 'F1', 'F2', 'G1', 'G2', 'H1', 'H2']
            
            stacked_data = []
            for yard in all_yards:
                if yard in yard_totals.index:
                    row = yard_totals.loc[yard]
                    di_count = int(row['yard_di_count'])
                    lo_count = int(row['yard_lo_count'])
                else:
                    # Yard not in data yet - show as 0
                    di_count = 0
                    lo_count = 0
                
                stacked_data.append((yard, di_count, lo_count))
            
            # Update stacked bar chart
            self.yard_stacked_chart.set_data(stacked_data)
            
            # Update progress indicators (removed - circular progress widgets removed from UI)
            # self.progress_di.setValue(int(di_pct))
            # self.progress_lo.setValue(int(lo_pct))
                
        except Exception as e:
            self.yard_label.setText(f"<span style='color: #E74C3C;'>Error: {e}</span>")
    
    def update_congestion_data(self):
        """Check for congestion and show popup alerts"""
        alert_file = self.data_folder / "congestion_alerts.csv"
        if not alert_file.exists():
            # self.progress_congestion.setValue(0)  # Removed - circular progress widgets removed from UI
            return
        
        try:
            df = pd.read_csv(alert_file)
            if df.empty:
                # self.progress_congestion.setValue(0)  # Removed - circular progress widgets removed from UI
                self.last_alert_count = 0
            else:
                # Count by severity
                critical = len(df[df['severity'] == 'CRITICAL'])
                high = len(df[df['severity'] == 'HIGH'])
                total_alerts = len(df)
                
                # Update congestion progress indicator (removed - circular progress widgets removed from UI)
                # congestion_level = min((critical * 10 + high * 5), 100)
                # self.progress_congestion.setValue(congestion_level)
                
                # Show popup if new alerts detected
                if total_alerts > self.last_alert_count:
                    # Get the latest alert
                    latest = df.iloc[-1]
                    severity = latest['severity']
                    message = latest['message']
                    
                    # Show popup for CRITICAL and HIGH only
                    if severity in ['CRITICAL', 'HIGH']:
                        alert_msg = f"🚨 {severity} ALERT!\n{message}"
                        self.congestion_alert.show_alert(alert_msg, duration=8000)
                    
                    self.last_alert_count = total_alerts
                
        except Exception as e:
            pass  # self.progress_congestion.setValue(0)  # Removed - circular progress widgets removed from UI
    
    def update_route_data(self):
        """Update route optimization information with progress bars"""
        route_file = self.data_folder / "route_optimization.csv"
        if not route_file.exists():
            self.route_label.setText("<span style='color: #F39C12; font-size: 16px;'>No data available yet...</span>")
            return
        
        try:
            df = pd.read_csv(route_file)
            if not df.empty:
                avg_efficiency = df['efficiency_%'].mean()
                total_routes = len(df)
                optimal_routes = len(df[df['efficiency_%'] >= 95])
                inefficient = len(df[df['efficiency_%'] < 80])
                total_detours = int(df['detours'].sum())
                total_backtrack = int(df['backtracking'].sum())
                
                optimal_pct = (optimal_routes / max(total_routes, 1)) * 100
                
                text = f"""
                <div style='line-height: 1.4; padding: 5px;'>
                    <p style='margin: 5px 0;'><span style='color: #3498DB; font-size: 14px; font-weight: bold;'>Avg Efficiency:</span> 
                       <span style='color: #FFFFFF; font-size: 18px; font-weight: bold;'>{avg_efficiency:.1f}%</span></p>
                    
                    <p style='margin: 5px 0;'><span style='color: #00D9FF; font-size: 12px; font-weight: bold;'>Routes:</span> 
                       <span style='color: #FFFFFF; font-size: 14px;'>{total_routes}</span></p>
                    <p style='margin: 5px 0;'><span style='color: #2ECC71; font-size: 11px; font-weight: bold;'>● Optimal:</span> 
                       <span style='color: #FFFFFF; font-size: 13px;'>{optimal_routes}</span> 
                       <span style='color: #2ECC71; font-size: 10px;'>({optimal_pct:.1f}%)</span></p>
                    <p style='margin: 5px 0;'><span style='color: #E74C3C; font-size: 11px; font-weight: bold;'>● Inefficient:</span> 
                       <span style='color: #FFFFFF; font-size: 13px;'>{inefficient}</span></p>
                    
                    <p style='margin: 8px 0 5px 0;'><span style='color: #F39C12; font-size: 11px;'>Detours:</span> 
                       <span style='color: #FFFFFF; font-size: 12px;'>{total_detours}</span></p>
                    <p style='margin: 5px 0;'><span style='color: #E74C3C; font-size: 11px;'>Backtrack:</span> 
                       <span style='color: #FFFFFF; font-size: 12px;'>{total_backtrack}</span></p>
                </div>
                """
                
                self.route_label.setText(text)
                
                # Update progress bars (removed - circular progress widgets removed from UI)
                # self.progress_efficiency.setValue(int(avg_efficiency))
                self.efficiency_bar.set_value(avg_efficiency)
                self.optimal_bar.set_value(optimal_pct)
                
        except Exception as e:
            self.route_label.setText(f"Error: {e}")


def launch_dashboard(data_folder: Path):
    """Launch the dashboard application"""
    app = QApplication(sys.argv)
    dashboard = PSADashboard(data_folder)
    dashboard.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    data_folder = Path("data/analytics_logs")
    launch_dashboard(data_folder)
