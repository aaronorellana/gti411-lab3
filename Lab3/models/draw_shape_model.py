import numpy as np
import cv2

import sys
sys.setrecursionlimit(100000)


def is_close(vec1, vec2):
    max_diff = np.max(np.abs(vec1 - vec2))
    return max_diff < 50


class DrawShapeModel:
    def __init__(self) -> None:
        w, h = 1250, 490
        self.shape_type = 'Circle'
        self.color = [255, 0, 0]
        self.line_thickness = 3
        self.reset_image(h, w)
        
        self.fill_color = np.array([255, 255, 0])
        self.boundary_color = np.array([255, 0, 0])


    def reset_image(self, h=490, w=1250):
        self.image = np.ones((h, w, 3)) * np.array([255, 255, 255])
        self.image = self.image.astype(np.uint8)
        
    
    def update_shape_type(self, shape_type:str):
        print(f"New shape type {shape_type}")
        self.shape_type = shape_type


    def update_color(self, r, g, b):
        self.color = [r, g, b]



    def bresenham_line(self, x0, y0, x1, y1):
        """Algorithme de Bresenham pour tracer une ligne entre deux points."""
        points = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        x, y = x0, y0

        while True:
            points.append((x, y))

            if x == x1 and y == y1:
                break

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

        return points


    def draw_shape(self, start_point:tuple[int], end_point:tuple[int]):
        """Draw shape at the desired location based on the starting point and end point.

        You can use self.color to get the color selected with the picker
        Implement the logic for 'Line', 'Circle' and 'Rectangle'

        Args:
            start_point (tuple[int]): Coordinates (x,y) of the click point
            end_point (tuple[int]): Coordinates (x,y) of the released point

        Returns:
            np.ndarray: Image with the shape on it
        """
        if start_point is None or end_point is None or len(start_point) == 0 or len(end_point) == 0:
            return
        print(f"Drawing shape {self.shape_type} at p1={start_point} p2={end_point}")

        x0, y0 = start_point
        x1, y1 = end_point

        if self.shape_type == "Line":
            # Ligne avec l'algorithme de Bresenham
            points = self.bresenham_line(x0, y0, x1, y1)
            for x, y in points:
                if 0 <= y < self.image.shape[0] and 0 <= x < self.image.shape[1]:
                    self.image[y, x] = self.color

        elif self.shape_type == "Circle":
            # Cercle : centre=p1, rayon=distance entre p1 et p2
            center = (x0, y0)
            radius = int(np.sqrt((x1 - x0)**2 + (y1 - y0)**2))
            cv2.circle(self.image, center, radius, self.color, self.line_thickness)

        elif self.shape_type == "Rectangle":
            # Rectangle avec Bresenham pour les 4 côtés
            # p1 = coin haut gauche, p2 = coin bas droite
            # Tracer les 4 lignes du rectangle
            # Ligne du haut
            points_top = self.bresenham_line(x0, y0, x1, y0)
            # Ligne du bas
            points_bottom = self.bresenham_line(x0, y1, x1, y1)
            # Ligne gauche
            points_left = self.bresenham_line(x0, y0, x0, y1)
            # Ligne droite
            points_right = self.bresenham_line(x1, y0, x1, y1)

            all_points = points_top + points_bottom + points_left + points_right
            for x, y in all_points:
                if 0 <= y < self.image.shape[0] and 0 <= x < self.image.shape[1]:
                    self.image[y, x] = self.color

        elif self.shape_type == "Ellipse":
            # Ellipse : centre=p1, semi-grand axe jusqu'à p2
            center = (x0, y0)
            # Semi-grand axe = distance entre p1 et p2
            semi_major_axis = int(np.sqrt((x1 - x0)**2 + (y1 - y0)**2))
            # Semi-petit axe = moitié du grand axe
            semi_minor_axis = semi_major_axis // 2

            # Calculer l'angle de rotation basé sur la direction de p1 vers p2
            angle = int(np.degrees(np.arctan2(y1 - y0, x1 - x0)))

            # Dessiner l'ellipse
            cv2.ellipse(self.image, center, (semi_major_axis, semi_minor_axis),
                       angle, 0, 360, self.color, self.line_thickness)

        return self.image