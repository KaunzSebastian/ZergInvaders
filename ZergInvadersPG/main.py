import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Set up the display
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE | pygame.SRCALPHA)
pygame.display.set_caption("Zerg Invaders")

# Load the background image
def load_background_image(background_image):
    background_image = pygame.image.load(background_image)
    background_image = pygame.transform.scale(background_image, (screen_width, screen_height))
    return background_image
background_image = load_background_image("images/map_background_image.jpg")

# Center point
center_x = math.ceil(screen_width / 2)
center_y = math.ceil(screen_height / 2)

# Corpse class
class Corpse:
    def __init__(self, x, y, sprite, image):
        self.x = x
        self.y = y
        self.sprites = {"zergling": [410, 548, 65, 53], "hydralisk": [437, 233, 97, 71]}
        self.sprite = self.sprites[sprite]
        self.images = {"zergling": "images/ZerglingSprites.png", "hydralisk": "images/HydraliskSprites.png"}
        self.image = pygame.image.load(self.images[image]).convert_alpha()
        self.timer = 120

    def redraw_sprite(self):
        source_rectangle = pygame.Rect(self.sprite[0], self.sprite[1], self.sprite[2], self.sprite[3])
        cropped_surface = pygame.Surface((source_rectangle.width, source_rectangle.height), pygame.SRCALPHA)
        cropped_surface.blit(self.image, (0, 0), source_rectangle)
        self.mask = pygame.mask.from_surface(cropped_surface)
        screen.blit(cropped_surface, (self.x - self.sprite[2] // 4, self.y - self.sprite[3] // 4))

# Bullet class
class Bullet:
    def __init__(self, x, y, trajectory):
        self.image = pygame.image.load("images/bullet_sprite.png")
        self.x = x - self.image.get_width() // 2
        self.y = y - self.image.get_height() // 2
        self.trajectory = trajectory
        self.mask = pygame.mask.from_surface(self.image)
        self.out_of_bounds = False
        self.damage = 10
        self.hit = False
    
    # Draw the bullet
    def redraw_sprite(self):
        screen.blit(self.image, (self.x, self.y))

    # Move the bullet
    def move_sprite(self):
        if (self.y > 0) and (self.y < screen_height) and (self.x > 0) and (self.x < screen_width):
            if (self.trajectory == "north"):
                self.y += -12
            elif (self.trajectory == "northeast"):
                self.y += -8
                self.x += 8
            elif (self.trajectory == "northwest"):
                self.y += -8
                self.x += -8
            elif (self.trajectory == "east"):
                self.x += 12
            elif (self.trajectory == "west"):
                self.x += -12
            elif (self.trajectory == "southeast"):
                self.y += 8
                self.x += 8
            elif (self.trajectory == "southwest"):
                self.y += 8
                self.x += -8
            elif (self.trajectory == "south"):
                self.y += 12
        else:
            self.out_of_bounds = True

# Acid class
class Acid:
    def __init__(self, x, y):
        self.image = pygame.image.load("images/acid_sprite.png")
        self.x = x
        self.y = y
        self.mask = pygame.mask.from_surface(self.image)
        self.out_of_bounds = False
        self.damage = 10
        self.hit = False

    # Draw the acid
    def redraw_sprite(self):
        screen.blit(self.image, (self.x, self.y))

    # Move the acid
    def move_sprite(self):
        if(self.y < screen_height):
            self.y += 12
        else:
            self.out_of_bounds = True
    
# Entity lists
bullets = []
acids = []
zerglings = []
hydralisks = []
corpses = []

# Zergling class
class Zergling:
    def __init__(self, orientation, action, x, y):
        self.x = x
        self.y = y
        self.image = pygame.image.load("images/ZerglingSprites.png").convert_alpha()
        self.orientations = {"north": [346, 40]}
        self.actions = {"standing": [2, 39], "running1": [44, 39], "running2": [86, 39], "running3": [128, 39], "running4": [170, 39], "running5": [212, 39], "running6": [254, 39], "attacking1": [296, 39], "attacking2": [338, 39], "attacking3": [380, 39], "attacking4": [422, 39], "attacking5": [464, 39]}
        self.orientation = self.orientations[orientation]
        self.action = self.actions[action]
        self.running_stage = 0
        self.attack_stage = 0
        self.delay = 0
        self.cooldown = 0
        self.life = 20
        self.damage = 10

    # Attack sequence
    def attack(self):
        self.running_stage = 0
        if (self.cooldown < 1):
            self.cooldown += 1
        else:
            self.cooldown = 0
            if (self.attack_stage < 5):
                self.attack_stage += 1
                self.action = self.actions[f"attacking{self.attack_stage}"]
            else:
                self.attack_stage = 0
                self.action = self.actions[f"standing"]

    # Move the Zergling sprite
    def move_sprite(self, x_change, y_change):
        self.attack_stage = 0
        if (self.delay < 3):
            self.delay += 1
        else:
            self.delay = 0
            self.x += x_change
            self.y += y_change
            if (self.running_stage < 6):
                self.running_stage += 1
                self.action = self.actions[f"running{self.running_stage}"]
            else:
                self.running_stage = 0
                self.action = self.actions[f"standing"]

    def redraw_sprite(self):
        source_rectangle = pygame.Rect(self.orientation[0], self.action[0], self.orientation[1], self.action[1])
        cropped_surface = pygame.Surface((source_rectangle.width, source_rectangle.height), pygame.SRCALPHA)
        cropped_surface.blit(self.image, (0, 0), source_rectangle)
        self.mask = pygame.mask.from_surface(cropped_surface)
        screen.blit(cropped_surface, (self.x, self.y))

# Hydralisk class
class Hydralisk:
    def __init__(self, orientation, action, x, y):
        self.x = x
        self.y = y
        self.image = pygame.image.load("images/HydraliskSprites.png").convert_alpha()
        self.orientations = {"north": [362, 42]}
        self.actions = {"standing": [2, 55], "running1": [60, 55], "running2": [118, 55], "running3": [176, 55], "running4": [234, 55], "running5": [292, 55], "running6": [350, 55], "attacking1": [408, 55], "attacking2": [466, 55], "attacking3": [524, 55], "attacking4": [582, 55], "attacking5": [640, 55]}
        self.orientation = self.orientations[orientation]
        self.action = self.actions[action]
        self.running_stage = 0
        self.attack_stage = 0
        self.delay = 0
        self.cooldown = 0
        self.life = 30
        self.damage = 10
        self.attacking = False

    # Attack sequence
    def attack(self):
        self.attacking = True
        self.running_stage = 0
        if (self.cooldown < 2):
            self.cooldown += 1
        else:
            self.cooldown = 0
            if (self.attack_stage < 5):
                self.attack_stage += 1
                self.action = self.actions[f"attacking{self.attack_stage}"]
            elif (self.attack_stage < 8):
                self.attack_stage += 1
            else:
                acid_x = self.x + 13
                acid_y = self.y
                create_acid(acid_x, acid_y)
                self.attack_stage = 0
                self.action = self.actions[f"standing"]
                self.attacking = False

    # Move the Hydralisk sprite
    def move_sprite(self, x_change, y_change):
        if (self.delay < 3):
            self.delay += 1
        else:
            self.delay = 0
            self.x += x_change
            self.y += y_change
            if (self.running_stage < 6):
                self.running_stage += 1
                self.action = self.actions[f"running{self.running_stage}"]
            else:
                self.running_stage = 0
                self.action = self.actions[f"standing"]

    def redraw_sprite(self):
        source_rectangle = pygame.Rect(self.orientation[0], self.action[0], self.orientation[1], self.action[1])
        cropped_surface = pygame.Surface((source_rectangle.width, source_rectangle.height), pygame.SRCALPHA)
        cropped_surface.blit(self.image, (0, 0), source_rectangle)
        self.mask = pygame.mask.from_surface(cropped_surface)
        screen.blit(cropped_surface, (self.x, self.y))

# Marine class
class Marine:
    def __init__(self, action, orientation, x, y, walking_stage, west, right):
        self.action = action
        self.orientation = orientation
        self.x = x
        self.y = y
        self.walking_stage = walking_stage
        self.west = west
        self.right = right
        self.aiming_stage = 0
        self.cooldown = 0
        self.aiming = False
        self.max_life = 50
        self.life = self.max_life

    # Move the Marine sprite
    def move_sprite(self, orientation, west, x_change, y_change):
        self.aiming_stage = 0
        self.cooldown = 0
        self.action = 5
        self.orientation = orientation
        self.west = west
        self.x += x_change
        self.y += y_change
        if self.right == True:
            if (self.walking_stage < 9):
                self.walking_stage += 1
            else:
                self.right = False
        else:
            if (self.walking_stage > 1):
                self.walking_stage -= 1
            else:
                self.right = True

    # Aim the gun
    def aim_gun(self):
        self.aiming_stage += 1
        if (self.aiming_stage == 3):
            self.action = 2
        elif (self.aiming_stage == 6):
            self.action = 3
        elif (self.aiming_stage == 8):
            self.aiming = False
        elif (self.aiming_stage >= 9):
            self.shoot_gun()

    # Shoot the gun
    def shoot_gun(self):
        self.cooldown += 1
        if (self.cooldown <= 10):
            if (self.cooldown == 1):
                if (self.orientation == 1):
                    bullet_x = self.x
                    bullet_y = self.y - self.image.get_height() // 2 - 8
                    bullet_trajectory = "north"
                elif (self.orientation == 2):
                    if (self.west):
                        bullet_x = self.x - self.image.get_width() // 2 - 6
                        bullet_y = self.y - self.image.get_height() // 2 - 4
                        bullet_trajectory = "northwest"
                    else:
                        bullet_x = self.x + self.image.get_width() // 2 + 6
                        bullet_y = self.y - self.image.get_height() // 2 - 4
                        bullet_trajectory = "northeast"
                elif (self.orientation == 3):
                    if (self.west):
                        bullet_x = self.x - self.image.get_width() // 2 - 6
                        bullet_y = self.y
                        bullet_trajectory = "west"
                    else:
                        bullet_x = self.x + self.image.get_width() // 2 + 6
                        bullet_y = self.y
                        bullet_trajectory = "east"
                elif (self.orientation == 4):
                    if (self.west):
                        bullet_x = self.x - self.image.get_width() // 2 - 6
                        bullet_y = self.y + self.image.get_height() // 2
                        bullet_trajectory = "southwest"
                    else:
                        bullet_x = self.x + self.image.get_width() // 2 + 6
                        bullet_y = self.y + self.image.get_height() // 2
                        bullet_trajectory = "southeast"
                elif (self.orientation == 5):
                    bullet_x = self.x
                    bullet_y = self.y + self.image.get_height() // 2 + 4
                    bullet_trajectory = "south"
                create_bullet(bullet_x, bullet_y, bullet_trajectory)
            self.action = 4
        elif (self.cooldown == 20):
            self.cooldown = 0
            self.aiming = False
        else:
            self.action = 3

    # Load the Marine sprite
    def redraw_sprite(self):
        walking_stages = ["", "9", "8", "7", "6", "1", "2", "3", "4", "5"]
        actions = ["", "standing", "ready", "aim", "fire", "walking", "death"]
        orientations = ["", "north", "northeast", "east", "southeast", "south"]
        if self.action == 5:
            self.image = pygame.image.load(f"images/MarineSprites/marine_{actions[self.action]}_{orientations[self.orientation]}{walking_stages[self.walking_stage]}.png")
        elif self.action == 6:
            self.image = pygame.image.load(f"images/MarineSprites/marine_death.png")
        else:
            self.image = pygame.image.load(f"images/MarineSprites/marine_{actions[self.action]}_{orientations[self.orientation]}.png")
        if (self.west):
            self.image = pygame.transform.flip(self.image, True, False)
        self.mask = pygame.mask.from_surface(self.image)
        element_x = self.x - self.image.get_width() // 2
        element_y = self.y - self.image.get_height() // 2
        screen.blit(self.image, (element_x, element_y))

# Level class
class Level:
    def __init__(self, zergling_count, hydralisk_count, life):
        self.zergling_count = zergling_count
        self.hydralisk_count = hydralisk_count
        self.life = life
        self.lost = False
        self.lost_timer = 120
        self.victory = False
        self.victory_timer = 120

    def play(self):
        running = True
        player.redraw_sprite()
        while running:
            
            # Limit the frame rate
            clock.tick(30)

            # Handle loss and victory
            if (self.lost_timer == 0):
                background_image = load_background_image("images/defeat_background_image.png")
                screen.blit(background_image, (0, 0))
                pygame.display.update()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                pygame.display.flip()
            elif (self.victory_timer == 0):
                background_image = load_background_image("images/victory_background_image.jpg")
                screen.blit(background_image, (0, 0))
                pygame.display.update()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                pygame.display.flip()
            else:
                # Redraw window
                redraw_window()

                # Victory countdown
                if (self.victory == True):
                    if (self.victory_timer > 0):
                        self.victory_timer -= 1

                # Defeat countdown
                if (self.lost == True):
                    if (self.lost_timer > 0):
                        self.lost_timer -= 1

                # Corpse A.I.
                for corpse in corpses:
                    if (corpse.timer > 0):
                        corpse.timer -= 1
                        corpse.redraw_sprite()
                    else:
                        corpses.remove(corpse)

                # Redraw player
                player.redraw_sprite()
                
                # Zergling A.I.
                for zergling in zerglings:
                    zergling.redraw_sprite()
                    if (collide(zergling, player)):
                        zergling.attack()
                        if (zergling.action == [464, 39]) and (zergling.cooldown == 0):
                            player.life -= zergling.damage
                            if (player.life <= 0):
                                player.action = 6
                    else:
                        zergling.move_sprite(0, 4)
                    if (zergling.y > screen_height):
                        self.life -= zergling.life
                        zerglings.remove(zergling)
                        self.zergling_count -= 1

                # Hydralisk A.I.
                for hydralisk in hydralisks:
                    hydralisk.redraw_sprite()
                    if (hydralisk.attacking == True):
                        hydralisk.attack()
                    else:
                        chance = random.randint(1, 150)
                        if (chance == 1) and (hydralisk.y > 0):
                            hydralisk.attack()
                        else:
                            hydralisk.move_sprite(0, 4)
                            if (hydralisk.y > screen_height):
                                self.life -= hydralisk.life
                                hydralisks.remove(hydralisk)
                                self.hydralisk_count -= 1

                # Check bullets
                for bullet in bullets:
                    if (bullet.out_of_bounds == True):
                        bullets.remove(bullet)
                    else:
                        bullet.move_sprite()
                        bullet.redraw_sprite()
                        for zergling in zerglings:
                            if (collide(bullet, zergling)):
                                bullet.hit = True
                                zergling.life -= bullet.damage
                                if (zergling.life <= 0):
                                    create_corpse(zergling.x, zergling.y, "zergling", "zergling")
                                    zerglings.remove(zergling)
                                    self.zergling_count -= 1
                        for hydralisk in hydralisks:
                            if (collide(bullet, hydralisk)):
                                bullet.hit = True
                                hydralisk.life -= bullet.damage
                                if (hydralisk.life <= 0):
                                    create_corpse(hydralisk.x, hydralisk.y, "hydralisk", "hydralisk")
                                    hydralisks.remove(hydralisk)
                                    self.hydralisk_count -= 1
                        if (bullet.hit == True):
                            bullets.remove(bullet)

                # Check acids
                for acid in acids:
                    if (acid.out_of_bounds == True):
                        acids.remove(acid)
                    else:
                        acid.move_sprite()
                        acid.redraw_sprite()
                        if (collide(acid, player)):
                            acid.hit = True
                            player.life -= acid.damage
                            if (player.life <= 0):
                                player.action = 6
                        if (acid.hit == True):
                            acids.remove(acid)

                # Handle events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                if (player.life <= 0) or (self.life <= 0):
                    self.lost = True
                elif (self.zergling_count == 0) and (self.hydralisk_count == 0):
                    self.victory = True
                keys = pygame.key.get_pressed()
                if (self.lost == False):
                    if (player.aiming == True):
                        player.aim_gun()
                    elif (keys[pygame.K_LEFT]):
                        player.aiming = True
                        player.aim_gun()
                    elif (keys[pygame.K_w]) and (keys[pygame.K_d]) and (player.y > 0) and (player.x < screen_width):
                        player.move_sprite(2, False, 2, -2)
                    elif (keys[pygame.K_w]) and (keys[pygame.K_a]) and (player.y > 0) and (player.x > 0):
                        player.move_sprite(2, True, -2, -2)
                    elif (keys[pygame.K_s]) and (keys[pygame.K_d]) and (player.y < screen_height) and (player.x < screen_width):
                        player.move_sprite(4, False, 2, 2)
                    elif (keys[pygame.K_s]) and (keys[pygame.K_a]) and (player.y < screen_height) and (player.x > 0):
                        player.move_sprite(4, True, -2, 2)
                    elif (keys[pygame.K_w]) and (player.y > 0):
                        player.move_sprite(1, False, 0, -3)
                    elif (keys[pygame.K_d]) and (player.x < screen_width):
                        player.move_sprite(3, False, 3, 0)
                    elif (keys[pygame.K_s]) and (player.y < screen_height):
                        player.move_sprite(5, False, 0, 3)
                    elif (keys[pygame.K_a]) and (player.x > 0):
                        player.move_sprite(3, True, -3, 0)
                    else:
                        player.walking_stage = 5
                        player.action = 1
                        player.right = True
                        player.aiming_stage = 0
                        player.cooldown = 0
                        player.aiming = False

                # Update the display
                pygame.display.flip()

# Create a clock object to control the frame rate
clock = pygame.time.Clock()

# Create the levels
level1 = Level(zergling_count = 9, hydralisk_count = 3, life = 150)

# Create player character
player = Marine(action = 1, orientation = 1, x = center_x, y = center_y, walking_stage = 0, west = False, right = True)

# # Draw the background and element images
# screen.blit(background_image, (0, 0))
# player.redraw_sprite()

# Redraw window function
def redraw_window():
    screen.blit(background_image, (0, 0))
    pygame.display.update()

# Create zergling function
def create_zergling(orientation, action, x, y):
    zergling = Zergling(orientation, action, x, y)
    zerglings.append(zergling)

# Create hydralisk function
def create_hydralisk(orientation, action, x, y):
    hydralisk = Hydralisk(orientation, action, x, y)
    hydralisks.append(hydralisk)

# Create zerglings
for i in range(level1.zergling_count):
    create_zergling("north", "standing", random.randrange(50, screen_width - 100), random.randrange(-1200, -100))

# Create hydralisks
for i in range(level1.hydralisk_count):
    create_hydralisk("north", "standing", random.randrange(50, screen_width - 100), random.randrange(-1200, -100))

# Create bullet function
def create_bullet(bullet_x, bullet_y, bullet_trajectory):
    bullet = Bullet(bullet_x, bullet_y, bullet_trajectory)
    bullets.append(bullet)

# Create acid function
def create_acid(acid_x, acid_y):
    acid = Acid(acid_x, acid_y)
    acids.append(acid)

# Create corpse function
def create_corpse(x, y, sprite, image):
    corpse = Corpse(x, y, sprite, image)
    corpses.append(corpse)

# Collide function
def collide(object1, object2):
    offset_x = object2.x - object1.x
    offset_y = object2.y - object1.y
    return object1.mask.overlap(object2.mask, (offset_x, offset_y)) != None

# Game loop
def main():
    level1.play()

# Start the game
main()

# Quit the game
pygame.quit()