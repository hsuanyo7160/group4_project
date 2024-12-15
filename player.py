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
        self.trail_counter = 2
        ############ Need to Optimize##############
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        # Status
        self.pos_x = x
        self.pos_y = y   
        self.health = 200
        self.energy = 0
        self.displayed_health = 0
        self.displayed_energy = 0   
        self.y_velocity = 0
        self.last_jump_time = 0 
        self.jump_count = 0   
        self.attack_time = 0
        self.range_attack_time = 0
        self.movelimittime = 0
        self.prehealth = self.health
        self.atkbufftime = 0
        self.guardtime = 0
        self.dashtime = 0
        self.ultbufftime = 0
        self.bleed = 0
        #boolin
        self.facing_left = False if color == RED else True
        self.movable = True
        self.moving = False
        self.attacking = False
        self.waitdash = False
        self.dashing = False
        self.jumping = False
        self.defending = False
        self.atkcollide = False
        # action status
        self.status = IDLE
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
        # 狀態屬性
        self.trails = []  # 存放殘影數據的列表
        self.trail_lifetime = 10  # 殘影的生命時間（幀數）

    def setOpponent(self, player):
        self.other_player = player

    def setProjectileGroup(self, group):
        self.projectiles_group = group

    def leave_trail(self):
        """生成殘影"""
        trail_image = self.image.copy()
        trail_rect = self.rect.copy()
        self.trails.append({"image": trail_image, "rect": trail_rect, "life": self.trail_lifetime})

    def draw_trails(self, screen):
        """繪製殘影"""
        for trail in self.trails:
            # 調整透明度
            alpha = int(255 * (trail["life"] / self.trail_lifetime))  # 根據生命週期計算透明度
            trail_image = trail["image"].copy()
            trail_image.set_alpha(alpha)
            screen.blit(trail_image, trail["rect"])

    def update_trails(self):
        """更新殘影的生命週期"""
        self.trail_counter += 1
        for trail in self.trails:
            trail["life"] -= 1  # 減少生命時間
        self.trails = [trail for trail in self.trails if trail["life"] > 0]  # 移除過期的殘影

    def update(self):
        
        self.increaseframe()
        self.movable = True
        # Debuff
        if self.bleed > 0:
            self.bleed -= 1
            self.other_player.energy = 0
        # Buff 
        if self.atkbufftime > 0:
            self.atkbufftime -= 1
            if self.atkbufftime <= 0:
                self.attack_damage = self.attack_damage - 3
                self.velocity = self.velocity - 3
        
        if self.dashtime > 0:
            self.movable = False
            self.dashtime -= 1
            self.pos_x += 10 if self.facing_left else -10
            if self.dashtime <= 0:
                self.dashtime = 0
                
        if self.ultbufftime > 0:
            self.ultbufftime -= 1
            self.energy = 0
            # Archer
            if self.index == 0:
                if self.ultbufftime <= 0:
                    self.range_cooldown = 0.5
                    self.range_damage = self.range_damage - 3
                    self.velocity = self.velocity + 2
            # Samurai
            elif self.index == 1:
                if self.ultbufftime <= 0:
                    self.attack_damage = self.attack_damage - 3
                    self.defend_strength = self.defend_strength + 5
                    self.velocity = self.velocity - 3
        
        # Update trails
        if self.trails:
            self.update_trails()
        # Guard and move limit
        if self.waitdash:
            self.changeStatus(ATK)
            self.range_atk_timer = self.range_cooldown + 1
            self.common_timer = ATTACK_COOLDOWN + 1
            #self.range_attack(self.other_player, self.projectiles_group, "normal")
            self.range_attack("normal")
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
                self.attacking = False
                self.other_player.movelimittime = 30
                if self.atkbufftime <= 0:
                    self.attack_damage = self.attack_damage + 3
                    self.velocity = self.velocity + 3
                self.atkbufftime = 300
        if self.movelimittime > 0:
            self.movable = False
            self.movelimittime -= 1
            if self.movelimittime <= 0:
                self.movelimittime = 0

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
        current_time = time.time()
        time_passed = current_time - self.last_tick
        self.atk_timer += time_passed
        self.range_atk_timer += time_passed
        self.special_timer += time_passed
        self.common_timer += time_passed
        self.last_tick = current_time
        # check idle
        if not self.jumping and not self.defending and not self.moving and not self.attacking and self.status != DEAD:
            self.changeStatus(IDLE)
        # check falling
        if self.y_velocity > 0 and self.y_velocity != MAX_FALL_SPEED and not self.attacking and self.status != DEAD:
            self.changeStatus(FALL)
                
    def attack(self):
        if(self.atk_timer > ATTACK_COOLDOWN and not self.defending and self.common_timer > ATTACK_COOLDOWN):
            # 流血狀態攻擊會扣血
            if self.bleed > 0:
                self.health -= 5
            #player1_attack_time = current_time
            self.changeStatus(ATK)
            self.atk_timer = 0
            self.attacking = True
            self.common_timer = 0
            # offset = (self.other_player.pos_x - self.pos_x, self.other_player.pos_y - self.pos_y)
            
            # if self.mask.overlap(self.other_player.mask, offset):
            #     damage = self.attack_damage
            #     if self.other_player.defending:
            #         damage -= self.other_player.defend_strength
            #         if damage < 0:
            #             damage = 0
            #     self.other_player.health -= damage
    
    def attack_hit_check(self):
        """檢查攻擊是否命中對手"""
        if self.other_player:
            # 計算對手相對於當前角色的位置偏移
            offset = (self.other_player.pos_x - self.pos_x, self.other_player.pos_y - self.pos_y)
            
            # 使用 mask 檢查碰撞
            if self.mask.overlap(self.other_player.mask, offset) and self.atkcollide == False:
                damage = self.attack_damage
                self.atkcollide = True
                # 如果對手正在防禦，減少傷害
                if self.other_player.status == DEFEND:
                    damage -= self.other_player.defend_strength
                    damage = max(damage, 0)  # 確保傷害不為負數

                # 將傷害應用到對手
                self.other_player.health -= damage

    def range_attack(self, type):
        """發射遠程攻擊（子彈）"""
        # 創建一個子彈並設定其初始位置和方向
        if(self.range_atk_timer > self.range_cooldown and self.defending == False and self.common_timer > ATTACK_COOLDOWN):
            if self.bleed > 0:
                self.health -= 5
            self.changeStatus(RANGE_ATK)
            self.attacking = True
            self.range_atk_timer = 0
            self.common_timer = 0
            direction = -1 if self.facing_left else 1
            projectile = Projectile(self.pos_x, self.pos_y, self.other_player, self.range_damage, direction, image_path=character.character_data[self.index]['Arrow'],
                                    size = character.character_data[self.index]['Arrow_scale'], effect = type)
            self.projectiles_group.add(projectile)
    
    def special_attack(self):
        if(self.atk_timer < ATTACK_COOLDOWN or self.energy < 30):
            return None
        if self.bleed > 0:
            self.health -= 5
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
            self.changeStatus(SPEC_ATK)
            self.attacking = True
            ## if health drop -> restore to original health, stunned enemy for 2s, spd atk up for 5s

        elif self.index == 2:
            ## teleport to enemy side and start shyuli
            self.pos_x = self.other_player.pos_x
            self.pos_y = self.other_player.pos_y
            self.movelimittime = 60
            ## deal lots of damage
            self.other_player.health -= 10
            
        self.energy -= 30
    
    # J attack
    def power_attack(self):
        if(self.energy < 100):
            return None
        if self.bleed > 0:
            self.health -= 5
        if self.index == 0:
            self.ultbufftime = 600
            self.range_cooldown = 0.2
            self.range_damage += 3
            self.velocity -= 2
            
        elif self.index == 1:
            ## Increase Speed, attack, and Decrease defense for 10s
            self.ultbufftime = 600
            self.attack_damage = self.attack_damage + 3
            self.defend_strength = self.defend_strength - 5
            self.velocity = self.velocity + 3

        elif self.index == 2:
            # normal attack
            self.changeStatus(ATK)
            self.atk_timer = 0
            self.common_timer = 0
            offset = (self.other_player.pos_x - self.pos_x, self.other_player.pos_y - self.pos_y)
            if self.mask.overlap(self.other_player.mask, offset):
                # Add bleed effect
                self.other_player.bleed = 450
            
        self.energy -= 100
    
    def draw(self, screen, camera_pos=(600, 300)): # camera_pos = half of distance between players
        # Draw trails
        self.draw_trails(screen)
        # Draw player
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

        screen.blit(self.image, self.rect)
        return zoom
        
        
        

    def changeStatus(self, status):
        if self.status != status :
            self.frame = 0
            self.frame_counter = 0
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
            self.frame_rate = 15 // character.character_data[self.index]['attack1Frame']
            self.sprite_sheet = Spritesheet(character.character_data[self.index]['attack1'], character.character_data[self.index]['attack1Frame'])
        elif status == DEFEND:
            self.frame_rate = 8 // character.character_data[self.index]['protectFrame']
            self.sprite_sheet = Spritesheet(character.character_data[self.index]['protect'], character.character_data[self.index]['protectFrame'])
        elif status == FALL:
            self.frame_rate = 10
            self.sprite_sheet = Spritesheet(character.character_data[self.index]['fall'], character.character_data[self.index]['fallFrame'])
        elif status == KNEEL:
            self.frame_rate = 10
            self.sprite_sheet = Spritesheet(character.character_data[self.index]['kneel'], character.character_data[self.index]['kneelFrame'])
        elif status == RANGE_ATK:
            self.frame_rate = 8 // character.character_data[self.index]['attack2Frame']
            self.sprite_sheet = Spritesheet(character.character_data[self.index]['attack2'], character.character_data[self.index]['attack2Frame'])
        elif status == SPEC_ATK:
            self.frame_rate = 60 // character.character_data[self.index]['attack3Frame']
            self.sprite_sheet = Spritesheet(character.character_data[self.index]['attack3'], character.character_data[self.index]['attack3Frame'])
        elif status == DEAD:
            self.frame_rate = 60 // character.character_data[self.index]['deadFrame']
            self.sprite_sheet = Spritesheet(character.character_data[self.index]['dead'], character.character_data[self.index]['deadFrame'])

    def increaseframe(self):
        """增加動畫幀，根據 frame_rate 決定是否更新"""
        self.frame_counter += 1
        if self.frame_counter >= self.frame_rate:
            self.mask = pygame.mask.from_surface(self.image)
            if self.status == JUMP and self.frame == character.character_data[self.index]['jumpFrame'] - 1:
                return
            if self.status == ATK:
                self.attack_hit_check()  # 執行攻擊判定
                if self.frame == character.character_data[self.index]['attack1Frame'] - 1:
                    self.atkcollide = False
                    self.attacking = False
                    return
            if self.status == DEFEND and self.frame == character.character_data[self.index]['protectFrame'] - 1:
                return
            if self.status == RANGE_ATK and self.frame == character.character_data[self.index]['attack2Frame'] - 1:
                self.attacking = False
                return
            if self.status == SPEC_ATK and self.frame == character.character_data[self.index]['attack3Frame'] - 1:
                self.attacking = False
                return
            if self.status == DEAD and self.frame == character.character_data[self.index]['deadFrame'] - 1:
                return
            self.frame = (self.frame + 1) % self.sprite_sheet.num_sprites  # 更新幀
            self.frame_counter = 0  # 重置計數器

    def playerdead(self):
        self.changeStatus(DEAD)

    def handleinput(self, keys):
        if self.status == DEAD:
            return
        self.moving = False
        if self.movable:
            if self.jumping: # If you're in the air and press down, you will fall faster
                if keys[self.down]:  # 加速下落
                    self.y_velocity = MAX_FALL_SPEED
                    self.changeStatus(KNEEL)
            else:
                # If you're on the ground and press down, you will defend
                if keys[self.down]:  # 防禦狀態
                    self.defending = True
                    self.changeStatus(DEFEND)
                else:
                    self.defending = False
            # 移動邏輯
            move_delta = 0
            if not (keys[self.left] and keys[self.right]):
                if keys[self.left] and self.pos_x > BORDER[0]:
                    if not self.defending: move_delta = -self.velocity
                    self.facing_left = True
                elif keys[self.right] and self.pos_x < BORDER[1]:
                    if not self.defending: move_delta = self.velocity
                    self.facing_left = False
                if move_delta != 0:
                    #check velocity and leave trail
                    if self.velocity > character.character_data[self.index]['velocity'] and self.trail_counter > 1:
                        self.leave_trail()
                        self.trail_counter = 0
                    self.pos_x += move_delta
                    self.moving = True
                    if not self.jumping: self.changeStatus(WALK)
                    #self.image = pygame.transform.flip(self.image, not self.facing_left, False)
            # Jump logic with 0.5 second delay after last jump
            if keys[self.up] and self.jump_count < 2 and self.last_tick - self.last_jump_time > 0.4 and not self.defending:
                self.y_velocity = JUMP_STRENGTH
                self.jumping = True
                self.changeStatus(JUMP)
                self.jump_count += 1
                self.last_jump_time = self.last_tick  # Update last jump time
            # else:
            #     self.changeStatus(DEFEND)
            
        # attack kits
        if keys[self.atk_key]:
            self.attack()
            self.movelimittime = 15 # 0.25s can't move, run animation
        if keys[self.range_atk_key]:
            self.movelimittime = 8 # 0.13s can't move, run animation
            if self.ultbufftime > 0 and self.index == 0:
                #self.range_attack(self.other_player, self.projectiles_group, "back")
                self.range_attack("back")
            else:
                #self.range_attack(self.other_player, self.projectiles_group, "normal")
                self.range_attack("normal")
        if keys[self.special_key]:
            self.special_attack()    
        if keys[self.energy_atk_key]:
            self.power_attack()

            
 ## range attack for commander and samurai
 ## samurai: lower dmg but slow enemy
 ## commander: add spd

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, other_player, damage, direction, image_path, size, effect):
        super().__init__()
        self.base_image = pygame.image.load(image_path)
        self.base_image = pygame.transform.scale(self.base_image, (size,size))
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
        self.effect = effect
        
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
            if self.effect == "back":
                backdir = -1 if self.target.rect.x - self.rect.x > 0 else 1
                self.target.pos_x += 10 * backdir
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

