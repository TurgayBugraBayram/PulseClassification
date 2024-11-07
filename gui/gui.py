import sys
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QHBoxLayout,
                             QFileDialog, QMessageBox, QLabel, QSlider, QDesktopWidget)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import re


class MatplotlibCanvas(FigureCanvas):
    def __init__(self, parent=None):
        # Grafik boyutlarını ayarla
        self.fig, self.ax = plt.subplots(figsize=(8, 5))
        super().__init__(self.fig)
        self.setParent(parent)

        # Grafik ayarları
        self.fig.set_facecolor('white')
        self.ax.grid(True, linestyle='--', alpha=0.7)
        self.ax.tick_params(axis='both', which='major', labelsize=8)
        self.fig.tight_layout(pad=3.5)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pulse Classification")
        self.setGeometry(100, 100, 1000, 800)
        icon = QIcon("aybu_icon.png")
        app.setWindowIcon(icon)

        # Ekran ve pencere konumlandırması
        screen = QDesktopWidget().screenGeometry()
        screen_width, screen_height = screen.width(), screen.height()
        window_width, window_height = self.frameGeometry().width(), self.frameGeometry().height()
        self.move((screen_width - window_width) // 2, (screen_height - window_height) // 2)

        # Canvas'ları ve toolbar'ları oluştur
        self.acc_time_1 = MatplotlibCanvas(self)
        self.acc_time_2 = MatplotlibCanvas(self)
        self.toolbar_1 = NavigationToolbar(self.acc_time_1, self)
        self.toolbar_2 = NavigationToolbar(self.acc_time_2, self)

        self.acc_time_1.ax.set_xlabel("Time (sec)", fontsize=10)
        self.acc_time_1.ax.set_ylabel("Acceleration (g)", fontsize=10)
        self.acc_time_2.ax.set_xlabel("Time (sec)", fontsize=10)
        self.acc_time_2.ax.set_ylabel("Acceleration (g)", fontsize=10)

        # Dosya yolu etiketi ve düğmeler
        self.label_files = QLabel("No files selected")
        self.label_files.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_files.setStyleSheet("color: gray; font-size: 12px;")

        self.browse_button = QPushButton("Browse AT2 Files")
        self.browse_button.clicked.connect(self.browse_files)
        self.browse_button.setStyleSheet("padding: 10px; font-size: 12px; color: white; background-color: #1E90FF;")

        self.open_window_button = QPushButton("Calculate Pulse")
        self.open_window_button.clicked.connect(self.open_new_window)
        self.open_window_button.setStyleSheet(
            "padding: 10px; font-size: 12px; color: white; background-color: #32CD32;")

        #kaydırma çubuğu
        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setRange(1, 100)
        self.time_slider.setValue(100)
        self.time_slider.valueChanged.connect(self.update_time_axis)

        # Ana pencere layout
        layout = QVBoxLayout()
        layout.addWidget(self.label_files)
        layout.addWidget(self.toolbar_1)
        layout.addWidget(self.acc_time_1)
        layout.addWidget(self.toolbar_2)
        layout.addWidget(self.acc_time_2)
        layout.addWidget(self.time_slider)

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
        self.time_data = []  # Store time data for each graph

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
            self.time_data = []  # Reset time data for each plot
            for i, file_path in enumerate(self.file_paths):
                # Dosyayı satır satır oku
                with open(file_path, 'r') as file:
                    lines = file.readlines()

                # NPTS ve DT değerlerini al
                npts_line = lines[3]
                npts_match = re.search(r'NPTS=\s*(\d+)', npts_line)
                dt_match = re.search(r'DT=\s*([\d.]+)', npts_line)
                if npts_match and dt_match:
                    npts = int(npts_match.group(1))
                    dt = float(dt_match.group(1))
                else:
                    QMessageBox.critical(self, "Error", f"Could not find NPTS and DT in file: {file_path}")
                    return

                # Zaman ekseni
                time_data = np.linspace(0, (npts - 1) * dt, npts)
                self.time_data.append(time_data)  # Store time data for each plot

                accel_data = []

                # Acceleration verileri
                for line in lines[4:]:
                    accel_data.extend(map(float, line.split()))

                # Grafiği çiz
                canvas = self.acc_time_1 if i == 0 else self.acc_time_2
                canvas.ax.clear()
                canvas.ax.plot(time_data, accel_data, label=f"File {file_path.split('/')[-1]}")
                canvas.ax.set_xlabel("Time (sec)", fontsize=10)
                canvas.ax.set_ylabel("Acceleration (g)", fontsize=10)
                canvas.ax.legend()
                canvas.ax.grid(True, linestyle='--', alpha=0.7)

                canvas.fig.tight_layout()
                canvas.draw()

        except Exception as e:
            QMessageBox.critical(self, "Error", "Error occurred while plotting: " + str(e))

    def update_time_axis(self, value):
        for i, canvas in enumerate([self.acc_time_1, self.acc_time_2]):
            if self.time_data:
                max_time = self.time_data[i][-1] * (value / 100)
                canvas.ax.set_xlim(0, max_time)
                canvas.draw()

    def on_plot_hover(self, event):
        """
        The mouse event that occurs when the user hovers over the plot.
        """
        if event.inaxes:
            x, y = event.xdata, event.ydata
            QMessageBox.information(self, "Data Point", f"Time: {x:.2f} sec, Acceleration: {y:.2f} g")

    def open_new_window(self):
        self.new_window = SecondWindow()
        self.new_window.show()


class SecondWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculate Pulse")
        self.setGeometry(200, 200, 1000, 1000)

        screen = QDesktopWidget().screenGeometry()
        screen_width, screen_height = screen.width(), screen.height()
        window_width, window_height = self.frameGeometry().width(), self.frameGeometry().height()
        self.move((screen_width - window_width) // 2, (screen_height - window_height) // 2)

        # Canvas
        self.acc_graph = MatplotlibCanvas(self)
        self.pulse_graph = MatplotlibCanvas(self)
        self.acc_pulse_graph = MatplotlibCanvas(self)

        self.acc_graph_toolbar = NavigationToolbar(self.acc_graph, self)
        self.pulse_graph_toolbar = NavigationToolbar(self.pulse_graph, self)
        self.acc_pulse_graph_toolbar = NavigationToolbar(self.acc_pulse_graph, self)

        self.acc_graph.ax.set_xlabel("Time (sec)", fontsize=10)
        self.acc_graph.ax.set_ylabel("Acceleration (g)", fontsize=10)

        self.pulse_graph.ax.set_xlabel("Time (sec)", fontsize=10)
        self.pulse_graph.ax.set_ylabel("Pulse (m/s)", fontsize=10)

        self.acc_pulse_graph.ax.set_xlabel("Time (sec)", fontsize=10)
        self.acc_pulse_graph.ax.set_ylabel("Acceleration-Pulse (m/s)", fontsize=10)

        # 2. pencere butonlar
        self.save_csv = QPushButton("Save as CSV")
        self.save_csv.setStyleSheet("padding: 10px; font-size: 12px; background-color: #FFD700;")
        self.save_csv.clicked.connect(self.save_as_csv)

        self.save_png = QPushButton("Save as PNG")
        self.save_png.setStyleSheet("padding: 10px; font-size: 12px; background-color: #FFA07A;")
        self.save_png.clicked.connect(self.save_graphs)

        # 2. pencere layout'u
        layout = QVBoxLayout()
        layout.addWidget(self.acc_graph_toolbar)
        layout.addWidget(self.acc_graph)
        layout.addWidget(self.pulse_graph_toolbar)
        layout.addWidget(self.pulse_graph)
        layout.addWidget(self.acc_pulse_graph_toolbar)
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