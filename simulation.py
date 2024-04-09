from threading import Thread
import time
import pygame
from traffic_system import Traffic
from pygame import Surface
from roads import mainRoad, leftRoadA, leftRoadB, leftRoadC, leftRoadD, leftRoadAr
import random
from matplotlib import pyplot as plt
import matplotlib.backends.backend_agg as agg


WIDTH, HEIGHT = 800, 600
WORLD_WIDTH, WORLD_HEIGHT = 2000, 2000

background = pygame.image.load("assets/road_structure.png")
background = pygame.transform.scale(background, (WORLD_WIDTH, WORLD_HEIGHT))
background.set_alpha(128)

class Graph:
    def __init__(self,parent=None) -> None:
        self.x = [0,1]
        self.y = [0,1]
        self.figure, self.ax = plt.subplots()
    
    def draw(self,surface):
        self.ax.clear()
        self.ax.plot(self.x, self.y)
        canvas = agg.FigureCanvasAgg(self.figure)
        canvas.draw()
        renderer = canvas.get_renderer()
        raw_data = renderer.tostring_rgb()
        size = canvas.get_width_height()
        # create in new window
        surf = pygame.image.fromstring(raw_data, size, "RGB")
        surface.blit(surf, (0, 0))

class Simulation:
    def __init__(self,screen:Surface) -> None:
        self.clock = pygame.time.Clock()
        self.fps = 24
        self.running = True

        self.zoom_level = 1
        self.zoom_speed = 0.05
        self.background_pos = [-337, -1400]
        self.move_speed = 1
        self.screen = screen

        self.events = SimulationEvents(pygame.event.get(),self)
        self.traffic = Traffic(screen,self.zoom_level,self.background_pos)
        self.traffic.addObstacle(849,1482,50,50)
        self.traffic.roads.append(mainRoad)
        self.traffic.roads.append(leftRoadA)
        self.traffic.roads.append(leftRoadAr)
        self.traffic.roads.append(leftRoadB)
        self.traffic.roads.append(leftRoadC)
        self.traffic.roads.append(leftRoadD)
        
        vthread = Thread(target=self.addVehiclesByInterval)
        vthread.start()

        self.vehicleVelocityHistory = []

        histoThread = Thread(target=self.recordVehicleVelocity)
        histoThread.start()

        # self.graph = Graph()

    
        # self.traffic.addVehicle(1,4)
        # self.traffic.addVehicle(1, 2)

    def recordVehicleVelocity(self):
        while True:
            if len(self.traffic.vehicles) > 0:
                self.vehicleVelocityHistory.append(self.traffic.vehicles[0].km_h)
                time.sleep(1)

    def runEvents(self):
        for event in pygame.event.get():
            self.events = SimulationEvents(event,self)
            self.events.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.events.zoom_in()
                self.events.zoom_out()
                self.events.clickInObstacle()
                    
            if event.type == pygame.KEYDOWN:
                self.events.moveCameraRight()
                self.events.moveCameraLeft()
                self.events.moveCameraUp()
                self.events.moveCameraDown()

    def run(self):
        # Limit the view to the background size
        self.background_pos[0] = min(max(self.background_pos[0], WIDTH - WORLD_WIDTH * self.zoom_level), 0)
        self.background_pos[1] = min(max(self.background_pos[1], HEIGHT - WORLD_HEIGHT * self.zoom_level), 0)
        
        scaled_background = pygame.transform.scale(background, (int(WORLD_WIDTH * self.zoom_level), int(WORLD_HEIGHT * self.zoom_level)))
        self.screen.blit(scaled_background, self.background_pos)

        # self.displayCongestionAtSections()
        for road in self.traffic.roads:
            road.show(self.screen,self.zoom_level,self.background_pos)

    def spawnVehicleButton(self):
        box = pygame.Rect(10, 500, 100, 50)
        pygame.draw.rect(self.screen, (0, 0, 0), box)
        font = pygame.font.Font(None, 36)
        text = font.render("Add Vehicle", True, (255, 255, 255))
        self.screen.blit(text, (10, 500))
    
    def displayStats(self):
        mouse = pygame.mouse.get_pos()

        # show mouse position on screen
        font = pygame.font.Font(None, 16)
        # Calculate the position of the mouse on the map
        map_mouse_pos = [round((mouse[0] - self.background_pos[0]) / self.zoom_level, 2), round((mouse[1] - self.background_pos[1]) / self.zoom_level, 2)]
        text = font.render(f"Mouse: {map_mouse_pos}", True, (0, 0, 0))
        self.screen.blit(text, (WIDTH-130, HEIGHT-15))

        # show zoom level on screen
        text = font.render(f"Zoom: {round(self.zoom_level, 2)}", True, (0, 0, 0))
        self.screen.blit(text, (WIDTH-130, HEIGHT-30))

        # show the vehicles on the screen
        text = font.render(f"Vehicles: {len(self.traffic.vehicles)}", True, (0, 0, 0))
        self.screen.blit(text, (WIDTH-130, HEIGHT-45))

    def kmHToPixelsPerS(self,kmh):
        # 73.44 km/h = 1 pixel/s
        return kmh / 73.44

    def addVehiclesByInterval(self):
        while True:
            if len(self.traffic.vehicles) >= 1:
                return
            time.sleep(1 / self.traffic.vehiclesPerSecond)
            random_mass = 1
            random_speed = self.kmHToPixelsPerS(80)
            self.traffic.addVehicle(random_mass, random_speed)



    def displayCongestionAtSections(self):
        points = self.traffic.roads[0].points
        for i in range(len(points) - 1):
            start = points[i]
            end = points[i + 1]
            congestion = self.traffic.getCongestionAtSection(start, end)
            font = pygame.font.Font(None, 16)
            text = font.render(f"{congestion}", True, (0, 0, 0))
            textPosition = ((start.x + (end.x - start.x) / 2) * self.zoom_level + self.background_pos[0], (start.y + (end.y - start.y) / 2) * self.zoom_level + self.background_pos[1])
            self.screen.blit(text, textPosition)

            # draw a line between the points
            lineColor = (0, 0, 255) if i % 2 == 0 else (0, 255, 0)
            pygame.draw.line(self.screen, lineColor, (start.x * self.zoom_level + self.background_pos[0], start.y * self.zoom_level + self.background_pos[1]), (end.x * self.zoom_level + self.background_pos[0], end.y * self.zoom_level + self.background_pos[1]), 2)
        

    def pauseSimulation(self):
        self.fps = 0
    
    def resumeSimulation(self):
        self.fps = 24

