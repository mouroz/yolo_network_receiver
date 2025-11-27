#!/usr/bin/env python3
"""
YOLO Defect Detection Server Interface
A PyQt6 GUI for the AsyncReceiver server with dashboard visualization.
"""

import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime

# Setup paths
FILE = Path(__file__).resolve()
INTERFACE_DIR = FILE.parent
ROOT = FILE.parents[1]  # yolo_network_receiver
COMM_DIR = ROOT / 'communication_submodule'

if str(COMM_DIR) not in sys.path:
    sys.path.insert(0, str(COMM_DIR))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QStackedWidget, QListWidget, QListWidgetItem, QStatusBar, QFrame,
    QSplitter, QScrollArea, QComboBox, QGroupBox, QGridLayout,
    QHeaderView, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer
from PyQt6.QtGui import QPixmap, QFont, QColor, QPalette, QIcon

import pandas as pd

# Import the receiver module
from async_communication import AsyncReceiver


# ══════════════════════════════════════════════════════════════════════════════
# STYLE CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════

STYLE_SHEET = """
QMainWindow {
    background-color: #0d1117;
}

QWidget {
    background-color: #0d1117;
    color: #c9d1d9;
    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
    font-size: 13px;
}

QGroupBox {
    border: 1px solid #30363d;
    border-radius: 8px;
    margin-top: 12px;
    padding: 16px;
    background-color: #161b22;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 16px;
    padding: 0 8px;
    color: #58a6ff;
    font-weight: bold;
    font-size: 14px;
}

QLabel {
    color: #c9d1d9;
    background: transparent;
}

QLineEdit {
    background-color: #21262d;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 10px 14px;
    color: #c9d1d9;
    selection-background-color: #388bfd;
}

QLineEdit:focus {
    border-color: #58a6ff;
    background-color: #161b22;
}

QPushButton {
    background-color: #238636;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    color: #ffffff;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #2ea043;
}

QPushButton:pressed {
    background-color: #238636;
}

QPushButton:disabled {
    background-color: #21262d;
    color: #484f58;
}

QPushButton#secondary {
    background-color: #21262d;
    border: 1px solid #30363d;
    color: #c9d1d9;
}

QPushButton#secondary:hover {
    background-color: #30363d;
    border-color: #8b949e;
}

QPushButton#danger {
    background-color: #da3633;
}

QPushButton#danger:hover {
    background-color: #f85149;
}

QTableWidget {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    gridline-color: #21262d;
    selection-background-color: #388bfd40;
}

QTableWidget::item {
    padding: 8px;
    border-bottom: 1px solid #21262d;
}

QTableWidget::item:selected {
    background-color: #388bfd40;
    color: #c9d1d9;
}

QHeaderView::section {
    background-color: #21262d;
    color: #8b949e;
    padding: 10px;
    border: none;
    border-bottom: 1px solid #30363d;
    font-weight: bold;
}

QListWidget {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 4px;
}

QListWidget::item {
    padding: 10px;
    border-radius: 4px;
    margin: 2px;
}

QListWidget::item:selected {
    background-color: #388bfd40;
}

QListWidget::item:hover {
    background-color: #21262d;
}

QTabWidget::pane {
    border: 1px solid #30363d;
    border-radius: 8px;
    background-color: #161b22;
}

QTabBar::tab {
    background-color: #21262d;
    border: 1px solid #30363d;
    padding: 10px 20px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    color: #8b949e;
}

QTabBar::tab:selected {
    background-color: #161b22;
    border-bottom-color: #161b22;
    color: #58a6ff;
}

QTabBar::tab:hover:!selected {
    background-color: #30363d;
}

QComboBox {
    background-color: #21262d;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 8px 14px;
    color: #c9d1d9;
    min-width: 150px;
}

QComboBox:hover {
    border-color: #8b949e;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox QAbstractItemView {
    background-color: #21262d;
    border: 1px solid #30363d;
    selection-background-color: #388bfd;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical {
    background-color: #161b22;
    width: 10px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background-color: #30363d;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #484f58;
}

QStatusBar {
    background-color: #161b22;
    border-top: 1px solid #30363d;
    color: #8b949e;
    padding: 4px;
}

QFrame#statsCard {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 16px;
}

QLabel#statValue {
    font-size: 32px;
    font-weight: bold;
}

QLabel#statLabel {
    font-size: 12px;
    color: #8b949e;
}

QLabel#scratchValue { color: #f0883e; }
QLabel#spotValue { color: #a371f7; }
QLabel#rustValue { color: #f85149; }
QLabel#totalValue { color: #58a6ff; }
"""


