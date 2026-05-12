import pygame
import sys
import random

pygame.init()

screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Real Sparkle?")
clock = pygame.time.Clock()

player_w=50
player_h=50
player_x=400
hp=3
distance=0

bg=pygame.Surface((1280,720)) #sky
bg.fill('WHITE')

def create_platform(x):
    width=random.randint(400,800)
    height=random.randint(300,500)
    y=random.randint(430, 620)
    gd_surf=pygame.Surface((width,height))
    gd_surf.fill('BLACK')
    gd_rect=gd_surf.get_rect(topleft=(x,y))
    return {
        "surf":gd_surf,
        "rect":gd_rect
    }

def create_platform2(x): #upper-level platforms
    width=random.randint(400,800)
    height=random.randint(600,800)
    y=random.randint(200, 360)
    gd_surf=pygame.Surface((width,height))
    gd_surf.fill('GRAY')
    gd_rect=gd_surf.get_rect(topleft=(x,y))
    return {
        "surf":gd_surf,
        "rect":gd_rect
    }



platforms=[]
platforms2=[]

start_surf = pygame.Surface((900, 120)) #initial platform
start_surf.fill("BLACK")
start_rect = start_surf.get_rect(topleft=(0, 600))
platforms.append({
    "surf": start_surf,
    "rect": start_rect
})

x=start_rect.right+150
for i in range(5):
    platform=create_platform(x)
    platforms.append(platform)
    gap=random.randint(120,320)
    x=platform["rect"].right+gap

player=pygame.Surface((player_w,player_h)) #Sparkle
player.fill('RED')
player_rect=player.get_rect(midbottom=(player_x,start_rect.top))

vel_y=0
gravity=0.8
jump_power=-16
return_vel=8

jump_count=2

on_ground=False

platform_speed=5
target_speed=5
speed_up_every=1000 #speed up

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_w and jump_count > 0: #double jump
                vel_y = jump_power
                jump_count-=1
                on_ground=False

    old_bottom = player_rect.bottom #last position

    vel_y += gravity
    player_rect.y += vel_y
    on_ground=False
    touching_side=False
    
    distance+=platform_speed

    if distance >3000 and len(platforms2)==0: #creat upper-level platforms
        x2=1400
        for i in range(5):
            platform2=create_platform2(x2)
            platforms2.append(platform2)
            gap2=random.randint(120,320)
            x2=platform2["rect"].right+gap2
        
    if distance>=speed_up_every:
        target_speed+=0.1
        speed_up_every+=1000
    if platform_speed<target_speed:
        platform_speed+=0.01 #smoothing the process of speeding up

    for platform in platforms:
        rect=platform["rect"]
        rect.x-=platform_speed
        if player_rect.colliderect(rect):
            if old_bottom<= rect.top and vel_y>=0:
                player_rect.bottom=rect.top
                vel_y=0
                on_ground=True
                jump_count=2
            else:
                player_rect.right=rect.left
                touching_side=True
    platforms=[platform for platform in platforms if platform["rect"].right>0]
    #removing platforms that are off screen

    last_platform=platforms[-1]

    if last_platform["rect"].right<1280:
        gap=random.randint(120,320)
        new_x=last_platform["rect"].right+gap
        platforms.append(create_platform(new_x))

    for platform2 in platforms2:
        rect=platform2["rect"]
        rect.x -= platform_speed * 0.9
        if player_rect.colliderect(rect):
            if old_bottom<=rect.top and vel_y>=0:
                player_rect.bottom=rect.top
                vel_y=0
                on_ground=True
                jump_count=2
    platforms2=[platform2 for platform2 in platforms2 if platform2["rect"].right>0]
    
    if len(platforms2)>0:
        last_platform2 = platforms2[-1]
        if last_platform2["rect"].right<1280:
            gap2=random.randint(120,320)
            new_x2=last_platform2["rect"].right+gap2
            platforms2.append(create_platform2(new_x2))

    if not touching_side:
        if player_rect.x<player_x:
            player_rect.x+=2
            if player_rect.x > player_x:
                player_rect.x=player_x

    if player_rect.top>800:
        print("Game Over")
        pygame.quit()
        sys.exit()

    screen.blit(bg,(0,0))

    for platform2 in platforms2:
        screen.blit(platform2["surf"], platform2["rect"])
    for platform in platforms:
        screen.blit(platform["surf"], platform["rect"])
    
    screen.blit(player,player_rect)

    pygame.display.update()
    clock.tick(60)