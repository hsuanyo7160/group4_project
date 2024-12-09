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
        self.rect.centerx = x
        self.rect.centery = y
        # Status
        self.pos_x = x
        self.pos_y = y
        
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
        self.movelimittime = 0
        self.prehealth = self.health
        self.atkbufftime = 0
        self.guardtime = 0
        self.waitdash = False
        self.dashing = False
        self.dashtime = 0
        self.attacking = False
        self.movable = True
        self.moving = False
        # action status
        self.status = IDLE
        # attack counter
        self.attack_counter = 0
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
        self.energy_atk_key = pygame.K_j if color == RED else pygame.K_m
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
        # keys = pygame.key.get_pressed()
        # self.moving = False
        #self.defending = False
        self.movable = True
        # Buff 
        if self.atkbufftime > 0:
            self.atkbufftime -= 1
            if self.atkbufftime <= 0:
                self.attack_damage = 5
                self.velocity = 5
        
        if self.dashtime > 0:
            self.movable = False
            self.dashtime -= 1
            self.pos_x += 10 if self.facing_left else -10
            if self.dashtime <= 0:
                self.dashtime = 0
        
        # Guard and move limit
        if self.waitdash:
            self.changeStatus(ATK)
            self.range_atk_timer = self.range_cooldown + 1
            self.common_timer = ATTACK_COOLDOWN + 1
            self.range_attack(self.other_player, self.projectiles_group)
            self.movable = False
            self.waitdash = False
            self.dashtime = 30
        # Guard    
        if self.guardtime > 0:
            self.movable = False
            self.guardtime -= 1
            if(self.health < self.prehealth):
                print("guard")
                self.health = self.prehealth
                self.guardtime = 0
                self.other_player.movelimmitime = 30
                self.attack_damage = 8
                self.velocity = 8
                self.atkbufftime = 300

        if self.movelimittime > 0:
            self.movable = False
            self.movelimittime -= 1
            if self.movelimittime <= 0:
                self.movelimittime = 0
        # if self.movable:
        #     # If you're in the air and press down, you will fall faster
        #     if keys[self.down] and self.jumping:
        #         self.y_velocity = MAX_FALL_SPEED
        #         self.changeStatus(KNEEL)
        #     # If you're on the ground and press down, you will defend
        #     elif keys[self.down]:
        #         self.defending = True
        #         self.changeStatus(DEFEND)
                
        #     if(self.defending == False):
        #         if keys[self.left]:
        #             if self.jumping == False:
        #                 self.changeStatus(WALK)
        #             if self.pos_x > BORDER[0]:
        #                 self.pos_x -= self.velocity
        #             moved = True
        #             if not self.facing_left:  # Only flip if direction has changed
        #                 self.facing_left = True
        #                 self.image = pygame.transform.flip(self.image, True, False)  # Flip horizontally
        #         if keys[self.right]:
        #             if self.jumping == False:
        #                 self.changeStatus(WALK)
        #             if self.pos_x < BORDER[1]:
        #                 self.pos_x += self.velocity
        #             moved = True
        #             if self.facing_left:  # Only flip if direction has changed
        #                 self.facing_left = False
        #                 #self.image = self.image
        #                 self.image = pygame.transform.flip(self.image, True, False)
        #             # Jump logic with 0.5 second delay after last jump
        #         current_time = pygame.time.get_ticks()  # Get current time in milliseconds
        #         if keys[self.up] and self.jump_count < 2 and current_time - self.last_jump_time > 400:
        #             self.y_velocity = JUMP_STRENGTH
        #             self.jumping = True
        #             self.changeStatus(JUMP)
        #             self.jump_count += 1
        #             self.last_jump_time = current_time  # Update last jump time
        #     # else:
        #     #     self.changeStatus(DEFEND)
        #     if keys[self.up] == False and keys[self.left] == False and keys[self.right] == False and keys[self.down] == False and self.jumping == False and keys[self.atk_key] == False and keys[self.range_atk_key] == False and keys[self.special_key] == False:
        #         self.changeStatus(IDLE)
        #         print("idle")

        # 更新能量
        if self.moving:
            self.energy += self.energy_gain_per_move
            if self.energy > ENERGY_FULL:
                self.energy = ENERGY_FULL

        # Gravity
        if self.jumping:
            self.y_velocity += GRAVITY
            if self.y_velocity > MAX_FALL_SPEED:
                self.y_velocity = MAX_FALL_SPEED

        self.pos_y += self.y_velocity

        # Check if landed
        if self.pos_y >= HEIGHT - 420:
            self.pos_y = HEIGHT - 420
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
        # if keys[self.atk_key]:
        #     self.attack(self.other_player)
        #     self.movelimittime = 15 # 0.25s can't move, run animation
        # if keys[self.range_atk_key]:
        #     self.range_attack(self.other_player, self.projectiles_group)
        # if keys[self.special_key]:
        #     self.special_attack(self.other_player)    
        # if keys[self.energy_atk_key]:
        #     self.attack(self.other_player, powerful=True)

        # check falling
        if self.y_velocity > 0 and self.y_velocity != MAX_FALL_SPEED:
            self.changeStatus(FALL)
            
    def attack(self, other_player, powerful=False):
        
        # global player1_attack_time, player2_attack_time

        # if self.color == RED and current_time - self.attack_time > ATTACK_COOLDOWN: # player1_attack_time >= ATTACK_COOLDOWN:
        if(self.atk_timer > ATTACK_COOLDOWN and self.defending == False and self.common_timer > ATTACK_COOLDOWN):
            #player1_attack_time = current_time
            self.changeStatus(ATK)
            self.atk_timer = 0
            self.common_timer = 0
            offset = (other_player.pos_x - self.pos_x, other_player.pos_y - self.pos_y)
            if self.mask.overlap(other_player.mask, offset):
            #if abs(self.rect.x - other_player.rect.x) < self.attack_range:
                damage = self.attack_damage_powerful if (powerful and self.energy == 100) else self.attack_damage
                if other_player.defending:
                    damage -= other_player.defend_strength
                    if damage < 0:
                        damage = 0
                if powerful:
                    self.energy = 0
                other_player.health -= damage
                
    def range_attack(self, other_player, projectiles_group):
        """發射遠程攻擊（子彈）"""
        # 創建一個子彈並設定其初始位置和方向
        if(self.range_atk_timer > self.range_cooldown and self.defending == False and self.common_timer > ATTACK_COOLDOWN):
            self.range_atk_timer = 0
            self.common_timer = 0
            direction = -1 if self.facing_left else 1
            projectile = Projectile(self.pos_x, self.pos_y, other_player, self.range_damage, direction)
            projectiles_group.add(projectile)
    
    def special_attack(self, other_player):
        if(self.atk_timer < ATTACK_COOLDOWN or self.energy < 30):
            return None
        self.atk_timer = 0
        if self.index == 0:
            ## wait for next input
            self.waitdash = True        
            ## increase speed of that input(dash)
            ## deal damage, add progectile , energy -30 and animation
            
            
        elif self.index == 1:
            ## cant move and animation
            self.prehealth = self.health
            self.guardtime = 60
            ## if health drop -> restore to original health, stunned enemy for 2s, spd atk up for 5s

        elif self.index == 2:
            ## teleport to enemy side and start shyuli
            self.pos_x = other_player.pos_x
            self.pos_y = other_player.pos_y
            self.movelimittime = 60
            ## deal lots of damage
            other_player.health -= 10
            
        self.energy -= 30
    
    def draw(self, screen, camera_pos=(600, 300)): # camera_pos = half of distance between players
        self.image = self.sprite_sheet.get_image(self.frame, (0,0,0))
        if self.facing_left:
            self.image = pygame.transform.flip(self.image, True, False)
        if abs(camera_pos[0] - self.pos_x) < 500:
            zoom = 1
            self.image = scale_image(self.image, 300 * zoom)
            self.rect = self.image.get_rect()
            self.rect.centerx = self.pos_x - camera_pos[0] + 600
            self.rect.centery = self.pos_y - camera_pos[1] + 300
        else:
            zoom = 1000 / (abs(camera_pos[0] - self.pos_x) *2)
            self.image = scale_image(self.image, 300 * zoom)
            self.rect = self.image.get_rect()
            self.rect.centerx = 100 if self.pos_x < camera_pos[0] else 1100
            self.rect.centery = self.pos_y - camera_pos[1] + 300
        
        self.mask = pygame.mask.from_surface(self.image)

        return zoom
        
        
        

    def changeStatus(self, status):
        if self.status != status :#or status == JUMP:
            self.frame = 0

        self.status = status

        if status == IDLE:
            self.frame_rate = 10
            self.sprite_sheet = Spritesheet(character.character_data[self.index]['idle'], character.character_data[self.index]['idleFrame'])
        elif status == JUMP:
            self.frame_rate  = 10
            self.sprite_sheet = Spritesheet(character.character_data[self.index]['jump'], character.character_data[self.index]['jumpFrame'])    
        elif status == WALK:
            self.frame_rate = 10
            self.sprite_sheet = Spritesheet(character.character_data[self.index]['walk'], character.character_data[self.index]['walkFrame'])
        elif status == ATK:
            if character.character_data[self.index]['name'] == "Samurai" or character.character_data[self.index]['name'] == "Commander":
                self.frame_rate = 3
            else: # Archer
                self.frame_rate = 1
            self.sprite_sheet = Spritesheet(character.character_data[self.index]['attack1'], character.character_data[self.index]['attack1Frame'])
        elif status == DEFEND:
            if character.character_data[self.index]['name'] == "Samurai" or character.character_data[self.index]['name'] == "Commander":
                self.frame_rate = 4
            else: # Archer
                self.frame_rate = 3
            self.sprite_sheet = Spritesheet(character.character_data[self.index]['protect'], character.character_data[self.index]['protectFrame'])
        elif status == FALL:
            self.frame_rate = 10
            self.sprite_sheet = Spritesheet(character.character_data[self.index]['fall'], character.character_data[self.index]['fallFrame'])
        elif status == KNEEL:
            self.frame_rate = 10
            self.sprite_sheet = Spritesheet(character.character_data[self.index]['kneel'], character.character_data[self.index]['kneelFrame'])
    
    
    def increaseframe(self):
        """增加動畫幀，根據 frame_rate 決定是否更新"""
        self.frame_counter += 1
        if self.frame_counter >= self.frame_rate:
            if self.status == JUMP and self.frame == character.character_data[self.index]['jumpFrame'] - 1:
                self.frame_counter = 0  # 重置計數器，但不更新幀
                return
        
            # 攻擊動畫到最後一幀時不循環
            if self.status == ATK and self.frame == character.character_data[self.index]['attack1Frame'] - 1:
                self.frame_counter = 0  # 重置計數器，但不更新幀
                self.changeStatus(IDLE)
                return
                # 如果不在特殊狀態，或動畫可以循環

            if self.status == DEFEND and self.frame == character.character_data[self.index]['protectFrame'] - 1:
                self.frame_counter = 0  # 重置計數器，但不更新幀
                return
            self.frame = (self.frame + 1) % self.sprite_sheet.num_sprites  # 更新幀
            self.frame_counter = 0  # 重置計數器


    def handleinput(self, keys):
        self.moving = False
        if self.movable:
            # If you're in the air and press down, you will fall faster
            if keys[self.down] and self.jumping:
                self.y_velocity = MAX_FALL_SPEED
                self.changeStatus(KNEEL)
            # If you're on the ground and press down, you will defend
            elif keys[self.down]:
                self.defending = True
                self.changeStatus(DEFEND)
            # on the ground and not defending
            if not keys[self.down] and not self.jumping:
                self.defending = False
            #if(self.defending == False):
            if keys[self.left]:
                if self.jumping == False and not self.defending:
                    self.changeStatus(WALK)
                if self.pos_x > BORDER[0] and not self.defending:
                    self.pos_x -= self.velocity
                    self.moving = True
                if not self.facing_left:  # Only flip if direction has changed
                    self.facing_left = True
                    self.image = pygame.transform.flip(self.image, True, False)  # Flip horizontally
            elif keys[self.right]:
                if self.jumping == False and not self.defending:
                    self.changeStatus(WALK)
                if self.pos_x < BORDER[1] and not self.defending:
                    self.pos_x += self.velocity
                    self.moving = True
                if self.facing_left:  # Only flip if direction has changed
                    self.facing_left = False
                    #self.image = self.image
                    self.image = pygame.transform.flip(self.image, True, False)
                # Jump logic with 0.5 second delay after last jump
            current_time = pygame.time.get_ticks()  # Get current time in milliseconds
            if keys[self.up] and self.jump_count < 2 and current_time - self.last_jump_time > 400:
                self.y_velocity = JUMP_STRENGTH
                self.jumping = True
                self.changeStatus(JUMP)
                self.jump_count += 1
                self.last_jump_time = current_time  # Update last jump time
            # else:
            #     self.changeStatus(DEFEND)
            if keys[self.up] == False and keys[self.left] == False and keys[self.right] == False and keys[self.down] == False and self.jumping == False and keys[self.atk_key] == False and keys[self.range_atk_key] == False and keys[self.special_key] == False:
                self.changeStatus(IDLE)
        # attack kits
        if keys[self.atk_key]:
            self.attack(self.other_player)
            self.movelimittime = 15 # 0.25s can't move, run animation
        if keys[self.range_atk_key]:
            self.range_attack(self.other_player, self.projectiles_group)
        if keys[self.special_key]:
            self.special_attack(self.other_player)    
        if keys[self.energy_atk_key]:
            self.attack(self.other_player, powerful=True)

        
 ## range attack for commander and samurai
 ## samurai: lower dmg but slow enemy
 ## commander: add spd

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, other_player, damage, direction):
        super().__init__()
        self.base_image = pygame.image.load('images/character/Archer/Arrow.png')
        self.base_image = pygame.transform.scale(self.base_image, (100, 100))
        if direction == -1:
            self.base_image = pygame.transform.flip(self.base_image, True, False)
        self.mask = pygame.mask.from_surface(self.base_image)
        self.rect = self.base_image.get_rect()
        self.pos_x = x
        self.pos_y = y
        self.rect.centerx = x
        self.rect.centery = y
        self.velocity_x = 30  # Speed of the projectile
        self.velocity_y = -5
        self.direction = direction  # Direction vector (1, 0 for right, -1, 0 for left)
        self.target = other_player
        self.damage = damage
        
    def update(self, zoom, camera_pos):
        """Update projectile's position"""
        self.velocity_y += GRAVITY
        self.pos_x += self.velocity_x * self.direction  # Update x position based on direction
        self.pos_y += self.velocity_y

        if self.pos_x < BORDER[0] or self.pos_x > BORDER[1]:  # If the projectile goes off the screen
            self.kill()  # Remove the projectile from the game
        elif self.pos_y > HEIGHT:
            self.kill()  # Remove the projectile from the game
        
        # rotate image based on velocity_x and velocity_y
        angle = 0
        if self.velocity_x != 0:
            angle = -self.velocity_y / self.velocity_x * self.direction
            angle = angle * 180 / 3.14159 # Convert to degrees
        self.image = pygame.transform.rotate(self.base_image, angle)
        self.image = scale_image(self.image, 100 * zoom)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        
        self.rect.centerx = self.pos_x - camera_pos[0] + 600
        self.rect.centery = self.pos_y - camera_pos[1] + 300

        # print(self.rect)
        # print(self.target.rect)
        
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


class Background(pygame.sprite.Sprite):
    def __init__(self, map_choice):
        super().__init__()
        self.base_image = pygame.image.load(f'images/background/{map_choice}')
        self.image = scale_image(self.base_image, HEIGHT*3)
        self.rect = self.image.get_rect()
        self.rect.topleft = (0, 0)
        
    def draw(self, screen):
        screen.blit(self.image, self.rect)
        
    def update(self, zoom, camera_pos):
        self.image = scale_image(self.base_image, HEIGHT * 3 * zoom)
        self.rect = self.image.get_rect()
        self.rect.centerx = 1200 - camera_pos[0]
        self.rect.centery = 600 - camera_pos[1]

