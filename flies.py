import os
import pygame
import random
import math

# Initialize pygame
pygame.init()

# Avoid absolute paths by using the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Path for score data
data_folder_path = os.path.join(script_dir, "data", "score")

# Window dimensions
w_screen = 1600
h_screen = 1024

# Create window
def create_window():
    screen = pygame.display.set_mode((w_screen, h_screen))
    pygame.display.set_caption("Swat Silliness")
    return screen

# Create score file
def create_score_file():
    score_file_path = os.path.join(data_folder_path, "Score.txt")
    try:
        with open(score_file_path, "x") as file:
            pass
    except FileExistsError:
        pass

def clear_score_file():
    score_file_path = os.path.join(data_folder_path, "Score.txt")
    with open(score_file_path, "w") as file:
        file.write("0")
    return 0, 0

create_score_file()

# Load score document
def load_score():
    score_file_path = os.path.join(data_folder_path, "Score.txt")
    try:
        with open(score_file_path, "r") as file:
            content = file.read()
            if content.strip() == "":
                return 0, 0
            score = int(content)
            return score, score
    except (FileExistsError, ValueError):
        return 0, 0

# Save the highest score
def save_score(score):
    high_score, _ = load_score()
    if score > high_score:
        score_file_path = os.path.join(data_folder_path, "Score.txt")
        with open(score_file_path, "w") as file:
            file.write(str(score))

# Create mixer
def play_music(music_path):
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.play(-1)

def load_sprite_sheet():
    # Load sprite sheet image
    sprite_sheet_path = os.path.join("data", "img", "sprite_sheet.png")
    sprite_sheet = pygame.image.load(sprite_sheet_path).convert()
    sprite_sheet.set_colorkey((0, 255, 0))

    return sprite_sheet

def flee_mouse(flies, flee_distance):
    """
    Move the flies away from the mouse position if it's close.

    :param flies: List of fly positions [x, y]
    :param flee_distance: Flee distance, if the mouse is closer than this, the flies will flee
    """
    for fly in flies:
        # Get the current mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Calculate the distance between the fly and the mouse position
        distance = math.sqrt((fly[0] - mouse_x) ** 2 + (fly[1] - mouse_y) ** 2)

        # Check if the distance is less than the flee distance
        if distance < flee_distance:
            # Calculate the direction to flee from the mouse
            direction_x = fly[0] - mouse_x
            direction_y = fly[1] - mouse_y

            # Update the fly's position to move it away from the mouse position
            fly[0] += direction_x * 0.1
            fly[1] += direction_y * 0.1

            # Update the fly's position with some randomness
            fly[0] += random.uniform(-1, 1)
            fly[1] += random.uniform(-1, 1)

            # Limit the fly's position within the screen boundaries
            fly[0] = min(max(fly[0], 0), w_screen - 100)
            fly[1] = min(max(fly[1], 0), h_screen - 100)

# Initialize the game
def initialize_game():
    screen = create_window()
    pygame.mouse.set_visible(False)
    sprite_sheet = load_sprite_sheet()
    background_texture = get_background_texture(sprite_sheet)
    fly_swatter_texture, fly_swatter_clicked_texture = get_fly_swatter_texture(sprite_sheet)
    fly_dead_texture = get_fly_dead_texture(sprite_sheet)

    return screen, sprite_sheet, background_texture, fly_swatter_texture, fly_swatter_clicked_texture, fly_dead_texture

# Get textures for the fly swatter
def get_fly_swatter_texture(sprite_sheet):
    # Fly swatter
    fly_swatter_rect = pygame.Rect(2, 2, 16, 40)
    fly_swatter_texture = sprite_sheet.subsurface(fly_swatter_rect)
    fly_swatter_texture = pygame.transform.scale(fly_swatter_texture, (50, 100))

    # Fly swatter clicked
    fly_swatter_clicked_rect = pygame.Rect(36, 27, 14, 15)
    fly_swatter_clicked_texture = sprite_sheet.subsurface(fly_swatter_clicked_rect)
    fly_swatter_clicked_texture = pygame.transform.scale(fly_swatter_clicked_texture, (100, 100))

    return fly_swatter_texture, fly_swatter_clicked_texture

# Get texture for the dead fly
def get_fly_dead_texture(sprite_sheet):
    # Dead fly
    fly_dead_rect = pygame.Rect(88, 110, 16, 15)
    fly_dead_texture = sprite_sheet.subsurface(fly_dead_rect)
    fly_dead_texture = pygame.transform.scale(fly_dead_texture, (100, 100))

    return fly_dead_texture

