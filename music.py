import pygame
from const import soundpack
class Music:
    def __init__(self, filename):
        self.bgm = pygame.mixer.music.load(filename)
        self.filename = filename
        self.jump = pygame.mixer.Sound(soundpack["jump"])
        self.atk = pygame.mixer.Sound(soundpack["atk"])
        self.arrow = pygame.mixer.Sound(soundpack["arrow"])
        self.dead = pygame.mixer.Sound(soundpack["dead"])
        self.defend = pygame.mixer.Sound(soundpack["defend"])
        self.archerult = pygame.mixer.Sound(soundpack["archult"])
        self.commanderult = pygame.mixer.Sound(soundpack["comult"])
        self.samuraiult = pygame.mixer.Sound(soundpack["samult"])
        self.comspec = pygame.mixer.Sound(soundpack["comspec"])
        

    def stop(self):
        pygame.mixer.music.stop()

    def pause(self):
        pygame.mixer.music.pause()

    def unpause(self):
        pygame.mixer.music.unpause()

    def changebgm(self, filename):
        pygame.mixer.music.load(filename)
        self.filename = filename

    def play(self, sound = "bgm"):
        if sound == "bgm":
            pygame.mixer.music.play(-1)
        elif sound == "jump":
            self.jump.set_volume(0.5)
            self.jump.play()
        elif sound == "atk":
            self.atk.play()
        elif sound == "arrow":
            self.arrow.play()
        elif sound == "dead":
            self.dead.play()
        elif sound == "defend":
            self.defend.play()
        elif sound == "archult":
            self.archerult.play()
        elif sound == "comult":
            self.commanderult.play()
        elif sound == "samult":
            self.samuraiult.play()
        elif sound == "comspec":
            self.comspec.play()
        else:
            print("sound not found")