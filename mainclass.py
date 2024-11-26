import pygame
import sys
from player import Player
from const import *
from screen import Screen
# 初始化 pygame
pygame.init()

# 設定遊戲畫面
pygame.display.set_caption('2D Battle Game - Player vs Player')
scrn= Screen(WIDTH, HEIGHT)



# 主遊戲迴圈
def main_game():
    running = True
    # choose character
    pygame.time.wait(100)
    playerlist = scrn.choose_character()
    # 選擇地圖
    map_choice = scrn.choose_map()
    # 倒數計時
    countdown_time = 180
    font = pygame.font.SysFont('Arial', 36)
    # 載入背景圖像
    background_image = pygame.image.load(f'images/background/{map_choice}')
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
    
    # 初始化玩家位置
    player1_x, player1_y = 100, HEIGHT - 520
    player2_x, player2_y = WIDTH - 200, HEIGHT - 520

    # 初始化玩家
    player1 = Player(RED, player1_x, player1_y, playerlist[0])
    player2 = Player(BLUE, player2_x, player2_y, playerlist[1])

    player1.other_player = player2
    player2.other_player = player1
    
    scrn.addPlayer(player1, player2)
    
    # 初始化射擊物件群組
    projectiles_group = pygame.sprite.Group()
    player1.projectiles_group = projectiles_group
    player2.projectiles_group = projectiles_group

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        player1.update()
        player2.update()
        projectiles_group.update()
        
        # 更新倒數計時
        countdown_time -= 1 / FPS
        if countdown_time <= 0:
            countdown_time = 0  # Stop the countdown at 0
        minutes = int(countdown_time // 60)
        seconds = int(countdown_time % 60)
        countdown_text = font.render(f'Time: {minutes:02}:{seconds:02}', True, BLACK)

        # Blit background image
        scrn.screen.blit(background_image, (0, 0))
        scrn.all_sprites.draw(scrn.screen)
        projectiles_group.draw(scrn.screen)
        #blit player
        player1.draw(scrn.screen)
        player2.draw(scrn.screen)
        # 顯示玩家血量, 能量條, 倒數計時
        scrn.draw_health_energy_bar()
        scrn.screen.blit(countdown_text, (WIDTH // 2 - countdown_text.get_width() // 2, 20))
        
        ######## draw hitbox ########
        
        mask_surface = player1.mask.to_surface(setcolor=(255, 0, 0), unsetcolor=(0, 0, 0, 0))
        scrn.screen.blit(mask_surface, player1.rect.topleft)
        mask_surface = player2.mask.to_surface(setcolor=(255, 0, 0), unsetcolor=(0, 0, 0, 0))
        scrn.screen.blit(mask_surface, player2.rect.topleft)
        
        # 檢查遊戲結束
        if player1.health <= 0 or player2.health <= 0 or countdown_time <= 0:
            winner = "Player 1" if player2.health < player1.health else "Player 2"
            if(player1.health == player2.health):
                winner = "Tie"
            scrn.show_game_over(winner)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                player1.health = player2.health = 100
                player1.energy = player2.energy = 0
                player1.rect.x = player1_x
                player1.rect.y = HEIGHT - 220
                player2.rect.x = player2_x
                player2.rect.y = HEIGHT - 220
            elif keys[pygame.K_q]:
                running = False
        
        pygame.display.update()
        scrn.clock.tick(FPS)
    pygame.quit()
    sys.exit()

def menu_loop():
    menu_running = True
    while menu_running:
        scrn.show_main_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu_running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                # Start Game
                if HEIGHT // 2 <= mouse_y <= HEIGHT // 2 + 40 and WIDTH // 2 - 150 <= mouse_x <= WIDTH // 2 + 150:
                    menu_running = False
                    main_game()
                # Quit Game
                if HEIGHT // 2 + 60 <= mouse_y <= HEIGHT // 2 + 100 and WIDTH // 2 - 100 <= mouse_x <= WIDTH // 2 + 100:
                    menu_running = False
                    pygame.quit()
                    sys.exit()

menu_loop()