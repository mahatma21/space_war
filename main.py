import pygame
import pygame.freetype
from pygame.locals import *
import sys
import os
import pyautogui  # To get window size

class Player:
    def __init__(
            self, x: int, y: int, width: int, height: int, vel: int,
            border: pygame.Rect, facing: int, bullet_size: tuple,
            bullet_vel: int, img: pygame.Surface, color: tuple, health: int,
            health_font_size: int, key_binding: tuple):
        self.rect = pygame.Rect(x, y, width, height)
        self.vel = vel
        self.border = border
        self.color = color
        self.health_font_size = health_font_size
        self.facing = facing
        self.bullet_size = bullet_size
        self.bullet_vel = bullet_vel
        self.health = health
        self.update_health_text()  # Create health text
        self.img = img
        self.key_binding = key_binding
        self.bullets = []

    def handle_movement(self, keys_pressed):
        # Move
        if keys_pressed[self.key_binding[MOVE_LEFT]]:
            self.rect.x -= self.vel
        if keys_pressed[self.key_binding[MOVE_RIGHT]]:
            self.rect.x += self.vel
        if keys_pressed[self.key_binding[MOVE_UP]]:
            self.rect.y -= self.vel
        if keys_pressed[self.key_binding[MOVE_DOWN]]:
            self.rect.y += self.vel
        # Border
        if self.rect.x < self.border.x:
            self.rect.x = self.border.x
        elif self.rect.x + self.rect.width > self.border.x + self.border.width:
            self.rect.x = self.border.x + self.border.width - self.rect.width
        if self.rect.y < self.border.y:
            self.rect.y = self.border.y
        elif self.rect.y + self.rect.height > self.border.y + self.border.height:
            self.rect.y = self.border.y + self.border.height - self.rect.height

    def handle_bullets(self, enemy):
        for bullet in self.bullets:
            bullet.x += self.bullet_vel * self.facing
            # Collision
            if enemy.rect.colliderect(bullet):
                enemy.hit()
                self.bullets.remove(bullet)
            elif self.facing == 1:
                if bullet.x > display.get_width():
                    self.bullets.remove(bullet)
            else:
                if bullet.x + bullet.width < 0:
                    self.bullets.remove(bullet)

    def shoot(self):
        # Play shoot sound effect
        BULLET_FIRE_SOUND.play()
        # Create bullet
        if self.facing == 1:
            self.bullets.append(
                pygame.Rect(
                    self.rect.x + self.rect.width, self.rect.y +
                    (self.rect.height / 2) - (self.bullet_size[1] / 2),
                    *self.bullet_size))
        else:
            self.bullets.append(
                pygame.Rect(
                    self.rect.x - self.bullet_size[0], self.rect.y +
                    (self.rect.height / 2) - (self.bullet_size[1] / 2),
                    *self.bullet_size))

    def hit(self):
        # Play hit sound effect
        BULLET_HIT_SOUND.play()
        # Decrease player health
        self.health -= 1
        # re-render health text
        self.update_health_text()

    def draw_health_text(self, win: pygame.Surface):
        # Draw health text
        if self.facing == 1:
            win.blit(self.health_text, (40, 40))
        else:
            win.blit(
                self.health_text,
                (display.get_width() - self.health_text.get_width() - 40, 40))

    def draw_spaceship(self, win: pygame.Surface):
        # Draw player spaceship
        win.blit(self.img, self.rect)

    def draw_bullets(self, win: pygame.Surface):
        # Draw player bullets
        for bullet in self.bullets:
            pygame.draw.rect(win, self.color, bullet)

    def update_health_text(self):
        if self.health > 3:
            self.health_text = FONT.render(
                f"Health: {self.health}", WHITE, size=self.health_font_size)[0]
        else:
            self.health_text = FONT.render(
                f"Health: {self.health}", RED, size=self.health_font_size)[0]


def redraw_window(
        display, blue: Player, red: Player, bg: pygame.Surface,
        winner_text=None):
    # Draw background image
    display.blit(bg, (0, 0))
    # Draw player stuff
    blue.draw_health_text(display)
    blue.draw_spaceship(display)
    blue.draw_bullets(display)

    red.draw_health_text(display)
    red.draw_spaceship(display)
    red.draw_bullets(display)

    if winner_text != None:
        display.blit(
            winner_text,
            ((display.get_width() / 2) - (winner_text.get_width() / 2),
             (display.get_height() / 2) - (winner_text.get_height() / 2)))

    pygame.display.update()


