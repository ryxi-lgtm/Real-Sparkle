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

def load_danmaku_font(size):
    chinese_font_names = [
        "PingFang SC",
        "Hiragino Sans GB",
        "Heiti SC",
        "Songti SC",
        "Noto Sans CJK SC",
        "Microsoft YaHei",
        "SimHei",
        "WenQuanYi Zen Hei",
        "Arial Unicode MS"
    ]

    for font_name in chinese_font_names:
        matched_font = pygame.font.match_font(font_name)
        if matched_font:
            return pygame.font.Font(matched_font, size), True

    return pygame.font.Font("assets/PixelifySans-VariableFont_wght.ttf", size), False

danmaku_font, supports_chinese_danmaku = load_danmaku_font(46)
drone_label_font, supports_chinese_labels = load_danmaku_font(30)

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
            y = random.randint(180, 330)
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

class CardMissile:
    def __init__(self, x, y, dir_x=-1, dir_y=0):
        self.x=x
        self.y=y
        length=max(1, (dir_x * dir_x + dir_y * dir_y) ** 0.5)
        self.dir_x=dir_x / length
        self.dir_y=dir_y / length
        self.speed=50
        self.visual_w=92
        self.visual_h=34
        self.hit_w=120
        self.hit_h=66
        self.rect=pygame.Rect(x - self.hit_w / 2, y - self.hit_h / 2, self.hit_w, self.hit_h)
        self.state="flying"
        self.flash_timer=0
        self.rotation=0
        self.trail=[]
        self.deflect_dir=(1, -0.25)

    def update(self, dt):
        self.trail.append((self.x, self.y))
        if len(self.trail)>7:
            self.trail.pop(0)

        if self.state=="deflected":
            self.x+=self.deflect_dir[0] * 28 * dt
            self.y+=self.deflect_dir[1] * 28 * dt
            self.rotation+=24 * dt
            self.flash_timer=max(0, self.flash_timer - dt)
        elif self.state == "charging":
            self.rotation += 6 * dt
        else:
            self.x+=self.dir_x * self.speed * dt
            self.y+=self.dir_y * self.speed * dt

        self.rect.center=(int(self.x), int(self.y))

    def deflect(self):
        self.state="deflected"
        self.flash_timer=16
        self.rotation=-20
        self.trail=[(self.x, self.y)]
        self.deflect_dir=self.make_deflect_dir(self.dir_x, self.dir_y)

    def make_deflect_dir(self, in_x, in_y):
        out_x=-in_x
        out_y=-in_y - 0.25
        if out_x<0:
            out_x=abs(out_x)
        length=max(1, (out_x * out_x + out_y * out_y) ** 0.5)
        return (out_x / length, out_y / length)

    def hit_player(self):
        self.state="dead"

    def off_screen(self):
        if self.state=="dead":
            return True
        return (
            self.rect.right < -80
            or self.rect.left > GAME_W + 120
            or self.rect.bottom < -80
            or self.rect.top > GAME_H + 80
        )

    def draw(self, surface):
        color=(255, 245, 250)
        border=(230, 50, 70)
        for index, point in enumerate(self.trail[:-1]):
            alpha=int(45 + 130 * (index + 1) / max(1, len(self.trail)))
            length=int(22 + 20 * (index + 1) / max(1, len(self.trail)))
            start=(int(point[0] - self.dir_x * length), int(point[1] - self.dir_y * length))
            end=(int(point[0]), int(point[1]))
            pygame.draw.line(surface, (255, 210, 220, alpha), start, end, 10)

        card_surface=pygame.Surface((self.visual_w, self.visual_h), pygame.SRCALPHA)
        pygame.draw.rect(card_surface, color, card_surface.get_rect(), border_radius=4)
        pygame.draw.rect(card_surface, border, card_surface.get_rect(), 3, border_radius=4)
        pygame.draw.circle(card_surface, border, (28, 18), 5)
        pygame.draw.circle(card_surface, border, (72, 18), 5)

        if self.state=="deflected":
            angle=self.rotation
        else:
            angle=-pygame.math.Vector2(self.dir_x, self.dir_y).angle_to(pygame.math.Vector2(1, 0))
        rotated_card=pygame.transform.rotate(card_surface, angle)
        surface.blit(rotated_card, rotated_card.get_rect(center=self.rect.center))

        if self.flash_timer>0:
            flash_rect=self.rect.inflate(28, 28)
            pygame.draw.rect(surface, (255, 255, 180), flash_rect, 3, border_radius=6)

