import math
import time
import random
import pygame
from enum import Enum
import numpy as np

FPS = 60
WIDTH = 1280
HEIGHT = 720
BACKGROUND_COLOR = (20, 20, 20)

screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption('STL')



class cell_type(Enum):
    SPACE = 1
    STATION = 2
    PLANET = 3

class cell_class:
    CELL_SIZE = 30
    def __init__(self, type=cell_type.SPACE):
        self.type = type
        self.ground = {"type":"", "variant_num":0}
        self.ground_cover = {"type":"", "variant_num":0}
        self.main = ""
        self.roof = ""

class world_type(Enum):
    SHIP = 1
    LAND = 2

class world_class:
    active_worlds = []
    world_num = 0
    def __init__(self, type=world_type.SHIP, rows=100, cols=100):

        #design stuff that needs to be somewhere else
        self.room_size = 40
        self.room_color = (220, 220, 220)
        self.room_color = (102, 81, 24)

        self.type = type
        self.row_num = rows
        self.col_num = cols

        self.max_x = self.col_num * self.room_size
        self.max_y = self.row_num * self.room_size

        # center the world
        self.offset_x = (WIDTH - self.room_size * self.col_num) / 2
        self.offset_y = (HEIGHT - self.room_size * self.row_num) / 2

        # Add the new world to the active list
        self.id = world_class.world_num
        world_class.active_worlds.append(world_class.world_num)
        world_class.world_num += 1

        # Make an empty grid
        self.cell = np.empty( (self.col_num, self.row_num), dtype=object)
        for y in range(self.row_num):
            for x in range(self.col_num):
                self.cell[x, y] = cell_class()

        # Store the players in this world
        self.avatar_list = []

    def map_to_graph(self):
        pass

    def draw_world(self):
        for y in range(self.row_num):
            for x in range(self.col_num):
                this_x = self.offset_x + x * self.room_size
                this_y = self.offset_y + y * self.room_size

                # ground layer
                screen.blit(img_asset[self.cell[x][y].ground["type"]][self.cell[x][y].ground["variant_num"]][self.room_size], ([this_x, this_y]))
                #pygame.draw.rect(screen, self.room_color, (this_x + 1, this_y + 1, self.room_size - 2, self.room_size - 2))

                # ground cover layer
                if self.cell[x][y].ground_cover["type"] != "":
                    screen.blit( img_asset[self.cell[x][y].ground_cover["type"]] [self.cell[x][y].ground_cover["variant_num"]] [self.room_size], ([this_x, this_y]))

        # player layer
        for this_avatar in self.avatar_list:
            this_avatar.move_avatar()

            # facing block
            this_x = self.offset_x + this_avatar.col * self.room_size
            this_y = self.offset_y + this_avatar.row * self.room_size
            if this_avatar.facing == "left" and this_avatar.col > 0:
                this_x = self.offset_x + (this_avatar.col - 1) * self.room_size
            elif this_avatar.facing == "right" and this_avatar.col < (self.col_num - 1):
                this_x = self.offset_x + (this_avatar.col + 1) *self.room_size
            elif this_avatar.facing == "up" and this_avatar.row > 0:
                this_y = self.offset_y + (this_avatar.row - 1) * self.room_size
            elif this_avatar.facing == "down" and this_avatar.row < (self.row_num - 1):
                this_y = self.offset_y + (this_avatar.row + 1) * self.room_size
            #pygame.draw.rect(screen, (150, 150, 200), (this_x + 1, this_y + 1, self.room_size - 2, self.room_size - 2))

            # current col/row
            this_x = self.offset_x + this_avatar.col * self.room_size
            this_y = self.offset_y + this_avatar.row * self.room_size
            #pygame.draw.rect(screen, (200, 150, 150), (this_x + 1, this_y + 1, self.room_size - 2, self.room_size - 2))

            this_avatar.draw_avatar()

    def to_global_coor(self, coor):
        return [self.offset_x + coor[0] - (self.room_size / 2), self.offset_y + coor[1] - self.room_size]

    def to_local_coor(self, coor):
        return[coor[0] - self.offset_x, coor[1] - self.offset_y]


