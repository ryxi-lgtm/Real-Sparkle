import pygame
import sys

pygame.init()

screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Real Sparkle?")
clock = pygame.time.Clock()

player_w=50
player_h=50

bg=pygame.Surface((1280,720)) #sky
bg.fill('WHITE')
gd=pygame.Surface((1280,600)) #ground
gd.fill('BLACK')
player=pygame.Surface((player_w,player_h))
player.fill('RED')
player_rect=player.get_rect(midbottom=(100,600))

vel_y=0
gravity=0.8
jump_power=-16

ground_y=600
on_ground=False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    screen.blit(bg,(0,0))
    screen.blit(gd,(0,600))
    screen.blit(player,player_rect)
    pygame.display.update()
    clock.tick(60)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        player_rect.left -= 5

    if keys[pygame.K_d]:
        player_rect.left += 5

    if keys[pygame.K_w] and on_ground:
        vel_y = jump_power
        on_ground = False
    
    vel_y += gravity
    player_rect.y += vel_y
    
    if player_rect.bottom >= ground_y:
       player_rect.bottom = ground_y
       vel_y = 0
       on_ground = True