class HomingCard:
    def __init__(self, x, y):
        self.x=x
        self.y=y
        self.speed_x=random.uniform(8, 11)
        self.max_y_adjust=random.uniform(2.0, 2.8)
        self.visual_w=86
        self.visual_h=40
        self.hit_w=102
        self.hit_h=60
        self.rect=pygame.Rect(x - self.hit_w / 2, y - self.hit_h / 2, self.hit_w, self.hit_h)
        self.state="flying"
        self.flash_timer=0
        self.rotation=0
        self.vel_x=-9.5
        self.vel_y=0
        self.speed=10.5
        self.turn_rate=0.045
        self.deflect_dir=(1, -0.3)

    def update(self, dt):
        if self.state=="deflected":
            self.x+=self.deflect_dir[0] * 24 * dt
            self.y+=self.deflect_dir[1] * 24 * dt
            self.flash_timer=max(0, self.flash_timer - dt)
            self.rotation+=22 * dt
        else:
            target_dx=player_rect.centerx - self.x
            target_dy=player_rect.centery - self.y
            target_length=max(1, (target_dx * target_dx + target_dy * target_dy) ** 0.5)
            target_vx=target_dx / target_length * self.speed
            target_vy=target_dy / target_length * self.speed

            self.vel_x+=(target_vx - self.vel_x) * self.turn_rate * dt
            self.vel_y+=(target_vy - self.vel_y) * self.turn_rate * dt
            length=max(1, (self.vel_x * self.vel_x + self.vel_y * self.vel_y) ** 0.5)
            self.vel_x=self.vel_x / length * self.speed
            self.vel_y=self.vel_y / length * self.speed

            self.x+=self.vel_x * dt
            self.y+=self.vel_y * dt
            self.rotation+=10 * dt

            self.x=max(-120, min(GAME_W + 140, self.x))
            self.y=max(-80, min(GAME_H + 80, self.y))

        self.rect.center=(int(self.x), int(self.y))

    def deflect(self):
        self.state="deflected"
        self.flash_timer=18
        self.deflect_dir=self.make_deflect_dir(self.vel_x, self.vel_y)

    def make_deflect_dir(self, in_x, in_y):
        out_x=-in_x
        out_y=-in_y - 0.25
        if out_x<0:
            out_x=abs(out_x)
        length=max(1, (out_x * out_x + out_y * out_y) ** 0.5)
        return (out_x / length, out_y / length)

    def hit_player(self):
        self.state="dead"

    def off_screen(self):
        if self.state=="dead":
            return True
        if self.state!="deflected":
            return False
        return (
            self.rect.right < -80
            or self.rect.left > GAME_W + 120
            or self.rect.bottom < -80
            or self.rect.top > GAME_H + 80
        )

    def draw(self, surface):
        color=(255, 235, 250)
        border=(180, 80, 255)
        card_surface=pygame.Surface((self.visual_w, self.visual_h), pygame.SRCALPHA)
        pygame.draw.rect(card_surface, color, card_surface.get_rect(), border_radius=5)
        pygame.draw.rect(card_surface, border, card_surface.get_rect(), 3, border_radius=5)
        pygame.draw.circle(card_surface, border, (25, 20), 6)
        pygame.draw.circle(card_surface, border, (61, 20), 6)

        rotated_card=pygame.transform.rotate(card_surface, self.rotation)
        surface.blit(rotated_card, rotated_card.get_rect(center=self.rect.center))

        if self.flash_timer>0:
            flash_rect=self.rect.inflate(34, 34)
            pygame.draw.rect(surface, (255, 255, 180), flash_rect, 3, border_radius=8)

