
# 設定遊戲畫面
WIDTH, HEIGHT = 1200, 600
# 字體
FONT = "font/Modak-Regular.ttf"
FONT2 = "font/LowresPixel-Regular.otf"
# 顏色設置
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GRAY = (130, 130, 130)
GRAY1 = (112, 112, 112)
GRAY2 = (222, 222, 222)
FPS = 60
# 設定遊戲的增減速度
HEALTH_CHANGE_SPEED = 2
ENERGY_CHANGE_SPEED = 1
# 重力與跳躍設定
GRAVITY = 0.5
JUMP_STRENGTH = -15
MAX_FALL_SPEED = 20
ATTACK_COOLDOWN = 0.5
ENERGY_FULL = 100
# 設定玩家狀態
IDLE = 0
WALK = 1
JUMP = 2
DEFEND = 3
FALL = 4
KNEEL = 5
NONE = 6
ATK = 7
SPEC_ATK = 8
RANGE_ATK = 9
POW_ATK = 10
DEAD = 11
# 邊界
BORDER = (-200, 1400)
#sound pack
soundpack = { "jump": "sound/jump.mp3", "atk": "sound/atk.mp3",
              "dead": "sound/dead.mp3", "defend": "sound/block.mp3",
              "bgm1": "sound/bgm1.mp3", "bgm2": "sound/bgm2.mp3",
              "comult": "sound/comult.mp3", "archult": "sound/archult.mp3",
              "samult": "sound/samult.mp3", "arrow": "sound/arrow.mp3",
              "comspec": "sound/comspec.mp3",}