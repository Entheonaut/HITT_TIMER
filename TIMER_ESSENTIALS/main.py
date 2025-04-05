import pygame
import json
import os

# Pygame setup
pygame.init()
pygame.mixer.init()

# Screen setup
WIDTH, HEIGHT = 400, 300
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("HIIT Timer")

# Colors and styles
WHITE = pygame.Color(224, 255, 255)  # Light cyan
CYAN = pygame.Color(0, 255, 255)  # Spring green
GREEN = pygame.Color(100, 149, 237)  # Cornflower blue
MARK = 'X'

# Fonts
main_font = pygame.font.SysFont('Stencil', (HEIGHT * 5) // 8)
small_font = pygame.font.SysFont("lucidaconsole", HEIGHT // 15, bold=True)

# --- Settings Persistence ---
SETTINGS_FILE = "settings.json"


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as file_to_read:
            return json.load(file_to_read)
    return {"work_seconds": 40,
            "rest_time": 20,
            "long_break_time": 300}


def save_settings(settings_file):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as file_to_write:
        json.dump(settings_file, file_to_write)


def clamp(value, min_value=5, max_value=600):
    return max(min_value, min(value, max_value))


def adjust_time(setting, increment=True):
    global work_seconds, rest_time, long_break_time
    if setting == 0:  # work time
        work_seconds = clamp(work_seconds + (5 if increment else -5))
    elif setting == 1:  # rest time
        rest_time = clamp(rest_time + (5 if increment else -5))
    elif setting == 2:  # long break time
        long_break_time = clamp(long_break_time + (5 if increment else -5))


# Load or set defaults
settings = load_settings()
work_seconds = settings["work_seconds"]
rest_time = settings["rest_time"]
long_break_time = 300  # hardcoded for now

# State
time_left = work_seconds
is_working = True
reps = 0
running = False
in_settings = False
in_timer = True
selected_setting = 0  # 0 = work, 1 = rest

# Timer tick event
TIMER_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(TIMER_EVENT, 1000)

clock = pygame.time.Clock()


# Drawing functions
def draw_timer():
    screen.fill(CYAN if not is_working else GREEN)
    text = main_font.render(str(time_left), True, WHITE)
    screen.blit(text, (((WIDTH * 2) // 7), HEIGHT // 6))

    rep_markers = small_font.render(MARK * (reps // 2), True, WHITE)
    screen.blit(rep_markers, ((WIDTH // 2) - (10 * reps // 2), (HEIGHT * 7) // 10))

    instruction_text = small_font.render("SPACE: Start/Pause | R: Reset | S: Settings", True, WHITE)
    screen.blit(instruction_text, (WIDTH // 50, (HEIGHT * 37) // 40))


def draw_settings():
    screen.fill("gray20")
    title = small_font.render("SETTINGS", True, WHITE)
    screen.blit(title, (WIDTH // 2 - 50, 30))

    color_a = "yellow" if selected_setting == 0 else WHITE
    color_b = "yellow" if selected_setting == 1 else WHITE
    color_c = "yellow" if selected_setting == 2 else WHITE

    work_text = small_font.render(f"Work Time: {work_seconds}s", True, color_a)
    rest_text = small_font.render(f"Rest Time: {rest_time}s", True, color_b)
    long_break_text = small_font.render(f"Long Break Time: {long_break_time}s", True, color_c)

    screen.blit(work_text, (WIDTH // 5, 100))
    screen.blit(rest_text, (WIDTH // 5, 150))
    screen.blit(long_break_text, (WIDTH // 5, 200))

    info = small_font.render("↑↓ to adjust | TAB: Toggle | Enter: Back", True, WHITE)
    screen.blit(info, (WIDTH // 20, HEIGHT - 40))


# Main loop
running_game = True
while running_game:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running_game = False

        elif event.type == pygame.KEYDOWN:
            if in_settings:
                if event.key == pygame.K_UP:
                    if selected_setting == 0:
                        work_seconds = clamp(work_seconds + 5)
                    else:
                        rest_time = clamp(rest_time + 5)
                elif event.key == pygame.K_DOWN:
                    if selected_setting == 0:
                        work_seconds = clamp(work_seconds - 5)
                    else:
                        rest_time = clamp(rest_time - 5)
                elif event.key == pygame.K_TAB:
                    selected_setting = (selected_setting + 1) % 3
                elif event.key == pygame.K_RETURN:
                    # Save & reset timer state
                    work_seconds = clamp(work_seconds)
                    rest_time = clamp(rest_time)
                    save_settings({"work_seconds": work_seconds, "rest_time": rest_time})
                    time_left = work_seconds
                    is_working = True
                    reps = 0
                    running = False
                    in_settings = False
                    in_timer = not in_settings

            elif in_timer:
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
                    in_timer = not in_settings

        elif event.type == TIMER_EVENT and running and in_timer:
            time_left -= 1
            if time_left <= 0:
                if reps % 8 == 7 and not is_working:
                    time_left = long_break_time
                else:
                    is_working = not is_working
                    time_left = work_seconds if is_working else rest_time
                reps += 1

    # Draw UI
    if in_settings:
        draw_settings()
    elif in_timer:
        draw_timer()

    pygame.display.flip()
    clock.tick(20)

pygame.quit()
