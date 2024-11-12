import pygame
import sys

# 初始化 pygame
pygame.init()

# 設定遊戲畫面
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('2D Battle Game - Player vs Player')

# 載入背景圖像
background_image = pygame.image.load('images/background1.jpg')
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

# 顏色設置
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# FPS 設置
FPS = 60
clock = pygame.time.Clock()

# 遊戲變數
player1_health = 100
player2_health = 100
player1_x, player1_y = 100, HEIGHT - 120
player2_x, player2_y = WIDTH - 160, HEIGHT - 120

# 設定遊戲的增減速度
HEALTH_CHANGE_SPEED = 2
ENERGY_CHANGE_SPEED = 1

# 重力與跳躍設定
GRAVITY = 0.5
JUMP_STRENGTH = -13
MAX_FALL_SPEED = 20

# 攻擊冷卻時間設置（秒）
ATTACK_COOLDOWN = 0.5
player1_attack_time = 0
player2_attack_time = 0
attack_range = 100
energy_gain_per_move = 0.5
energy_full = 100

class Player(pygame.sprite.Sprite):
    def __init__(self, color, x, y):
        super().__init__()
        self.color = color
        self.image = pygame.Surface((50, 50))
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.velocity = 5
        self.health = 100
        self.energy = 0
        self.displayed_health = 100
        self.displayed_energy = 0
        self.defending = False
        self.y_velocity = 0
        self.jumping = False
        self.last_move_direction = None
        self.last_jump_time = 0 
        self.jump_count = 0
        
    def update(self):
        # 使顯示的血量和能量逐漸逼近實際值
        health_change_speed = 1  # 控制血量變化速度
        energy_change_speed = 3  # 控制能量變化速度

        if self.displayed_health < self.health:
            self.displayed_health += health_change_speed
            if self.displayed_health > self.health:
                self.displayed_health = self.health
        elif self.displayed_health > self.health:
            self.displayed_health -= health_change_speed
            if self.displayed_health < self.health:
                self.displayed_health = self.health

        if self.displayed_energy < self.energy:
            self.displayed_energy += energy_change_speed
            if self.displayed_energy > self.energy:
                self.displayed_energy = self.energy
        elif self.displayed_energy > self.energy:
            self.displayed_energy -= energy_change_speed
            if self.displayed_energy < self.energy:
                self.displayed_energy = self.energy
        
        # 移動控制和能量增加
        keys = pygame.key.get_pressed()
        moved = False
        
        if self.color == RED:  # 玩家1
            if keys[pygame.K_a]:
                self.rect.x -= self.velocity
                moved = True
            if keys[pygame.K_d]:
                self.rect.x += self.velocity
                moved = True
             # Jump logic with 0.5 second delay after last jump
            current_time = pygame.time.get_ticks()  # Get current time in milliseconds
            if keys[pygame.K_w] and self.jump_count < 2 and current_time - self.last_jump_time > 400:
                self.y_velocity = JUMP_STRENGTH
                self.jumping = True
                self.jump_count += 1
                self.last_jump_time = current_time  # Update last jump time
                
            # If you're in the air and press down, you will fall faster
            if keys[pygame.K_s] and self.jumping:
                self.y_velocity = MAX_FALL_SPEED
            elif keys[pygame.K_s]:
                self.defending = True
                
        elif self.color == BLUE:  # 玩家2
            if keys[pygame.K_LEFT]:
                self.rect.x -= self.velocity
                moved = True
            if keys[pygame.K_RIGHT]:
                self.rect.x += self.velocity
                moved = True
            
            # Jump logic with 0.5 second delay after last jump
            current_time = pygame.time.get_ticks()  # Get current time in milliseconds
            if keys[pygame.K_UP] and self.jump_count < 2 and current_time - self.last_jump_time > 400:
                # if you are in the sky and press up, velocity will be 
                self.y_velocity = JUMP_STRENGTH
                self.jumping = True
                self.jump_count += 1
                self.last_jump_time = current_time
                
            # If you're in the air and press down, you will fall faster
            if keys[pygame.K_DOWN] and self.jumping:
                self.y_velocity = MAX_FALL_SPEED
            elif keys[pygame.K_DOWN]:
                self.defending = True

        # 更新能量
        if moved:
            self.energy += energy_gain_per_move
            if self.energy > energy_full:
                self.energy = energy_full

        # Gravity
        if self.jumping:
            self.y_velocity += GRAVITY
            if self.y_velocity > MAX_FALL_SPEED:
                self.y_velocity = MAX_FALL_SPEED

        self.rect.y += self.y_velocity

        # Check if landed
        if self.rect.y >= HEIGHT - 120:
            self.rect.y = HEIGHT - 120
            self.jumping = False
            self.y_velocity = 0
            self.jump_count = 0  # Reset jump count when the player lands
            
    def attack(self, other_player, current_time, powerful=False):
        global player1_attack_time, player2_attack_time

        if self.color == RED and current_time - player1_attack_time >= ATTACK_COOLDOWN:
            player1_attack_time = current_time
            if abs(self.rect.x - other_player.rect.x) < attack_range:
                damage = 30 if powerful else 10
                if other_player.defending:
                    damage //= 2
                other_player.health -= damage

        elif self.color == BLUE and current_time - player2_attack_time >= ATTACK_COOLDOWN:
            player2_attack_time = current_time
            if abs(self.rect.x - other_player.rect.x) < attack_range:
                damage = 30 if powerful else 10
                if other_player.defending:
                    damage //= 2
                other_player.health -= damage

