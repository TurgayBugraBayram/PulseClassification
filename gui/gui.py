import sys
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QSpacerItem,
                             QSizePolicy, QFileDialog, QMessageBox)


class MatplotlibCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        super().__init__(self.fig)
        self.setParent(parent)
        self.fig.set_facecolor('white')
        self.ax.grid(True, linestyle='--', alpha=0.7)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main")
        self.setGeometry(100, 100, 800, 600)

        # Canvas'ları oluştur ama plot yapma
        self.canvas1 = MatplotlibCanvas(self)
        self.canvas2 = MatplotlibCanvas(self)

        # main pencere butonlar
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_files)

        self.open_window_button = QPushButton("Calculate Pulse")
        self.open_window_button.clicked.connect(self.open_new_window)

        # main pencere layout'u
        layout = QVBoxLayout()
        layout.addWidget(self.canvas1)
        layout.addWidget(self.canvas2)

        # butonlar için yatay layout
        button_layout = QHBoxLayout()
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        button_layout.addItem(spacer)
        button_layout.addWidget(self.browse_button)
        button_layout.addWidget(self.open_window_button)

        layout.addLayout(button_layout)

        # widget oluşturup ve layout'u ekle
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # File paths
        self.file_paths = []

    def browse_files(self):
        try:
            # Dosya seçme window
            options = QFileDialog.Options()
            files, _ = QFileDialog.getOpenFileNames(self, "Open AT2 Files", "", "AT2 Files (*.AT2)", options=options)

            if files and len(files) == 2:
                self.file_paths = files
                print("Selected files:", self.file_paths)
                self.main_plot()
            else:
                QMessageBox.warning(self, "File Selection", "Please select exactly two AT2 files.")

        except Exception as e:
            QMessageBox.critical(self, "Error", "Hata oluştu: " + str(e))

    def main_plot(self):
        try:
            for i, file_path in enumerate(self.file_paths):
                # Load data from each AT2 file
                pass

                # Plot data on each canvas
                canvas = self.canvas1 if i == 0 else self.canvas2
                canvas.ax.clear()
                canvas.ax.plot(time_data, accel_data, label=f"File {i+1}")
                canvas.ax.set_xlabel("Time (sec)")
                canvas.ax.set_ylabel("Acceleration (g)")
                canvas.ax.legend()
                canvas.draw()

        except Exception as e:
            QMessageBox.critical(self, "Error", "Error occurred while plotting: " + str(e))

    def open_new_window(self):
        # 2. pencereye geçme
        self.new_window = SecondWindow()
        self.new_window.show()


class SecondWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Second")
        self.setGeometry(200, 200, 800, 800)

        # 2. pencere grafik alanları
        self.acc_graph = MatplotlibCanvas(self)
        self.pulse_graph = MatplotlibCanvas(self)
        self.acc_pulse_graph = MatplotlibCanvas(self)

        # 2. pencere İki buton
        self.save_csv = QPushButton("Write .CSV")
        self.save_csv.clicked.connect(self.save_as_csv)

        self.save_png = QPushButton("Save as .PNG")
        self.save_png.clicked.connect(self.save_graphs)

        # 2. pencere layout'u
        layout = QVBoxLayout()
        layout.addWidget(self.acc_graph)
        layout.addWidget(self.pulse_graph)
        layout.addWidget(self.acc_pulse_graph)

        # 2. pencere butonlar için yatay layout
        button_layout = QHBoxLayout()
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        button_layout.addItem(spacer)
        button_layout.addWidget(self.save_csv)
        button_layout.addWidget(self.save_png)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def save_as_csv(self):
        try:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self, "Save CSV File", "", "CSV Files (*.csv)", options=options)

            if file_name:
                # Sample data for CSV, replace with actual computations
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
                QMessageBox.information(self, "Success", "CSV file saved successfully at: " + file_name)

        except Exception as e:
            QMessageBox.critical(self, "Error", "Error occurred while saving CSV: " + str(e))

    def save_graphs(self):
        try:
            folder_path = QFileDialog.getExistingDirectory(self, "Select Folder", "")

            if folder_path:
                self.acc_graph.fig.savefig(f"{folder_path}/Acc.png", bbox_inches='tight', dpi=300)
                self.pulse_graph.fig.savefig(f"{folder_path}/Pulse.png", bbox_inches='tight', dpi=300)
                self.acc_pulse_graph.fig.savefig(f"{folder_path}/Acc-Pulse.png", bbox_inches='tight', dpi=300)
                QMessageBox.information(self, "Success", "Graphs saved in: " + folder_path)

        except Exception as e:
            QMessageBox.critical(self, "Error", "Error occurred while saving graphs: " + str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
