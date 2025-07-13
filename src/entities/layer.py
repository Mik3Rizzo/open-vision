import pygame
from enums.layer_type import LayerType

# TODO separate enum
# TODO extract from config width and similar parameters
# TODO add a draw method

class Layer:
    RED_COLOR = (255, 0, 0)
    BLUE_COLOR = (0, 0, 255)
    
    def __init__(self, config, layer_type: LayerType, width: int, height: int, square_size: int, disparity: int):
        self.layer_type = layer_type
        self.width = width  
        self.height = height
        self.square_size = square_size
        self.disparity = disparity
        self.surface = None
        
    def create_surface(self, noise_matrix, square_rel_x: int, square_rel_y: int):
        """Creates the layer surface with noise and square based on layer type"""
        self.surface = pygame.Surface((self.width, self.height))
        
        for y in range(self.height):
            for x in range(self.width):
                val = noise_matrix[y][x]
                
                # Calculate square position based on layer type
                adjusted_square_rel_x = square_rel_x
                if self.layer_type == LayerType.BLUE:
                    # The square in the blue layer is shifted by disparity
                    adjusted_square_rel_x += self.disparity
                
                # Check if current pixel is inside the square
                xy_is_inside_square = (
                    adjusted_square_rel_x <= x < adjusted_square_rel_x + self.square_size and
                    square_rel_y <= y < square_rel_y + self.square_size
                )
                
                # Handle blue layer special case for disparity
                if xy_is_inside_square and self.layer_type == LayerType.BLUE:
                    # Note:
                    # - the square is just a portion of the noise matrix
                    # - in the red layer, the square starts from square_rel_x
                    # - in the blue layer, the square is translated to square_rel_x + disparity, to recreate 3D effect
                    # - in the blue layer, the pixels between square_rel_x and square_rel_x + disparity are copied from 
                    #   the red layer, so they are equal to the first disparity pixels of the square itself
                    # - the pixels between square_rel_x + square_size and square_rel_x + square_size + disparity of the 
                    #   red layer are overridden by the square in the blue layer

                    # Shift the square to the right by the disparity
                    original_x = x - self.disparity
                    if 0 <= original_x < self.width:
                        val = noise_matrix[y][original_x]
                
                # Set pixel color based on layer type
                if self.layer_type == LayerType.RED:
                    self.surface.set_at((x, y), (val, 0, 0))
                elif self.layer_type == LayerType.BLUE:
                    self.surface.set_at((x, y), (0, 0, val))
        
        return self.surface
    
    def get_color(self):
        """Returns the base color for this layer type"""
        return self.RED_COLOR if self.layer_type == LayerType.RED else self.BLUE_COLOR
    
    def is_red(self):
        """Returns True if this is a red layer"""
        return self.layer_type == LayerType.RED
    
    def is_blue(self):
        """Returns True if this is a blue layer"""
        return self.layer_type == LayerType.BLUE