class DanmakuLine:
    def __init__(self, text, x, y, speed):
        self.text=text
        self.x=x
        self.y=y
        self.speed=speed
        self.surf=danmaku_font.render(text, True, (245, 245, 255))
        self.rect=self.surf.get_rect(topleft=(x, y))

    def update(self, dt):
        self.x-=self.speed * dt
        self.rect.x=int(self.x)

    def off_screen(self):
        return self.rect.right < -40

    def draw(self, surface):
        shadow=self.surf.copy()
        shadow.fill((0, 0, 0), special_flags=pygame.BLEND_RGB_MULT)
        surface.blit(shadow, self.rect.move(3, 3))
        surface.blit(self.surf, self.rect)

class DanmakuBarrage:
    def __init__(self, area):
        self.area=area
        self.timer=180
        self.spawn_timer=0
        self.lines=[]

    def area_rect(self):
        if self.area==DANMAKU_TOP:
            return pygame.Rect(0, 100, GAME_W, 230)
        return pygame.Rect(0, 390, GAME_W, 250)

    def update(self, dt):
        self.timer-=dt
        self.spawn_timer-=dt
        if self.spawn_timer<=0 and self.timer>0:
            self.spawn_timer=random.randint(2, 5)
            area_rect=self.area_rect()
            text=random.choice(DANMAKU_TEXTS)
            y=random.randint(area_rect.top + 4, area_rect.bottom - 54)
            speed=random.randint(9, 16)
            self.lines.append(DanmakuLine(text, GAME_W + random.randint(0, 120), y, speed))
            if random.random()<0.55:
                text2=random.choice(DANMAKU_TEXTS)
                y2=random.randint(area_rect.top + 4, area_rect.bottom - 54)
                speed2=random.randint(9, 16)
                self.lines.append(DanmakuLine(text2, GAME_W + random.randint(80, 220), y2, speed2))

        for line in self.lines:
            line.update(dt)
        self.lines=[line for line in self.lines if not line.off_screen()]

    def active(self):
        return self.timer>0 or len(self.lines)>0

    def hits_player(self):
        return any(line.rect.colliderect(player_rect) for line in self.lines)

    def draw(self, surface):
        for line in self.lines:
            line.draw(surface)