class SimulationEvents:
    def __init__(self,event,parent) -> None:
        self.event = event
        self.simulation:Simulation = parent
    
    def clickOnCar(self):
        mouse = pygame.mouse.get_pos()
        for vehicle in self.simulation.traffic.vehicles:
            if vehicle.position.x * self.simulation.zoom_level + self.simulation.background_pos[0] < mouse[0] < vehicle.position.x * self.simulation.zoom_level + self.simulation.background_pos[0] + vehicle.width * self.simulation.zoom_level and vehicle.position.y * self.simulation.zoom_level + self.simulation.background_pos[1] < mouse[1] < vehicle.position.y * self.simulation.zoom_level + self.simulation.background_pos[1] + vehicle.height * self.simulation.zoom_level:
                vehicle.max_speed = 0
        return False

    def clickInObstacle(self):
        mouse = pygame.mouse.get_pos()
        for obstacle in self.simulation.traffic.obstacles:
            if obstacle.x * self.simulation.zoom_level + self.simulation.background_pos[0] < mouse[0] < obstacle.x * self.simulation.zoom_level + self.simulation.background_pos[0] + obstacle.width * self.simulation.zoom_level and obstacle.y * self.simulation.zoom_level + self.simulation.background_pos[1] < mouse[1] < obstacle.y * self.simulation.zoom_level + self.simulation.background_pos[1] + obstacle.height * self.simulation.zoom_level:
                return self.simulation.traffic.removeObstacle(obstacle)
        return False

    def clickSpawnVehicle(self):
        mouse = pygame.mouse.get_pos()
        box = pygame.Rect(10, 500, 100, 50)
        if box.collidepoint(mouse):
            self.simulation.traffic.addVehicle()

    def quit(self):
        if self.event.type == pygame.QUIT:
            self.simulation.running = False
        
    def zoom_in(self):
        if self.event.button == 4:
            # max zoom in to 1
            self.simulation.zoom_level += self.simulation.zoom_speed
            if self.simulation.zoom_level > 1:
                self.simulation.zoom_level = 1
            
            mouse = pygame.mouse.get_pos()

            self.simulation.background_pos[0] -= mouse[0] * self.simulation.zoom_speed
            self.simulation.background_pos[1] -= mouse[1] * self.simulation.zoom_speed
            
    def zoom_out(self):
        if self.event.button == 5:
            self.simulation.zoom_level -= self.simulation.zoom_speed
            if self.simulation.zoom_level < 0.1:  # Prevent zoom_level from going below a certain level
                self.simulation.zoom_level = 0.1
            self.simulation.zoom_level = max(self.simulation.zoom_level, 0.3)
    
    def moveCameraRight(self):
        if self.event.key == pygame.K_RIGHT:
            self.simulation.background_pos[0] -= self.simulation.move_speed * 10

    def moveCameraLeft(self):
        if self.event.key == pygame.K_LEFT:
            self.simulation.background_pos[0] += self.simulation.move_speed * 10

    def moveCameraUp(self):
        if self.event.key == pygame.K_UP:
            self.simulation.background_pos[1] += self.simulation.move_speed * 10
    
    def moveCameraDown(self):
        if self.event.key == pygame.K_DOWN:
            self.simulation.background_pos[1] -= self.simulation.move_speed * 10