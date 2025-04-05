import pygame
import json
import os

pygame.init()
pygame.mixer.init()

# Screen setup
WIDTH, HEIGHT = 400, 300
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("HIIT Timer")

# Colors and styles
WHITE = pygame.Color(224, 255, 255)
CYAN = pygame.Color(0, 255, 255)
GREEN = pygame.Color(100, 149, 237)
GREY = pygame.Color(92, 92, 92)
MARK = 'X'

# Fonts
main_font = pygame.font.SysFont('Stencil', (HEIGHT * 5) // 8)
small_font = pygame.font.SysFont("lucidaconsole", HEIGHT // 25, bold=True)

# Settings file
SETTINGS_FILE = "settings.json"
SETTINGS_KEYS = ["work_seconds", "rest_time", "long_break_time"]


def clamp(val, min_val=5, max_val=600):
    return max(min_val, min(val, max_val))


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"work_seconds": 40, "rest_time": 20, "long_break_time": 300}


def save_settings(data):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)


# Load settings
settings = load_settings()
work_seconds = settings.get("work_seconds", 40)
rest_time = settings.get("rest_time", 20)
long_break_time = settings.get("long_break_time", 300)

# State
time_left = work_seconds
is_working = True
reps = 0
running = False
in_settings = False
selected_setting = 0

# Timer
TIMER_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(TIMER_EVENT, 1000)
clock = pygame.time.Clock()


def draw_timer():
    screen.fill(GREEN if is_working else CYAN)
    timer_text = main_font.render(str(time_left), True, WHITE)
    screen.blit(timer_text, ((WIDTH * 2) // 7, HEIGHT // 6))

    marks = small_font.render(MARK * (reps // 2), True, WHITE)
    screen.blit(marks, ((WIDTH // 2) - (10 * reps // 2), (HEIGHT * 7) // 10))

    instruction = small_font.render("SPACE: Start/Pause | R: Reset | S: Settings", True, WHITE)
    screen.blit(instruction, (WIDTH // 50, (HEIGHT * 37) // 40))


def draw_settings():
    screen.fill(GREY)
    title = small_font.render("SETTINGS", True, WHITE)
    screen.blit(title, (WIDTH // 2 - 50, 30))

    values = [work_seconds, rest_time, long_break_time]
    labels = ["Work Time", "Rest Time", "Long Break"]
    for i, (label, val) in enumerate(zip(labels, values)):
        color = "yellow" if i == selected_setting else WHITE
        setting_text = small_font.render(f"{label}: {val}s", True, color)
        screen.blit(setting_text, (WIDTH // 5, 100 + i * 50))

    help_text = small_font.render("↑↓ to adjust | TAB: Toggle | Enter: Back", True, WHITE)
    screen.blit(help_text, (WIDTH // 20, HEIGHT - 40))


# Main loop
running_game = True
while running_game:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running_game = False

        elif event.type == pygame.KEYDOWN:
            if in_settings:
                if event.key in [pygame.K_UP, pygame.K_DOWN]:
                    delta = 15 if selected_setting == 2 else 5
                    inc = 1 if event.key == pygame.K_UP else -1
                    if selected_setting == 0:
                        work_seconds = clamp(work_seconds + inc * delta)
                    elif selected_setting == 1:
                        rest_time = clamp(rest_time + inc * delta)
                    elif selected_setting == 2:
                        long_break_time = clamp(long_break_time + inc * delta, 60, 1800)

                elif event.key == pygame.K_TAB:
                    selected_setting = (selected_setting + 1) % 3

                elif event.key == pygame.K_RETURN:
                    save_settings({
                        "work_seconds": work_seconds,
                        "rest_time": rest_time,
                        "long_break_time": long_break_time
                    })
                    time_left = work_seconds
                    is_working = True
                    reps = 0
                    running = False
                    in_settings = False

            else:
                if event.key == pygame.K_SPACE:
                    running = not running
                elif event.key == pygame.K_r:
                    running = False
                    is_working = True
                    time_left = work_seconds
                    reps = 0
                elif event.key == pygame.K_s:
                    running = False
                    in_settings = True

        elif event.type == TIMER_EVENT and running and not in_settings:
            time_left -= 1
            if time_left <= 0:
                if reps % 8 == 7 and not is_working:
                    time_left = long_break_time
                else:
                    is_working = not is_working
                    time_left = work_seconds if is_working else rest_time
                reps += 1

    # Drawing
    if in_settings:
        draw_settings()
    else:
        draw_timer()

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