def draw_winner(
        display, winner, winner_color, winner_font_size, fullscreen, blue, red,
        bg):

    isFullscreen = fullscreen

    winner_text = FONT.render(winner, winner_color, size=winner_font_size)[0]
    redraw_window(display, blue, red, bg, winner_text)

    # Just allow QUIT event for game restart delay
    pygame.event.set_allowed(QUIT)
    # Delay before game restart
    currTm = pygame.time.get_ticks()  # current time
    startTm = currTm
    # Game restart delay loop
    while currTm - startTm < 3_000:  # 3 seconds before game restart
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    sys.exit()
                if event.key == K_F11:
                    isFullscreen = not isFullscreen

                    display, player_size, player_vel, blue_pos, blue_border, blue_spaceship, blue_health, red_pos, red_border, red_spaceship, red_health, bullet_size, bullet_vel, bg_img, winner_font_size, health_font_size = toggle_fullscreen(
                        isFullscreen, blue, red)

                    bg = bg_img

                    blue = Player(
                        *blue_pos, *player_size, player_vel, blue_border, 1,
                        bullet_size, bullet_vel, blue_spaceship, CYAN,
                        blue_health, health_font_size, BLUE_KEY_BINDING)

                    red = Player(
                        *red_pos, *player_size, player_vel, red_border, -1,
                        bullet_size, bullet_vel, red_spaceship, RED,
                        red_health, health_font_size, RED_KEY_BINDING)

                    winner_text = FONT.render(
                        winner, winner_color, size=winner_font_size)[0]

                    redraw_window(display, blue, red, bg, winner_text)

        # Preven CPU bound
        pygame.time.wait(10)
        # Update current time
        currTm = pygame.time.get_ticks()

    return isFullscreen


def toggle_fullscreen(fullscreen, blue=0, red=0):
    if fullscreen:
        # Display
        display = pygame.display.set_mode(
            FULLSCREEN_SIZE, FULLSCREEN | DOUBLEBUF | HWSURFACE, vsync=1)
        # Player stuff
        player_size = FULLSCREEN_PLAYER_SIZE
        player_vel = FULLSCREEN_PLAYER_VEL
        # Blue
        blue_border = FULLSCREEN_BLUE_BORDER
        blue_spaceship = FULLSCREEN_BLUE_SPACESHIP
        # Red
        red_border = FULLSCREEN_RED_BORDER
        red_spaceship = FULLSCREEN_RED_SPACESHIP
        # Bullet
        bullet_size = FULLSCREEN_BULLET_SIZE
        bullet_vel = FULLSCREEN_BULLET_VEL
        bg_img = FULLSCREEN_BG
        # Font
        winner_font_size = 100 * FULLSCREEN_HEIGHT_RATIO
        health_font_size = 40 * FULLSCREEN_HEIGHT_RATIO
    else:
        # Display
        display = pygame.display.set_mode(WIN_SIZE, vsync=1)
        # Player stuff
        player_size = WIN_PLAYER_SIZE
        player_vel = WIN_PLAYER_VEL
        # Blue
        blue_pos = (
            (WIN_SIZE[0] * 0.25) - (player_size[0] / 2),
            (WIN_SIZE[1] / 2) - (player_size[1] / 2))
        blue_border = WIN_BLUE_BORDER
        blue_spaceship = WIN_BLUE_SPACESHIP
        # Red
        red_pos = (
            (WIN_SIZE[0] * 0.75) - (player_size[0] / 2),
            (WIN_SIZE[1] / 2) - (player_size[1] / 2))
        red_border = WIN_RED_BORDER
        red_spaceship = WIN_RED_SPACESHIP
        # Bullet
        bullet_size = WIN_BULLET_SIZE
        bullet_vel = WIN_BULLET_VEL
        bg_img = WIN_BG
        # Font
        winner_font_size = 100 * WIN_HEIGHT_RATIO
        health_font_size = 40 * WIN_HEIGHT_RATIO

    if blue:
        blue_health = blue.health

        if fullscreen:
            blue_pos = (round(
                blue.rect.x * FULLSCREEN_SIZE[0] /
                WIN_SIZE[0]),
                round(
                blue.rect.y * FULLSCREEN_SIZE[1] /
                WIN_SIZE[1]))
        else:
            blue_pos = (round(
                blue.rect.x * WIN_SIZE[0] /
                FULLSCREEN_SIZE[0]),
                round(
                blue.rect.y * WIN_SIZE[1] /
                FULLSCREEN_SIZE[1]))
    else:
        blue_health = PLAYER_HEALTH
        blue_pos = (
            (display.get_width() * 0.25) - (player_size[0] / 2),
            (display.get_height() / 2) - (player_size[1] / 2))
    if red:
        red_health = red.health

        if fullscreen:
            red_pos = (round(
                red.rect.x * FULLSCREEN_SIZE[0] / WIN_SIZE[0]),
                round(
                red.rect.y * FULLSCREEN_SIZE[1] /
                WIN_SIZE[1]))
        else:
            red_pos = (round(
                red.rect.x * WIN_SIZE[0] / FULLSCREEN_SIZE[0]),
                round(
                red.rect.y * WIN_SIZE[1] /
                FULLSCREEN_SIZE[1]))
    else:
        red_health = PLAYER_HEALTH

        red_pos = (
            (display.get_width() * 0.75) - (player_size[0] / 2),
            (display.get_height() / 2) - (player_size[1] / 2))

    return display, player_size, player_vel, blue_pos, blue_border, blue_spaceship, blue_health, red_pos, red_border, red_spaceship, red_health, bullet_size, bullet_vel, bg_img, winner_font_size, health_font_size


