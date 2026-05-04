import pygame
import sys

pygame.init()

screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Real Sparkle?")
clock = pygame.time.Clock()

player_w=50
player_h=50
player_x=400
hp=3

bg=pygame.Surface((1280,720)) #sky
bg.fill('WHITE')
gd=pygame.Surface((1280,600)) #ground
gd.fill('BLACK')
player=pygame.Surface((player_w,player_h))
player.fill('RED')
player_rect=player.get_rect(midbottom=(player_x,600))
obstacle=pygame.Surface((50,50))
obstacle.fill('BLACK')
obstacle_rect=obstacle.get_rect(midbottom=(1300,600))

vel_y=0
gravity=0.8
jump_power=-16
return_vel=8

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
    screen.blit(obstacle,obstacle_rect)
    pygame.display.update()
    clock.tick(60)

    keys = pygame.key.get_pressed()

    if keys[pygame.K_w] and on_ground: #Jump
        vel_y = jump_power
        on_ground = False
    
    old_bottom = player_rect.bottom #last position

    vel_y += gravity
    player_rect.y += vel_y
    
    if player_rect.bottom >= ground_y: #Ground Collision(Standing)
       player_rect.bottom = ground_y
       vel_y = 0
       on_ground = True

    obstacle_rect.x -= 5 #Obstacles moving
    if obstacle_rect.right < 0:
        obstacle_rect.x = 1300
    if player_rect.colliderect(obstacle_rect): #Obstacles pushing
        if old_bottom <= obstacle_rect.top and vel_y >= 0:
            player_rect.bottom = obstacle_rect.top
            vel_y = 0
            on_ground = True
        else:
            player_rect.right=obstacle_rect.left
    
    else:
        if player_rect.x<player_x:
            player_rect.x+=2
            if player_rect.x > player_x:
                player_rect.x=player_x