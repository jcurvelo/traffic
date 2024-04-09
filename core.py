from pygame import Surface
import numpy as np
import pygame
import time
import matplotlib.pyplot as plt
from threading import Thread
import scipy
from pymunk.vec2d import Vec2d
import scipy.interpolate

class SpriteSheet:
    def __init__(self, file_name) -> None:
        self.sheet = pygame.image.load(file_name).convert()

    def getSprite(self, x, y, width, height):
        sprite = pygame.Surface((width, height))
        sprite.blit(self.sheet, (0, 0), (x, y, width, height))
        sprite.set_colorkey((0, 0, 0))
        return sprite

class Obstacle:
    def __init__(self, x, y, width, height) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def show(self, screen:Surface, zoom_level, background_pos):
        pygame.draw.rect(screen, (0, 255, 255), (int((self.x * zoom_level) + background_pos[0]), int((self.y * zoom_level) + background_pos[1]), self.width * zoom_level, self.height * zoom_level))

class RoadPath:
    def __init__(self) -> None:
        self.radius = 20
        self.points:list[Vec2d,Vec2d] = []
        self.direction = 'south-to-north'
        self.roadName = ''

    def addPoint(self, x,y):
        self.points.append(Vec2d(x,y))
    
    def show(self, screen:Surface,zoom_level,background_pos):
        pygame.draw.lines(screen, (0, 0, 0), False, [(int((point.x * zoom_level) + background_pos[0]), int((point.y * zoom_level) + background_pos[1])) for point in self.points], 2)
        font = pygame.font.Font(None, 16)
        textPosition = ((self.points[0].x + (self.points[-1].x - self.points[0].x) / 2) * zoom_level + background_pos[0] - 100, (self.points[0].y + (self.points[-1].y - self.points[0].y) / 2) * zoom_level + background_pos[1])
        text = font.render(f"{self.roadName}", True, (0, 0, 0))
        screen.blit(text, textPosition)
    