def main(fullscreen=0):
    clock = pygame.time.Clock()

    isFullscreen = fullscreen

    display, player_size, player_vel, blue_pos, blue_border, blue_spaceship, blue_health, red_pos, red_border, red_spaceship, red_health, bullet_size, bullet_vel, bg_img, winner_font_size, health_font_size = toggle_fullscreen(
        isFullscreen)

    bg = bg_img

    blue = Player(
        *blue_pos, *player_size, player_vel, blue_border, 1, bullet_size,
        bullet_vel, blue_spaceship, CYAN, blue_health, health_font_size,
        BLUE_KEY_BINDING)

    red = Player(*red_pos, *player_size, player_vel, red_border, -1,
                 bullet_size, bullet_vel, red_spaceship, RED, red_health,
                 health_font_size, RED_KEY_BINDING)

    # Play background music
    pygame.mixer.music.play(-1)

    # Set allowed event to limit event loop
    pygame.event.set_allowed((QUIT, KEYDOWN))

    # Main loop
    while 1:
        # Set game FPS
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    sys.exit()
                if event.key == K_F11:
                    isFullscreen = not isFullscreen

                    display, player_size, player_vel, blue_pos, blue_border, blue_spaceship, blue_health, red_pos, red_border, red_spaceship, red_health, bullet_size, bullet_vel, bg_img, winner_font_size, health_font_size = toggle_fullscreen(
                        isFullscreen, blue, red)
                    

                    bg = bg_img

                    blue = Player(
                        *blue_pos, *player_size, player_vel, blue_border, 1,
                        bullet_size, bullet_vel, blue_spaceship, CYAN,
                        blue_health, health_font_size, BLUE_KEY_BINDING)

                    red = Player(
                        *red_pos, *player_size, player_vel, red_border, -1,
                        bullet_size, bullet_vel, red_spaceship, RED,
                        red_health, health_font_size, RED_KEY_BINDING)

                if event.key == blue.key_binding[SHOOT]:
                    if len(blue.bullets) < MAX_BULLET:
                        blue.shoot()

                if event.key == red.key_binding[SHOOT]:
                    if len(red.bullets) < MAX_BULLET:
                        red.shoot()

        keys_pressed = pygame.key.get_pressed()

        # Handle players movement and bullets
        blue.handle_movement(keys_pressed)
        blue.handle_bullets(red)

        red.handle_movement(keys_pressed)
        red.handle_bullets(blue)

        redraw_window(display, blue, red, bg)

        # Check for winner
        if blue.health <= 0 or red.health <= 0:
            if blue.health <= 0 and red.health <= 0:
                winner = "Draw!"
                winner_color = WHITE
            elif blue.health <= 0:
                winner = "Red Wins!"
                winner_color = RED
            elif red.health <= 0:
                winner = "Blue Wins!"
                winner_color = CYAN
            # Stop background music
            pygame.mixer.music.stop()
            # Draw the winner
            isFullscreen = draw_winner(
                display, winner, winner_color, winner_font_size, isFullscreen,
                blue, red, bg)
            # Restart the game
            main(isFullscreen)


# Colors
CYAN = (0, 235, 235)
RED = (235, 0, 0)
WHITE = (235, 235, 235)

# Fullscreen
FULLSCREEN_SIZE = pyautogui.size()
FULLSCREEN_WIDTH_RATIO = FULLSCREEN_SIZE[0] / 960
FULLSCREEN_HEIGHT_RATIO = FULLSCREEN_SIZE[1] / 540
# Main window
WIN_SIZE = round((FULLSCREEN_SIZE[1] - 200) * 16 / 9), FULLSCREEN_SIZE[1] - 200
WIN_WIDTH_RATIO = WIN_SIZE[0] / 960
WIN_HEIGHT_RATIO = WIN_SIZE[1] / 540
WIN_ICON = pygame.image.load(os.path.join('assets', 'icon.png'))
# Display
display_size = WIN_SIZE
# Set window caption and icon
pygame.display.set_caption("Space War")
pygame.display.set_icon(WIN_ICON)

