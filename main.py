import pygame
from pygame.locals import *
import sys
import os
import pyautogui  # To get window size


class Player:
    def __init__(
            self, x: int, y: int,
            border: pygame.Rect, facing: int,
            img: pygame.Surface, color: tuple, key_binding: tuple):
        self.rect = pygame.Rect(x, y, *PLAYER_SIZE)
        self.border = border
        self.color = color
        self.facing = facing
        self.health = PLAYER_HEALTH
        self.update_health_text()  # Create health text
        self.img = img
        self.key_binding = key_binding
        self.bullets = []

    def handle_movement(self, keys_pressed):
        # Move
        if keys_pressed[self.key_binding[MOVE_LEFT]]:
            self.rect.x -= PLAYER_VEL
        if keys_pressed[self.key_binding[MOVE_RIGHT]]:
            self.rect.x += PLAYER_VEL
        if keys_pressed[self.key_binding[MOVE_UP]]:
            self.rect.y -= PLAYER_VEL
        if keys_pressed[self.key_binding[MOVE_DOWN]]:
            self.rect.y += PLAYER_VEL
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
            bullet.x += BULLET_VEL * self.facing
            # Collision
            if enemy.rect.colliderect(bullet):
                enemy.hit()
                self.bullets.remove(bullet)
            elif self.facing == 1:
                if bullet.x > WIN_WIDTH:
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
                    (self.rect.height / 2) - (BULLET_HEIGHT / 2),
                    *BULLET_SIZE))
        else:
            self.bullets.append(
                pygame.Rect(
                    self.rect.x - BULLET_WIDTH, self.rect.y +
                    (self.rect.height / 2) - (BULLET_HEIGHT / 2),
                    *BULLET_SIZE))

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
            win.blit(self.health_text, (20, 20))
        else:
            win.blit(
                self.health_text,
                (WIN_WIDTH - self.health_text.get_width() - 20, 20))

    def draw_spaceship(self, win: pygame.Surface):
        # Draw player spaceship
        win.blit(self.img, self.rect)

    def draw_bullets(self, win: pygame.Surface):
        # Draw player bullets
        for bullet in self.bullets:
            pygame.draw.rect(win, self.color, bullet)

    def update_health_text(self):
        if self.health > 3:
            self.health_text = HEALTH_FONT.render(
                f"Health: {self.health}", 1, WHITE)
        else:
            self.health_text = HEALTH_FONT.render(
                f"Health: {self.health}", 1, RED)


def redraw_window(blue: Player, red: Player):
    # Draw background image
    WIN.blit(BG, (0, 0))
    # Draw player stuff
    blue.draw_health_text(WIN)
    blue.draw_spaceship(WIN)
    blue.draw_bullets(WIN)

    red.draw_health_text(WIN)
    red.draw_spaceship(WIN)
    red.draw_bullets(WIN)

    pygame.display.update()


def draw_winner(winner_text):
    WIN.blit(
        winner_text,
        ((WIN_WIDTH / 2) - (winner_text.get_width() / 2),
         (WIN_HEIGHT / 2) - (winner_text.get_height() / 2)))

    pygame.display.update()

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
        # Preven CPU bound
        pygame.time.wait(10)
        # Update current time
        currTm = pygame.time.get_ticks()


def main():
    clock = pygame.time.Clock()

    blue = Player(*BLUE_STARTING_POINT, BLUE_BORDER, 1,
                  BLUE_SPACESHIP, CYAN, BLUE_KEY_BINDING)

    red = Player(*RED_STARTING_POINT, RED_BORDER, -1,
                 RED_SPACESHIP, RED, RED_KEY_BINDING)

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

        redraw_window(blue, red)

        # Check for winner
        if blue.health <= 0 or red.health <= 0:
            if blue.health <= 0 and red.health <= 0:
                winner_text = WINNER_FONT.render("Draw!", 1, WHITE)
            elif blue.health <= 0:
                winner_text = WINNER_FONT.render("Red Wins!", 1, RED)
            elif red.health <= 0:
                winner_text = WINNER_FONT.render("Blue Wins!", 1, CYAN)
            # Stop background music
            pygame.mixer.music.stop()
            # Draw the winner
            draw_winner(winner_text)
            # Restart the game
            main()


# Colors
CYAN = (0, 235, 235)
RED = (235, 0, 0)
WHITE = (235, 235, 235)

