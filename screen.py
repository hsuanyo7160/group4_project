import pygame
import sys
from player import scale_image
from const import *
from ch import character
from pygame import Color

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
        font_path = "font/Modak-Regular.ttf"  # 替換為你的字體路徑
        font = pygame.font.Font(font_path, 48)
        text = font.render(f"Game Over!  {winner} Wins!", True, RED)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))  # Center the text
        self.screen.blit(text, text_rect)

        # Second text (tip message)
        font = pygame.font.SysFont('Arial', 20)
        tip = font.render("Press 'R' to restart , Q to leave", True, WHITE)
        tip_rect = tip.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))  # Center the tip text
        self.screen.blit(tip, tip_rect)
    
    def draw_gradient_bar(self, screen, start_color, end_color, rect):
        for i in range(rect.width):
            # 計算漸層顏色
            ratio = i / rect.width
            color = Color(
                int(start_color.r * (1 - ratio) + end_color.r * ratio),
                int(start_color.g * (1 - ratio) + end_color.g * ratio),
                int(start_color.b * (1 - ratio) + end_color.b * ratio)
            )
            pygame.draw.line(screen, color, (rect.x + i, rect.y), (rect.x + i, rect.y + rect.height))

        
    def draw_health_energy_bar(self):
        # 玩家1的血量條 - 漸層從亮紅到深紅
        self.draw_gradient_bar(self.screen, Color(255, 0, 0), Color(139, 0, 0), pygame.Rect(20, 20, self.player1.displayed_health * 2, 18))
        pygame.draw.rect(self.screen, WHITE, (20, 20, 400, 20), 2)  # 邊框

        # 玩家1的能量條 - 漸層從亮黃到橙色
        self.draw_gradient_bar(self.screen, Color(255, 255, 0), Color(255, 140, 0), pygame.Rect(20, 50, self.player1.displayed_energy * 3, 8))
        pygame.draw.rect(self.screen, WHITE, (20, 50, 300, 10), 2)  # 邊框

        # 玩家2的血量條
        self.draw_gradient_bar(self.screen, Color(0, 0, 255), Color(0, 0, 139), pygame.Rect(WIDTH - 20 - self.player2.displayed_health * 2, 20, self.player2.displayed_health * 2, 18))
        pygame.draw.rect(self.screen, WHITE, (WIDTH - 420, 20, 400, 20), 2)

        # 玩家2的能量條
        self.draw_gradient_bar(self.screen, Color(255, 255, 0), Color(255, 140, 0), pygame.Rect(WIDTH - 20 - self.player2.displayed_energy * 3, 50, self.player2.displayed_energy * 3, 8))
        pygame.draw.rect(self.screen, WHITE, (WIDTH - 320, 50, 300, 10), 2)

    def show_main_menu(self):
        # 加載字體
        font_path = "font/Modak-Regular.ttf"  # 替換為你的字體路徑
        font_108 = pygame.font.Font(font_path, 108)  # 字體大小
        font_52 = pygame.font.Font(font_path, 52) 
        font_48 = pygame.font.Font(font_path, 48) 
        
        # 載入背景圖像
        menu_image = pygame.image.load('images/background/b2.png')
        menu_image = pygame.transform.scale(menu_image, (WIDTH, HEIGHT))
        
        running = True

        while (running):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            # 加載文字
            title = font_108.render('2D Battle Game', True, BLACK)
            start_button = font_48.render('Start Game', True, WHITE)
            quit_button = font_48.render('Quit', True, WHITE)

            mouse_x, mouse_y = pygame.mouse.get_pos()
            if HEIGHT // 2 <= mouse_y <= HEIGHT // 2 + 40 and WIDTH // 2 - 150 <= mouse_x <= WIDTH // 2 + 150:
                start_button = font_52.render('Start Game', True, RED)
                if pygame.mouse.get_pressed()[0]:
                    return True

            if HEIGHT // 2 + 60 <= mouse_y <= HEIGHT // 2 + 100 and WIDTH // 2 - 100 <= mouse_x <= WIDTH // 2 + 100:
                quit_button = font_52.render('Quit', True, RED)
                if pygame.mouse.get_pressed()[0]:
                    pygame.quit()
                    sys.exit()
                    return False

            self.screen.blit(menu_image, (0, 0))
            self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 200))
            self.screen.blit(start_button, (WIDTH // 2 - start_button.get_width() // 2, HEIGHT // 2))
            self.screen.blit(quit_button, (WIDTH // 2 - quit_button.get_width() // 2, HEIGHT // 2 + 60))
        
            pygame.display.update()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()
        
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
        """Function to display the character selection screen for both Player 1 and Player 2."""
        running = True
        # 載入背景圖像
        characterbackground = pygame.image.load('images/background/map.png')
        characterbackground = pygame.transform.scale(characterbackground, (WIDTH, HEIGHT))

        font = pygame.font.SysFont('Arial', 32)
        title_text = font.render('Choose Your Character:', True, WHITE)
        player_texts = [
            font.render('Player 1, Choose Your Character:', True, WHITE),
            font.render('Player 2, Choose Your Character:', True, WHITE)
        ]

        # 載入角色圖像
        previews = []
        for i in range(len(character.character_data)):
            preview = pygame.image.load(character.character_data[i]['icon'])
            preview = scale_image(preview, 200)
            previews.append(preview)

        # 設定圖像原始大小和預覽區域位置
        original_size = (150, 200)
        option_rects = [pygame.Rect(WIDTH // 2 - 450 + 400 * i, HEIGHT // 2 - 100, *original_size) for i in range(len(character.character_data))]

        selected_characters = [None, None]  # 用來儲存兩位玩家的選擇
        player_index = 0  # 用來追蹤目前是為哪位玩家選擇角色 (0 表示玩家 1，1 表示玩家 2)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # 獲取滑鼠位置
            mouse_x, mouse_y = pygame.mouse.get_pos()

            # 檢查滑鼠是否在預覽區域上方，以進行縮放效果
            zoom_factors = [1.0] * len(character.character_data)
            for i, option_rect in enumerate(option_rects):
                if option_rect.collidepoint(mouse_x, mouse_y):
                    zoom_factors[i] = 1.1  # 放大 10%

            # 縮放圖像並顯示在螢幕上
            self.screen.blit(characterbackground, (0, 0))
            self.screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT - 500))
            # 顯示當前玩家選擇的提示文字
            self.screen.blit(player_texts[player_index], (WIDTH // 2 - player_texts[player_index].get_width() // 2, HEIGHT - 550))
            
            for i, preview in enumerate(previews):
                scaled_preview = pygame.transform.scale(preview, (int(original_size[0] * zoom_factors[i]), int(original_size[1] * zoom_factors[i])))
                preview_x = option_rects[i].x - (scaled_preview.get_width() - original_size[0]) // 2
                preview_y = option_rects[i].y - (scaled_preview.get_height() - original_size[1]) // 2
                self.screen.blit(scaled_preview, (preview_x, preview_y))

            # 檢查滑鼠點擊事件
            if pygame.mouse.get_pressed()[0]:  # 左鍵點擊
                for i, option_rect in enumerate(option_rects):
                    if option_rect.collidepoint(mouse_x, mouse_y):
                        selected_characters[player_index] = i  # 為當前玩家儲存選擇的角色索引
                        player_index += 1  # 切換到下一位玩家
                        pygame.time.wait(100)  # 等待片刻以避免重複點擊
                        break

            # 如果兩位玩家都選擇完成，結束選擇並返回結果
            if player_index >= 2:
                return selected_characters  # 返回一個包含玩家 1 和玩家 2 選擇角色索引的列表

            pygame.display.update()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

