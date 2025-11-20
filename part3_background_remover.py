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
        self.replacement_image = None

        # Essayer de charger une image de remplacement
        try:
            self.replacement_image = cv2.imread("images/stm.jpg")
            if self.replacement_image is not None:
                self.replacement_image = cv2.cvtColor(self.replacement_image, cv2.COLOR_BGR2RGB)
        except:
            pass

    
    def set_modify_effect(self, mode:str):
        self.modify_effect = mode


    def set_background_image(self, bg_image):
        self.background_image = bg_image

    
    def remove_background(self, image:np.ndarray) -> np.ndarray:
        """Enlève le fond de l'image en utilisant la soustraction de fond

        Args:
            image (np.ndarray): Image RGB (h, w, 3)

        Returns:
            np.ndarray: Image avec le fond modifié
        """

        # Si on n'a pas encore capturé le fond, on retourne l'image telle quelle
        if self.background_image is None:
            return image

        # Étape 1: Calculer la différence entre l'image actuelle et le fond
        diff = cv2.absdiff(image, self.background_image)

        # Convertir en niveaux de gris
        gray_diff = cv2.cvtColor(diff, cv2.COLOR_RGB2GRAY)

        # Créer un masque binaire (blanc = personne, noir = fond)
        # Méthode 1: Seuillage adaptatif pour gérer les variations d'éclairage
        mask_adaptive = cv2.adaptiveThreshold(
            gray_diff, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, -5
        )

        # Méthode 2: Seuillage classique
        _, mask_global = cv2.threshold(gray_diff, 30, 255, cv2.THRESH_BINARY)

        # Combiner les deux masques
        mask = cv2.bitwise_or(mask_adaptive, mask_global)

        # Étape 2: Nettoyer le masque pour enlever le bruit

        # Filtre médian pour enlever les pixels isolés
        mask = cv2.medianBlur(mask, 5)

        # Morphologie pour nettoyer progressivement
        kernel_tiny = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_tiny)

        kernel_small = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        mask = cv2.erode(mask, kernel_small, iterations=2)

        kernel_medium = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.dilate(mask, kernel_medium, iterations=3)

        kernel_large = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_large, iterations=1)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel_large, iterations=2)

        # Garder seulement le plus grand contour (normalement la personne)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) > 0:
            largest_contour = max(contours, key=cv2.contourArea)
            mask_clean = np.zeros_like(mask)
            cv2.drawContours(mask_clean, [largest_contour], -1, 255, -1)

            if cv2.contourArea(largest_contour) > 5000:
                mask = mask_clean

        # Adoucir les contours
        mask = cv2.GaussianBlur(mask, (7, 7), 0)

        # Créer un gradient pour des transitions plus douces
        mask_dilated = cv2.dilate(mask, kernel_medium, iterations=2)
        mask_gradient = cv2.GaussianBlur(mask_dilated, (15, 15), 0)
        mask_final = cv2.addWeighted(mask, 0.7, mask_gradient, 0.3, 0)

        # Convertir le masque en 3 canaux pour le combiner avec l'image
        mask_float = mask_final.astype(np.float32) / 255.0
        mask_3channel = np.stack([mask_float] * 3, axis=-1)

        # Étape 3: Appliquer l'effet choisi
        if self.modify_effect == "blur":
            # Flouter le fond
            blurred_image = cv2.GaussianBlur(image, (45, 45), 0)
            blurred_image = cv2.GaussianBlur(blurred_image, (25, 25), 0)

            # Combiner: personne nette + fond flouté
            new_image = (image * mask_3channel + blurred_image * (1 - mask_3channel)).astype(np.uint8)

        elif self.modify_effect == "replace":
            # Remplacer le fond par une autre image
            if self.replacement_image is not None:
                replacement_resized = cv2.resize(self.replacement_image,
                                                (image.shape[1], image.shape[0]))
            else:
                replacement_resized = self.background_image

            # Combiner: personne + nouveau fond
            new_image = (image * mask_3channel + replacement_resized * (1 - mask_3channel)).astype(np.uint8)

        else:
            new_image = image

        return new_image





class WebcamApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GTI411 - Laboratoire 3 - Partie 3")
        self.setGeometry(100, 100, 640, 480)

        # Nombre d'images par seconde (réduire si l'ordinateur est lent)
        frames_per_second = 30

        # Ouvrir la webcam
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open webcam.")
            sys.exit()

        # Créer l'interface
        self.init_ui()

        # Timer pour rafraîchir les images
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(round(1/frames_per_second * 1000))

        # Créer l'objet qui enlève le fond
        self.bg_remover = BackgroundRemover()


    def init_ui(self):
        # Zone d'affichage de la vidéo
        self.image_label = QLabel("Starting webcam...")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFrameShape(QFrame.Box)
        self.image_label.setFixedHeight(360)

        # Boutons
        self.save_backgroud_image_btn = QPushButton("Save background image")
        self.blur_background_btn = QPushButton("Blur background")
        self.replace_background_btn = QPushButton("Replace background")

        # Disposition des boutons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_backgroud_image_btn)
        btn_layout.addWidget(self.blur_background_btn)
        btn_layout.addWidget(self.replace_background_btn)
        btn_layout.addStretch()

        # Disposition principale
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.image_label)
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

        # Connecter les boutons aux fonctions
        self.save_backgroud_image_btn.clicked.connect(self.update_bg_image)
        self.blur_background_btn.clicked.connect(lambda : self.bg_remover.set_modify_effect("blur"))
        self.replace_background_btn.clicked.connect(lambda : self.bg_remover.set_modify_effect("replace"))


    def update_bg_image(self):
        """Capture l'image de fond (sans personne)"""
        ret, frame = self.cap.read()
        if not ret:
            return

        # Convertir BGR (OpenCV) en RGB (Qt)
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.bg_remover.set_background_image(rgb_image)


    def update_frame(self):
        """Capture et affiche une image de la webcam"""
        ret, frame = self.cap.read()
        if not ret:
            return

        # Convertir BGR (OpenCV) en RGB (Qt)
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Enlever le fond
        result_image = self.bg_remover.remove_background(rgb_image)

        # Convertir pour Qt
        h, w, ch = result_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(result_image.data, w, h, bytes_per_line, QImage.Format_RGB888)

        # Afficher l'image
        self.image_label.setPixmap(QPixmap.fromImage(qt_image).scaled(
            self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio))


    def closeEvent(self, event):
        """Libérer la webcam quand on ferme la fenêtre"""
        if self.cap.isOpened():
            self.cap.release()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WebcamApp()
    window.show()
    sys.exit(app.exec_())