# Main window
WIN_HEIGHT = pyautogui.size()[1] - 200
WIN_WIDTH = WIN_HEIGHT * 4 // 3
WIN_SIZE = WIN_WIDTH, WIN_HEIGHT
WIN_ICON = pygame.image.load(os.path.join('assets', 'icon.png'))
# Set window caption and icon
pygame.display.set_caption("Space War")
pygame.display.set_icon(WIN_ICON)

# Player binding
MOVE_LEFT, MOVE_RIGHT, MOVE_UP, MOVE_DOWN, SHOOT = [i for i in range(5)]

""" How to get adaptive size
If its width: WIN_WIDTH / default values of a attribute
              times the result with WIN_WIDTH
If its height: same but instead of WIN_WIDTH, use WIN_HEIGHT
If its size: can use WIN_WIDTH or WIN_HEIGHT but i use WIN_WIDTH
 """

# Player stuff
PLAYER_WIDTH = round(WIN_WIDTH / 14.58)
PLAYER_HEIGHT = round(WIN_HEIGHT / 14.58)
PLAYER_SIZE = PLAYER_WIDTH, PLAYER_HEIGHT
PLAYER_VEL = round(WIN_WIDTH / 116.62, 2)
PLAYER_HEALTH = 10

BLUE_STARTING_POINT = (
    (WIN_WIDTH * 0.25) - (PLAYER_WIDTH / 2),
    (WIN_HEIGHT / 2) - (PLAYER_HEIGHT / 2))
BLUE_BORDER = pygame.Rect(0, 0, (WIN_WIDTH / 2) - 10, WIN_HEIGHT)
BLUE_KEY_BINDING = (K_a, K_d, K_w, K_s, K_LCTRL)

RED_STARTING_POINT = (
    (WIN_WIDTH * 0.75) - (PLAYER_WIDTH / 2),
    (WIN_HEIGHT / 2) - (PLAYER_HEIGHT / 2))
RED_BORDER = pygame.Rect((WIN_WIDTH / 2) + 10, 0,
                         (WIN_WIDTH / 2) - 10, WIN_HEIGHT)
RED_KEY_BINDING = (K_LEFT, K_RIGHT, K_UP, K_DOWN, K_RCTRL)

# Player bullets
BULLET_WIDTH = round(WIN_WIDTH / 77.75, 2)
BULLET_HEIGHT = round(WIN_HEIGHT / 175.0, 2)
BULLET_SIZE = BULLET_WIDTH, BULLET_HEIGHT
BULLET_VEL = 2 * PLAYER_VEL
MAX_BULLET = 3

# Sounds
pygame.mixer.init(48000)
BULLET_FIRE_SOUND = pygame.mixer.Sound(os.path.join('assets', 'laser.wav'))
BULLET_FIRE_SOUND.set_volume(0.2)
BULLET_HIT_SOUND = pygame.mixer.Sound(os.path.join('assets', 'explosion.wav'))
BULLET_HIT_SOUND.set_volume(0.16)
pygame.mixer.music.load(os.path.join('assets', 'backsound.wav'))
pygame.mixer.music.set_volume(0.2)

# Fonts
pygame.font.init()
HEALTH_FONT = pygame.font.Font(
    os.path.join('assets', 'pixel_font.ttf'),
    round(WIN_WIDTH / 23.32))
WINNER_FONT = pygame.font.Font(
    os.path.join('assets', 'pixel_font.ttf'),
    round(WIN_WIDTH / 9.33))

# Game fps
FPS = 60

# Create main window
WIN = pygame.display.set_mode(WIN_SIZE)

# Import images
BG = pygame.transform.smoothscale(pygame.image.load(
    os.path.join('assets', 'bg.png')).convert(), WIN_SIZE)

BLUE_SPACESHIP = pygame.transform.smoothscale(pygame.transform.rotate(
    pygame.image.load(
        os.path.join(
            'assets',
            'blue_spaceship.png')).convert_alpha(),
    90),
    PLAYER_SIZE)

RED_SPACESHIP = pygame.transform.smoothscale(pygame.transform.rotate(
    pygame.image.load(
        os.path.join(
            'assets',
            'red_spaceship.png')).convert_alpha(),
    270),
    PLAYER_SIZE)

if __name__ == '__main__':
    main()
