import cv2
import numpy as np

class FloodFillModel:
    def __init__(self) -> None:
        self.low_threshold = 0
        self.high_treshold = 10

        self.fill_color = [255, 0, 0]


    # TODO
    def fill(self, image, x, y):
        return image

    
    # TODO
    # Hint: Vous pouvez utiliser la fonction d'OpenCV
    def fill_temp(self, image, x, y):
        return image


    def set_fill_color(self, color):
        self.fill_color = color


    def set_low_threshold(self, val):
        self.low_threshold = val
        print(f"New low threshold = {val}")


    def set_high_threshold(self, val):
        self.high_treshold = val
        print(f"New high threshold = {val}")
