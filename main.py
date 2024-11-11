import pygame
import sys

# 初始化 pygame
pygame.init()

# 設定遊戲畫面
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('2D Battle Game - Player vs Player')

# 載入背景圖像
background_image = pygame.image.load('images/background1.jpg')  # 替換為您的背景圖片檔案
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))  # 確保背景適合畫面

# 顏色設置
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# FPS 設置
FPS = 60
clock = pygame.time.Clock()

# 遊戲變數
player1_health = 100
player2_health = 100
player1_x, player1_y = 100, HEIGHT - 120
player2_x, player2_y = WIDTH - 160, HEIGHT - 120
player1_velocity = 5
player2_velocity = 5
attack_range = 100  # 攻擊範圍（像素）

# 重力與跳躍設定
GRAVITY = 0.5
JUMP_STRENGTH = -15
MAX_FALL_SPEED = 10

# 攻擊冷卻時間設置（秒）
ATTACK_COOLDOWN = 0.5  # 每次攻擊之間的間隔時間
player1_attack_time = 0  # 玩家1的攻擊冷卻時間
player2_attack_time = 0  # 玩家2的攻擊冷卻時間

# 玩家類別
class Player(pygame.sprite.Sprite):
    def __init__(self, color, x, y):
        super().__init__()
        self.color = color  # 設置顏色屬性
        self.image = pygame.Surface((50, 50))
        self.image.fill(self.color)  # 根據顏色填充玩家
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.velocity = 5
        self.health = 100
        self.defending = False  # 防禦狀態
        self.y_velocity = 0  # Y軸速度（用於跳躍和重力）
        self.jumping = False  # 是否在跳躍

    def update(self):
        # 移動控制（玩家1和玩家2不同的控制）
        keys = pygame.key.get_pressed()
        
        # 玩家1控制 (WASD)
        if self.color == RED:  
            if keys[pygame.K_a]:
                self.rect.x -= self.velocity
            if keys[pygame.K_d]:
                self.rect.x += self.velocity
                
            if keys[pygame.K_s]:  # 玩家1按下 S 鍵進行防禦
                self.defending = True
            else:
                self.defending = False

            if keys[pygame.K_w] and not self.jumping:  # 按空格鍵跳躍
                self.y_velocity = JUMP_STRENGTH  # 向上加速
                self.jumping = True

        # 玩家2控制 (箭頭)
        elif self.color == BLUE:  
            if keys[pygame.K_LEFT]:
                self.rect.x -= self.velocity
            if keys[pygame.K_RIGHT]:
                self.rect.x += self.velocity

            if keys[pygame.K_DOWN]:  # 玩家2按下 下箭頭鍵進行防禦
                self.defending = True
            else:
                self.defending = False

            if keys[pygame.K_UP] and not self.jumping:  # 玩家2按下 Enter 鍵跳躍
                self.y_velocity = JUMP_STRENGTH  # 向上加速
                self.jumping = True

        # 應用重力
        if self.jumping:
            self.y_velocity += GRAVITY  # 增加重力
            if self.y_velocity > MAX_FALL_SPEED:  # 限制下落速度
                self.y_velocity = MAX_FALL_SPEED

        # 更新 Y 位置
        self.rect.y += self.y_velocity

        # 碰撞檢測：如果碰到地面，停止跳躍並重置 Y 速度
        if self.rect.y >= HEIGHT - 120:
            self.rect.y = HEIGHT - 120  # 確保玩家不會掉出畫面
            self.jumping = False
            self.y_velocity = 0  # 停止下落

    def attack(self, other_player, current_time):
        global player1_attack_time, player2_attack_time

        # 計算冷卻時間
        if self.color == RED:
            if current_time - player1_attack_time >= ATTACK_COOLDOWN:  # 玩家1是否能攻擊
                player1_attack_time = current_time  # 更新攻擊時間
                # 檢查是否在攻擊範圍內
                if abs(self.rect.x - other_player.rect.x) < attack_range and abs(self.rect.y - other_player.rect.y) < attack_range:
                    damage = 10
                    if other_player.defending:  # 防禦時減少傷害
                        damage = damage // 2
                    other_player.health -= damage  # 攻擊傷害

        elif self.color == BLUE:
            if current_time - player2_attack_time >= ATTACK_COOLDOWN:  # 玩家2是否能攻擊
                player2_attack_time = current_time  # 更新攻擊時間
                # 檢查是否在攻擊範圍內
                if abs(self.rect.x - other_player.rect.x) < attack_range and abs(self.rect.y - other_player.rect.y) < attack_range:
                    damage = 10
                    if other_player.defending:  # 防禦時減少傷害
                        damage = damage // 2
                    other_player.health -= damage  # 攻擊傷害

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

# 主遊戲迴圈
running = True
while running:
    # 處理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 更新玩家位置和狀態
    player1.update()
    player2.update()

    # 玩家攻擊判斷
    current_time = pygame.time.get_ticks() / 1000  # 獲取當前時間（秒）
    keys = pygame.key.get_pressed()
    if keys[pygame.K_j]:  # 玩家1的攻擊
        player1.attack(player2, current_time)
    if keys[pygame.K_k]:  # 玩家2的攻擊
        player2.attack(player1, current_time)

    # 填充背景
    screen.blit(background_image, (0, 0))

    # 繪製所有精靈
    all_sprites.draw(screen)

    # 顯示玩家1血量條
    pygame.draw.rect(screen, BLACK, (10, 10, 200, 20))  # 邊框
    pygame.draw.rect(screen, GREEN, (10, 10, 2 * player1.health, 20))  # 血量條 (根據血量調整長度)

    # 顯示玩家2血量條
    pygame.draw.rect(screen, BLACK, (WIDTH - 210, 10, 200, 20))  # 邊框
    pygame.draw.rect(screen, GREEN, (WIDTH - 210, 10, 2 * player2.health, 20))  # 血量條 (根據血量調整長度)

    # 檢查遊戲結束
    if player1.health <= 0 or player2.health <= 0:
        winner = "Player 1" if player2.health <= 0 else "Player 2"
        show_game_over(winner)

        # 處理遊戲結束後的重啟或退出
        if keys[pygame.K_r]:
            player1.health = player2.health = 100
            player1.rect.x = 100
            player1.rect.y = HEIGHT - 120
            player2.rect.x = WIDTH - 160
            player2.rect.y = HEIGHT - 120
        elif keys[pygame.K_q]:
            running = False

    # 更新畫面
    pygame.display.update()

    # 控制遊戲速度
    clock.tick(FPS)

# 離開遊戲
pygame.quit()
sys.exit()
