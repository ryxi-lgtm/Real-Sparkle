import pygame
import sys
import random

pygame.init()

GAME_W = 1280
GAME_H = 720
DISPLAY_SCALE = 0.8

DISPLAY_W = int(GAME_W * DISPLAY_SCALE)
DISPLAY_H = int(GAME_H * DISPLAY_SCALE)

game_surface = pygame.Surface((GAME_W, GAME_H))
screen = pygame.display.set_mode((DISPLAY_W, DISPLAY_H))
pygame.display.set_caption("Real Sparkle?")
clock = pygame.time.Clock()

player_w=50
player_h=50
player_x=400
hp=3
distance=0

font = pygame.font.Font(
    "assets/PixelifySans-VariableFont_wght.ttf",
    36
)

bg_star1 = pygame.image.load("assets/STAR1.png").convert()
bg_star2 = pygame.image.load("assets/STAR2.png").convert()

bg_star1=pygame.transform.scale(bg_star1, (1280, 720))
bg_star2=pygame.transform.scale(bg_star2, (1280, 720))

bg_star=[bg_star1,bg_star2]
bg_star_index=0
bg_timer=0

def create_platform(x):
    width=random.randint(350,650)
    y=random.randint(430, 620)
    height=720-y
    gd_surf=pygame.Surface((width,height))
    gd_surf.fill('BLACK')
    gd_rect=gd_surf.get_rect(topleft=(x,y))
    return {
        "surf":gd_surf,
        "rect":gd_rect
    }

def create_platform2(x): #upper-level platforms
    width=random.randint(280,520)
    y=random.randint(120, 280)
    height=720-y
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

jump_count=2

on_ground=False

platform_speed=6
speed_goal=6
max_speed=12
speed_up_every=1000 #speed up

slide_x=500 #slide distance
target_x=player_x
slide_timer=0
slide_duration=15
fast_land=False

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
            
            if event.key==pygame.K_s:
                if not on_ground: #fast landing
                    vel_y=18
                    fast_land=True
                else:
                    slide_timer=slide_duration #slide
                    target_x=slide_x
                

    old_bottom = player_rect.bottom #last position

    vel_y += gravity
    player_rect.y += vel_y
    on_ground=False
    touching_side=False
    
    distance+=platform_speed

    bg_timer+=1
    if bg_timer>=60:
        bg_timer=0
        bg_star_index+=1
        if bg_star_index>=len(bg_star):
            bg_star_index=0 #background

    if distance >3000 and len(platforms2)==0: #creat upper-level platforms
        x2=1400
        for i in range(5):
            platform2=create_platform2(x2)
            platforms2.append(platform2)
            gap2=random.randint(120,320)
            x2=platform2["rect"].right+gap2
        
    if distance>=speed_up_every:
        speed_goal+=0.2
        speed_up_every+=1000
    if speed_goal > max_speed:
        speed_goal = max_speed#the maximum of speed
    if platform_speed<speed_goal:
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
                if fast_land: #little slide after landing
                    slide_timer=int(slide_duration/1.5)
                    target_x=450
                    fast_land=False
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
                if fast_land: #little slide after landing
                    slide_timer=int(slide_duration/1.5)
                    target_x=450
                    fast_land=False
    platforms2=[platform2 for platform2 in platforms2 if platform2["rect"].right>0]
    
    if len(platforms2)>0:
        last_platform2 = platforms2[-1]
        if last_platform2["rect"].right<1280:
            gap2=random.randint(260,500)
            new_x2=last_platform2["rect"].right+gap2
            platforms2.append(create_platform2(new_x2))

    if slide_timer>0:
        slide_timer-=1
    else:
        if on_ground:
            target_x=player_x

    if not touching_side:
        if player_rect.x<target_x:
            player_rect.x+=4 #back to normal position
            if player_rect.x > target_x:
                player_rect.x=target_x
        elif player_rect.x > target_x:
            player_rect.x -= 4
            if player_rect.x < target_x:
                player_rect.x = target_x

    if player_rect.top>800:
        fast_land=False
        print("Game Over")
        pygame.quit()
        sys.exit()

    game_surface.blit(bg_star[bg_star_index],(0,0))

    for platform2 in platforms2:
        game_surface.blit(platform2["surf"], platform2["rect"])
    for platform in platforms:
        game_surface.blit(platform["surf"], platform["rect"])
    
    game_surface.blit(player,player_rect)

    distance_text = font.render(
        f"DIST {int(distance*0.08)}",
        False,
        (220,220,230)
    )

    speed_text = font.render(
        f"SPD {platform_speed:.1f}",
        False,
        (220,220,230)
    )
    
    game_surface.blit(distance_text, (30, 20))
    game_surface.blit(speed_text, (30, 55))

    scaled_surface = pygame.transform.scale(
    game_surface,
    (DISPLAY_W, DISPLAY_H)
    )
    screen.blit(scaled_surface, (0, 0))
    pygame.display.update()
    clock.tick(60)