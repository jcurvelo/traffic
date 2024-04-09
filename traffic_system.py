from core import Vehicle, RoadPath, Obstacle
from threading import Thread
import itertools
import time
import random
from pymunk.vec2d import Vec2d

class Traffic:
    def __init__(self,screen,zoom_level,background_pos) -> None:
        # from 0 to 11 hours, the rate of vehicles per hour
        self.vehicleRatePerHour = [0.64, 0.65, 0.5, 0.43, 0.44, 0.45, 0.47, 0.52, 0.56, 0.71, 0.79, 0.65]
        self.currentHour = 0
        self.vehiclesPerSecond = self.vehicleRatePerHour[self.currentHour]
        self.screen = screen
        self.zoom_level = zoom_level
        self.background_pos = background_pos
        self.roads:list[RoadPath] = []
        self.vehicles:list[Vehicle] = []

        timeThread = Thread(target=self.updateVehicleRate)
        timeThread.start()
        self.congestionAtBegeining = 0

        self.obstacles:list[Obstacle] = []

        # deleteThread = Thread(target=self.deleteVehicles)
        # deleteThread.start()

    def showVehicles(self):
        for obstacle in self.obstacles:
            obstacle.show(self.screen,self.zoom_level,self.background_pos)
        
        for vehicle in self.vehicles:
            vehicle.follow(self.zoom_level,self.background_pos)
            vehicle.update()
            vehicle.show(self.zoom_level,self.background_pos)
            vehicle.displayVehicleStats(self.zoom_level,self.background_pos)

            # if vehicle.nextRoad is not None:
            #     # if the vehicle is near the next road, change the road
            #     if vehicle.position.get_distance(Vec2d(vehicle.nextRoad.points[0].x,vehicle.nextRoad.points[0].y)) < 500 and vehicle.position.get_distance(Vec2d(vehicle.nextRoad.points[0].x,vehicle.nextRoad.points[0].y)) > 100:
            #         vehicle.arrive(vehicle.nextRoad.points[0])
            #         vehicle.state = "changing road"
            #     if vehicle.position.get_distance(Vec2d(vehicle.nextRoad.points[0].x,vehicle.nextRoad.points[0].y)) < 100:
            #         vehicle.road = vehicle.nextRoad
            #         vehicle.nextRoad = None
                    # vehicle.kwonObstacles = self.obstacles
                    # vehicle.otherKwonVehicles = [v for v in self.vehicles if v != vehicle]

            # lastPoint = Vec2d(vehicle.road.points[-1].x,vehicle.road.points[-1].y)
            if vehicle.state == 'idle':
                self.vehicles.remove(vehicle)

    def deleteVehicles(self):
        for vehicle in self.vehicles:
            if vehicle.position.x * self.zoom_level + self.background_pos[0] > self.roads[0].points[-1].x * self.zoom_level + self.background_pos[0] and vehicle.position.y * self.zoom_level + self.background_pos[1] < self.roads[0].points[-1].y * self.zoom_level + self.background_pos[1]:
                self.vehicles.remove(vehicle)
    
    def addVehicle(self,mass:int=1,max_speed:int=1):
        vehicle = Vehicle(800,1900,self.screen)
        # random float between 0.5 and 3
        vehicle.mass = mass
        vehicle.road = list(filter(lambda road: road.roadName == 'Main Road',self.roads))[0]
        vehicle.nextRoad = list(filter(lambda road: road.roadName == 'Left Road A R',self.roads))[0]
        vehicle.max_speed = max_speed
        vehicle.kwonObstacles = self.obstacles
        vehicle.otherKwonVehicles = [v for v in self.vehicles if v != vehicle]
        self.vehicles.append(vehicle)
        return vehicle
    
    def updateZoomAndBackground(self,zoom_level,background_pos):
        self.zoom_level = zoom_level
        self.background_pos = background_pos
    
    def updateVehicleRate(self):
        while True:
            time.sleep(30)
            if self.congestionAtBegeining > 10:
                return
            if self.currentHour == 11:
                self.currentHour = 0
            else:
                self.currentHour += 1
            self.vehiclesPerSecond = self.vehicleRatePerHour[self.currentHour]
    
    def getCongestionAtSection(self,start:Vec2d,end:Vec2d):
        congestion = 0
        # we're trying to get the congestion at the section of the road, vehicles in the section of the road
        for vehicle in self.vehicles:
            distance = vehicle.position.get_distance(start)
            normal = (end - start).normalized()
            projection = start + normal * distance
            if projection.get_distance(vehicle.position) < 10:
                congestion += 1
        return congestion
    
    def addObstacle(self,x,y,w,h):
        self.obstacles.append(Obstacle(x,y,w,h))

    def removeObstacle(self,obstacle):
        self.obstacles.remove(obstacle)
        print(len(self.obstacles), " obstacles left")
        