class Drone:
    def __init__(self, kind):
        self.kind=kind
        self.x=GAME_W + 90
        self.area=choose_black_barrage_area() if kind==DRONE_BLACK else DANMAKU_TOP
        if kind==DRONE_WHITE:
            self.y=115
        elif self.area==DANMAKU_TOP:
            self.y=500
        else:
            self.y=160
        self.target_x=GAME_W - 110 if kind==DRONE_WHITE else GAME_W - 145
        self.phase="enter"
        self.timer=0
        self.aim_start=(self.x, self.y)
        self.locked_target=(player_rect.centerx, player_rect.centery)
        self.aim_dir=(-1, 0)
        self.attack_type="snipe_card"
        self.snipe_card=None
        self.alive=True

        if kind==DRONE_WHITE and random.random()>=0.7:
            self.attack_type="homing_card"

    def update(self, dt):
        if self.phase=="enter":
            self.x-=5 * dt
            if self.x<=self.target_x:
                self.x=self.target_x
                if self.kind==DRONE_WHITE:
                    self.phase="snipe_timing" if self.attack_type=="snipe_card" else "homing_charge"
                else:
                    self.phase="warning"
                self.timer=0

        elif self.kind==DRONE_WHITE:
            self.update_white(dt)
        else:
            self.update_black(dt)

        if self.phase=="exit":
            self.x+=6 * dt
            if self.x>GAME_W + 160:
                self.alive=False

    def update_white(self, dt):
        if self.attack_type=="homing_card":
            self.update_white_homing(dt)
            return

        if self.phase=="snipe_timing":
            self.timer+=dt
            if self.timer<SNIPE_TIMING_TIME:
                self.aim_start=(self.x - 32, self.y)
                self.locked_target=player_rect.center
            self.update_snipe_direction()
            if self.timer>=SNIPE_TIMING_TIME:
                self.fire_snipe_card()
                self.phase="snipe_late"
                self.timer=0

        elif self.phase=="snipe_late":
            self.timer+=dt
            if self.snipe_card and self.snipe_card.state=="flying":
                can_parry=is_parry_active() or parry_state in (PARRY_HOLDING, PARRY_SLOWMO)
                if can_parry and missile_near_player(self.snipe_card, PARRY_RADIUS):
                    self.resolve_snipe(True)
                    return
            if self.timer>=SNIPE_LATE_WINDOW:
                if self.snipe_card and self.snipe_card.state=="deflected":
                    self.phase="recover"
                    self.timer=0
                    return
                self.resolve_snipe(False)

        elif self.phase=="recover":
            self.timer+=dt
            if self.timer>=45:
                self.phase="exit"

    def update_snipe_direction(self):
        dx=self.locked_target[0] - self.aim_start[0]
        dy=self.locked_target[1] - self.aim_start[1]
        length=max(1, (dx * dx + dy * dy) ** 0.5)
        self.aim_dir=(dx / length, dy / length)

    def snipe_in_good_window(self):
        if self.phase=="snipe_timing":
            return self.timer>=SNIPE_TIMING_TIME - SNIPE_GOOD_WINDOW
        return self.phase=="snipe_late" and self.timer<=SNIPE_LATE_WINDOW

    def fire_snipe_card(self):
        if self.snipe_card is None:
            self.snipe_card = CardMissile(self.aim_start[0], self.aim_start[1], self.aim_dir[0], self.aim_dir[1])
            missiles.append(self.snipe_card)
        self.snipe_card.state = "flying"
        self.snipe_card.speed = 50

    def resolve_snipe(self, parried):
        self.fire_snipe_card()
        if parried:
            self.snipe_card.deflect()
            trigger_parry("snipe")
            start_screen_shake(16, 12)
            self.phase = "recover"
            self.timer = 0
            return
        self.snipe_card.hit_player()
        damage_player()
        start_screen_shake(10, 7)
        self.phase = "recover"
        self.timer = 0

    def update_white_homing(self, dt):
        self.aim_start=(self.x - 32, self.y)

        if self.phase=="homing_charge":
            self.timer+=dt
            if self.timer>=25:
                missiles.append(HomingCard(self.aim_start[0], self.aim_start[1]))
                start_screen_shake(4, 3)
                self.phase="recover"
                self.timer=0

        elif self.phase=="recover":
            self.timer+=dt
            if self.timer>=55:
                self.phase="exit"

    def update_black(self, dt):
        if self.phase=="warning":
            self.timer+=dt
            if self.timer>=165 and len(barrages)==0:
                barrages.append(DanmakuBarrage(self.area))
                self.phase="recover"
                self.timer=0

        elif self.phase=="recover":
            self.timer+=dt
            if self.timer>=130:
                self.phase="exit"

    def draw(self, surface):
        rect=pygame.Rect(int(self.x - 32), int(self.y - 24), 64, 48)
        color=(245, 245, 255) if self.kind==DRONE_WHITE else (20, 20, 28)
        accent=(255, 70, 90) if self.kind==DRONE_WHITE else (120, 220, 255)
        pygame.draw.rect(surface, color, rect, border_radius=8)
        pygame.draw.rect(surface, accent, rect, 3, border_radius=8)
        pygame.draw.circle(surface, accent, (rect.left + 16, rect.centery), 5)
        pygame.draw.circle(surface, accent, (rect.right - 16, rect.centery), 5)

        if self.kind==DRONE_WHITE and self.phase=="homing_charge":
            if int(self.timer / 4) % 2==0:
                glow_rect=rect.inflate(18, 18)
                pygame.draw.rect(surface, (210, 120, 255), glow_rect, 4, border_radius=10)

        if self.kind==DRONE_WHITE and self.phase in ("snipe_timing", "snipe_late"):
            if self.snipe_in_good_window() and int(self.timer / 4) % 2==0:
                return
            line_color=(255, 40, 40)
            muzzle=(int(self.aim_start[0]), int(self.aim_start[1]))
            target=(int(self.locked_target[0]), int(self.locked_target[1]))
            dx=target[0] - muzzle[0]
            dy=target[1] - muzzle[1]
            if dx!=0:
                t=(0 - muzzle[0]) / dx
                end_y=muzzle[1] + dy * t
                ray_end=(0, int(end_y))
            else:
                ray_end=target
            pygame.draw.line(surface, line_color, muzzle, ray_end, 4)
            pygame.draw.circle(surface, line_color, muzzle, 7)
            pygame.draw.circle(surface, line_color, target, 9, 2)

        if self.kind==DRONE_BLACK and self.phase=="warning":
            area_rect=DanmakuBarrage(self.area).area_rect()
            warning="UPPER WARNING" if self.area==DANMAKU_TOP else "LOWER WARNING"
            warning_surf=font.render(warning, False, (255, 200, 230))
            surface.blit(warning_surf, warning_surf.get_rect(center=(GAME_W / 2, area_rect.centery)))