world = []
world.append( world_class(rows=12, cols=20) )

class avatar_class:
    WALK_CYCLE = ["idle", "left1", "left2", "idle", "right1", "right2"]
    def __init__(self, world_num):
        self.world = world_num
        self.row = 0
        self.col = 0
        self.x = 0
        self.y = 0
        self.facing = "left"
        self.speed = 50
        self.moving = False
        self.current_pose = self.WALK_CYCLE[0]
        self.pose_counter = 0
        self.pose_index_counter = 0
        self.new_x = 0
        self.new_y = 0

    def draw_avatar(self):
        screen.blit(avatar["goblin"][self.facing][self.WALK_CYCLE[self.pose_index_counter % 6]][world[self.world].room_size], (world[self.world].to_global_coor([self.x, self.y])))

    def move_avatar(self):
        if self.moving:
            self.pose_counter += 1
            if int(self.pose_counter % (self.speed / 6)) == 0:
                self.pose_index_counter += 1

            distance_x = self.new_x - self.x
            distance_y = self.new_y - self.y
            angle = math.atan2(distance_y, distance_x)
            total_distance = math.dist((self.new_x, self.new_y), (self.x, self.y))
            distance_travelled = (self.speed / 1000) * world[self.world].room_size

            distance_travelled_x = distance_travelled * math.cos(angle)
            distance_travelled_y = distance_travelled * math.sin(angle)

            # Move the avatar, or snap it to the end
            if total_distance <= (2 * distance_travelled):
                self.moving = False
                self.x = self.new_x
                self.y = self.new_y
                self.pose_index_counter = 0
            else:
                self.x += distance_travelled_x
                self.y += distance_travelled_y

            # Figure out which way to face the avatar
            if abs(distance_x) < abs(distance_y):
                if distance_y < 0:
                    self.facing = "up"
                else:
                    self.facing = "down"
            else:
                if distance_x < 0:
                    self.facing = "left"
                else:
                    self.facing = "right"

            # Figure out which row/col the avatar is in
            self.col = math.floor(self.x / world[self.world].room_size)
            self.row = math.floor(self.y / world[self.world].room_size)

    def set_position(self, coor):
        self.x = coor[0]
        self.y = coor[1]

    def direct_avatar(self, coor):
        if (coor[0] > 0 and coor[1] > 0 and coor[0] < world[self.world].max_x and coor[1] < world[self.world].max_y ):
            self.moving = True
            self.pose_counter = 0
            self.pose_index_counter = 0
            self.new_x = coor[0]
            self.new_y = coor[1]

def load_sprite_sheet(sheet_name):
    sprite_sheet = pygame.image.load("img/" + sheet_name + "_sprite.png").convert_alpha()
    avatar[sheet_name] = {}
    for this_direction in DIRECTION_LIST:
        avatar[sheet_name][this_direction] = {}
        for this_pose in POSE_LIST:
            avatar[sheet_name][this_direction][this_pose] = {}

    for direction_num, this_direction in enumerate(DIRECTION_LIST):
        for pose_num, this_pose in enumerate(POSE_LIST):
            rect = pygame.Rect(pose_num * SPRITE_FULL_SIZE, direction_num * SPRITE_FULL_SIZE, SPRITE_FULL_SIZE, SPRITE_FULL_SIZE)
            avatar[sheet_name][this_direction][this_pose]["full"] = pygame.Surface(rect.size).convert_alpha()
            avatar[sheet_name][this_direction][this_pose]["full"].fill((255, 255, 255, 0), special_flags=pygame.BLEND_RGBA_MULT)
            avatar[sheet_name][this_direction][this_pose]["full"].blit(sprite_sheet, (0, 0), rect)

            for this_size in SIZE_LIST:
                avatar[sheet_name][this_direction][this_pose][this_size] = pygame.transform.scale( avatar[sheet_name][this_direction][this_pose]["full"], (this_size, this_size))

