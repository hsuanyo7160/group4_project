import pygame
import sys
from player import Player
from const import *

class Screen:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.all_sprites = pygame.sprite.Group()
    def addPlayer(self, p1, p2):
        self.player1 = p1
        self.player2 = p2
        self.all_sprites.add(self.player1)
        self.all_sprites.add(self.player2)
    # 顯示 "遊戲結束" 畫面
    def show_game_over(self, winner):
        # First text (game over message)
        font = pygame.font.SysFont('Arial', 60)
        text = font.render(f"Game Over!  {winner} Wins!", True, RED)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))  # Center the text
        self.screen.blit(text, text_rect)

        # Second text (tip message)
        font = pygame.font.SysFont('Arial', 20)
        tip = font.render("Press 'R' to restart , Q to leave", True, WHITE)
        tip_rect = tip.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))  # Center the tip text
        self.screen.blit(tip, tip_rect)
        
    def draw_health_energy_bar(self):
        # 玩家1的血量條
        pygame.draw.rect(self.screen, RED, (20, 20, self.player1.displayed_health * 2, 20))  # 使用顯示的血量
        pygame.draw.rect(self.screen, WHITE, (20, 20, 200, 20), 2)  # 邊框
        
        # 玩家1的能量條
        pygame.draw.rect(self.screen, YELLOW, (20, 50, self.player1.displayed_energy * 2, 10))  # 使用顯示的能量
        pygame.draw.rect(self.screen, WHITE, (20, 50, 200, 10), 2)

        # 玩家2的血量條
        pygame.draw.rect(self.screen, BLUE, (WIDTH - 220, 20, self.player2.displayed_health * 2, 20))
        pygame.draw.rect(self.screen, WHITE, (WIDTH - 220, 20, 200, 20), 2)

        # 玩家2的能量條
        pygame.draw.rect(self.screen, YELLOW, (WIDTH - 220, 50, self.player2.displayed_energy * 2, 10))
        pygame.draw.rect(self.screen, WHITE, (WIDTH - 220, 50, 200, 10), 2)

    def show_main_menu(self):
        font = pygame.font.SysFont('Arial', 40)
        title = font.render('2D Battle Game', True, WHITE)
        start_button = font.render('Start Game', True, WHITE)
        quit_button = font.render('Quit', True, WHITE)
        
        # 載入背景圖像
        menu_image = pygame.image.load('images/background/b2.png')
        menu_image = pygame.transform.scale(menu_image, (WIDTH, HEIGHT))
        self.screen.blit(menu_image, (0, 0))
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3))
        self.screen.blit(start_button, (WIDTH // 2 - start_button.get_width() // 2, HEIGHT // 2))
        self.screen.blit(quit_button, (WIDTH // 2 - quit_button.get_width() // 2, HEIGHT // 2 + 60))
        
        pygame.display.update()   
    def choose_map(self):
        """Function to display the map selection screen with mouse-based selection and preview."""
        running = True
        # Load background image
        mapbackground = pygame.image.load('images/background/map.png')
        mapbackground = pygame.transform.scale(mapbackground, (WIDTH, HEIGHT))

        font = pygame.font.SysFont('Arial', 32)
        title_text = font.render('Choose Your Map:', True, WHITE)

        # Load preview images for map selection
        preview_b1 = pygame.image.load('images/background/b1.jpg')
        preview_b2 = pygame.image.load('images/background/b2.png')
        preview_b3 = pygame.image.load('images/background/b3.png')

        # Original sizes for previews
        original_size = (400, 200)

        # Set up positions for options and preview images
        option1_rect = pygame.Rect(WIDTH // 2 - 450, (HEIGHT // 2) - 200, *original_size)
        option2_rect = pygame.Rect(WIDTH // 2 + 50, HEIGHT // 2 - 200, *original_size)
        option3_rect = pygame.Rect(WIDTH // 2 - 450, (HEIGHT // 2) + 50, *original_size)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Get the mouse position
            mouse_x, mouse_y = pygame.mouse.get_pos()

            # Check if mouse is hovering over the preview images and zoom in if so
            # Scaling factor for zoom effect (1.0 is original size, 1.2 is 20% zoomed in)
            zoom_factor1 = 1.0
            zoom_factor2 = 1.0
            zoom_factor3 = 1.0
            if option1_rect.collidepoint(mouse_x, mouse_y):
                zoom_factor1 = 1.1
            elif option2_rect.collidepoint(mouse_x, mouse_y):
                zoom_factor2 = 1.1
            elif option3_rect.collidepoint(mouse_x, mouse_y):
                zoom_factor3 = 1.1

            # Scale the preview images based on the zoom factor
            scaled_b1 = pygame.transform.scale(preview_b1, (int(original_size[0] * zoom_factor1), int(original_size[1] * zoom_factor1)))
            scaled_b2 = pygame.transform.scale(preview_b2, (int(original_size[0] * zoom_factor2), int(original_size[1] * zoom_factor2)))
            scaled_b3 = pygame.transform.scale(preview_b3, (int(original_size[0] * zoom_factor3), int(original_size[1] * zoom_factor3)))

            # Blit the background image
            self.screen.blit(mapbackground, (0, 0))
            
            # Draw the title
            self.screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT - 580))
            
            # Draw the preview images (zoomed in or normal size)
            self.screen.blit(scaled_b1, (WIDTH // 2 - 450, HEIGHT // 2 - 200))  # Show preview for b1
            self.screen.blit(scaled_b2, (WIDTH // 2 + 50, HEIGHT // 2 - 200))      # Show preview for b2
            self.screen.blit(scaled_b3, (WIDTH // 2 - 450, HEIGHT // 2 + 50))  # Show preview for b3

            # Check if mouse click is inside any of the option areas
            if pygame.mouse.get_pressed()[0]:  # Left mouse button
                if option1_rect.collidepoint(mouse_x, mouse_y):
                    return 'b1.jpg'
                elif option2_rect.collidepoint(mouse_x, mouse_y):
                    return 'b2.png'
                elif option3_rect.collidepoint(mouse_x, mouse_y):
                    return 'b3.png'

            pygame.display.update()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()
    
    def choose_character(self):
        """Function to display the character selection screen with mouse-based selection and preview."""
        running = True
        # Load background image
        characterbackground = pygame.image.load('images/background/map.png')
        characterbackground = pygame.transform.scale(characterbackground, (WIDTH, HEIGHT))

        font = pygame.font.SysFont('Arial', 32)
        title_text = font.render('Choose Your Character:', True, WHITE)

        # Load preview images for character selection
        preview_p1 = pygame.image.load('images/character/Archer/Idle.png')
        preview_p2 = pygame.image.load('images/character/Samurai/Idle.png')
        

        # Original sizes for previews
        original_size = (200, 200)

        # Set up positions for options and preview images
        option1_rect = pygame.Rect(WIDTH // 2 - 250, (HEIGHT // 2) - 100, *original_size)
        option2_rect = pygame.Rect(WIDTH // 2 + 50, HEIGHT // 2 - 100, *original_size)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Get the mouse position
            mouse_x, mouse_y = pygame.mouse.get_pos()

            # Check if mouse is hovering over the preview images and zoom in if so
            # Scaling factor for zoom effect (1.0 is original size, 1.2 is 20% zoomed in)
            zoom_factor1 = 1.0
            zoom_factor2 = 1.0
            if option1_rect.collidepoint(mouse_x, mouse_y):
                zoom_factor1 = 1.1
            elif option2_rect.collidepoint(mouse_x, mouse_y):
                zoom_factor2 = 1.1

            # Scale the preview images based on the zoom factor
            scaled_p1 = pygame.transform.scale(preview_p1, (int(original_size[0] * zoom_factor1), int(original_size[1] * zoom_factor1)))
            scaled_p2 = pygame.transform.scale(preview_p2, (int(original_size[0] * zoom_factor2), int(original_size[1] * zoom_factor2)))

            # Blit the background image
            self.screen.blit(characterbackground, (0, 0))
            
            # Draw the title
            self.screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT - 580))
            
            # Draw the preview images (zoomed in or normal size)
            self.screen.blit(scaled_p1, (WIDTH // 2 - 450, HEIGHT // 2 - 200))  
            self.screen.blit(scaled_p2, (WIDTH // 2 + 50, HEIGHT // 2 - 200))
            
            # Check if mouse click is inside any of the option areas
            if pygame.mouse.get_pressed()[0]:
                if option1_rect.collidepoint(mouse_x, mouse_y):
                    return 'Archer'
                elif option2_rect.collidepoint(mouse_x, mouse_y):
                    return 'Samurai'

            pygame.display.update()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()