player=pygame.Surface((player_w,player_h)) #Sparkle
player.fill('RED')
gravity=0.8
jump_power=-16
max_speed=13
slide_x=500 #slide distance
slide_duration=15

PARRY_READY = "ready"
PARRY_HOLDING = "holding"
PARRY_SLOWMO = "slowmo"
PARRY_ACTIVE = "active"
PARRY_COOLDOWN = "cooldown"

PARRY_HOLD_THRESHOLD = 0.18
PARRY_SHORT_ACTIVE_TIME = 12
PARRY_LONG_ACTIVE_TIME = 14
PARRY_COOLDOWN_TIME = 28
PARRY_SLOWMO_SCALE = 0.35
PARRY_RADIUS = 100
SNIPE_TIMING_TIME = 105
SNIPE_GOOD_WINDOW = 24
SNIPE_PERFECT_WINDOW = 8
SNIPE_LATE_WINDOW = 24

DRONE_WHITE = "white"
DRONE_BLACK = "black"

DRONE_SPAWN_TIME = 360
PLAYER_INVULN_TIME = 70
DANMAKU_TOP = "top"
DANMAKU_BOTTOM = "bottom"
if supports_chinese_danmaku:
    DANMAKU_TEXTS = ["666", "哈哈哈", "草", "???", "前方高能"]
else:
    DANMAKU_TEXTS = ["666", "LOL", "???", "HYPE", "WATCH OUT"]

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
platform_speed=7
speed_goal=7
speed_up_every=1000 #speed up
target_x=player_x
slide_timer=0
fast_land=False
final_distance=0
parry_state=PARRY_READY
parry_hold_timer=0
parry_active_timer=0
parry_active_total=1
parry_cooldown_timer=0
parry_ring_timer=0
parry_ring_total=1
parry_kind="short"
time_scale=1.0
drones=[]
missiles=[]
barrages=[]
drone_spawn_timer=DRONE_SPAWN_TIME
invuln_timer=0
screen_shake_timer=0
screen_shake_power=0

def has_reachable_upper_platform():
    for platform in platforms2:
        rect=platform.rect
        if rect.right<player_rect.left + 80:
            continue
        if rect.left>player_rect.right + 650:
            continue
        if rect.top<180 or rect.top>340:
            continue
        return True
    return False

def choose_black_barrage_area():
    if has_reachable_upper_platform():
        return random.choice([DANMAKU_TOP, DANMAKU_BOTTOM])
    return DANMAKU_TOP