# 初始化玩家
player1 = Player(RED, player1_x, player1_y)
player2 = Player(BLUE, player2_x, player2_y)



all_sprites = pygame.sprite.Group()
all_sprites.add(player1)
all_sprites.add(player2)

# 顯示 "遊戲結束" 畫面
def show_game_over(winner):
    font = pygame.font.SysFont('Arial', 20)
    text = font.render(f"Game Over! {winner} Wins! Press R to Restart or Q to Quit", True, BLACK)
    screen.blit(text, (WIDTH // 4, HEIGHT // 2))
    
def draw_health_energy_bar():
    # 玩家1的血量條
    pygame.draw.rect(screen, RED, (20, 20, player1.displayed_health * 2, 20))  # 使用顯示的血量
    pygame.draw.rect(screen, WHITE, (20, 20, 200, 20), 2)  # 邊框
    
    # 玩家1的能量條
    pygame.draw.rect(screen, YELLOW, (20, 50, player1.displayed_energy * 2, 10))  # 使用顯示的能量
    pygame.draw.rect(screen, WHITE, (20, 50, 200, 10), 2)

    # 玩家2的血量條
    pygame.draw.rect(screen, BLUE, (WIDTH - 220, 20, player2.displayed_health * 2, 20))
    pygame.draw.rect(screen, WHITE, (WIDTH - 220, 20, 200, 20), 2)

    # 玩家2的能量條
    pygame.draw.rect(screen, YELLOW, (WIDTH - 220, 50, player2.displayed_energy * 2, 10))
    pygame.draw.rect(screen, WHITE, (WIDTH - 220, 50, 200, 10), 2)
    
# 主遊戲迴圈
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    player1.update()
    player2.update()

    # 玩家攻擊判斷
    current_time = pygame.time.get_ticks() / 1000
    keys = pygame.key.get_pressed()
    if keys[pygame.K_f]:
        player1.attack(player2, current_time)
    if keys[pygame.K_SLASH]:
        player2.attack(player1, current_time)

    # 強力攻擊
    if keys[pygame.K_g] and player1.energy >= energy_full:
        player1.attack(player2, current_time, powerful=True)
        player1.energy = 0
    if keys[pygame.K_PERIOD] and player2.energy >= energy_full:
        player2.attack(player1, current_time, powerful=True)
        player2.energy = 0

    screen.blit(background_image, (0, 0))
    all_sprites.draw(screen)

    # 顯示玩家1血量和能量條
    draw_health_energy_bar()

    # 檢查遊戲結束
    if player1.health <= 0 or player2.health <= 0:
        winner = "Player 1" if player2.health <= 0 else "Player 2"
        show_game_over(winner)
        if keys[pygame.K_r]:
            player1.health = player2.health = 100
            player1.energy = player2.energy = 0
            player1.rect.x = player1_x
            player1.rect.y = HEIGHT - 120
            player2.rect.x = player2_x
            player2.rect.y = HEIGHT - 120
        elif keys[pygame.K_q]:
            running = False
    
    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
sys.exit()
