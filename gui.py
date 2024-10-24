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
        # Grafik stilini ayarla
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

    def browse_files(self):
        try:
            # Dosya seçme window
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Text Files (*.txt)",
                                                       options=options)
            if file_name:
                print("Selected file:", file_name)
                self.main_plot()

        except Exception as e:
            QMessageBox.critical(self, "Error", "Hata oluştu: " + str(e))


    def main_plot(self):
        # main pencere grafik işlemleri
        pass

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

    def second_plot(self):
        # ikinci pencere grafik işlemleri
        pass

    def save_graphs(self):
        try:
            folder_path = QFileDialog.getExistingDirectory(self, "Klasör Seçin", "")

            if folder_path:
                self.acc_graph.fig.savefig(f"{folder_path}/Acc.png", bbox_inches='tight', dpi=300)
                self.pulse_graph.fig.savefig(f"{folder_path}/Pulse.png", bbox_inches='tight', dpi=300)
                self.acc_pulse_graph.fig.savefig(f"{folder_path}/Acc-Pulse.png", bbox_inches='tight', dpi=300)
                QMessageBox.information(self, "Success", "Grafikler kaydedildi: " + folder_path)

            else:
                print("Klasör seçilmedi.")

        except Exception as e:
            QMessageBox.critical(self, "Error", "Hata oluştu: " + str(e))

    def save_as_csv(self):
        try:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Excel Files (*.xlsx)", options=options)

            if file_name:
                # x ve y parametrelerini al
                # Örnek veri ile test
                x_data1 = np.linspace(0, 10, 100)
                y_data1 = np.sin(x_data1)

                x_data2 = np.linspace(0, 10, 100)
                y_data2 = np.cos(x_data2)

                x_data3 = np.linspace(0, 10, 100)
                y_data3 = np.tan(x_data3)

                df1 = pd.DataFrame({'X': x_data1, 'Y': y_data1})
                df2 = pd.DataFrame({'X': x_data2, 'Y': y_data2})
                df3 = pd.DataFrame({'X': x_data3, 'Y': y_data3})

                with pd.ExcelWriter(file_name) as writer:
                    df1.to_excel(writer, sheet_name='Graph1', index=False)
                    df2.to_excel(writer, sheet_name='Graph2', index=False)
                    df3.to_excel(writer, sheet_name='Graph3', index=False)

                QMessageBox.information(self, "Success", "Excel dosyası kaydedildi: " + file_name)

        except Exception as e:
            QMessageBox.critical(self, "Error", "Hata oluştu: " + str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