# ══════════════════════════════════════════════════════════════════════════════
# ASYNC SERVER THREAD
# ══════════════════════════════════════════════════════════════════════════════

class ServerThread(QThread):
    """Thread to run the AsyncReceiver server without blocking the GUI."""
    
    log_message = pyqtSignal(str)
    client_connected = pyqtSignal(str)
    file_received = pyqtSignal(str)
    server_started = pyqtSignal(bool, str)
    
    def __init__(self, host: str, port: int, save_dir: str):
        super().__init__()
        self.host = host
        self.port = port
        self.save_dir = save_dir
        self.receiver = None
        self._running = False
        self.loop = None
        
    def run(self):
        """Run the async server in this thread."""
        self._running = True
        
        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            self.receiver = AsyncReceiver(
                host=self.host,
                port=self.port,
                save_dir=self.save_dir
            )
            
            self.server_started.emit(True, f"Server listening on {self.host}:{self.port}")
            self.log_message.emit(f"[{self._timestamp()}] Server started on {self.host}:{self.port}")
            
            self.loop.run_until_complete(self.receiver.start())
            
        except OSError as e:
            self.server_started.emit(False, f"Failed to bind: {e}")
            self.log_message.emit(f"[{self._timestamp()}] ERROR: {e}")
        except Exception as e:
            self.log_message.emit(f"[{self._timestamp()}] ERROR: {e}")
        finally:
            self._running = False
            if self.loop:
                self.loop.close()
    
    def stop(self):
        """Stop the server gracefully."""
        self._running = False
        if self.receiver and self.receiver.server:
            self.receiver.server.close()
        if self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)
            
    def _timestamp(self):
        return datetime.now().strftime("%H:%M:%S")


# ══════════════════════════════════════════════════════════════════════════════
# STATS CARD WIDGET
# ══════════════════════════════════════════════════════════════════════════════

class StatsCard(QFrame):
    """A card widget displaying a statistic with label and value."""
    
    def __init__(self, label: str, value: int = 0, color_class: str = "totalValue"):
        super().__init__()
        self.setObjectName("statsCard")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(20, 16, 20, 16)
        
        self.value_label = QLabel(str(value))
        self.value_label.setObjectName(color_class)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.text_label = QLabel(label)
        self.text_label.setObjectName("statLabel")
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.value_label)
        layout.addWidget(self.text_label)
        
    def set_value(self, value: int):
        self.value_label.setText(str(value))


# ══════════════════════════════════════════════════════════════════════════════
# IMAGE VIEWER WIDGET
# ══════════════════════════════════════════════════════════════════════════════

class ImageViewer(QScrollArea):
    """Scrollable image viewer with scaling."""
    
    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("background-color: #0d1117; padding: 20px;")
        self.image_label.setText("Selecione uma imagem na tabela")
        self.image_label.setMinimumSize(400, 300)
        
        self.setWidget(self.image_label)
        self.current_pixmap = None
        
    def load_image(self, path: str):
        """Load and display an image from path."""
        if not os.path.exists(path):
            self.image_label.setText(f"Imagem não encontrada:\n{path}")
            self.current_pixmap = None
            return False
            
        pixmap = QPixmap(path)
        if pixmap.isNull():
            self.image_label.setText(f"Falha ao carregar imagem:\n{path}")
            self.current_pixmap = None
            return False
            
        self.current_pixmap = pixmap
        self._update_display()
        return True
        
    def _update_display(self):
        """Update the displayed image scaled to fit."""
        if self.current_pixmap:
            # Scale to fit the viewport while maintaining aspect ratio
            viewport_size = self.viewport().size()
            scaled = self.current_pixmap.scaled(
                viewport_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled)
            
    def resizeEvent(self, event):
        """Handle resize to rescale image."""
        super().resizeEvent(event)
        self._update_display()
        
    def clear(self):
        """Clear the displayed image."""
        self.current_pixmap = None
        self.image_label.clear()
        self.image_label.setText("Selecione uma imagem na tabela")


