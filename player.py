import pygame
from ch import character
from const import *
from spritesheet import Spritesheet
import time

def scale_image(image, target_height):
    # 獲取原始尺寸
    original_width, original_height = image.get_size()
    # 計算新寬度，保持比例
    aspect_ratio = original_width / original_height
    target_width = int(target_height * aspect_ratio)
    # 使用新尺寸進行縮放
    scaled_image = pygame.transform.scale(image, (target_width, target_height))
    return scaled_image

class Player(pygame.sprite.Sprite):
    def __init__(self, color, x, y, index):
        super().__init__()
        # Model
        self.color = color
        self.image = pygame.image.load(character.character_data[index]['icon']) if color == RED else pygame.image.load(character.character_data[index]['icon'])
        self.image = scale_image(self.image, 200)
        self.mask = pygame.mask.from_surface(self.image)
        self.index = index
        self.sprite_sheet = Spritesheet(character.character_data[index]['idle'], character.character_data[self.index]['idleFrame'])
        self.frame_counter = 0  # 計數器
        self.frame_rate = 10    # 幀速率，每 10 幀更新一次動畫幀
        self.frame = 0
        ############ Need to Optimize##############
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        # Status
        self.status = IDLE
        self.health = 200
        self.energy = 0
        self.displayed_health = 200
        self.displayed_energy = 0
        self.defending = False
        self.y_velocity = 0
        self.jumping = False
        self.last_jump_time = 0 
        self.jump_count = 0
        self.facing_left = False
        self.attack_time = 0
        self.range_attack_time = 0
        # timer
        self.atk_timer = 0
        self.range_atk_timer = 0
        self.special_timer = 0
        self.common_timer = 0
        self.last_tick = time.time()
        # Attributes
        self.attack_damage = character.character_data[index]['attack_damage']
        self.attack_damage_powerful = character.character_data[index]['attack_damage_powerful']
        self.energy_gain_per_move = character.character_data[index]['energy_gain_per_move']
        self.velocity = character.character_data[index]['velocity']
        self.attack_range = character.character_data[index]['attack_range']
        self.defend_strength = character.character_data[index]['defend_strength']
        self.range_damage = character.character_data[index]['range_damage']
        self.range_cooldown = character.character_data[index]['range_cooldown']
        
        # Key bindings
        self.left = pygame.K_a if color == RED else pygame.K_LEFT
        self.right = pygame.K_d if color == RED else pygame.K_RIGHT
        self.up = pygame.K_w if color == RED else pygame.K_UP
        self.down = pygame.K_s if color == RED else pygame.K_DOWN
        self.atk_key = pygame.K_f if color == RED else pygame.K_SLASH
        self.range_atk_key = pygame.K_g if color == RED else pygame.K_PERIOD
        self.special_key = pygame.K_h if color == RED else pygame.K_COMMA
        # player binding
        self.other_player = None
        #group binding
        self.projectiles_group = None
        
    def update(self):
        self.increaseframe()
        # print(self.frame)
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
        self.defending = False
        
        # If you're in the air and press down, you will fall faster
        if keys[self.down] and self.jumping:
            self.y_velocity = MAX_FALL_SPEED
        # If you're on the ground and press down, you will defend
        elif keys[self.down]:
            self.defending = True
            
        if(self.defending == False):
            if keys[self.left]:
                if self.jumping == False:
                    self.changeStatus(WALK)
                if self.mask.centroid()[0]+self.rect.x > BORDER[0]:
                    self.rect.x -= self.velocity
                moved = True
                if not self.facing_left:  # Only flip if direction has changed
                    self.facing_left = True
                    self.image = pygame.transform.flip(self.image, True, False)  # Flip horizontally
            if keys[self.right]:
                if self.jumping == False:
                    self.changeStatus(WALK)
                if self.mask.centroid()[0]+self.rect.x < BORDER[1]:
                    self.rect.x += self.velocity
                moved = True
                if self.facing_left:  # Only flip if direction has changed
                    self.facing_left = False
                    self.image = self.image
                    self.image = pygame.transform.flip(self.image, True, False)
                # Jump logic with 0.5 second delay after last jump
            current_time = pygame.time.get_ticks()  # Get current time in milliseconds
            if keys[self.up] and self.jump_count < 2 and current_time - self.last_jump_time > 400:
                self.y_velocity = JUMP_STRENGTH
                self.jumping = True
                self.changeStatus(JUMP)
                self.jump_count += 1
                self.last_jump_time = current_time  # Update last jump time
        if keys[self.up] == False and keys[self.left] == False and keys[self.right] == False and keys[self.down] == False and self.jumping == False:
            self.changeStatus(IDLE)

        # 更新能量
        if moved:
            self.energy += self.energy_gain_per_move
            if self.energy > ENERGY_FULL:
                self.energy = ENERGY_FULL

        # Gravity
        if self.jumping:
            self.y_velocity += GRAVITY
            if self.y_velocity > MAX_FALL_SPEED:
                self.y_velocity = MAX_FALL_SPEED

        self.rect.y += self.y_velocity

        # Check if landed
        if self.rect.y >= HEIGHT - 220:
            self.rect.y = HEIGHT - 220
            self.jumping = False
            self.y_velocity = 0
            self.jump_count = 0  # Reset jump count when the player lands
        
        # update timer
        self.atk_timer += time.time() - self.last_tick
        self.range_atk_timer += time.time() - self.last_tick
        self.special_timer += time.time() - self.last_tick
        self.common_timer += time.time() - self.last_tick
        self.last_tick = time.time()

        # attack kits
        if keys[self.atk_key]:
            self.attack(self.other_player)
        if keys[self.range_atk_key]:
            self.range_attack(self.other_player, self.projectiles_group)
        if keys[self.special_key]:
            self.attack(self.other_player, powerful=True)
        # if keys[self.special_key]:
        #     self.special_attack(self.other_player)
        
            
    def attack(self, other_player, powerful=False):
        # global player1_attack_time, player2_attack_time

        # if self.color == RED and current_time - self.attack_time > ATTACK_COOLDOWN: # player1_attack_time >= ATTACK_COOLDOWN:
        if(self.atk_timer > ATTACK_COOLDOWN and self.defending == False and self.common_timer > ATTACK_COOLDOWN):
            #player1_attack_time = current_time
            self.atk_timer = 0
            self.common_timer = 0
            if abs(self.rect.x - other_player.rect.x) < self.attack_range:
                damage = self.attack_damage_powerful if powerful else self.attack_damage
                if other_player.defending:
                    damage -= other_player.defend_strength
                    if damage < 0:
                        damage = 0
                other_player.health -= damage
                
    def range_attack(self, other_player, projectiles_group):
        """發射遠程攻擊（子彈）"""
        # 創建一個子彈並設定其初始位置和方向
        if(self.range_atk_timer > self.range_cooldown and self.defending == False and self.common_timer > ATTACK_COOLDOWN):
            self.range_atk_timer = 0
            self.common_timer = 0
            direction = -1 if self.facing_left else 1
            projectile = Projectile(self.rect.centerx, self.rect.centery, other_player, self.range_damage, direction)
            projectiles_group.add(projectile)
    
    def special_attack(self, other_player):
        if(self.energy < 30):
            return None
        if self.index == 0:
            None
            ## wait for next input
            
            ## increase speed of that input(dash)
            
            ## deal damage, add progectile , energy -30 and animation 
        elif self.index == 1:
            None
            ## cant move and animation
            
            ## if health drop -> restore to original health, stunned enemy for 2s, spd atk up for 5s
        elif self.index == 2:
            None
            ## teleport to enemy side and start shyuli
            
            ## deal lots of damage
    
    def draw(self, screen):
        self.image = self.sprite_sheet.get_image(self.frame, (0,0,0))
        if self.facing_left:
            self.image = pygame.transform.flip(self.image, True, False)
        self.image = scale_image(self.image, 300)
        self.mask = pygame.mask.from_surface(self.image)
        
        
        

    def changeStatus(self, status):
        if self.status != status:
            self.frame = 0
        self.status = status
        if status == IDLE:
            self.sprite_sheet = Spritesheet(character.character_data[self.index]['idle'], character.character_data[self.index]['idleFrame'])
        elif status == JUMP:
            self.frame_rate  = 8
            self.sprite_sheet = Spritesheet(character.character_data[self.index]['jump'], character.character_data[self.index]['jumpFrame'])    
        elif status == WALK:
            self.sprite_sheet = Spritesheet(character.character_data[self.index]['walk'], character.character_data[self.index]['walkFrame'])
        elif status == ATTACK1:
            self.sprite_sheet = Spritesheet(character.character_data[self.index]['attack1'], character.character_data[self.index]['attack1Frame'])
        
    def increaseframe(self):
        """增加動畫幀，根據 frame_rate 決定是否更新"""
        self.frame_counter += 1
        if self.frame_counter >= self.frame_rate:
            self.frame = (self.frame + 1) % self.sprite_sheet.num_sprites  # 更新幀
            self.frame_counter = 0  # 重置計數器

 ## range attack for commander and samurai
 ## samurai: lower dmg but slow enemy
 ## commander: add spd

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, other_player, damage, direction):
        super().__init__()
        self.image = pygame.image.load('images/character/Archer/Arrow.png')
        self.image = pygame.transform.scale(self.image, (100, 100))
        if direction == -1:
            self.image = pygame.transform.flip(self.image, True, False)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.velocity = 10  # Speed of the projectile
        self.direction = direction  # Direction vector (1, 0 for right, -1, 0 for left)
        self.target = other_player
        self.damage = damage
        
    def update(self):
        """Update projectile's position"""
        self.rect.x += self.velocity * self.direction  # Update x position based on direction
        if self.rect.right < 0 or self.rect.left > WIDTH:  # If the projectile goes off the screen
            self.kill()  # Remove the projectile from the game

        # Check collision with the target
        offset = (self.target.rect.x - self.rect.x, self.target.rect.y - self.rect.y)
        if self.mask.overlap(self.target.mask, offset):
            print("hit")
            damage = self.damage
            if self.target.defending:
                damage = self.damage - self.target.defend_strength
                if damage < 0:
                    damage = 0
            self.target.health -= damage  # Apply damage
            self.kill() 
            
    def draw(self, screen): 
        screen.blit(self.image, self.rect)

