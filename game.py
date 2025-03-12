import pygame
import json
import os
import random

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

font = pygame.font.Font(None, 36)  # Default font with size 36

# Colors
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
BLACK = (0, 0, 0)

# Button setup
button_rect = pygame.Rect(540, 600, 200, 50)  # x, y, width, height
button_color = GRAY
txt_button = "Reveal"

# Text input setup
input_box = pygame.Rect(440, 500, 400, 50)
text = ""
input_active = False

codes = {}
stats = {}
stat_file = {}
state = 0 #0 = normal, 1 = display answer

with open("countries.json", "r") as f:
    codes = json.load(f)

# Get a random PNG file from the "flags" directory
def get_random_file(directory):
    files = [f for f in os.listdir(directory) if f.endswith(".png")]
    if files:
        return os.path.join(directory, random.choice(files))
    return None  # Return None if no PNGs are found

# Load the first random flag
png_path = get_random_file("png")  # Change directory to where your PNGs are stored
flag = pygame.image.load(png_path).convert_alpha() if png_path else None
flag = pygame.transform.scale(flag, (600, 350))  # Adjust size as needed

# Display the image
screen.fill((15, 0, 25))

screen.blit(flag, (390, 50))

# Paint screen once
pygame.display.flip()

while running:

    # Fill screen
    screen.fill((15, 0, 25))

    # Draw flag
    screen.blit(flag, (390, 50))

    # Draw text input box
    pygame.draw.rect(screen, WHITE if input_active else GRAY, input_box, 2)
    text_surface = font.render(text, True, WHITE)
    screen.blit(text_surface, (input_box.x + 10, input_box.y + 10))

    # Draw button
    pygame.draw.rect(screen, button_color, button_rect)
    button_text = font.render(txt_button, True, BLACK)
    screen.blit(button_text, (button_rect.x + 50, button_rect.y + 10))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            with open("stats.json", "r") as f:
                stat_file = json.load(f)
                for i in stats.keys():
                    if i in stat_file.keys():
                        print("hihi")
                        stat_file[i][0] += stats[i][0]
                        stat_file[i][1] += stats[i][1]
                    else:
                        stat_file[i] = stats[i]
            with open("stats.json", "w") as f:
                json.dump(stat_file, f)
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if input_box.collidepoint(event.pos):
                input_active = True  # Activate text input
            else:
                input_active = False  # Deactivate text input

            if button_rect.collidepoint(event.pos):
                if state == 0:
                    code_country = png_path[4:-4].upper()
                    if code_country in stats.keys():
                        stats[code_country][1] += 1
                    else:
                        stats[code_country] = [0,1]
                    text = codes[code_country]
                    txt_button = "Next"
                    state = 1
                else:
                    txt_button = "Reveal"
                    png_path = get_random_file("png")  # Change directory to where your PNGs are stored
                    flag = pygame.image.load(png_path).convert_alpha() if png_path else None
                    flag = pygame.transform.scale(flag, (600, 350))  # Adjust size as needed
                    text = ""
                    button_color = GRAY
                    state = 0
                

        if event.type == pygame.KEYDOWN and input_active:
            if event.key == pygame.K_RETURN and state == 0:
                    code_country = png_path[4:-4].upper()
                    country = codes[code_country].lower()
                    if country == text.lower():
                        png_path = get_random_file("png")  # Change directory to where your PNGs are stored
                        flag = pygame.image.load(png_path).convert_alpha() if png_path else None
                        flag = pygame.transform.scale(flag, (600, 350))  # Adjust size as needed
                        text = ""
                        button_color = GRAY
                    else: 
                        print(text.lower(), country)
                        button_color = (255, 100, 100)
                        text = ""

            elif event.key == pygame.K_BACKSPACE:
                text = text[:-1]  # Remove last character
            else:
                text += event.unicode  # Add character

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