# Player binding
MOVE_LEFT, MOVE_RIGHT, MOVE_UP, MOVE_DOWN, SHOOT = [i for i in range(5)]

# Player
PLAYER_HEALTH = 10
# Player size
WIN_PLAYER_SIZE = round(56 * WIN_WIDTH_RATIO), round(40 * WIN_HEIGHT_RATIO)
FULLSCREEN_PLAYER_SIZE = round(
    56 * FULLSCREEN_WIDTH_RATIO), round(40 * FULLSCREEN_HEIGHT_RATIO)
# Player vel
WIN_PLAYER_VEL = round(8 * WIN_WIDTH_RATIO)
FULLSCREEN_PLAYER_VEL = round(8 * FULLSCREEN_WIDTH_RATIO)

# Blue
BLUE_KEY_BINDING = (K_a, K_d, K_w, K_s, K_LCTRL)
WIN_BLUE_BORDER = pygame.Rect(0, 0, (WIN_SIZE[0] / 2) - 10, WIN_SIZE[1])
FULLSCREEN_BLUE_BORDER = pygame.Rect(
    0, 0, (FULLSCREEN_SIZE[0] / 2) - 10, FULLSCREEN_SIZE[1])
# Red
RED_KEY_BINDING = (K_LEFT, K_RIGHT, K_UP, K_DOWN, K_RCTRL)
WIN_RED_BORDER = pygame.Rect((WIN_SIZE[0] / 2) + 10, 0,
                             (WIN_SIZE[0] / 2) - 10, WIN_SIZE[1])
FULLSCREEN_RED_BORDER = pygame.Rect(
    (FULLSCREEN_SIZE[0] / 2) + 10, 0, (FULLSCREEN_SIZE[0] / 2) - 10,
    FULLSCREEN_SIZE[1])

# Player bullets
MAX_BULLET = 3
WIN_BULLET_SIZE = round(12 * WIN_WIDTH_RATIO), round(4 * WIN_HEIGHT_RATIO)
FULLSCREEN_BULLET_SIZE = round(
    12 * FULLSCREEN_WIDTH_RATIO), round(4 * FULLSCREEN_HEIGHT_RATIO)

WIN_BULLET_VEL = 2 * WIN_PLAYER_VEL
FULLSCREEN_BULLET_VEL = 2 * FULLSCREEN_PLAYER_VEL

# Sounds
pygame.mixer.init(48000)
BULLET_FIRE_SOUND = pygame.mixer.Sound(os.path.join('assets', 'laser.wav'))
BULLET_FIRE_SOUND.set_volume(0.2)
BULLET_HIT_SOUND = pygame.mixer.Sound(os.path.join('assets', 'explosion.wav'))
BULLET_HIT_SOUND.set_volume(0.16)
pygame.mixer.music.load(os.path.join('assets', 'backsound.wav'))
pygame.mixer.music.set_volume(0.2)

# Fonts
pygame.freetype.init()
FONT = pygame.freetype.Font(os.path.join('assets', 'pixel_font.ttf'))

# Game fps
FPS = 60

# Create dummy main window
display = pygame.display.set_mode(WIN_SIZE, vsync=1)

# Import images
FULLSCREEN_BG = pygame.transform.smoothscale(pygame.image.load(
    os.path.join('assets', 'bg.png')).convert(), FULLSCREEN_SIZE)
WIN_BG = pygame.transform.smoothscale(FULLSCREEN_BG, WIN_SIZE)

FULLSCREEN_BLUE_SPACESHIP = pygame.transform.smoothscale(pygame.transform.rotate(
    pygame.image.load(
        os.path.join(
            'assets',
            'blue_spaceship.png')).convert_alpha(),
    90),
    FULLSCREEN_PLAYER_SIZE)
WIN_BLUE_SPACESHIP = pygame.transform.smoothscale(
    FULLSCREEN_BLUE_SPACESHIP, WIN_PLAYER_SIZE)

FULLSCREEN_RED_SPACESHIP = pygame.transform.smoothscale(pygame.transform.rotate(
    pygame.image.load(
        os.path.join(
            'assets',
            'red_spaceship.png')).convert_alpha(),
    270),
    FULLSCREEN_PLAYER_SIZE)
WIN_RED_SPACESHIP = pygame.transform.smoothscale(
    FULLSCREEN_RED_SPACESHIP, WIN_PLAYER_SIZE)


if __name__ == '__main__':
    main()
