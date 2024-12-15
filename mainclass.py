import pygame
import sys
from player import Player, Background
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
    # show menu
    if not scrn.show_main_menu():
        return
    # choose character
    pygame.time.wait(100)
    playerlist = scrn.choose_character()
    # 選擇地圖
    map_choice = scrn.choose_map()
    # 倒數計時
    countdown_time = 185
    font = pygame.font.SysFont('Arial', 36)
    # 載入背景圖像
    background = Background(map_choice)
    
    # 初始化玩家位置
    player1_x, player1_y = 100, HEIGHT - 420
    player2_x, player2_y = WIDTH - 400, HEIGHT - 420

    # 初始化玩家
    player1 = Player(RED, player1_x, player1_y, playerlist[0])
    player2 = Player(BLUE, player2_x, player2_y, playerlist[1])

    # 設定玩家對手
    player1.setOpponent(player2)
    player2.setOpponent(player1)
    
    # 加入玩家到畫面
    scrn.addPlayer(player1, player2)
    
    # 初始化射擊物件群組
    projectiles_group = pygame.sprite.Group()
    player1.setProjectileGroup(projectiles_group)
    player2.setProjectileGroup(projectiles_group)

    while running:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        if countdown_time > 0 and countdown_time < 180 and player1.health > 0 and player2.health > 0:
            player1.handleinput(keys)
            player2.handleinput(keys)
            player1.update()
            player2.update()
            projectiles_group.update(zoom, camera_pos)
        
        # 更新倒數計時
        if countdown_time > 0 and player1.health > 0 and player2.health > 0:
            countdown_time -= 1 / FPS
        # Stop the countdown at 0
        if countdown_time <= 0:
            countdown_time = 0  
        
        # 設定倒數計時文字
        minutes = int(countdown_time // 60)
        seconds = int(countdown_time % 60)
        countdown_text = font.render(f'Time: {minutes:02}:{seconds:02}', True, BLACK)

        # Blit background image
        background.draw(scrn.screen)
        #scrn.all_sprites.draw(scrn.screen)
        projectiles_group.draw(scrn.screen)
        
        #blit player
        camera_pos = ((player1.pos_x + player2.pos_x)/2, (player1.pos_y + player2.pos_y)/2)
        zoom = player1.draw(scrn.screen, camera_pos)
        zoom = player2.draw(scrn.screen, camera_pos)
        # print(camera_pos, player1.pos_x, player2.pos_x)
        # update background
        background.update(zoom, camera_pos)


        # 顯示玩家血量, 能量條, 倒數計時
        if countdown_time > 180:
            scrn.show_ready_countdown(countdown_time)
        scrn.draw_health_energy_bar()
        scrn.screen.blit(countdown_text, (WIDTH // 2 - countdown_text.get_width() // 2, 20))

        ### print mask hitbox ###
        
        
        # 檢查遊戲結束
        if player1.health <= 0 or player2.health <= 0 or countdown_time <= 0:
            # 顯示遊戲結束畫面
            # winner = "Player 1" if player2.health < player1.health else "Player 2"
            # if(player1.health == player2.health):
            #     winner = "Tie"
            scrn.show_game_over()

            # 重新開始遊戲或離開遊戲
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                # 重置玩家
                player1.kill()
                player2.kill()

                player1 = Player(RED, player1_x, player1_y, playerlist[0])
                player2 = Player(BLUE, player2_x, player2_y, playerlist[1])

                player1.setOpponent(player2)
                player2.setOpponent(player1)
                scrn.addPlayer(player1, player2)
                # 初始化射擊物件群組
                projectiles_group = pygame.sprite.Group()
                player1.setProjectileGroup(projectiles_group)
                player2.setProjectileGroup(projectiles_group)

                # 重置倒計時
                countdown_time = 185
            elif keys[pygame.K_q]:
                running = False
        
        pygame.display.update()
        scrn.clock.tick(FPS)
    pygame.quit()
    sys.exit()

# def menu_loop():
#     menu_running = True
#     while menu_running:
#         scrn.show_main_menu()
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 menu_running = False
#             if event.type == pygame.MOUSEBUTTONDOWN:
#                 mouse_x, mouse_y = pygame.mouse.get_pos()
#                 # Start Game
#                 if HEIGHT // 2 <= mouse_y <= HEIGHT // 2 + 40 and WIDTH // 2 - 150 <= mouse_x <= WIDTH // 2 + 150:
#                     menu_running = False
#                     main_game()
#                 # Quit Game
#                 if HEIGHT // 2 + 60 <= mouse_y <= HEIGHT // 2 + 100 and WIDTH // 2 - 100 <= mouse_x <= WIDTH // 2 + 100:
#                     menu_running = False
#                     pygame.quit()
#                     sys.exit()

#menu_loop()

main_game()