# Get texture for the background
def get_background_texture(sprite_sheet):
    # Background
    background_rect = pygame.Rect(2, 226, 256, 224)
    background_texture = sprite_sheet.subsurface(background_rect)
    background_texture = pygame.transform.scale(background_texture, (w_screen, h_screen))

    return background_texture

# Draw the score on the screen
def draw_score(screen, sprite_sheet, score):
    score_string = str(score).zfill(1)
    digit_width = 16
    digit_height = 16
    spacing = 2
    starting_x = 10
    scale_factor = 3

    for i, digit in enumerate(score_string):
        if digit == ' ':
            continue
        digit_rect = pygame.Rect(684 + int(digit) * (digit_width + spacing), 2, digit_width, digit_height)
        digit_texture = sprite_sheet.subsurface(digit_rect)
        scaled_texture = pygame.transform.scale(digit_texture, (digit_width * scale_factor, digit_height * scale_factor))
        screen.blit(scaled_texture, (starting_x + i * (digit_width + spacing) * scale_factor, 10))
    pygame.display.flip()

# Handle mouse click events
def handle_mouse_click(flies, dead_flies, hitbox, w_screen, h_screen, score):
    hit_sound = pygame.mixer.Sound(os.path.join("data", "ost", "smash_sound.mp3"))
    mouse_x, mouse_y = pygame.mouse.get_pos()
    for i, (fly_x, fly_y) in enumerate(flies):
        if fly_x - hitbox <= mouse_x <= fly_x + 100 + hitbox and fly_y - hitbox <= mouse_y <= fly_y + 100 + hitbox:
            del flies[i]
            flies.append([random.randint(0, w_screen - 100), random.randint(0, h_screen - 100)])
            dead_flies.append([mouse_x - 50, mouse_y - 50, pygame.time.get_ticks()])
            score += 1
            save_score(score)
            hit_sound.play()
            break

    return score

# Handle game events
def handle_events(flies, dead_flies, hitbox, w_screen, h_screen, running, score):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            score = handle_mouse_click(flies, dead_flies, hitbox, w_screen, h_screen, score)

    return flies, dead_flies, running, score