def reset_game():
    global platforms, platforms2, player_rect, vel_y, jump_count, on_ground
    global platform_speed, speed_goal, speed_up_every, target_x, slide_timer
    global fast_land, distance, bg_star_index, bg_timer, final_distance
    global parry_state, parry_hold_timer, parry_active_timer, parry_active_total
    global parry_cooldown_timer, parry_ring_timer, parry_ring_total, parry_kind
    global time_scale, drones, missiles, barrages, drone_spawn_timer, hp
    global invuln_timer, screen_shake_timer, screen_shake_power

    platforms=[]
    platforms2=[]
    drones=[]
    missiles=[]
    barrages=[]

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
    platform_speed=7
    speed_goal=7
    speed_up_every=1000
    target_x=player_x
    slide_timer=0
    fast_land=False
    distance=0
    bg_star_index=0
    bg_timer=0
    final_distance=0
    parry_state=PARRY_READY
    parry_hold_timer=0
    parry_active_timer=0
    parry_active_total=1
    parry_cooldown_timer=0
    parry_ring_timer=0
    parry_ring_total=1
    parry_kind="short"
    time_scale=1.0
    drone_spawn_timer=220
    hp=3
    invuln_timer=0
    screen_shake_timer=0
    screen_shake_power=0

def start_parry_hold():
    global parry_state, parry_hold_timer

    if try_snipe_timing_parry():
        return

    if parry_state!=PARRY_READY:
        return

    parry_state=PARRY_HOLDING
    parry_hold_timer=0

def try_snipe_timing_parry():
    return False

def release_parry_hold():
    if parry_state==PARRY_HOLDING:
        trigger_parry("short")
    elif parry_state==PARRY_SLOWMO:
        trigger_parry("long")

def cancel_parry():
    global parry_state, parry_hold_timer, parry_active_timer
    global parry_cooldown_timer, parry_ring_timer, time_scale

    parry_state=PARRY_READY
    parry_hold_timer=0
    parry_active_timer=0
    parry_cooldown_timer=0
    parry_ring_timer=0
    time_scale=1.0

def clear_screen_shake():
    global screen_shake_timer, screen_shake_power

    screen_shake_timer=0
    screen_shake_power=0

def is_parry_active():
    return parry_state==PARRY_ACTIVE and parry_active_timer>0

def missile_near_player(missile, radius):
    dx=missile.rect.centerx - player_rect.centerx
    dy=missile.rect.centery - player_rect.centery
    return dx * dx + dy * dy <= radius * radius

def start_screen_shake(duration, power):
    global screen_shake_timer, screen_shake_power

    if game_state!=STATE_RUNNING:
        return

    if screen_shake_timer<=0 or duration>=screen_shake_timer:
        screen_shake_timer=duration
        screen_shake_power=power
    else:
        screen_shake_power=max(screen_shake_power, power)

def deflect_missile(missile, kind):
    missile.deflect()
    trigger_parry(kind)
    start_screen_shake(16, 12)

def damage_player():
    global hp, invuln_timer, screen_shake_timer, screen_shake_power
    global game_state, final_distance

    if invuln_timer>0 or game_state!=STATE_RUNNING:
        return

    hp-=1
    invuln_timer=PLAYER_INVULN_TIME
    start_screen_shake(14, 8)

    if hp<=0:
        hp=0
        final_distance=distance
        cancel_parry()
        clear_screen_shake()
        game_state=STATE_GAME_OVER

def update_enemy_system(dt):
    global drone_spawn_timer, drones, missiles, barrages
    global invuln_timer, screen_shake_timer

    if invuln_timer>0:
        invuln_timer=max(0, invuln_timer - 1)
    if screen_shake_timer>0:
        screen_shake_timer=max(0, screen_shake_timer - 1)

    if distance<=6000 or len(platforms2)==0:
        return

    drone_spawn_timer-=dt
    if drone_spawn_timer<=0 and len(drones)<1:
        if len(barrages)==0:
            kind=random.choice([DRONE_WHITE, DRONE_BLACK])
        else:
            kind=DRONE_WHITE
        drones.append(Drone(kind))
        drone_spawn_timer=random.randint(300, 460)

    for drone in drones:
        drone.update(dt)
    drones=[drone for drone in drones if drone.alive]

    for missile in missiles:
        missile.update(dt)
        if missile.state!="flying":
            continue

        if is_parry_active() and missile_near_player(missile, PARRY_RADIUS):
            deflect_missile(missile, parry_kind)
            continue

        if parry_state in (PARRY_HOLDING, PARRY_SLOWMO) and missile_near_player(missile, PARRY_RADIUS+30):
            deflect_missile(missile, "long")
            continue

        if missile.rect.colliderect(player_rect):
            damage_player()
            missile.hit_player()

    missiles=[missile for missile in missiles if not missile.off_screen()]

    for barrage in barrages:
        barrage.update(dt)
        if barrage.hits_player():
            damage_player()
    barrages=[barrage for barrage in barrages if barrage.active()]

