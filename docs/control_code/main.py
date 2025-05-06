# main.py
import pygame
import sys
from hello_world import display_message

# Initialize Pygame
pygame.init()

# Set up the screen - this makes full screen on the whichever monitor
infoObject = pygame.display.Info()
screen_w = infoObject.current_w - 100
screen_h = infoObject.current_h - 100
screen = pygame.display.set_mode((screen_w, screen_h))

screen_centerX = screen_w/2
screen_thirdX = screen_w/3
screen_twoThirdX = (screen_w*2)/3
screen_centerY = screen_h/2
screen_thirdY = screen_h/3
screen_twoThirdY = (screen_h*2)/3
screen_sixthY = ((screen_h*5)/6)

#screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Hello World Buttons")

# Set up button properties
button_width = 200
button_height = 50
button_color = (0, 128, 255)
font = pygame.font.SysFont("Arial", 30)

# Display Box properties
box_color = (255, 255, 255) #white
display_height = 125
display_width = 300

# Define button rectangles - (x, y, button width, button height)
start_button_rect = pygame.Rect(screen_centerX, screen_thirdY, button_width, button_height)
stop_button_rect = pygame.Rect(screen_centerX, screen_centerY, button_width, button_height)
reset_button_rect = pygame.Rect(screen_centerX, screen_twoThirdY, button_width, button_height)
exit_button_rect = pygame.Rect(screen_centerX, screen_sixthY, button_width, button_height)

# Display Box Rectange 
disp_box_rect = pygame.Rect(screen_w/6, screen_centerY, display_width, display_height)
# Empty list of the words to display on the screen
disp_list = []

# Define button texts
start_text = font.render("Start", True, (255, 255, 255))
stop_text = font.render("Stop", True, (255, 255, 255))
reset_text = font.render("Reset", True, (255, 255, 255))
exit_text = font.render("Exit", True, (255, 255, 255))

# Initialize button states
start_clicked = False
stop_clicked = False
reset_clicked = False
exit_clicked = False

# helper function for words
def draw_text(text, font, x, y):
    text_col = (0, 0, 0)
    img = font.render(text, True, text_col)
    screen.blit(img, (x,y))

# Game loop
running = True
while running:
    screen.fill((179, 241, 242))  # Fill the screen with light blue

    # Draw buttons
    pygame.draw.rect(screen, button_color, start_button_rect)
    pygame.draw.rect(screen, button_color, stop_button_rect)
    pygame.draw.rect(screen, button_color, reset_button_rect)
    pygame.draw.rect(screen, button_color, exit_button_rect)
    # Draw Display
    pygame.draw.rect(screen, box_color, disp_box_rect)

    # Display button texts
    screen.blit(start_text, (start_button_rect.x+75, start_button_rect.y+10))
    screen.blit(stop_text, (stop_button_rect.x + 80, stop_button_rect.y + 10))
    screen.blit(reset_text, (reset_button_rect.x+65, reset_button_rect.y + 10))
    screen.blit(exit_text, (exit_button_rect.x + 80, exit_button_rect.y + 10))

    # White Display Box for Commands 
    line_spacing = 35
    for idx, r in enumerate(disp_list[-3:]): #show last 3 messages to fit in box
        y_offset = screen_centerY + idx * line_spacing # vert position
        draw_text(r, font, screen_w/6 + 10, y_offset)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if start_button_rect.collidepoint(event.pos):
                text_font = pygame.font.SysFont("Helvetica",30)
                start_clicked = True
                stop_clicked = False
                reset_clicked = False
                display_message("Start")  # Call the function when Start is clicked
                diss_msg = (display_message)
                print(diss_msg)
                disp_list.append(dis_msg)
            elif stop_button_rect.collidepoint(event.pos):
                start_clicked = False
                stop_clicked = True
                reset_clicked = False
                display_message("Stop")  # Call the function when Stop is clicked
                dis_msg = 'stop'
                disp_list.append(dis_msg)
            elif reset_button_rect.collidepoint(event.pos):
                start_clicked = False
                stop_clicked = False
                reset_clicked = True
                display_message("Reset")  # Call the function when Reset is clicked
            elif exit_button_rect.collidepoint(event.pos):
                display_message("Exit")
                running = False

    # Optionally, you can use the start_clicked, stop_clicked, and reset_clicked flags for logic control

    pygame.display.flip()

pygame.quit()
sys.exit()
