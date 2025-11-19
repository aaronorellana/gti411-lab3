import numpy as np



class BoundaryFillModel:
    def __init__(self) -> None:
        self.fill_color = np.array([255, 0, 0])
        self.boundary_color = np.array([255, 0, 0])
        self.image = None

    

    def boundary_fill(self, image, x, y):
        self.image = image.copy()
        self.fill(x, y)
        return self.image
    
    
    # TODO 
    # A implémenter manuellement
    def fill(self, x, y):
        """
        Algorithme de Boundary Fill (4-connexité) - VERSION ITÉRATIVE
        Remplit une région en s'arrêtant aux pixels de couleur boundary_color
        Utilise une pile au lieu de la récursion pour éviter les stack overflow

        Args:
            x: coordonnée x du point de départ
            y: coordonnée y du point de départ
        """
        # Vérifier les limites initiales
        if x < 0 or x >= self.image.shape[1] or y < 0 or y >= self.image.shape[0]:
            return

        # Pile pour stocker les pixels à traiter
        stack = [(x, y)]

        # Traiter tant qu'il y a des pixels dans la pile
        while stack:
            current_x, current_y = stack.pop()

            # Vérifier les limites
            if current_x < 0 or current_x >= self.image.shape[1] or current_y < 0 or current_y >= self.image.shape[0]:
                continue

            # Récupérer la couleur du pixel actuel
            current_color = self.image[current_y, current_x]

            # Si le pixel est déjà de la couleur de remplissage, continuer
            if np.array_equal(current_color, self.fill_color):
                continue

            # Si le pixel est de la couleur de bordure, continuer
            if np.array_equal(current_color, self.boundary_color):
                continue

            # Remplir le pixel actuel
            self.image[current_y, current_x] = self.fill_color

            # Ajouter les 4 voisins à la pile (4-connexité)
            stack.append((current_x + 1, current_y))  # droite
            stack.append((current_x - 1, current_y))  # gauche
            stack.append((current_x, current_y + 1))  # bas
            stack.append((current_x, current_y - 1))  # haut


    def set_fill_color(self, color):
        self.fill_color = np.array(color)


    def set_boundary_color(self, color):
        self.boundary_color = np.array(color)