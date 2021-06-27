import pygame
import sys
import os
import pyautogui

WIN_HEIGHT = pyautogui.size()[1] - 200
WIN_WIDTH = WIN_HEIGHT * 4 // 3
WIN_SIZE = WIN_WIDTH, WIN_HEIGHT
WIN = pygame.display.set_mode(WIN_SIZE)

MIDDLE_BORDER = pygame.Rect((WIN_WIDTH / 2) - 5, 0, 10, WIN_HEIGHT)

CYAN = (0, 235, 235)
RED = (235, 0, 0)
WHITE = (235, 235, 235)

BG = pygame.transform.smoothscale(pygame.image.load(
    os.path.join('assets', 'bg.png')), WIN_SIZE)

PLAYER_SIZE = PLAYER_WIDTH, PLAYER_HEIGHT = 64, 48
PLAYER_VEL = 8
PLAYER_HEALTH = 10

BLUE_SPACESHIP = pygame.transform.smoothscale(pygame.transform.rotate(
    pygame.image.load(
        os.path.join(
            'assets',
            'blue_spaceship.png')),
    90),
    PLAYER_SIZE)

RED_SPACESHIP = pygame.transform.smoothscale(pygame.transform.rotate(
    pygame.image.load(
        os.path.join(
            'assets',
            'red_spaceship.png')),
    270),
    PLAYER_SIZE)

BULLET_SIZE = BULLET_WIDTH, BULLET_HEIGHT = 12, 4
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

BLUE_HIT = pygame.USEREVENT + 1
RED_HIT = pygame.USEREVENT + 2

# FONT
pygame.font.init()
HEALTH_FONT = pygame.font.Font(os.path.join('assets', 'pixel_font.ttf'), 40)
WINNER_FONT = pygame.font.Font(os.path.join('assets', 'pixel_font.ttf'), 100)

FPS = 60


def draw_winner(winner_text):
    WIN.blit(
        winner_text,
        ((WIN_WIDTH / 2) - (winner_text.get_width() / 2),
         (WIN_HEIGHT / 2) - (winner_text.get_height() / 2)))

    pygame.display.update()

    for _ in range(300):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        pygame.time.delay(10)


def handle_bullets(blue, red, blue_bullets, red_bullets):
    for blue_bullet in blue_bullets:
        blue_bullet.x += BULLET_VEL
        # Collision
        if red.colliderect(blue_bullet):
            pygame.event.post(pygame.event.Event(RED_HIT))
            blue_bullets.remove(blue_bullet)
        elif blue_bullet.x > WIN_WIDTH:
            blue_bullets.remove(blue_bullet)

    for red_bullet in red_bullets:
        red_bullet.x -= BULLET_VEL
        # Collision
        if blue.colliderect(red_bullet):
            pygame.event.post(pygame.event.Event(BLUE_HIT))
            red_bullets.remove(red_bullet)
        elif red_bullet.x < 0:
            red_bullets.remove(red_bullet)


def red_handle_movement(red, keys_pressed):
    # Move
    if keys_pressed[pygame.K_LEFT]:  # LEFT
        red.x -= PLAYER_VEL
    if keys_pressed[pygame.K_RIGHT]:  # RIGHT
        red.x += PLAYER_VEL
    if keys_pressed[pygame.K_UP]:  # UP
        red.y -= PLAYER_VEL
    if keys_pressed[pygame.K_DOWN]:  # DOWN
        red.y += PLAYER_VEL
    # Border
    if red.x < MIDDLE_BORDER.x + MIDDLE_BORDER.width:  # LEFT
        red.x = MIDDLE_BORDER.x + MIDDLE_BORDER.width
    elif red.x + red.width > WIN_WIDTH:  # RIGHT
        red.x = WIN_WIDTH - red.width
    if red.y < 0:  # UP
        red.y = 0
    elif red.y + red.height > WIN_HEIGHT:  # DOWN
        red.y = WIN_HEIGHT - red.height


def blue_handle_movement(blue, keys_pressed):
    # Move
    if keys_pressed[pygame.K_a]:  # LEFT
        blue.x -= PLAYER_VEL
    if keys_pressed[pygame.K_d]:  # RIGHT
        blue.x += PLAYER_VEL
    if keys_pressed[pygame.K_w]:  # UP
        blue.y -= PLAYER_VEL
    if keys_pressed[pygame.K_s]:  # DOWN
        blue.y += PLAYER_VEL
    # Border
    if blue.x < 0:  # LEFT
        blue.x = 0
    elif blue.x + blue.width > MIDDLE_BORDER.x:  # RIGHT
        blue.x = MIDDLE_BORDER.x - blue.width
    if blue.y < 0:  # UP
        blue.y = 0
    elif blue.y + blue.height > WIN_HEIGHT:  # DOWN
        blue.y = WIN_HEIGHT - blue.height


