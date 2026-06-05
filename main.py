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

class Platform:
    def __init__(self, x, upper=False):
        if upper:
            width = random.randint(320, 600)
            y = random.randint(120, 280)
            color = "GRAY"
        else:
            width = random.randint(500, 850)
            y = random.randint(430, 620)
            color = "BLACK"

        height = 720 - y
        self.surf = pygame.Surface((width, height))
        self.surf.fill(color)
        self.rect = self.surf.get_rect(topleft=(x, y))
        self.upper = upper

    def update(self, speed):
        if self.upper:
            self.rect.x -= speed * 0.9
        else:
            self.rect.x -= speed

    def draw(self, surface):
        surface.blit(self.surf, self.rect)
player=pygame.Surface((player_w,player_h)) #Sparkle
player.fill('RED')
gravity=0.8
jump_power=-16
max_speed=12
slide_x=500 #slide distance
slide_duration=15

STATE_HOME = "home"
STATE_RUNNING = "running"
STATE_PAUSED = "paused"
STATE_GAME_OVER = "game_over"

game_state = STATE_HOME
platforms=[]
platforms2=[]
player_rect = player.get_rect()
vel_y=0
jump_count=2
on_ground=False
platform_speed=6
speed_goal=6
speed_up_every=1000 #speed up
target_x=player_x
slide_timer=0
fast_land=False
final_distance=0

def reset_game():
    global platforms, platforms2, player_rect, vel_y, jump_count, on_ground
    global platform_speed, speed_goal, speed_up_every, target_x, slide_timer
    global fast_land, distance, bg_star_index, bg_timer, final_distance

    platforms=[]
    platforms2=[]

    start_platform = Platform(0)
    start_platform.surf = pygame.Surface((900, 120))
    start_platform.surf.fill("BLACK")
    start_platform.rect = start_platform.surf.get_rect(topleft=(0, 600))
    platforms.append(start_platform)

    x=start_platform.rect.right+150
    for i in range(5):
        platform = Platform(x)
        platforms.append(platform)
        gap = random.randint(150, 300)
        x = platform.rect.right + gap

    player_rect = player.get_rect(midbottom=(player_x, start_platform.rect.top))
    vel_y=0
    jump_count=2
    on_ground=True
    platform_speed=6
    speed_goal=6
    speed_up_every=1000
    target_x=player_x
    slide_timer=0
    fast_land=False
    distance=0
    bg_star_index=0
    bg_timer=0
    final_distance=0

def draw_center_text(text, y, size=36, color=(230, 230, 240)):
    ui_font = pygame.font.Font(
        "assets/PixelifySans-VariableFont_wght.ttf",
        size
    )
    text_surf = ui_font.render(text, False, color)
    text_rect = text_surf.get_rect(center=(GAME_W / 2, y))
    game_surface.blit(text_surf, text_rect)

def present_screen():
    scaled_surface = pygame.transform.scale(
        game_surface,
        (DISPLAY_W, DISPLAY_H)
    )

    screen.blit(scaled_surface, (0, 0))
    pygame.display.update()

def draw_game():
    game_surface.blit(bg_star[bg_star_index], (0, 0))

    for platform2 in platforms2:
        platform2.draw(game_surface)
    for platform in platforms:
        platform.draw(game_surface)

    game_surface.blit(player, player_rect)

    display_distance = int(distance * 0.08)

    distance_text = font.render(
        f"DIST {display_distance}",
        False,
        (220, 220, 230)
    )

    speed_text = font.render(
        f"SPD {platform_speed:.1f}",
        False,
        (220, 220, 230)
    )

    game_surface.blit(distance_text, (30, 20))
    game_surface.blit(speed_text, (30, 55))

def draw_home():
    game_surface.blit(bg_star[bg_star_index], (0, 0))
    draw_center_text("REAL SPARKLE?", 230, 72, (255, 80, 90))
    draw_center_text("PRESS ENTER TO START", 360, 36)
    draw_center_text("W JUMP   S SLIDE / FAST FALL   P PAUSE", 425, 28, (180, 180, 195))

