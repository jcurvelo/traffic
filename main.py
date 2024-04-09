# Example file showing a basic pygame "game loop"
import pygame
from core import Vehicle, RoadPath
import time
from simulation import Simulation
import matplotlib.pyplot as plt
# pygame setup
pygame.init()

WIDTH, HEIGHT = 800, 600
BACKGROUND_WIDTH, BACKGROUND_HEIGHT = 2000, 2000

screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
running = True

FPS = 24



background = pygame.image.load("assets/road_structure.png")
background = pygame.transform.scale(background, (BACKGROUND_WIDTH, BACKGROUND_HEIGHT))

# Variables to keep track of the zoom level and position of the background

zoom_level = 1
zoom_speed = 0.05
background_pos = [-337, -1400]
move_speed = 1
# (773,1963),(853,1636)
path = RoadPath()


simulation = Simulation(screen)

while simulation.running:
    screen.fill((255, 255, 255))

    simulation.runEvents()
    simulation.run()
    simulation.displayStats()

    # singleVehicle.show(zoom_level,background_pos)
    simulation.traffic.showVehicles()
    simulation.traffic.updateZoomAndBackground(simulation.zoom_level,simulation.background_pos)

    # flip() the display to put your work on screen
    pygame.display.flip()

    simulation.clock.tick(simulation.fps)  # limits FPS