def redraw_window(
    blue, red, blue_bullets, red_bullets, blue_health_text,
        red_health_text):
    WIN.blit(BG, (0, 0))
    WIN.blit(blue_health_text, (20, 20))
    WIN.blit(red_health_text, (WIN_WIDTH - red_health_text.get_width() - 20, 20))
    WIN.blit(BLUE_SPACESHIP, blue)
    WIN.blit(RED_SPACESHIP, red)
    # Draw bullets
    for blue_bullet in blue_bullets:
        pygame.draw.rect(WIN, CYAN, blue_bullet)
    for red_bullet in red_bullets:
        pygame.draw.rect(WIN, RED, red_bullet)

    pygame.display.update()


def main():
    clock = pygame.time.Clock()

    blue = pygame.Rect(
        (WIN_WIDTH * 0.25) - (PLAYER_WIDTH / 2),
        (WIN_HEIGHT / 2) - (PLAYER_HEIGHT / 2),
        *PLAYER_SIZE)
    blue_bullets = []
    blue_health = PLAYER_HEALTH
    blue_health_text = HEALTH_FONT.render(f"Health: {blue_health}", 1, WHITE)

    red = pygame.Rect(
        (WIN_WIDTH * 0.75) - (PLAYER_WIDTH / 2),
        (WIN_HEIGHT / 2) - (PLAYER_HEIGHT / 2),
        *PLAYER_SIZE)
    red_bullets = []
    red_health = PLAYER_HEALTH
    red_health_text = HEALTH_FONT.render(f"Health: {red_health}", 1, WHITE)

    # Play background music
    pygame.mixer.music.play(-1)

    pygame.event.set_allowed((pygame.QUIT, pygame.KEYDOWN, BLUE_HIT, RED_HIT))

    # Main loop
    while 1:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_LCTRL:
                    if len(blue_bullets) < MAX_BULLET:
                        blue_bullets.append(
                            pygame.Rect(
                                blue.x + blue.width, blue.y +
                                (blue.height / 2) - (BULLET_HEIGHT / 2),
                                *BULLET_SIZE))
                        BULLET_FIRE_SOUND.play()

                if event.key == pygame.K_RCTRL:
                    if len(red_bullets) < MAX_BULLET:
                        red_bullets.append(
                            pygame.Rect(
                                red.x - BULLET_WIDTH, red.y +
                                (red.height / 2) - (BULLET_HEIGHT / 2),
                                *BULLET_SIZE))
                        BULLET_FIRE_SOUND.play()

            if event.type == BLUE_HIT:
                BULLET_HIT_SOUND.play()
                blue_health -= 1
                if blue_health > 3:
                    blue_health_text = HEALTH_FONT.render(
                        f"Health: {blue_health}", 1, WHITE)
                else:
                    blue_health_text = HEALTH_FONT.render(
                        f"Health: {blue_health}", 1, RED)

            if event.type == RED_HIT:
                BULLET_HIT_SOUND.play()
                red_health -= 1
                if red_health > 3:
                    red_health_text = HEALTH_FONT.render(
                        f"Health: {red_health}", 1, WHITE)
                else:
                    red_health_text = HEALTH_FONT.render(
                        f"Health: {red_health}", 1, RED)

        keys_pressed = pygame.key.get_pressed()

        blue_handle_movement(blue, keys_pressed)
        red_handle_movement(red, keys_pressed)

        handle_bullets(blue, red, blue_bullets, red_bullets)

        redraw_window(blue, red, blue_bullets, red_bullets,
                      blue_health_text, red_health_text)

        if blue_health <= 0 or red_health <= 0:
            if blue_health <= 0 and red_health <= 0:
                winner_text = WINNER_FONT.render("Draw!", 1, WHITE)
            elif blue_health <= 0:
                winner_text = WINNER_FONT.render("Red Wins!", 1, RED)
            elif red_health <= 0:
                winner_text = WINNER_FONT.render("Blue Wins!", 1, CYAN)
            # Stop background music
            pygame.mixer.music.stop()
            # Draw the winner
            draw_winner(winner_text)
            # Restart the game
            main()


if __name__ == '__main__':
    main()
