import sys
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QHBoxLayout,
                             QFileDialog, QMessageBox, QLabel)
from PyQt5.QtCore import Qt


class MatplotlibCanvas(FigureCanvas):
    def __init__(self, parent=None):
        # Figure boyutlarını artır
        self.fig, self.ax = plt.subplots(figsize=(8, 5))
        super().__init__(self.fig)
        self.setParent(parent)

        # Grafik ayarları
        self.fig.set_facecolor('white')
        self.ax.grid(True, linestyle='--', alpha=0.7)
        self.ax.set_xlabel("Time (sec)", fontsize=10)
        self.ax.set_ylabel("Acceleration (g)", fontsize=10)
        self.ax.tick_params(axis='both', which='major', labelsize=8)

        # Kenar boşluklarını ayarla
        self.fig.tight_layout(pad=2.5)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pulse Classification")
        self.setGeometry(100, 100, 1000, 800)  # Pencere boyutunu artır

        # Canvas'ları oluştur
        self.canvas1 = MatplotlibCanvas(self)
        self.canvas2 = MatplotlibCanvas(self)

        # Dosya yolunu göstermek için etiket
        self.label_files = QLabel("No files selected")
        self.label_files.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_files.setStyleSheet("color: gray; font-size: 12px;")

        # Düğmeleri oluştur
        self.browse_button = QPushButton("Browse AT2 Files")
        self.browse_button.clicked.connect(self.browse_files)
        self.browse_button.setStyleSheet("padding: 10px; font-size: 12px; color: white; background-color: #1E90FF;")

        self.open_window_button = QPushButton("Calculate Pulse")
        self.open_window_button.clicked.connect(self.open_new_window)
        self.open_window_button.setStyleSheet(
            "padding: 10px; font-size: 12px; color: white; background-color: #32CD32;")

        # Ana pencere layout
        layout = QVBoxLayout()
        layout.addWidget(self.label_files)
        layout.addWidget(self.canvas1)
        layout.addSpacing(20)  # Boşluğu artır
        layout.addWidget(self.canvas2)

        # butonlar için yatay layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.browse_button)
        button_layout.addWidget(self.open_window_button)

        layout.addLayout(button_layout)

        # Ana widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Dosya yolları
        self.file_paths = []

    def browse_files(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "Select Two AT2 Files", "", "AT2 Files (*.AT2)", options=options)

        if files and len(files) == 2:
            self.file_paths = files
            self.label_files.setText(f"Selected files: {files[0]}, {files[1]}")
            self.main_plot()
        else:
            QMessageBox.warning(self, "File Selection Error", "Please select exactly two AT2 files.")

    def main_plot(self):
        try:
            time_data = np.linspace(0, 10, 100)
            accel_data = np.sin(time_data)

            for i, file_path in enumerate(self.file_paths):
                canvas = self.canvas1 if i == 0 else self.canvas2
                canvas.ax.clear()
                canvas.ax.plot(time_data, accel_data, label=f"File {i + 1}")
                canvas.ax.set_xlabel("Time (sec)", fontsize=10)
                canvas.ax.set_ylabel("Acceleration (g)", fontsize=10)
                canvas.ax.legend()
                canvas.fig.tight_layout()  # Her plot için tight_layout uygula
                canvas.draw()

        except Exception as e:
            QMessageBox.critical(self, "Error", "Error occurred while plotting: " + str(e))

    def open_new_window(self):
        self.new_window = SecondWindow()
        self.new_window.show()


class SecondWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculate Pulse")
        self.setGeometry(200, 200, 1000, 1000)  # Pencere boyutunu artır

        # Canvas
        self.acc_graph = MatplotlibCanvas(self)
        self.pulse_graph = MatplotlibCanvas(self)
        self.acc_pulse_graph = MatplotlibCanvas(self)

        # 2. pencere butonlar
        self.save_csv = QPushButton("Save as CSV")
        self.save_csv.setStyleSheet("padding: 10px; font-size: 12px; background-color: #FFD700;")
        self.save_csv.clicked.connect(self.save_as_csv)

        self.save_png = QPushButton("Save as PNG")
        self.save_png.setStyleSheet("padding: 10px; font-size: 12px; background-color: #FFA07A;")
        self.save_png.clicked.connect(self.save_graphs)

        # 2. pencere layout'u
        layout = QVBoxLayout()
        layout.addWidget(self.acc_graph)
        layout.addSpacing(20)  # Boşlukları artır
        layout.addWidget(self.pulse_graph)
        layout.addSpacing(20)
        layout.addWidget(self.acc_pulse_graph)

        # 2. pencere butonlar için yatay layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.save_csv)
        button_layout.addWidget(self.save_png)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def save_as_csv(self):
        try:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self, "Save CSV File", "", "CSV Files (*.csv)", options=options)

            if file_name:
                time_data = np.linspace(0, 10, 100)
                velocity_data = np.sin(time_data)
                pulse_data = np.cos(time_data)
                velocity_pulse_data = velocity_data * pulse_data

                df = pd.DataFrame({
                    'Time': time_data,
                    'Velocity (m/s)': velocity_data,
                    'Pulse (m/s)': pulse_data,
                    'Velocity-Pulse (m/s)': velocity_pulse_data
                })

                df.to_csv(file_name, index=False)
                QMessageBox.information(self, "Success", f"CSV file saved successfully at: {file_name}")

        except Exception as e:
            QMessageBox.critical(self, "Error", "Error occurred while saving CSV: " + str(e))

    def save_graphs(self):
        try:
            folder_path = QFileDialog.getExistingDirectory(self, "Select Folder", "")

            if folder_path:
                # tight_layout uygulayarak kaydet
                for fig, name in [(self.acc_graph.fig, "Acc"),
                                  (self.pulse_graph.fig, "Pulse"),
                                  (self.acc_pulse_graph.fig, "Acc-Pulse")]:
                    fig.tight_layout()
                    fig.savefig(f"{folder_path}/{name}.png", bbox_inches='tight', dpi=300)

                QMessageBox.information(self, "Success", "Graphs saved in: " + folder_path)

        except Exception as e:
            QMessageBox.critical(self, "Error", "Error occurred while saving graphs: " + str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())