# ══════════════════════════════════════════════════════════════════════════════
# CONNECTION FORM WIDGET
# ══════════════════════════════════════════════════════════════════════════════

class ConnectionForm(QWidget):
    """Initial connection form for server configuration."""
    
    connect_requested = pyqtSignal(str, int)
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        
        # Logo/Title area
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setSpacing(8)
        
        title = QLabel("🔬 YOLO Defect Server")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #58a6ff;
            background: transparent;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        subtitle = QLabel("Sistema de Detecção de Defeitos")
        subtitle.setStyleSheet("""
            font-size: 14px;
            color: #8b949e;
            background: transparent;
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        
        # Form group
        form_group = QGroupBox("Configuração do Servidor")
        form_layout = QGridLayout(form_group)
        form_layout.setSpacing(16)
        form_layout.setContentsMargins(24, 24, 24, 24)
        
        # Host field
        host_label = QLabel("Host:")
        self.host_input = QLineEdit("0.0.0.0")
        self.host_input.setPlaceholderText("Ex: 0.0.0.0 ou 192.168.1.100")
        self.host_input.setMinimumWidth(280)
        
        # Port field
        port_label = QLabel("Porta:")
        self.port_input = QLineEdit("8888")
        self.port_input.setPlaceholderText("Ex: 8888")
        
        # Connect button
        self.connect_btn = QPushButton("▶  Iniciar Servidor")
        self.connect_btn.setMinimumHeight(48)
        self.connect_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.connect_btn.clicked.connect(self._on_connect)
        
        form_layout.addWidget(host_label, 0, 0)
        form_layout.addWidget(self.host_input, 0, 1)
        form_layout.addWidget(port_label, 1, 0)
        form_layout.addWidget(self.port_input, 1, 1)
        form_layout.addWidget(self.connect_btn, 2, 0, 1, 2)
        
        # Error label
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #f85149; background: transparent;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add all to main layout
        layout.addStretch()
        layout.addWidget(title_container)
        layout.addSpacing(20)
        layout.addWidget(form_group)
        layout.addWidget(self.error_label)
        layout.addStretch()
        
        # Set fixed width for form
        form_group.setMaximumWidth(400)
        
    def _on_connect(self):
        """Validate and emit connection request."""
        host = self.host_input.text().strip()
        port_str = self.port_input.text().strip()
        
        if not host:
            self.error_label.setText("❌ Host não pode estar vazio")
            return
            
        if not port_str.isdigit():
            self.error_label.setText("❌ Porta deve ser um número")
            return
            
        port = int(port_str)
        if port < 1 or port > 65535:
            self.error_label.setText("❌ Porta deve estar entre 1 e 65535")
            return
            
        self.error_label.setText("")
        self.connect_btn.setEnabled(False)
        self.connect_btn.setText("Iniciando...")
        self.connect_requested.emit(host, port)
        
    def reset(self):
        """Reset form state."""
        self.connect_btn.setEnabled(True)
        self.connect_btn.setText("▶  Iniciar Servidor")
        self.error_label.setText("")
        
    def set_error(self, message: str):
        """Display error message."""
        self.error_label.setText(f"❌ {message}")
        self.reset()


# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD WIDGET
# ══════════════════════════════════════════════════════════════════════════════

class DashboardWidget(QWidget):
    """Main dashboard with image viewer, defects table, and stats."""
    
    FLAT_MODE = "(Pasta Raiz)"  # Special value for flat file mode
    
    def __init__(self, received_dir: Path):
        super().__init__()
        self.received_dir = received_dir
        self.current_run = None
        self.df = None
        self._is_refreshing = False  # Prevent reload loops
        self._show_original = False  # False = yolo_out (labels), True = yolo_in (original)
        self._current_image_name = None  # Track current image for toggle
        self._setup_ui()
        
    def _setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(16, 16, 16, 16)
        
        # ─── LEFT PANEL: Controls & Stats ─────────────────────────────────────
        left_panel = QWidget()
        left_panel.setMaximumWidth(320)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(16)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Run selector group
        run_group = QGroupBox("Seleção de Run")
        run_layout = QVBoxLayout(run_group)
        
        self.run_combo = QComboBox()
        self.run_combo.currentTextChanged.connect(self._on_run_changed)
        
        self.reload_btn = QPushButton("🔄  Recarregar")
        self.reload_btn.setObjectName("secondary")
        self.reload_btn.clicked.connect(self.reload_data)
        
        run_layout.addWidget(self.run_combo)
        run_layout.addWidget(self.reload_btn)
        
        # Stats cards
        stats_group = QGroupBox("Contadores Totais")
        stats_layout = QGridLayout(stats_group)
        stats_layout.setSpacing(12)
        
        self.scratch_card = StatsCard("Scratches", 0, "scratchValue")
        self.spot_card = StatsCard("Spots", 0, "spotValue")
        self.rust_card = StatsCard("Rust", 0, "rustValue")
        self.total_card = StatsCard("Total Defeitos", 0, "totalValue")
        
        stats_layout.addWidget(self.scratch_card, 0, 0)
        stats_layout.addWidget(self.spot_card, 0, 1)
        stats_layout.addWidget(self.rust_card, 1, 0)
        stats_layout.addWidget(self.total_card, 1, 1)
        
        # Images count
        self.images_count_label = QLabel("Imagens: 0")
        self.images_count_label.setStyleSheet("color: #8b949e; padding: 8px;")
        
        left_layout.addWidget(run_group)
        left_layout.addWidget(stats_group)
        left_layout.addWidget(self.images_count_label)
        left_layout.addStretch()
        
        # ─── CENTER PANEL: Image Viewer ───────────────────────────────────────
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)
        center_layout.setContentsMargins(0, 0, 0, 0)
        
        viewer_group = QGroupBox("Visualizador de Imagem")
        viewer_layout = QVBoxLayout(viewer_group)
        
        # Toggle entre original e labels
        toggle_layout = QHBoxLayout()
        self.view_original_btn = QPushButton("Original")
        self.view_labels_btn = QPushButton("Com Labels")
        self.view_original_btn.setObjectName("secondary")
        self.view_labels_btn.setObjectName("secondary")
        self.view_original_btn.setCheckable(True)
        self.view_labels_btn.setCheckable(True)
        self.view_labels_btn.setChecked(True)  # Default: mostrar com labels
        self.view_original_btn.clicked.connect(lambda: self._set_view_mode(True))
        self.view_labels_btn.clicked.connect(lambda: self._set_view_mode(False))
        toggle_layout.addWidget(self.view_original_btn)
        toggle_layout.addWidget(self.view_labels_btn)
        toggle_layout.addStretch()
        
        self.image_viewer = ImageViewer()
        self.image_path_label = QLabel("")
        self.image_path_label.setStyleSheet("color: #8b949e; font-size: 11px; padding: 4px;")
        self.image_path_label.setWordWrap(True)
        
        viewer_layout.addLayout(toggle_layout)
        viewer_layout.addWidget(self.image_viewer, 1)
        viewer_layout.addWidget(self.image_path_label)
        
        center_layout.addWidget(viewer_group)
        
        # ─── RIGHT PANEL: Defects Table ───────────────────────────────────────
        right_panel = QWidget()
        right_panel.setMinimumWidth(400)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        table_group = QGroupBox("Tabela de Defeitos")
        table_layout = QVBoxLayout(table_group)
        
        self.defects_table = QTableWidget()
        self.defects_table.setColumnCount(4)
        self.defects_table.setHorizontalHeaderLabels(["Nome", "Scratch", "Spot", "Rust"])
        self.defects_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.defects_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.defects_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.defects_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.defects_table.setColumnWidth(1, 70)
        self.defects_table.setColumnWidth(2, 70)
        self.defects_table.setColumnWidth(3, 70)
        self.defects_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.defects_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.defects_table.itemSelectionChanged.connect(self._on_table_selection)
        self.defects_table.setAlternatingRowColors(True)
        
        # Filter row (show only with defects)
        filter_layout = QHBoxLayout()
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Todas", "Com Defeitos", "Sem Defeitos"])
        self.filter_combo.currentTextChanged.connect(self._apply_filter)
        filter_label = QLabel("Filtrar:")
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_combo)
        filter_layout.addStretch()
        
        table_layout.addLayout(filter_layout)
        table_layout.addWidget(self.defects_table)
        
        right_layout.addWidget(table_group)
        
        # ─── Add panels to splitter ───────────────────────────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(center_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([280, 500, 400])
        
        main_layout.addWidget(splitter)
        
    def reload_data(self):
        """Reload all data from the received directory."""
        if self._is_refreshing:
            return
        self._is_refreshing = True
        
        try:
            self._load_runs()
            if self.current_run:
                self._load_run_data(self.current_run)
        finally:
            self._is_refreshing = False
            
    def _load_runs(self):
        """Load available runs from received directory."""
        if not self.received_dir.exists():
            self.run_combo.blockSignals(True)
            self.run_combo.clear()
            self.run_combo.addItem("(Nenhum run disponível)")
            self.run_combo.blockSignals(False)
            return
        
        runs = set()
        
        # Check new structure: received/yolo_out/runX/ and received/yolo_in/runX/
        for subfolder in ['yolo_out', 'yolo_in']:
            sub_path = self.received_dir / subfolder
            if sub_path.exists():
                for d in sub_path.iterdir():
                    if d.is_dir() and d.name.startswith('run'):
                        runs.add(d.name)
        
        # Also check old structure: received/runX/ (backwards compat)
        for d in self.received_dir.iterdir():
            if d.is_dir() and d.name.startswith('run'):
                runs.add(d.name)
        
        runs = sorted(runs, 
            key=lambda x: int(x.replace('run', '')) if x.replace('run', '').isdigit() else 0,
            reverse=True)
        
        # Check for flat files (images directly in received/)
        image_exts = {'.jpg', '.jpeg', '.png'}
        has_flat_files = any(
            f.is_file() and f.suffix.lower() in image_exts 
            for f in self.received_dir.iterdir()
        )
        
        # Build new items list
        new_items = []
        if has_flat_files:
            new_items.append(self.FLAT_MODE)
        new_items.extend(runs)
        
        if not new_items:
            self.run_combo.blockSignals(True)
            self.run_combo.clear()
            self.run_combo.addItem("(Nenhum run disponível)")
            self.run_combo.blockSignals(False)
            return
        
        # Get current selection to preserve it
        current_selection = self.run_combo.currentText()
        
        # Check if items changed
        current_items = [self.run_combo.itemText(i) for i in range(self.run_combo.count())]
        if current_items == new_items:
            # No changes, don't update
            return
            
        self.run_combo.blockSignals(True)
        self.run_combo.clear()
        self.run_combo.addItems(new_items)
        
        # Restore selection if it still exists
        if current_selection in new_items:
            self.run_combo.setCurrentText(current_selection)
        else:
            self.current_run = new_items[0]
            
        self.run_combo.blockSignals(False)
        
    def _on_run_changed(self, run_name: str):
        """Handle run selection change."""
        if run_name and not run_name.startswith("(Nenhum"):
            self.current_run = run_name
            self._load_run_data(run_name)
            
    def _get_run_dir(self, run_name: str) -> Path:
        """Get the directory for a run (handles flat mode)."""
        if run_name == self.FLAT_MODE:
            return self.received_dir
        return self.received_dir / run_name
            
    def _load_run_data(self, run_name: str):
        """Load data for a specific run."""
        # Determine paths based on structure
        if run_name == self.FLAT_MODE:
            run_dir = self.received_dir
            csv_path = self.received_dir / "relatorio_defeitos_qtd.csv"
        else:
            # Try new structure first: yolo_out/runX/
            new_run_dir = self.received_dir / "yolo_out" / run_name
            old_run_dir = self.received_dir / run_name
            run_dir = new_run_dir if new_run_dir.exists() else old_run_dir
            csv_path = run_dir / "relatorio_defeitos_qtd.csv"
        
        if not run_dir.exists():
            self.images_count_label.setText("Imagens: 0")
            self.df = None
            self.defects_table.setRowCount(0)
            self._reset_stats()
            return
        
        # Count images
        image_exts = {'.jpg', '.jpeg', '.png'}
        images = [f for f in run_dir.iterdir() 
                  if f.is_file() and f.suffix.lower() in image_exts]
        self.images_count_label.setText(f"Imagens: {len(images)}")
        
        # Load CSV
        if csv_path.exists():
            try:
                self.df = pd.read_csv(csv_path)
                self._populate_table(self.filter_combo.currentText())
                self._update_stats()
            except Exception as e:
                self.df = None
                self.defects_table.setRowCount(0)
                self._reset_stats()
        else:
            # No CSV - create dataframe from images for viewing
            self.df = pd.DataFrame({
                'Nome_Arquivo': [f.name for f in images],
                'scratch': [0] * len(images),
                'spot': [0] * len(images),
                'rust': [0] * len(images)
            })
            self._populate_table(self.filter_combo.currentText())
            self._reset_stats()
            
        # Don't clear image viewer on data reload to preserve selection
        # self.image_viewer.clear()
        # self.image_path_label.setText("")
        
    def _populate_table(self, filter_mode: str = "Todas"):
        """Populate the defects table from dataframe."""
        if self.df is None:
            return
        
        # Remember current selection
        current_selected_file = None
        selected = self.defects_table.selectedItems()
        if selected:
            filename_item = self.defects_table.item(selected[0].row(), 0)
            if filename_item:
                current_selected_file = filename_item.data(Qt.ItemDataRole.UserRole)
            
        df_filtered = self.df.copy()
        
        if filter_mode == "Com Defeitos":
            df_filtered = df_filtered[
                (df_filtered['scratch'] > 0) | 
                (df_filtered['spot'] > 0) | 
                (df_filtered['rust'] > 0)
            ]
        elif filter_mode == "Sem Defeitos":
            df_filtered = df_filtered[
                (df_filtered['scratch'] == 0) & 
                (df_filtered['spot'] == 0) & 
                (df_filtered['rust'] == 0)
            ]
        
        # Block signals while updating to avoid triggering selection changed
        self.defects_table.blockSignals(True)
        self.defects_table.setRowCount(len(df_filtered))
        
        row_to_select = -1
        
        for row_idx, (_, row) in enumerate(df_filtered.iterrows()):
            # Filename
            name_item = QTableWidgetItem(row['Nome_Arquivo'])
            name_item.setData(Qt.ItemDataRole.UserRole, row['Nome_Arquivo'])
            
            # Check if this was the selected row
            if row['Nome_Arquivo'] == current_selected_file:
                row_to_select = row_idx
            
            # Defect counts with color coding
            scratch_item = QTableWidgetItem(str(int(row['scratch'])))
            spot_item = QTableWidgetItem(str(int(row['spot'])))
            rust_item = QTableWidgetItem(str(int(row['rust'])))
            
            # Center align numbers
            for item in [scratch_item, spot_item, rust_item]:
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
            # Color code non-zero values
            if row['scratch'] > 0:
                scratch_item.setForeground(QColor("#f0883e"))
            if row['spot'] > 0:
                spot_item.setForeground(QColor("#a371f7"))
            if row['rust'] > 0:
                rust_item.setForeground(QColor("#f85149"))
                
            self.defects_table.setItem(row_idx, 0, name_item)
            self.defects_table.setItem(row_idx, 1, scratch_item)
            self.defects_table.setItem(row_idx, 2, spot_item)
            self.defects_table.setItem(row_idx, 3, rust_item)
        
        self.defects_table.blockSignals(False)
        
        # Restore selection if it still exists
        if row_to_select >= 0:
            self.defects_table.selectRow(row_to_select)
            
    def _apply_filter(self, filter_mode: str):
        """Apply filter to table."""
        self._populate_table(filter_mode)
        
    def _update_stats(self):
        """Update stats cards from dataframe."""
        if self.df is None:
            self._reset_stats()
            return
            
        total_scratch = int(self.df['scratch'].sum())
        total_spot = int(self.df['spot'].sum())
        total_rust = int(self.df['rust'].sum())
        total = total_scratch + total_spot + total_rust
        
        self.scratch_card.set_value(total_scratch)
        self.spot_card.set_value(total_spot)
        self.rust_card.set_value(total_rust)
        self.total_card.set_value(total)
        
    def _reset_stats(self):
        """Reset all stats to zero."""
        self.scratch_card.set_value(0)
        self.spot_card.set_value(0)
        self.rust_card.set_value(0)
        self.total_card.set_value(0)
        
    def _set_view_mode(self, show_original: bool):
        """Toggle between original and labeled image view."""
        self._show_original = show_original
        self.view_original_btn.setChecked(show_original)
        self.view_labels_btn.setChecked(not show_original)
        # Reload current image with new mode
        if self._current_image_name:
            self._load_current_image()
    
    def _get_image_path(self, filename: str) -> Path:
        """Get image path based on current view mode (original vs labels)."""
        if self.current_run == self.FLAT_MODE:
            # Flat mode - images directly in received/
            return self.received_dir / filename
        
        # New structure: received/yolo_in/runX/ or received/yolo_out/runX/
        subfolder = "yolo_in" if self._show_original else "yolo_out"
        new_path = self.received_dir / subfolder / self.current_run / filename
        
        if new_path.exists():
            return new_path
        
        # Fallback: old structure received/runX/ (for backwards compat)
        return self.received_dir / self.current_run / filename
    
    def _load_current_image(self):
        """Load the current image with the selected view mode."""
        if not self._current_image_name or not self.current_run:
            return
        
        image_path = self._get_image_path(self._current_image_name)
        mode = "Original" if self._show_original else "Com Labels"
        
        if self.image_viewer.load_image(str(image_path)):
            self.image_path_label.setText(f"📁 [{mode}] {image_path}")
        else:
            self.image_path_label.setText(f"❌ [{mode}] Não encontrado: {image_path}")

    def _on_table_selection(self):
        """Handle table row selection to show image."""
        selected = self.defects_table.selectedItems()
        if not selected:
            return
            
        row = selected[0].row()
        filename_item = self.defects_table.item(row, 0)
        if not filename_item:
            return
            
        filename = filename_item.data(Qt.ItemDataRole.UserRole)
        if not filename or not self.current_run:
            return
        
        self._current_image_name = filename
        self._load_current_image()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN WINDOW
# ══════════════════════════════════════════════════════════════════════════════

class ServerMainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.server_thread = None
        self.received_dir = ROOT / "received"
        
        self._setup_window()
        self._setup_ui()
        
    def _setup_window(self):
        """Configure main window properties."""
        self.setWindowTitle("YOLO Defect Detection Server")
        self.setMinimumSize(1280, 800)
        self.resize(1400, 900)
        
    def _setup_ui(self):
        """Setup the main UI structure."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Stacked widget for form/dashboard
        self.stack = QStackedWidget()
        
        # Connection form
        self.connection_form = ConnectionForm()
        self.connection_form.connect_requested.connect(self._start_server)
        
        # Dashboard
        self.dashboard = DashboardWidget(self.received_dir)
        
        self.stack.addWidget(self.connection_form)
        self.stack.addWidget(self.dashboard)
        
        layout.addWidget(self.stack)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Aguardando configuração do servidor...")
        
        # Stop button (hidden initially)
        self.stop_btn = QPushButton("⏹  Parar Servidor")
        self.stop_btn.setObjectName("danger")
        self.stop_btn.clicked.connect(self._stop_server)
        self.stop_btn.hide()
        self.status_bar.addPermanentWidget(self.stop_btn)
        
    def _start_server(self, host: str, port: int):
        """Start the server in a background thread."""
        save_dir = str(self.received_dir)
        
        self.server_thread = ServerThread(host, port, save_dir)
        self.server_thread.server_started.connect(self._on_server_started)
        self.server_thread.log_message.connect(self._on_log_message)
        self.server_thread.start()
        
    def _on_server_started(self, success: bool, message: str):
        """Handle server start result."""
        if success:
            self.stack.setCurrentIndex(1)  # Switch to dashboard
            self.status_bar.showMessage(f"✅ {message}")
            self.stop_btn.show()
            self.dashboard.reload_data()
            
            # Setup periodic refresh (10 seconds to avoid UI interruption)
            self.refresh_timer = QTimer()
            self.refresh_timer.timeout.connect(self.dashboard.reload_data)
            self.refresh_timer.start(10000)  # Refresh every 10 seconds
        else:
            self.connection_form.set_error(message)
            
    def _on_log_message(self, message: str):
        """Handle log messages from server."""
        # Could show in a log panel if needed
        print(message)
        
    def _stop_server(self):
        """Stop the running server."""
        if self.server_thread:
            self.server_thread.stop()
            self.server_thread.wait(2000)
            self.server_thread = None
            
        if hasattr(self, 'refresh_timer'):
            self.refresh_timer.stop()
            
        self.stack.setCurrentIndex(0)  # Back to connection form
        self.connection_form.reset()
        self.stop_btn.hide()
        self.status_bar.showMessage("Servidor parado")
        
    def closeEvent(self, event):
        """Clean up on window close."""
        self._stop_server()
        event.accept()


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE_SHEET)
    
    # Set application properties
    app.setApplicationName("YOLO Defect Server")
    app.setOrganizationName("TI6")
    
    window = ServerMainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

