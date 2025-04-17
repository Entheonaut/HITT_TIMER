import pygame
import sys
import json
import os


# Function to get the path for the files
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


pygame.init()
pygame.mixer.init()

icon_relative_path = r'.\hitt_time_icon.ico'
icon = pygame.image.load(resource_path("hitt_time_icon.ico"))
pygame.display.set_icon(icon)
# Screen setup
WIDTH, HEIGHT = 600, 400
height_offset = HEIGHT // 5
settings_height_spacing = (height_offset * 2) // 3
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("HIIT Timer")

settings_button_rect = pygame.Rect(WIDTH - 110, HEIGHT - 40, 100, 30)


# Colors and styles
WHITE = pygame.Color(224, 255, 255)
Orange = pygame.Color(255, 165, 93)
powderBlue = pygame.Color(100, 149, 237)
GREY = pygame.Color(92, 92, 92)
MARK = 'X '

# Fonts
main_font = pygame.font.SysFont('Stencil', (HEIGHT * 5) // 8)
small_font = pygame.font.SysFont("lucidaconsole", HEIGHT // 20, bold=True)

# Settings file
SETTINGS_FILE = "HIIT_Timer_Settings.json"
SETTINGS_KEYS = ["Work Time", "Rest Time", "Long Rest Time", "Total Cycles", "Long Phase Cycle"]





# Load sound files
beep_warning = pygame.mixer.Sound(resource_path("beep-warning.mp3"))
livechat = pygame.mixer.Sound(resource_path("livechat.mp3"))
notification_positive = pygame.mixer.Sound(resource_path("notification-positive.mp3"))


# Sound functions
def play_warning_sound():
    beep_warning.play()


def play_livechat_sound():
    livechat.play()


def play_positive_notification():
    notification_positive.play()


def clamp(val, min_val=5, max_val=600):
    return max(min_val, min(val, max_val))


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "work_seconds": 7,
        "rest_time": 13,
        "long_break_time": 60,
        "total_reps": 10,
        "Long Phase Cycle": 5
    }


def save_settings(data):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)


# Load settings
settings = load_settings()
work_seconds = settings.get("work_seconds", 7)
rest_time = settings.get("rest_time", 18)
long_break_time = settings.get("long_break_time", 30)
total_reps = settings.get("total_reps", 10)
LONG_BREAK_EVERY = settings.get("LONG_BREAK_EVERY", 5)

# State
time_left = work_seconds
is_working = True
phase_count = 0  # incremented every phase (work/rest)
running = False
in_settings = False
selected_setting = 0

start_sequence_texts = ["Ready", "Set", "Go!"]
start_sequence_index = 0
show_start_sequence = False
start_sequence_timer = 0

# Timer
TIMER_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(TIMER_EVENT, 1000)
clock = pygame.time.Clock()


def get_rep_count(phase_count):
    return (phase_count + 1) // 2


def reps_display(count):
    return MARK * get_rep_count(count)


