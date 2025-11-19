import sys
import cv2
import numpy as np
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFrame
)


class BackgroundRemover:
    def __init__(self):
        self.background_image = None
        self.modify_effect = "blur"

    
    def set_modify_effect(self, mode:str):
        self.modify_effect = mode


    def set_background_image(self, bg_image):
        self.background_image = bg_image

    
    def remove_background(self, image:np.ndarray) -> np.ndarray:
        """Remove the background from an RGB image

        Args:
            image (np.ndarray): (h, w, 3) image

        Returns:
            np.ndarray: (h, w, 3) image with removed background
        """

        if self.background_image is None:
            return image

        if self.modify_effect == "blur":
            new_image = ...
            # TODO Implement blur logic here

        elif self.modify_effect == "replace":
            # TODO Replace the background with an image
            new_image = ...


        return image





class WebcamApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GTI411 - Laboratoire 3 - Partie 3")
        self.setGeometry(100, 100, 640, 480)

        # CHANGER CE PARAMETRE SI VOTRE ORDINATEUR N'EST PAS ASSEZ PUISSANT
        frames_per_second = 30

        # Initialize webcam
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open webcam.")
            sys.exit()

        # Create UI
        self.init_ui()

        # Timer for updating frames
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)


        self.timer.start(round(1/frames_per_second * 1000))  

        self.bg_remover = BackgroundRemover()


    def init_ui(self):
        # Webcam feed area
        self.image_label = QLabel("Starting webcam...")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFrameShape(QFrame.Box)
        self.image_label.setFixedHeight(360)

        # Buttons
        self.save_backgroud_image_btn = QPushButton("Save background image")
        self.blur_background_btn = QPushButton("Blur background")
        self.replace_background_btn = QPushButton("Replace background")

        # Button layout
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_backgroud_image_btn)
        btn_layout.addWidget(self.blur_background_btn)
        btn_layout.addWidget(self.replace_background_btn)
        btn_layout.addStretch()

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.image_label)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

        self.save_backgroud_image_btn.clicked.connect(self.update_bg_image)
        self.blur_background_btn.clicked.connect(lambda : self.bg_remover.set_modify_effect("blur"))
        self.replace_background_btn.clicked.connect(lambda : self.bg_remover.set_modify_effect("replace"))



    def update_bg_image(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        # Convert the image from BGR (OpenCV) to RGB (Qt)
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.bg_remover.set_background_image(rgb_image)



    def update_frame(self):
        """Grab a frame from the webcam and display it."""
        ret, frame = self.cap.read()
        if not ret:
            return

        # Convert the image from BGR (OpenCV) to RGB (Qt)
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        result_image = self.bg_remover.remove_background(rgb_image)

        h, w, ch = result_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(result_image.data, w, h, bytes_per_line, QImage.Format_RGB888)

        # Display image
        self.image_label.setPixmap(QPixmap.fromImage(qt_image).scaled(
            self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio))


    def closeEvent(self, event):
        """Release the webcam when closing the window."""
        if self.cap.isOpened():
            self.cap.release()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WebcamApp()
    window.show()
    sys.exit(app.exec_())
