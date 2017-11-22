"""
Sample Python/Pygame Programs
Simpson College Computer Science
http://programarcadegames.com/
http://simpson.edu/computer-science/
"""
import time
import pygame

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
MIX = (150, 150, 255)


def draw_stick_figure(kinect, screen):
    # Head
    #pygame.draw.ellipse(screen, MIX, [x, y, 20, 20], 0)


    #skeleton = kinect.skeleton
    #if not skeleton:
    #    return

    joint_positions = kinect.get_joint_positions()
    for x, y in joint_positions:
        #
        # position = skeleton.get_joint(i).position
        # x, y = kinect.user_tracker.convert_joint_coordinates_to_depth(position.x, position.y, position.z)
        try:
            x, y = int(x), int(y)
            print "X: %s, Y: %s", (x,y)
            pygame.draw.ellipse(screen, MIX, [x, y, 20, 20], 0)

        except Exception as e:
            print e

def start(kinect):
    #
    pygame.init()

    # Set the width and height of the screen [width,height]
    size = [700, 500]
    screen = pygame.display.set_mode(size)

    pygame.display.set_caption("My Game")

    # Loop until the user clicks the close button.
    done = False

    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()

    # Hide the mouse cursor
    pygame.mouse.set_visible(0)

    # -------- Main Program Loop -----------
    while not done:
        # ALL EVENT PROCESSING SHOULD GO BELOW THIS COMMENT
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
        # ALL EVENT PROCESSING SHOULD GO ABOVE THIS COMMENT

        # ALL GAME LOGIC SHOULD GO BELOW THIS COMMENT

        # Call draw stick figure function
        # pos = pygame.mouse.get_pos()
        # = pos[0]
        # y = pos[1]

        # ALL GAME LOGIC SHOULD GO ABOVE THIS COMMENT

        # ALL CODE TO DRAW SHOULD GO BELOW THIS COMMENT

        # First, clear the screen to white. Don't put other drawing commands
        # above this, or they will be erased with this command.
        screen.fill(WHITE)
        draw_stick_figure(kinect, screen)

        # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT

        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()

        # Limit to 20 frames per second
        clock.tick(60)

    # Close the window and quit.
    # If you forget this line, the program will 'hang'
    # on exit if running from IDLE.
    pygame.quit()





    # # Setup
    # pygame.init()
    #
    # # Set the width and height of the screen [width,height]
    # size = [700, 500]
    # screen = pygame.display.set_mode(size)
    #
    # pygame.display.set_caption("My Game")
    #
    # # Loop until the user clicks the close button.
    # done = False
    #
    # # Used to manage how fast the screen updates
    # clock = pygame.time.Clock()
    #
    # # Hide the mouse cursor
    # pygame.mouse.set_visible(0)
    #
    # # -------- Main Program Loop -----------
    # while not done:
    #     # ALL EVENT PROCESSING SHOULD GO BELOW THIS COMMENT
    #     for event in pygame.event.get():
    #         if event.type == pygame.QUIT:
    #             done = True
    #     # ALL EVENT PROCESSING SHOULD GO ABOVE THIS COMMENT
    #
    #     # ALL GAME LOGIC SHOULD GO BELOW THIS COMMENT
    #
    #     # Call draw stick figure function
    #     pos = pygame.mouse.get_pos()
    #     x = pos[0]
    #     y = pos[1]
    #
    #     # ALL GAME LOGIC SHOULD GO ABOVE THIS COMMENT
    #
    #     # ALL CODE TO DRAW SHOULD GO BELOW THIS COMMENT
    #
    #     # First, clear the screen to white. Don't put other drawing commands
    #     # above this, or they will be erased with this command.
    #     screen.fill(WHITE)
    #     draw_stick_figure(screen, x, y)
    #
    #     # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT
    #
    #     # Go ahead and update the screen with what we've drawn.
    #     pygame.display.flip()
    #
    #     # Limit to 20 frames per second
    #     clock.tick(60)
    #
    # # Close the window and quit.
    # # If you forget this line, the program will 'hang'
    # # on exit if running from IDLE.
    # pygame.quit()