class Vehicle:
    def __init__(self,x:int,y:int,screen:Surface) -> None:
        self.position = Vec2d(x, y)
        self.velocity = Vec2d(0, 0)
        self.acceleration = Vec2d(0, 0)
        self.max_speed = 3
        self.minimum_speed = 0.4
        self.max_force = 0.2
        self.mass = 1
        self.screen = screen
        self.load_image()
        self.debug = True
        self.breakStrength = 0.4
        self.safeDistance = 50
        self.frontBumperDistance = 50
        self.collitionRadius = 40
        self.kwonObstacles:list[Obstacle] = []
        self.otherKwonVehicles:list['Vehicle'] = []
        self.obstacleInFront = None
        self.isTooCloseToOtherCar = False
        self.road:RoadPath = None
        self.nextRoad:RoadPath = None
        self.state = 'normal'
        self.km_h = 0
        self.speedHistory = [0,1]
    
    def getSpeedInKmH(self):
        # the world is 1.7km height, 2000 are the max pixels        scale_factor = 1.7 / 2000
        scale_factor = 1.7 / 2000
        
        frame_rate = 24
        km_s = self.velocity.length * scale_factor * frame_rate
        self.km_h = km_s * 3600
    
    def setVectorLimit(self, vector:Vec2d, limit):
        if vector.length > limit:
            vector = vector.normalized() * limit
        return vector

    def map(self, value, start1, stop1, start2, stop2):
        return start2 + (stop2 - start2) * ((value - start1) / (stop1 - start1))
    
    def getNormalPoint(self, p:Vec2d, a:Vec2d, b:Vec2d):
        ap = p - a
        ab = b - a
        ab = ab.normalized()
        ab *= ap.dot(ab)
        normal_point = a + ab
        return normal_point

    def load_image(self):
        self.image = pygame.image.load("assets/car.png")
        original_size = self.image.get_size()
        max_dimension = 50
        aspect_ratio = original_size[0] / original_size[1]
        if original_size[0] > original_size[1]:
            new_width = max_dimension
            new_height = int(max_dimension / aspect_ratio)
        else:
            new_height = max_dimension
            new_width = int(max_dimension * aspect_ratio)
        self.image = pygame.transform.scale(self.image, (new_width, new_height))
    
    def applyForce(self, force):
        self.acceleration += force/self.mass
    
    def update(self):
        if self.state != 'idle' and self.state != 'forcedStop':
            self.velocity += self.acceleration
            self.velocity = self.setVectorLimit(self.velocity, self.max_speed)
            self.position += self.velocity
            self.acceleration *= 0
    
    def show(self, zoom_level, background_pos):
        vehiclePosition = (self.position.x * zoom_level) + background_pos[0], (self.position.y * zoom_level) + background_pos[1]
        if self.debug:
            pygame.draw.circle(self.screen, (255, 0, 0), (int(vehiclePosition[0]), int(vehiclePosition[1])), 5)
            end_point = self.position + self.velocity.normalized() * 20
            pygame.draw.line(self.screen, (0, 0, 255), (int((self.position.x * zoom_level) + background_pos[0]), int((self.position.y * zoom_level) + background_pos[1])), (int((end_point.x * zoom_level) + background_pos[0]), int((end_point.y * zoom_level) + background_pos[1])), 2)
        
            # draw the collition radius
            # pygame.draw.circle(self.screen, (0, 255, 0), (int(vehiclePosition[0]), int(vehiclePosition[1])), int(self.collitionRadius * zoom_level))

            # add the safe distance
            safeCircle = pygame.surface.Surface((int(self.safeDistance * 2 * zoom_level), int(self.safeDistance * 2 * zoom_level)), pygame.SRCALPHA)
            self.screen.blit(safeCircle, (int(vehiclePosition[0] - self.safeDistance * zoom_level), int(vehiclePosition[1] - self.safeDistance * zoom_level)))

        angle = np.arctan2(-self.velocity.y, self.velocity.x)
        scaled_image = pygame.transform.scale(self.image, (int(self.image.get_width() * zoom_level), int(self.image.get_height() * zoom_level)))
        rotated_image = pygame.transform.rotate(scaled_image, np.degrees(angle) - 90)
        self.screen.blit(rotated_image, (vehiclePosition[0] - rotated_image.get_width() / 2, vehiclePosition[1] - rotated_image.get_height() / 2))

    def seek(self,target:Vec2d):
        desired = target - self.position
        desired = desired.normalized() * self.max_speed
        steer = desired - self.velocity
        steer = self.setVectorLimit(steer, self.max_force)
        self.applyForce(steer)

    def stopVehicle(self):
        self.state = 'forcedStop'
        self.acceleration = Vec2d(0, 0)
        
    
    def continueVehicle(self):
        self.state = 'normal'
        # Continue the vehicle like a car
        desired = Vec2d(0, 0) - self.velocity
        steer = desired + self.velocity
        steer = self.setVectorLimit(steer, self.max_force)
        self.applyForce(steer)


    def arrive(self,target:Vec2d):
        desired = target - self.position
        d = desired.length
        if d < 100:
            m = self.map(d, 0, 100, 0, self.max_speed)
            desired = desired.normalized() * m
        else:
            desired = desired.normalized() * self.max_speed
        steer = desired - self.velocity
        steer = self.setVectorLimit(steer, self.max_force)
        self.applyForce(steer)
    
    def detectTooCloseToOtherCar(self, zoom_level, background_pos):
        if self.state != 'normal':
            return
        for other in self.otherKwonVehicles:
            if self.position.y > other.position.y + other.collitionRadius:
                continue
            distance = self.position.get_distance(other.position) + other.collitionRadius*2
            if distance < self.safeDistance + self.collitionRadius + other.collitionRadius and self.position.y < other.position.y:
                if self.debug:
                    pygame.draw.line(self.screen, (255, 0, 255), (int((self.position.x * zoom_level) + background_pos[0]), int((self.position.y * zoom_level) + background_pos[1])), (int((other.position.x * zoom_level) + background_pos[0]), int(((other.position.y+other.collitionRadius) * zoom_level) + background_pos[1])), 2)
                self.isTooCloseToOtherCar = True
                self.state = 'tryingNotToCollide'
                return True
            else:
                self.isTooCloseToOtherCar = False
                self.state = 'normal'
                return False
        return False

    def keepSafeDistance(self):
        if self.state != 'normal':
            return
        for other in self.otherKwonVehicles:
            distance = self.position.get_distance(other.position)
            speed = self.map(distance, 0, self.safeDistance + self.collitionRadius + other.collitionRadius, 0, self.max_speed)
            desired = other.position - self.position
            desired = desired.normalized() * speed
            steer = desired - self.velocity
            steer = self.setVectorLimit(steer, self.max_force)
            self.applyForce(steer)


    def reduceVelocity(self, factor):
        self.velocity *= factor

    def detectObstacle(self, zoom_level, background_pos):
        for obstacle in self.kwonObstacles:
            distance = self.position.get_distance(Vec2d(obstacle.x, obstacle.y))
            if distance < self.safeDistance + self.collitionRadius and self.position.y > obstacle.y + obstacle.height:
                if self.debug:
                    pygame.draw.line(self.screen, (255, 0, 0), (int((self.position.x * zoom_level) + background_pos[0]), int((self.position.y * zoom_level) + background_pos[1])), (obstacle.x * zoom_level + background_pos[0], (obstacle.y+obstacle.height) * zoom_level + background_pos[1]), 2)
                self.obstacleInFront = obstacle
                return True
        return False

    def slowDown(self,factor):
        speed = self.map(self.velocity.length, 0, self.max_speed, self.minimum_speed, self.max_speed)
        desired = Vec2d(0, 0) - self.velocity
        desired = desired.normalized() * speed
        steer = desired - self.velocity
        steer = self.setVectorLimit(steer, self.max_force)
        self.applyForce(steer)

    def slowOnObstacle(self):
        if self.state != 'normal':
            return
        if self.obstacleInFront:
            distance = self.position.get_distance(Vec2d(self.obstacleInFront.x, self.obstacleInFront.y))
            # the closer it gets to the obstacle, the slower it goes, until reaches the minimum speed
            speed = self.map(distance, 0, self.safeDistance + self.collitionRadius, self.minimum_speed, self.max_speed)
            desired = Vec2d(0, 0) - self.velocity
            desired = desired.normalized() * speed
            steer = desired - self.velocity
            steer = self.setVectorLimit(steer, self.max_force)
            self.applyForce(steer)

    def follow_west_to_east(self, future:Vec2d):
        target = Vec2d(0, 0)
        world_record = np.inf
        for i,_ in enumerate(self.road.points):
            if i == len(self.road.points) - 1:
                break
            a = self.road.points[i]
            b = self.road.points[i+1]
            # normal point
            normalPoint = self.getNormalPoint(future, a, b)

            if normalPoint.x < a.x or normalPoint.x > b.x:
                normalPoint = b
            
            distance = future.get_distance(normalPoint)
            if distance < world_record:
                world_record = distance
                target = normalPoint
            
                dir = b - a
                dir = dir.normalized() * 15
                target = target + dir
        return target

    def follow_south_to_north(self, future:Vec2d):
        target = Vec2d(0, 0)
        world_record = np.inf
        for i,_ in enumerate(self.road.points):
            if i == len(self.road.points) - 1:
                break
            a = self.road.points[i]
            b = self.road.points[i+1]
            # normal point
            normalPoint = self.getNormalPoint(future, a, b)

            if normalPoint.y > a.y or normalPoint.y < b.y:
                normalPoint = b
            
            distance = future.get_distance(normalPoint)
            if distance < world_record:
                world_record = distance
                target = normalPoint
            
                dir = b - a
                dir = dir.normalized() * 15
                target = target + dir
        return target

    def follow_east_to_west(self, future:Vec2d):
        target = Vec2d(0, 0)
        world_record = np.inf
        for i,_ in enumerate(self.road.points):
            if i == len(self.road.points) - 1:
                break
            a = self.road.points[i]
            b = self.road.points[i+1]
            # normal point
            normalPoint = self.getNormalPoint(future, a, b)

            if normalPoint.x > a.x or normalPoint.x < b.x:
                normalPoint = b
            
            distance = future.get_distance(normalPoint)
            if distance < world_record:
                world_record = distance
                target = normalPoint
            
                dir = b - a
                dir = dir.normalized() * 15
                target = target + dir
        return target

    def follow_north_to_south(self, future:Vec2d):
        target = Vec2d(0, 0)
        world_record = np.inf
        for i,_ in enumerate(self.road.points):
            if i == len(self.road.points) - 1:
                break
            a = self.road.points[i]
            b = self.road.points[i+1]
            # normal point
            normalPoint = self.getNormalPoint(future, a, b)

            if normalPoint.y < a.y or normalPoint.y > b.y:
                normalPoint = b
            
            distance = future.get_distance(normalPoint)
            if distance < world_record:
                world_record = distance
                target = normalPoint
            
                dir = b - a
                dir = dir.normalized() * 15
                target = target + dir
        return target

    def changeRoad(self, road:RoadPath):
        # if the vehicle is already in the next road, don't change the road
        if self.position.get_distance(Vec2d(road.points[0].x, road.points[0].y)) < 100:
            return
        self.arrive(road.points[0])
        self.state = 'changingRoad'
    
    def changingRoads(self):
        if self.nextRoad:
            if self.position.get_distance(Vec2d(self.nextRoad.points[0].x, self.nextRoad.points[0].y)) < 50:
                self.road = self.nextRoad
                self.nextRoad = None
                return True
        return False

    def checkEndOfRoad(self):
        if self.position.get_distance(self.road.points[-1]) < 10:
            self.state = 'idle'
            return True
        return False

    def follow(self, zoom_level, background_pos):
        # predict the future position
        future = self.velocity.normalized() * 25
        future += self.position

        # find the normal point
        target = Vec2d(0, 0)
        normal = Vec2d(0, 0)
        world_record = np.inf

        if self.road.direction == 'south_to_north':
            target = self.follow_south_to_north(future)
        elif self.road.direction == 'west_to_east':
            target = self.follow_west_to_east(future)
        elif self.road.direction == 'east_to_west':
            target = self.follow_east_to_west(future)
        elif self.road.direction == 'north_to_south':
            target = self.follow_north_to_south(future)

        # self.detectObstacle(zoom_level, background_pos)
        self.checkEndOfRoad()
        if world_record > self.road.radius and target != Vec2d(0, 0):
            if self.detectObstacle(zoom_level, background_pos):
                self.arrive(target)
                self.state = 'stoppingByObstacle'
            elif self.detectTooCloseToOtherCar(zoom_level, background_pos):
                self.arrive(target)
                self.state = 'tryingNotToCollide'
            elif self.changingRoads():
                self.arrive(target)
                self.state = 'changingRoad'
            else:
                self.seek(target)
                self.state = 'normal'
        
        if self.debug:
            pygame.draw.line(self.screen, (0, 0, 0), (int((self.position.x * zoom_level) + background_pos[0]), int((self.position.y * zoom_level) + background_pos[1])), (int((target.x * zoom_level) + background_pos[0]), int((target.y * zoom_level) + background_pos[1])), 2)
        
    def displayVehicleStats(self, zoom_level, background_pos):
        # show vehicle angle
        font = pygame.font.Font(None, 16)
        text = font.render(f"Angle: {round(np.degrees(np.arctan2(-self.velocity.y, self.velocity.x)), 2)}", True, (0, 0, 0))
        self.screen.blit(text, (self.position.x * zoom_level + background_pos[0], self.position.y * zoom_level + background_pos[1] + 30))

        # show vehicle speed
        text = font.render(f"Speed: {round(self.velocity.length, 2)}", True, (0, 0, 0))
        self.screen.blit(text, (self.position.x * zoom_level + background_pos[0], self.position.y * zoom_level + background_pos[1] + 45))

        # show vehicle state
        text = font.render(f"State: {self.state}", True, (0, 0, 0))
        self.screen.blit(text, (self.position.x * zoom_level + background_pos[0], self.position.y * zoom_level + background_pos[1] + 60))

        # show vehicle km/h
        self.getSpeedInKmH()
        text = font.render(f"Km/h: {round(self.km_h, 2)}", True, (0, 0, 0))
        self.screen.blit(text, (self.position.x * zoom_level + background_pos[0], self.position.y * zoom_level + background_pos[1] + 75))

        # show current road
        text = font.render(f"Road: {self.road.roadName}", True, (0, 0, 0))
        self.screen.blit(text, (self.position.x * zoom_level + background_pos[0], self.position.y * zoom_level + background_pos[1] + 90))

    def recordSpeed(self):
        self.speedHistory.append(self.velocity.length)