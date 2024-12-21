import pygame
class Spritesheet:
    def __init__(self, filename, num_sprites):
        self.sheet = pygame.image.load(filename).convert_alpha()
        self.num_sprites = num_sprites

    def get_image(self, frame, colorkey=None):
        # Calculate the width of a single sprite
        sprite_width = self.sheet.get_width() // self.num_sprites
        sprite_height = self.sheet.get_height()

        # Create a new surface for the sprite
        image = pygame.Surface((sprite_width, sprite_height), pygame.SRCALPHA)  # Use SRCALPHA for transparency

        # Extract the sprite from the sprite sheet
        rect = (sprite_width * frame, 0, sprite_width, sprite_height)
        image.blit(self.sheet, (0, 0), rect)

        # Apply the colorkey for transparency (if provided)
        if colorkey is not None:
            image.set_colorkey(colorkey)
        return image
