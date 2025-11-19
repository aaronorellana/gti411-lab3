import numpy as np
import cv2
import matplotlib.pyplot as plt



boundary_color = np.array([255, 0, 0])
# boundary_color = [0, 0, 0]
fill_color = np.array([0, 255, 255])

image = cv2.imread("images/test.png")
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)



# TODO: IMPLEMENTER CETTE FONCTION
def boundary_fill(x, y):
    """
    Algorithme de Boundary Fill (4-connexité) - VERSION ITÉRATIVE
    Remplit une région en s'arrêtant aux pixels de couleur boundary_color
    Utilise une pile au lieu de la récursion pour éviter les stack overflow

    Args:
        x: coordonnée x du point de départ
        y: coordonnée y du point de départ
    """
    # Vérifier les limites initiales
    if x < 0 or x >= image.shape[1] or y < 0 or y >= image.shape[0]:
        return

    # Pile pour stocker les pixels à traiter
    stack = [(x, y)]

    # Traiter tant qu'il y a des pixels dans la pile
    while stack:
        current_x, current_y = stack.pop()

        # Vérifier les limites
        if current_x < 0 or current_x >= image.shape[1] or current_y < 0 or current_y >= image.shape[0]:
            continue

        # Récupérer la couleur du pixel actuel
        current_color = image[current_y, current_x]

        # Si le pixel est déjà de la couleur de remplissage, continuer
        if np.array_equal(current_color, fill_color):
            continue

        # Si le pixel est de la couleur de bordure, continuer
        if np.array_equal(current_color, boundary_color):
            continue

        # Remplir le pixel actuel
        image[current_y, current_x] = fill_color

        # Ajouter les 4 voisins à la pile (4-connexité)
        stack.append((current_x + 1, current_y))  # droite
        stack.append((current_x - 1, current_y))  # gauche
        stack.append((current_x, current_y + 1))  # bas
        stack.append((current_x, current_y - 1))  # haut


def main():
    plt.subplot(1, 2, 1)
    plt.title("Forme initiale")
    plt.imshow(image)
    boundary_fill(15, 15)
    # boundary_fill(559, 258)
    plt.subplot(1, 2, 2)
    plt.title("Résultat attendu")
    plt.imshow(image)
    plt.show()
    



if __name__ == "__main__":
    main()