def trigger_parry(kind):
    global parry_state, parry_active_timer, parry_active_total
    global parry_cooldown_timer, parry_ring_timer, parry_ring_total
    global parry_kind, time_scale

    parry_kind=kind
    if kind=="long":
        parry_active_total=PARRY_LONG_ACTIVE_TIME
        parry_ring_total=PARRY_LONG_ACTIVE_TIME
    elif kind=="snipe":
        parry_active_total=16
        parry_ring_total=18
    else:
        parry_active_total=PARRY_SHORT_ACTIVE_TIME
        parry_ring_total=PARRY_SHORT_ACTIVE_TIME

    parry_state=PARRY_ACTIVE
    parry_active_timer=parry_active_total
    parry_ring_timer=parry_ring_total
    parry_cooldown_timer=PARRY_COOLDOWN_TIME if kind=="long" else 0
    time_scale=1.0

def update_parry():
    global parry_state, parry_hold_timer, parry_active_timer
    global parry_cooldown_timer, parry_ring_timer, time_scale

    time_scale=1.0

    if parry_state==PARRY_HOLDING:
        parry_hold_timer+=1
        if parry_hold_timer>=PARRY_HOLD_THRESHOLD * 60:
            parry_state=PARRY_SLOWMO

    if parry_state==PARRY_SLOWMO:
        time_scale=PARRY_SLOWMO_SCALE

    elif parry_state==PARRY_ACTIVE:
        parry_active_timer-=1
        if parry_active_timer<=0:
            parry_active_timer=0
            if parry_cooldown_timer>0:
                parry_state=PARRY_COOLDOWN
            else:
                parry_state=PARRY_READY

    elif parry_state==PARRY_COOLDOWN:
        parry_cooldown_timer-=1
        if parry_cooldown_timer<=0:
            parry_cooldown_timer=0
            parry_state=PARRY_READY

    if parry_ring_timer>0:
        parry_ring_timer-=1

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

    if game_state==STATE_RUNNING and screen_shake_timer>0:
        shake=int(screen_shake_power * screen_shake_timer / 14)
        offset_x=random.randint(-shake, shake)
        offset_y=random.randint(-shake, shake)
    else:
        offset_x=0
        offset_y=0

    screen.fill((0, 0, 0))
    screen.blit(scaled_surface, (offset_x, offset_y))
    pygame.display.update()

def draw_enemy_system():
    for barrage in barrages:
        barrage.draw(game_surface)
    for drone in drones:
        drone.draw(game_surface)
    for missile in missiles:
        missile.draw(game_surface)

def draw_snipe_timing_effects():
    for drone in drones:
        if drone.kind!=DRONE_WHITE or drone.attack_type!="snipe_card":
            continue
        if drone.phase not in ("snipe_timing", "snipe_late"):
            continue

        progress=1 if drone.phase=="snipe_late" else min(1, drone.timer / SNIPE_TIMING_TIME)
        radius=int(145 - 105 * progress)
        remaining=0 if drone.phase=="snipe_late" else SNIPE_TIMING_TIME - drone.timer
        if drone.phase=="snipe_late":
            color=(255, 255, 255)
            width=8
        elif remaining<=SNIPE_PERFECT_WINDOW:
            color=(255, 255, 255)
            width=7
        elif remaining<=SNIPE_GOOD_WINDOW:
            color=(255, 225, 80)
            width=6
        else:
            color=(255, 70, 90)
            width=5

        ring_surface=pygame.Surface((radius * 2 + 16, radius * 2 + 16), pygame.SRCALPHA)
        pygame.draw.circle(
            ring_surface,
            (*color, 220),
            (radius + 8, radius + 8),
            radius,
            width
        )
        pygame.draw.circle(
            ring_surface,
            (*color, 80),
            (radius + 8, radius + 8),
            max(8, int(radius * 0.35)),
            2
        )
        game_surface.blit(ring_surface, ring_surface.get_rect(center=player_rect.center))

