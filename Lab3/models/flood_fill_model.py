import cv2
import numpy as np



class FloodFillModel:
    def __init__(self) -> None:
        self.low_threshold = 0
        self.high_treshold = 10

        self.fill_color = [255, 0, 0]
        self.image = None
        self.target_color = None


    # TODO
    def fill(self, image, x, y):
        """
        Algorithme de Flood Fill avec seuils - VERSION ITÉRATIVE
        Remplit une région de pixels dont la couleur est proche de la couleur de départ
        Utilise une pile au lieu de la récursion pour éviter les stack overflow

        Args:
            image: l'image à remplir
            x: coordonnée x du point de départ
            y: coordonnée y du point de départ

        Returns:
            np.ndarray: Image avec la région remplie
        """
        self.image = image.copy()

        # Vérifier les limites
        if x < 0 or x >= self.image.shape[1] or y < 0 or y >= self.image.shape[0]:
            return self.image

        # Sauvegarder la couleur cible (couleur du pixel de départ)
        self.target_color = self.image[y, x].astype(np.float32)

        # Pile pour stocker les pixels à traiter
        stack = [(x, y)]

        # Traiter tant qu'il y a des pixels dans la pile
        while stack:
            current_x, current_y = stack.pop()

            # Vérifier les limites
            if current_x < 0 or current_x >= self.image.shape[1] or current_y < 0 or current_y >= self.image.shape[0]:
                continue

            # Récupérer la couleur du pixel actuel
            current_color = self.image[current_y, current_x].astype(np.float32)

            # Vérifier si le pixel est déjà de la couleur de remplissage
            if np.allclose(current_color, self.fill_color, atol=1):
                continue

            # Calculer la différence entre la couleur actuelle et la couleur cible
            # On utilise la différence maximale sur les 3 canaux RGB
            diff = np.max(np.abs(current_color - self.target_color))

            # FloodFill avec seuils :
            # - low_threshold : borne inférieure de différence (généralement 0)
            # - high_threshold : borne supérieure de différence (tolérance maximale)
            # Un pixel est rempli si : low_threshold <= diff <= high_threshold

            # Typiquement, low_threshold = 0 (on remplit même les pixels identiques)
            # et high_threshold définit la tolérance (ex: 50 = accepte jusqu'à 50 de différence)

            if diff > self.high_treshold:
                continue

            # Remplir le pixel actuel
            self.image[current_y, current_x] = self.fill_color

            # Ajouter les 4 voisins à la pile (4-connexité)
            stack.append((current_x + 1, current_y))  # droite
            stack.append((current_x - 1, current_y))  # gauche
            stack.append((current_x, current_y + 1))  # bas
            stack.append((current_x, current_y - 1))  # haut

        return self.image

    
    # TODO
    # Hint: Vous pouvez utiliser la fonction d'OpenCV
    def fill_temp(self, image, x, y):
        """Version alternative utilisant OpenCV (pour comparaison/debug)"""
        img_copy = image.copy()
        h, w = img_copy.shape[:2]
        mask = np.zeros((h + 2, w + 2), np.uint8)

        # Utiliser cv2.floodFill avec les seuils
        lo = self.low_threshold
        hi = self.high_treshold

        cv2.floodFill(img_copy, mask, (x, y), self.fill_color,
                      loDiff=(lo, lo, lo), upDiff=(hi, hi, hi))

        return img_copy


    def set_fill_color(self, color):
        self.fill_color = color


    def set_low_threshold(self, val):
        self.low_threshold = val
        print(f"New low threshold = {val}")


    def set_high_threshold(self, val):
        self.high_treshold = val
        print(f"New high threshold = {val}")