def draw_timer():
    screen.fill(powderBlue if is_working else Orange)
    timer_text = main_font.render(str(time_left), True, WHITE)
    screen.blit(timer_text, ((WIDTH * 2) // 7, HEIGHT // 6))

    current_reps = get_rep_count(phase_count)
    marks = reps_display(phase_count)
    screen.blit(small_font.render(marks, True, WHITE), ((WIDTH // 2) - (10 * current_reps), (HEIGHT * 7) // 10))

    rep_count_text = small_font.render(f"Rounds: {current_reps}/{total_reps}", True, Orange)
    screen.blit(rep_count_text, ((WIDTH * 2) // 5, (HEIGHT * 33) // 40))

    instruction = small_font.render("SPACE: Start/Pause | R: Reset", True, GREY)
    screen.blit(instruction, (WIDTH // 50, (HEIGHT * 37) // 40))

    # Settings Button
    pygame.draw.rect(screen, GREY, settings_button_rect, border_radius=6)
    button_text = small_font.render("Settings", True, Orange)
    screen.blit(button_text, (settings_button_rect.x + 10, settings_button_rect.y + 5))


def draw_settings():
    screen.fill(GREY)
    title = small_font.render("SETTINGS", True, WHITE)
    screen.blit(title, ((WIDTH * 2) // 5, HEIGHT // 12))

    values = [work_seconds, rest_time, long_break_time, total_reps, LONG_BREAK_EVERY]
    labels = ["Work Time", "Rest Time", "Long Rest Time", "Total Cycles", "LONG_BREAK_EVERY"]

    for i, (label, val) in enumerate(zip(labels, values)):
        color = "yellow" if i == selected_setting else WHITE
        setting_text = small_font.render(f"{label}: {val}", True, color)
        screen.blit(setting_text, (WIDTH // 5, height_offset + i * settings_height_spacing))

    help_text = small_font.render("↑↓ to adjust | TAB: Toggle | Enter: Back", True, WHITE)
    screen.blit(help_text, (WIDTH // 20, HEIGHT - 40))


# Main loop
running_game = True
while running_game:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running_game = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if settings_button_rect.collidepoint(event.pos):
                running = False
                in_settings = True
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
                        long_break_time = clamp(long_break_time + inc * delta, 30, 600)
                    elif selected_setting == 3:
                        total_reps = clamp(total_reps + inc, 2, 100)
                    elif selected_setting == 4:
                        LONG_BREAK_EVERY = clamp(LONG_BREAK_EVERY + inc, 2, 100)

                elif event.key == pygame.K_TAB:
                    selected_setting = (selected_setting + 1) % 5

                elif event.key == pygame.K_RETURN:
                    save_settings({
                        "work_seconds": work_seconds,
                        "rest_time": rest_time,
                        "long_break_time": long_break_time,
                        "total_reps": total_reps,
                        "LONG_BREAK_EVERY": LONG_BREAK_EVERY
                    })
                    time_left = work_seconds
                    is_working = True
                    phase_count = 0
                    running = False
                    in_settings = False

            else:
                if event.key == pygame.K_SPACE:
                    if not running and not show_start_sequence and phase_count == 0:
                        show_start_sequence = True
                        start_sequence_index = 0
                        start_sequence_timer = pygame.time.get_ticks()
                    elif not show_start_sequence:
                        # Toggle pause/resume if not showing start sequence
                        running = not running
                elif event.key == pygame.K_r:
                    running = False
                    is_working = True
                    time_left = work_seconds
                    phase_count = 0
                elif event.key == pygame.K_s:
                    running = False
                    in_settings = True

        elif event.type == TIMER_EVENT and running and not in_settings:
            time_left -= 1
            if is_working:
                if (5 >= time_left > 2) and time_left % 2 == 1:
                    play_livechat_sound()
                elif time_left == 1:
                    play_positive_notification()
            else:
                if (5 >= time_left > 2) and time_left % 2 == 1:
                    play_livechat_sound()
                elif time_left == 1:
                    play_warning_sound()

            if time_left <= 0:
                if get_rep_count(phase_count) == total_reps:
                    phase_count = 0
                    running = False
                    is_working = True
                    time_left = work_seconds
                else:
                    if is_working and get_rep_count(phase_count) % LONG_BREAK_EVERY == (LONG_BREAK_EVERY - 1) and get_rep_count(
                            phase_count) > 0:
                        is_working = False
                        time_left = long_break_time
                    else:
                        is_working = not is_working
                        time_left = work_seconds if is_working else rest_time
                    phase_count += 1
        if show_start_sequence:
            now = pygame.time.get_ticks()
            if now - start_sequence_timer >= 1000:
                start_sequence_index += 1
                start_sequence_timer = now
                play_livechat_sound()
                if start_sequence_index >= len(start_sequence_texts):
                    show_start_sequence = False
                    running = True
        # Drawing
    if show_start_sequence:
        screen.fill(GREY)
        msg = start_sequence_texts[start_sequence_index]
        start_font = pygame.font.SysFont("Stencil", HEIGHT // 5)
        rendered_text = start_font.render(msg, True, WHITE)
        text_rect = rendered_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(rendered_text, text_rect)
    else:
        if in_settings:
            draw_settings()
        else:
            draw_timer()

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
