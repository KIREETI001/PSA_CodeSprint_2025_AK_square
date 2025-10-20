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
                             QMessageBox, QProgressBar)
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
        self.setMinimumHeight(60)
        
    def set_value(self, value):
        self.value = min(value, self.max_value)
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
        
        # Value text
        painter.setPen(QColor("#FFFFFF"))
        font = QFont("Segoe UI", 12, QFont.Bold)
        painter.setFont(font)
        text = f"{int(self.value)} / {int(self.max_value)}"
        painter.drawText(self.width() - 100, bar_y + 16, text)


class CircularProgressWidget(QWidget):
    """Circular progress indicator with enhanced styling"""
    
    def __init__(self, value=0, max_value=100, title="", color_start="#00D9FF", color_end="#667EEA"):
        super().__init__()
        self.value = value
        self.max_value = max_value
        self.title = title
        self.color_start = QColor(color_start)
        self.color_end = QColor(color_end)
        self.setMinimumSize(180, 220)  # Larger for better visibility
    
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
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Title with icon
        title_label = QLabel(f"{icon} {title}")
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {title_color};
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
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
        
        # Enhanced dark theme with better gradients
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0A0E27, stop:0.3 #16213E, stop:0.7 #0F3460, stop:1 #0A0E27);
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
        
        # Top row - Circular progress indicators with vibrant colors
        progress_layout = QHBoxLayout()
        progress_layout.setSpacing(25)
        
        self.progress_total = CircularProgressWidget(0, 20000, "TOTAL JOBS\nCOMPLETED", "#00D9FF", "#667EEA")
        self.progress_di = CircularProgressWidget(0, 100, "DI JOBS\nPERCENTAGE", "#F39C12", "#E67E22")
        self.progress_lo = CircularProgressWidget(0, 100, "LO JOBS\nPERCENTAGE", "#2ECC71", "#27AE60")
        self.progress_efficiency = CircularProgressWidget(0, 100, "ROUTE\nEFFICIENCY", "#3498DB", "#00D9FF")
        self.progress_emissions = CircularProgressWidget(0, 100, "EMISSIONS\nSTATUS", "#9B59B6", "#667EEA")
        self.progress_congestion = CircularProgressWidget(0, 100, "CONGESTION\nLEVEL", "#E74C3C", "#FF6B9D")
        
        progress_layout.addWidget(self.progress_total)
        progress_layout.addWidget(self.progress_di)
        progress_layout.addWidget(self.progress_lo)
        progress_layout.addWidget(self.progress_efficiency)
        progress_layout.addWidget(self.progress_emissions)
        progress_layout.addWidget(self.progress_congestion)
        scroll_layout.addLayout(progress_layout)
        
        # Middle section - Cards grid with proper theming
        cards_grid = QGridLayout()
        cards_grid.setSpacing(20)
        
        # HT Timeline Card - Dark Blue
        self.timeline_card = DashboardCard("🚛 HT TIMELINES", "", "#00D9FF")
        self.timeline_label = QLabel("Loading...")
        self.timeline_label.setStyleSheet("""
            color: #FFFFFF; 
            padding: 15px; 
            font-size: 16px;
            line-height: 1.6;
        """)
        self.timeline_label.setWordWrap(True)
        self.timeline_card.addContent(self.timeline_label)
        cards_grid.addWidget(self.timeline_card, 0, 0)
        
        # Emissions Card - Purple
        self.emissions_card = DashboardCard("💨 EMISSIONS TRACKER", "", "#9B59B6")
        
        # Container for emissions stats + chart
        emissions_container = QWidget()
        emissions_layout = QVBoxLayout(emissions_container)
        
        self.emissions_label = QLabel("Loading...")
        self.emissions_label.setStyleSheet("""
            color: #FFFFFF; 
            padding: 15px; 
            font-size: 16px;
            line-height: 1.6;
        """)
        self.emissions_label.setWordWrap(True)
        emissions_layout.addWidget(self.emissions_label)
        
        # Add bar chart for emissions comparison
        self.emissions_bar_chart = HorizontalBarChart("Emissions by Job Type")
        emissions_layout.addWidget(self.emissions_bar_chart)
        
        self.emissions_card.addContent(emissions_container)
        cards_grid.addWidget(self.emissions_card, 0, 1)
        
        # Yard Jobs Card - Green (EXPANDED to take both columns in row 1)
        self.yard_card = DashboardCard("📦 YARD JOB COUNTERS - LIVE STATUS", "", "#2ECC71")
        
        # Create container with horizontal layout for stats + charts
        yard_container = QWidget()
        yard_layout = QHBoxLayout(yard_container)
        yard_layout.setContentsMargins(10, 10, 10, 10)
        
        # Left side: Summary stats and pie chart
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        self.yard_label = QLabel("Loading...")
        self.yard_label.setStyleSheet("""
            color: #FFFFFF; 
            padding: 15px; 
            font-size: 16px;
            line-height: 1.6;
        """)
        self.yard_label.setWordWrap(True)
        left_layout.addWidget(self.yard_label)
        
        # Add pie chart for DI/LO split
        self.yard_pie_chart = PieChartWidget("Job Type Distribution")
        left_layout.addWidget(self.yard_pie_chart)
        
        yard_layout.addWidget(left_widget, stretch=1)
        
        # Right side: Horizontal bar chart showing all yards
        self.yard_bar_chart = HorizontalBarChart("All Yards Job Count")
        yard_layout.addWidget(self.yard_bar_chart, stretch=2)
        
        self.yard_card.addContent(yard_container)
        cards_grid.addWidget(self.yard_card, 1, 0, 1, 2)  # Span 2 columns
        
        # NOTE: Congestion alerts removed - will show as popup notifications
        
        # Route Optimization Card - Blue
        self.route_card = DashboardCard("🗺️ ROUTE OPTIMIZATION", "", "#3498DB")
        
        # Container for route stats + progress bars
        route_container = QWidget()
        route_layout = QVBoxLayout(route_container)
        
        self.route_label = QLabel("Loading...")
        self.route_label.setStyleSheet("""
            color: #FFFFFF; 
            padding: 15px; 
            font-size: 16px;
            line-height: 1.6;
        """)
        self.route_label.setWordWrap(True)
        route_layout.addWidget(self.route_label)
        
        # Add progress bars for efficiency metrics
        self.efficiency_bar = ProgressBar("Average Efficiency", 100, "#2ECC71")
        self.optimal_bar = ProgressBar("Optimal Routes", 100, "#00D9FF")
        route_layout.addWidget(self.efficiency_bar)
        route_layout.addWidget(self.optimal_bar)
        
        self.route_card.addContent(route_container)
        cards_grid.addWidget(self.route_card, 2, 0, 1, 2)
        
        scroll_layout.addLayout(cards_grid)
    
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
            <div style='line-height: 2.0;'>
                <p style='margin: 10px 0;'><span style='color: #00D9FF; font-size: 18px; font-weight: bold;'>● Active Jobs:</span> 
                   <span style='color: #FFFFFF; font-size: 20px; font-weight: bold;'>{active_jobs}</span></p>
                <p style='margin: 10px 0;'><span style='color: #2ECC71; font-size: 18px; font-weight: bold;'>● Completed:</span> 
                   <span style='color: #FFFFFF; font-size: 20px; font-weight: bold;'>{completed_jobs}</span></p>
                <p style='margin: 10px 0;'><span style='color: #F39C12; font-size: 18px; font-weight: bold;'>● Total Tracked:</span> 
                   <span style='color: #FFFFFF; font-size: 20px; font-weight: bold;'>{total_jobs}</span></p>
            </div>
            """
            self.timeline_label.setText(text)
            
            # Update progress indicator
            self.progress_total.setValue(completed_jobs)
            
        except Exception as e:
            self.timeline_label.setText(f"<span style='color: #E74C3C;'>Error: {e}</span>")
    
    def update_emissions_data(self):
        """Update emissions information with chart"""
        emissions_file = self.data_folder / "emissions.csv"
        if not emissions_file.exists():
            self.emissions_label.setText("<span style='color: #F39C12; font-size: 16px;'>No data available yet...</span>")
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
                
                text = f"""
                <div style='line-height: 2.0;'>
                    <p style='margin: 10px 0;'><span style='color: #E74C3C; font-size: 20px; font-weight: bold;'>Total Emissions:</span> 
                       <span style='color: #FFFFFF; font-size: 24px; font-weight: bold;'>{total_emissions:.2f} kg</span></p>
                    <p style='margin: 5px 0 15px 20px;'><span style='color: #9B59B6; font-size: 16px;'>≈ {total_emissions/1000:.3f} tons</span></p>
                    
                    <p style='margin: 10px 0;'><span style='color: #F39C12; font-size: 18px; font-weight: bold;'>● DI Jobs:</span> 
                       <span style='color: #FFFFFF; font-size: 20px;'>{di_emissions:.2f} kg</span> 
                       <span style='color: #F39C12; font-size: 16px;'>({di_pct:.1f}%)</span></p>
                    <p style='margin: 10px 0;'><span style='color: #2ECC71; font-size: 18px; font-weight: bold;'>● LO Jobs:</span> 
                       <span style='color: #FFFFFF; font-size: 20px;'>{lo_emissions:.2f} kg</span> 
                       <span style='color: #2ECC71; font-size: 16px;'>({lo_pct:.1f}%)</span></p>
                </div>
                """
                self.emissions_label.setText(text)
                
                # Update bar chart
                bar_data = [
                    ("DI Jobs", di_emissions, "#F39C12"),
                    ("LO Jobs", lo_emissions, "#2ECC71")
                ]
                self.emissions_bar_chart.set_data(bar_data, max_value=total_emissions)
                
                # Update progress (scaled to percentage of expected max)
                self.progress_emissions.setValue(min((total_emissions / 1000) * 10, 100))
        except Exception as e:
            self.emissions_label.setText(f"<span style='color: #E74C3C;'>Error: {e}</span>")
    
    def update_yard_data(self):
        """Update yard job counter information with charts"""
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
            
            # Update summary text (simplified)
            text = f"""
            <div style='line-height: 1.8;'>
                <p style='margin: 10px 0;'><span style='color: #2ECC71; font-size: 22px; font-weight: bold;'>Total Jobs:</span> 
                   <span style='color: #FFFFFF; font-size: 28px; font-weight: bold;'>{total_jobs}</span></p>
                
                <p style='margin: 10px 0;'><span style='color: #F39C12; font-size: 18px; font-weight: bold;'>● DI Jobs:</span> 
                   <span style='color: #FFFFFF; font-size: 22px;'>{total_di}</span> 
                   <span style='color: #F39C12; font-size: 16px;'>({di_pct:.1f}%)</span></p>
                
                <p style='margin: 10px 0;'><span style='color: #3498DB; font-size: 18px; font-weight: bold;'>● LO Jobs:</span> 
                   <span style='color: #FFFFFF; font-size: 22px;'>{total_lo}</span> 
                   <span style='color: #3498DB; font-size: 16px;'>({lo_pct:.1f}%)</span></p>
            </div>
            """
            self.yard_label.setText(text)
            
            # Update pie chart for DI/LO split
            pie_data = [
                ("Discharge (DI)", total_di, "#F39C12"),
                ("Load Out (LO)", total_lo, "#3498DB")
            ]
            self.yard_pie_chart.set_data(pie_data)
            
            # Update bar chart with all yards
            bar_data = []
            for yard, row in yard_totals.iterrows():
                total = int(row['yard_total'])
                # Color code by volume
                color = "#2ECC71" if total >= 50 else "#F39C12" if total >= 20 else "#3498DB"
                bar_data.append((str(yard), total, color))
            
            self.yard_bar_chart.set_data(bar_data)
            
            # Update progress indicators
            self.progress_di.setValue(int(di_pct))
            self.progress_lo.setValue(int(lo_pct))
                
        except Exception as e:
            self.yard_label.setText(f"<span style='color: #E74C3C;'>Error: {e}</span>")
    
    def update_congestion_data(self):
        """Check for congestion and show popup alerts"""
        alert_file = self.data_folder / "congestion_alerts.csv"
        if not alert_file.exists():
            self.progress_congestion.setValue(0)
            return
        
        try:
            df = pd.read_csv(alert_file)
            if df.empty:
                self.progress_congestion.setValue(0)
                self.last_alert_count = 0
            else:
                # Count by severity
                critical = len(df[df['severity'] == 'CRITICAL'])
                high = len(df[df['severity'] == 'HIGH'])
                total_alerts = len(df)
                
                # Update congestion progress indicator
                congestion_level = min((critical * 10 + high * 5), 100)
                self.progress_congestion.setValue(congestion_level)
                
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
            self.progress_congestion.setValue(0)
    
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
                <div style='line-height: 2.0;'>
                    <p style='margin: 10px 0;'><span style='color: #3498DB; font-size: 20px; font-weight: bold;'>Average Efficiency:</span> 
                       <span style='color: #FFFFFF; font-size: 26px; font-weight: bold;'>{avg_efficiency:.1f}%</span></p>
                    
                    <p style='margin: 10px 0;'><span style='color: #00D9FF; font-size: 18px; font-weight: bold;'>Total Routes:</span> 
                       <span style='color: #FFFFFF; font-size: 22px;'>{total_routes}</span></p>
                    <p style='margin: 10px 0;'><span style='color: #2ECC71; font-size: 18px; font-weight: bold;'>● Optimal (≥95%):</span> 
                       <span style='color: #FFFFFF; font-size: 22px;'>{optimal_routes}</span> 
                       <span style='color: #2ECC71; font-size: 16px;'>({optimal_pct:.1f}%)</span></p>
                    <p style='margin: 10px 0;'><span style='color: #E74C3C; font-size: 18px; font-weight: bold;'>● Inefficient (<80%):</span> 
                       <span style='color: #FFFFFF; font-size: 22px;'>{inefficient}</span></p>
                    
                    <p style='margin: 15px 0 10px 0;'><span style='color: #F39C12; font-size: 16px;'>Total Detours:</span> 
                       <span style='color: #FFFFFF; font-size: 18px;'>{total_detours}</span></p>
                    <p style='margin: 10px 0;'><span style='color: #E74C3C; font-size: 16px;'>Total Backtracking:</span> 
                       <span style='color: #FFFFFF; font-size: 18px;'>{total_backtrack}</span></p>
                </div>
                """
                
                self.route_label.setText(text)
                
                # Update progress bars
                self.progress_efficiency.setValue(int(avg_efficiency))
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