def draw_parry_effects():
    if parry_ring_timer<=0:
        return

    progress = 1 - parry_ring_timer / parry_ring_total
    if parry_kind=="long":
        start_radius = 45
        end_radius = 135
        ring_color = (255, 245, 255)
        width = 6
    else:
        start_radius = 35
        end_radius = 95
        ring_color = (255, 180, 210)
        width = 4

    radius = int(start_radius + (end_radius - start_radius) * progress)
    alpha = max(0, int(220 * (1 - progress)))
    ring_surface = pygame.Surface((radius * 2 + 8, radius * 2 + 8), pygame.SRCALPHA)
    pygame.draw.circle(
        ring_surface,
        (*ring_color, alpha),
        (radius + 4, radius + 4),
        radius,
        width
    )
    game_surface.blit(
        ring_surface,
        ring_surface.get_rect(center=player_rect.center)
    )

def draw_game():
    game_surface.blit(bg_star[bg_star_index], (0, 0))

    for platform2 in platforms2:
        platform2.draw(game_surface)
    for platform in platforms:
        platform.draw(game_surface)

    draw_enemy_system()

    if parry_state==PARRY_ACTIVE:
        player_color=(255, 225, 240)
    elif parry_state==PARRY_SLOWMO:
        player_color=(255, 120, 170)
    elif invuln_timer>0 and invuln_timer % 8 < 4:
        player_color=(255, 255, 255)
    else:
        player_color=(220, 35, 45)

    player.fill(player_color)
    game_surface.blit(player, player_rect)
    draw_snipe_timing_effects()
    draw_parry_effects()

    if parry_state==PARRY_SLOWMO:
        slowmo_overlay = pygame.Surface((GAME_W, GAME_H), pygame.SRCALPHA)
        slowmo_overlay.fill((20, 10, 35, 75))
        game_surface.blit(slowmo_overlay, (0, 0))

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

    hp_text = font.render(
        f"HP {hp}",
        False,
        (255, 170, 190)
    )

    game_surface.blit(distance_text, (30, 20))
    game_surface.blit(speed_text, (30, 55))
    game_surface.blit(hp_text, (30, 90))

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

    update_parry()
    old_bottom = player_rect.bottom #last position
    scaled_speed = platform_speed * time_scale

    vel_y += gravity * time_scale
    player_rect.y += vel_y * time_scale
    on_ground=False
    touching_side=False

    distance+=scaled_speed

    bg_timer+=time_scale
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
        platform_speed+=0.01 * time_scale #smoothing the process of speeding up

    for platform in platforms:
        platform.update(scaled_speed)
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
        platform2.update(scaled_speed)
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

    update_enemy_system(time_scale)

    if player_rect.top>800:
        fast_land=False
        final_distance=distance
        cancel_parry()
        clear_screen_shake()
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
                    cancel_parry()
                    clear_screen_shake()
                    game_state=STATE_PAUSED
                elif event.key==pygame.K_SPACE:
                    start_parry_hold()
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
                    cancel_parry()
                    clear_screen_shake()
                    game_state=STATE_HOME

            elif game_state==STATE_GAME_OVER:
                if event.key==pygame.K_r:
                    reset_game()
                    game_state=STATE_RUNNING
                elif event.key==pygame.K_RETURN:
                    game_state=STATE_HOME

        if event.type==pygame.KEYUP:
            if game_state==STATE_RUNNING and event.key==pygame.K_SPACE:
                release_parry_hold()

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