def draw_pause():
    draw_game()
    overlay = pygame.Surface((GAME_W, GAME_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    game_surface.blit(overlay, (0, 0))
    draw_center_text("PAUSED", 310, 64)
    draw_center_text("P RESUME   R RESTART   ESC HOME", 395, 30, (190, 190, 205))

def draw_game_over():
    draw_game()
    overlay = pygame.Surface((GAME_W, GAME_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    game_surface.blit(overlay, (0, 0))
    draw_center_text("GAME OVER", 285, 64, (255, 80, 90))
    draw_center_text(f"DIST {int(final_distance * 0.08)}", 370, 36)
    draw_center_text("R RETRY   ENTER HOME", 435, 30, (190, 190, 205))

def update_game():
    global vel_y, on_ground, jump_count, fast_land, slide_timer, target_x
    global distance, bg_timer, bg_star_index, speed_goal, speed_up_every
    global platform_speed, platforms, platforms2, game_state, final_distance

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
            platform2 = Platform(x2, upper=True)
            platforms2.append(platform2)
            gap2 = random.randint(260, 500)
            x2 = platform2.rect.right + gap2

    if distance>=speed_up_every:
        speed_goal+=0.2
        speed_up_every+=1000
    if speed_goal > max_speed:
        speed_goal = max_speed#the maximum of speed
    if platform_speed<speed_goal:
        platform_speed+=0.01 #smoothing the process of speeding up

    for platform in platforms:
        platform.update(platform_speed)
        rect = platform.rect
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
    platforms = [platform for platform in platforms if platform.rect.right > 0]
    #removing platforms that are off screen

    last_platform = platforms[-1]

    if last_platform.rect.right < 1280:
        gap=random.randint(200,320)
        new_x = last_platform.rect.right + gap
        platforms.append(Platform(new_x))

    for platform2 in platforms2:
        platform2.update(platform_speed)
        rect = platform2.rect
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
    platforms2 = [platform2 for platform2 in platforms2 if platform2.rect.right > 0]

    if len(platforms2)>0:
        last_platform2 = platforms2[-1]
        if last_platform2.rect.right < 1280:
            gap2=random.randint(260,500)
            new_x2 = last_platform2.rect.right + gap2
            platforms2.append(Platform(new_x2, upper=True))

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
        final_distance=distance
        game_state=STATE_GAME_OVER

reset_game()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type==pygame.KEYDOWN:
            if game_state==STATE_HOME:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    reset_game()
                    game_state=STATE_RUNNING

            elif game_state==STATE_RUNNING:
                if event.key==pygame.K_p:
                    game_state=STATE_PAUSED
                elif event.key==pygame.K_w and jump_count > 0: #double jump
                    vel_y = jump_power
                    jump_count-=1
                    on_ground=False
                elif event.key==pygame.K_s:
                    if not on_ground: #fast landing
                        vel_y=18
                        fast_land=True
                    else:
                        slide_timer=slide_duration #slide
                        target_x=slide_x

            elif game_state==STATE_PAUSED:
                if event.key==pygame.K_p:
                    game_state=STATE_RUNNING
                elif event.key==pygame.K_r:
                    reset_game()
                    game_state=STATE_RUNNING
                elif event.key==pygame.K_ESCAPE:
                    game_state=STATE_HOME

            elif game_state==STATE_GAME_OVER:
                if event.key==pygame.K_r:
                    reset_game()
                    game_state=STATE_RUNNING
                elif event.key==pygame.K_RETURN:
                    game_state=STATE_HOME

    if game_state==STATE_RUNNING:
        update_game()
        draw_game()
    elif game_state==STATE_HOME:
        draw_home()
    elif game_state==STATE_PAUSED:
        draw_pause()
    elif game_state==STATE_GAME_OVER:
        draw_game_over()

    present_screen()
    clock.tick(60)