def load_image_sprite_sheet(sheet_name, num_of_variants):
    sprite_sheet = pygame.image.load("img/" + sheet_name + "_sprite.png").convert_alpha()
    img_asset[sheet_name] = {}
    for variant_num in range(num_of_variants):
        img_asset[sheet_name][variant_num] = {}
        rect = pygame.Rect(variant_num * SPRITE_FULL_SIZE, 0, SPRITE_FULL_SIZE, SPRITE_FULL_SIZE)
        img_asset[sheet_name][variant_num]["full"] = pygame.Surface(rect.size).convert_alpha()
        img_asset[sheet_name][variant_num]["full"].fill((255, 255, 255, 0), special_flags=pygame.BLEND_RGBA_MULT)
        img_asset[sheet_name][variant_num]["full"].blit(sprite_sheet, (0, 0), rect)

        for this_size in SIZE_LIST:
            img_asset[sheet_name][variant_num][this_size] = pygame.transform.scale(img_asset[sheet_name][variant_num]["full"], (this_size, this_size))


# Global variables
avatar = {}
img_asset = {}


# Load image assets
SPRITE_FULL_SIZE = 46
DIRECTION_LIST = ["right", "left", "down", "up"]
POSE_LIST = ["idle", "left1", "left2", "right1", "right2"]
SIZE_LIST = [20, 30, 40]

load_sprite_sheet("goblin")
load_image_sprite_sheet("rock", 3)
load_image_sprite_sheet("dirt", 4)


# Load the world
player = avatar_class(world_num=0)
world[0].avatar_list.append( player )
player.set_position([0,0])

for x in range(world[0].col_num):
    for y in range(world[0].row_num):
        world[0].cell[x, y].ground["type"] = "dirt"
        world[0].cell[x, y].ground["variant_num"] = random.choice(list(img_asset["dirt"]))

world[0].cell[5, 1].ground_cover["type"] = "rock"
world[0].cell[5, 1].ground_cover["variant_num"] = random.choice(list( img_asset["rock"] ))
world[0].cell[5, 2].ground_cover["type"] = "rock"
world[0].cell[5, 2].ground_cover["variant_num"] = random.choice(list( img_asset["rock"] ))
world[0].cell[5, 3].ground_cover["type"] = "rock"
world[0].cell[5, 3].ground_cover["variant_num"] = random.choice(list( img_asset["rock"] ))
world[0].cell[5, 4].ground_cover["type"] = "rock"
world[0].cell[5, 4].ground_cover["variant_num"] = random.choice(list( img_asset["rock"] ))
world[0].cell[5, 5].ground_cover["type"] = "rock"
world[0].cell[5, 5].ground_cover["variant_num"] = random.choice(list( img_asset["rock"] ))
world[0].cell[4, 4].ground_cover["type"] = "rock"
world[0].cell[4, 4].ground_cover["variant_num"] = random.choice(list( img_asset["rock"] ))
world[0].cell[4, 5].ground_cover["type"] = "rock"
world[0].cell[4, 5].ground_cover["variant_num"] = random.choice(list( img_asset["rock"] ))
world[0].cell[3, 5].ground_cover["type"] = "rock"
world[0].cell[3, 5].ground_cover["variant_num"] = random.choice(list( img_asset["rock"] ))


clock = pygame.time.Clock()
running = True
while running:

    # Set the FPS
    clock.tick(FPS)

    # Quit the game
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            player.direct_avatar(world[0].to_local_coor(event.pos))


    # Fill the background
    screen.fill(BACKGROUND_COLOR)

    # Draw the current world
    world[0].draw_world()

    # Flip
    pygame.display.flip()