# Run the game loop
def run_game_loop(screen, sprite_sheet, background_texture, fly_swatter_texture, fly_swatter_clicked_texture, fly_dead_texture, w_screen, h_screen, score):
    flies = []
    num_flies = 20

    for _ in range(num_flies):
        flies.append([random.randint(0, w_screen - 100), random.randint(0, h_screen - 100)])

    hitbox = 25
    flee_distance = 200
    fly_state = 0
    dead_flies = []
    running = True
    clock = pygame.time.Clock()
    start_ticks = pygame.time.get_ticks()

    game_music_path = os.path.join("data", "ost", "game_music.mp3")
    play_music(game_music_path)
    pygame.time.delay(3000)

    while running:
        flies, dead_flies, running, score = handle_events(flies, dead_flies, hitbox, w_screen, h_screen, running, score)

        time_since_start = pygame.time.get_ticks() - start_ticks
        if time_since_start >= 60000:
            return False

        for fly_pos in flies:
            fly_pos[0] += random.uniform(-5, 5)
            fly_pos[1] += random.uniform(-5, 5)

            fly_pos[0] = min(max(fly_pos[0], 0), w_screen - 100)
            fly_pos[1] = min(max(fly_pos[1], 0), h_screen - 100)

        mouse_x, mouse_y = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()[0]

        screen.blit(background_texture, (0, 0))

        if fly_state == 0:
            # Fly_0
            fly_rect_0 = pygame.Rect(88, 135, 16, 15)
            fly_texture = sprite_sheet.subsurface(fly_rect_0)
            fly_texture = pygame.transform.scale(fly_texture, (100, 100))
            fly_state = 1
        else:
            # Fly_1
            fly_rect_1 = pygame.Rect(106, 135, 14, 15)
            fly_texture = sprite_sheet.subsurface(fly_rect_1)
            fly_texture = pygame.transform.scale(fly_texture, (100, 100))
            fly_state = 0

        for fly_pos in flies:
            screen.blit(fly_texture, (fly_pos[0], fly_pos[1]))

        if click:
            screen.blit(fly_swatter_clicked_texture, (mouse_x - 50, mouse_y - 50))
        else:
            swatter_width, swatter_height = fly_swatter_texture.get_size()
            screen.blit(fly_swatter_texture, (mouse_x - swatter_width // 2, mouse_y - swatter_height // 2))

        for dead_fly in dead_flies:
            screen.blit(fly_dead_texture, (dead_fly[0], dead_fly[1]))
            if pygame.time.get_ticks() - dead_fly[2] > 2000:
                dead_flies.remove(dead_fly)

        flee_mouse(flies, flee_distance)
        draw_score(screen, sprite_sheet, score)
        pygame.display.flip()
        clock.tick(60)

    return False

# Start screen
def start_screen(screen, sprite_sheet, start_x, start_y, end_x, end_y, center_x, center_y, final_x, final_y):
    start_music_path = os.path.join("data", "ost", "start_music.mp3")
    play_music(start_music_path)
    sprite_rects = [(550, 5, 16, 21), (568, 5, 16, 21), (586, 98, 16, 24)]
    sprite_textures = [pygame.transform.scale(sprite_sheet.subsurface(rect), (80, 105)) for rect in sprite_rects]

    current_x = start_x
    current_y = start_y
    current_sprite_index = 0
    change_sprite_timer = 0
    sprite_change_interval = 20
    movement_interval = 5

    font = pygame.font.Font(None, 100)
    text = font.render("Press any key to start", True, (0, 0, 0))
    text_rect = text.get_rect(center=(w_screen // 2, h_screen // 2))

    while current_x > end_x or current_y < end_y:
        screen.fill((255, 255, 255))

        # Draw the sprite at the current position
        screen.blit(sprite_textures[current_sprite_index], (current_x, current_y))
        screen.blit(text, text_rect)

        # Update the sprite's position
        if current_x > center_x:
            current_x -= 1
        elif current_x == center_x and current_y < center_y:
            current_y += 1
        elif current_x == center_x and current_y == center_y:
            current_sprite_index = 2

        # Update the sprite change timer
        if current_x != center_x or current_y != center_y:
            change_sprite_timer += 1
            if change_sprite_timer >= sprite_change_interval:
                current_sprite_index = 1 - current_sprite_index  # Switch between 0 and 1
                change_sprite_timer = 0

        # Update the screen
        pygame.display.flip()

        # Slow down the loop
        pygame.time.delay(movement_interval)

    # Loop to keep the sprite in the final position
    while True:
        screen.fill((255, 255, 255))
        screen.blit(sprite_textures[2], (final_x, final_y))
        screen.blit(text, text_rect)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                return
            
def end_screen(screen, sprite_sheet, high_score, current_score):
    # Load the end music
    end_music_path = os.path.join("data", "ost", "end_music.mp3")
    play_music(end_music_path)

    # Game loop for the end screen
    running = True
    while running:
        for event in pygame.event.get():
            # Check for quit event
            if event.type == pygame.QUIT:
                running = False
            # Check for key press event
            if event.type == pygame.KEYDOWN:
                running = False

        # Fill the screen with white
        screen.fill((255, 255, 255))
        font = pygame.font.Font(None, 50)

        # Display the best scores on the screen
        best_score_text = font.render("Best Scores", True, (0, 0, 0))
        screen.blit(best_score_text, (w_screen // 2 - best_score_text.get_width() // 2, h_screen // 4))

        # Display the current score
        actual_score_text = font.render(f"Current Score: {current_score}", True, (0, 0, 0))
        screen.blit(actual_score_text, (w_screen // 2 - actual_score_text.get_width() // 2, h_screen // 4 + 40))

        high_score_text = font.render(f"Highest Score: {high_score}", True, (0, 0, 0))
        screen.blit(high_score_text, (w_screen // 2 - high_score_text.get_width() // 2, h_screen // 4 + 80))

        pygame.display.flip()

    pygame.quit()

def game():
    # Initialize the game
    score = 0
    screen, sprite_sheet, background_texture, fly_swatter_texture, fly_swatter_clicked_texture, fly_dead_texture = initialize_game()
    running = True
    started = False

    while running:
        if not started:
            # Display the start screen
            start_screen(screen, sprite_sheet, w_screen, h_screen - 105, w_screen // 2, h_screen // 2, w_screen // 2, h_screen // 2, w_screen // 2, h_screen - 105)
            started = True
        else:
            # Run the game loop
            running = run_game_loop(screen, sprite_sheet, background_texture, fly_swatter_texture, fly_swatter_clicked_texture, fly_dead_texture, w_screen, h_screen, score)
            if not running:
                break

    # Load and display scores on the end screen
    high_score, current_score = load_score()
    end_screen(screen, sprite_sheet, high_score, current_score)    
    pygame.quit()

def main():
    game()

if __name__ == "__main__":
    main()