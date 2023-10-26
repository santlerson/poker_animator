import pygame

card_resource_dict={}

for suit in range(4):
    for rank in range(2,15):
        card_resource_dict[(suit,rank)]=pygame.image.load('res/cards/{}/{}_border.bmp'.format(suit,rank))

card_back_foreground = pygame.image.load('res/back_bicycle_border.bmp')
card_back_resource = pygame.Surface(card_back_foreground.get_size())
card_back_resource.fill((255, 0, 0))
card_back_resource.blit(card_back_foreground, (0, 0))

banner = pygame.image.load("res/banner.bmp")
chad_shmoose = pygame.image.load("res/chad_shmoose_bot.bmp")


pygame.font.init()
font = pygame.font.Font("res/Grand9K Pixel.ttf", 8)
title_font = pygame.font.Font("res/Grand9K Pixel.ttf", 16)


chip_resource = pygame.image.load("res/chip.bmp")
#scale up twofold
large_chip_resource = pygame.transform.scale(chip_resource, (chip_resource.get_width()*2, chip_resource.get_height()*2))
big_blind_resource = pygame.image.load("res/big_blind.bmp")
small_blind_resource = pygame.image.load("res/small_blind.bmp")
dealer_resource = pygame.image.load("res/dealer.bmp")
default_avatars =[pygame.image.load("res/default_avatar.bmp")]
CHIP_HEIGHT = chip_resource.get_height()

CHIP_WIDTH = chip_resource.get_width()