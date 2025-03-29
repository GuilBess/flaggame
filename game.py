import pygame
import json
import os
import random

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

font = pygame.font.Font(None, 36)

# Colors
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
BLACK = (0, 0, 0)
RED = (255, 100, 100)
DARK_BG = (15, 0, 25)

# Buttons
button_rect = pygame.Rect(540, 600, 200, 50)
stats_button_rect = pygame.Rect(1080, 20, 150, 50)
button_color = GRAY
txt_button = "Reveal"

# Text input setup
input_box = pygame.Rect(440, 500, 400, 50)
text = ""
input_active = False

# Game state variables
state = "game"
codes = {}
stats = {}
stat_file = {}

# Load country names
with open("data/countries.json", "r") as f:
    codes = json.load(f)

# Load stats from file
if os.path.exists("stats.json"):
    with open("stats.json", "r") as f:
        stat_file = json.load(f)

# Get a random PNG file from the "flags" directory
def get_random_file(directory):
    files = [f for f in os.listdir(directory) if f.endswith(".png")]
    return os.path.join(directory, random.choice(files)) if files else None

# Load & scale flag
def load_scaled_flag(png_path, height=100):
    """Loads an image and scales it to the given height while maintaining aspect ratio, centering it."""
    if png_path and os.path.exists(png_path):
        flag = pygame.image.load(png_path).convert_alpha()
        aspect_ratio = flag.get_width() / flag.get_height()
        new_width = int(height * aspect_ratio)
        return pygame.transform.scale(flag, (new_width, height)), new_width  # Return both scaled flag and width
    return None, 0

def get_top_stats():
    global stat_file
    if not stat_file:
        return [], []

    # Compute correct-to-wrong ratios
    flag_ratios = {
        code: (correct, wrong, (correct + 1) / (wrong + 1))  # Avoid division by zero
        for code, (correct, wrong) in stat_file.items()
    }

    # Sort by highest ratio for best known flags
    best_known = sorted(flag_ratios.items(), key=lambda x: x[1][2], reverse=True)[:5]
    
    # Sort by lowest ratio for worst known flags
    worst_known = sorted(flag_ratios.items(), key=lambda x: x[1][2])[:5]

    return best_known, worst_known

# Load first flag
png_path = get_random_file("png")
flag, flag_width = load_scaled_flag(png_path, height=350)

# Display loop
while running:
    screen.fill(DARK_BG)

    if state == "game":
        # Draw flag
        if flag:
            flag_x = (1280 - flag_width) // 2  # Center horizontally
            screen.blit(flag, (flag_x, 50))  # Y-position remains fixed

        # Draw input box
        pygame.draw.rect(screen, WHITE if input_active else GRAY, input_box, 2)
        text_surface = font.render(text, True, WHITE)
        screen.blit(text_surface, (input_box.x + 10, input_box.y + 10))

        # Draw "Reveal/Next" button
        pygame.draw.rect(screen, button_color, button_rect)
        button_text = font.render(txt_button, True, BLACK)
        screen.blit(button_text, (button_rect.x + 50, button_rect.y + 10))

        # Draw "Stats" button
        pygame.draw.rect(screen, GRAY, stats_button_rect)
        stats_text = font.render("Stats", True, BLACK)
        screen.blit(stats_text, (stats_button_rect.x + 50, stats_button_rect.y + 10))

    elif state == "stats":
        top_correct, top_wrong = get_top_stats()

        # Display "Most Correct" stats
        correct_text = font.render("Top 5 Best Known Flags:", True, WHITE)
        screen.blit(correct_text, (100, 100))
        for i, (code, (correct, _, ratio)) in enumerate(top_correct):
            country_name = codes.get(code, code)
            flag_path = f"png/{code.lower()}.png"
            if os.path.exists(flag_path):
                flag_image, width = load_scaled_flag(flag_path, height=50)  # Small flags
                screen.blit(flag_image, (100, 140 + i * 80))
            country_text = font.render(f"{i+1}. {country_name} - {ratio:.2f} ratio", True, WHITE)
            screen.blit(country_text, (220, 150 + i * 80))

        # Display "Most Incorrect" stats
        wrong_text = font.render("Top 5 Worst Known Flags:", True, WHITE)
        screen.blit(wrong_text, (650, 100))
        for i, (code, (_, wrong, ratio)) in enumerate(top_wrong):
            country_name = codes.get(code, code)
            flag_path = f"png/{code.lower()}.png"
            if os.path.exists(flag_path):
                flag_image, width = load_scaled_flag(flag_path, height=50)  # Small flags
                screen.blit(flag_image, (650, 140 + i * 80))
            country_text = font.render(f"{i+1}. {country_name} - {ratio:.2f} ratio", True, WHITE)
            screen.blit(country_text, (770, 150 + i * 80))

        # "Back" button to return to game
        pygame.draw.rect(screen, GRAY, stats_button_rect)
        back_text = font.render("Back", True, BLACK)
        screen.blit(back_text, (stats_button_rect.x + 50, stats_button_rect.y + 10))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            with open("stats.json", "w") as f:
                json.dump(stat_file, f)
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if state == "game":
                if input_box.collidepoint(event.pos):
                    input_active = True
                else:
                    input_active = False

                if button_rect.collidepoint(event.pos):
                    code_country = png_path[4:-4].upper()
                    if txt_button == "Reveal":
                        if code_country in stats:
                            stats[code_country][1] += 1
                        else:
                            stats[code_country] = [0, 1]
                        text = codes.get(code_country, "Unknown")
                        txt_button = "Next"
                    else:
                        png_path = get_random_file("png")
                        flag, flag_width = load_scaled_flag(png_path, height=350)
                        text = ""
                        txt_button = "Reveal"

                if stats_button_rect.collidepoint(event.pos):
                   if stats_button_rect.collidepoint(event.pos):
                        # Merge in-memory stats into stat_file before showing stats
                        for code in stats:
                            if code in stat_file:
                                stat_file[code][0] += stats[code][0]  # Add correct guesses
                                stat_file[code][1] += stats[code][1]  # Add incorrect guesses
                            else:
                                stat_file[code] = stats[code]

                        with open("stats.json", "w") as f:
                            json.dump(stat_file, f)  # Save updated stats

                        stats.clear()  # We empty the stats we have in memory here

                        state = "stats"  # Switch to stats screen

            elif state == "stats":
                if stats_button_rect.collidepoint(event.pos):
                    state = "game"

        if event.type == pygame.KEYDOWN and input_active and state == "game":
            if event.key == pygame.K_RETURN:
                code_country = png_path[4:-4].upper()
                if text.lower() == codes.get(code_country, "").lower():
                    if code_country in stats:
                        stats[code_country][0] += 1
                    else:
                        stats[code_country] = [1, 0]
                    png_path = get_random_file("png")
                    flag, flag_width = load_scaled_flag(png_path, height=350)
                    text = ""
                    txt_button = "Reveal"
                else:
                    button_color = RED
            elif event.key == pygame.K_BACKSPACE:
                text = text[:-1]
            else:
                text += event.unicode

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
