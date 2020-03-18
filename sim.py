#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
import random
import collision
from human import Human

pygame.init()

WIDTH = 640
HEIGHT = 480

screen = pygame.display.set_mode((WIDTH, HEIGHT))  # try out larger values and see what happens !
screenrect = screen.get_rect()
background = pygame.Surface(screen.get_size())  #create surface for background
background.fill((255, 255, 255))  #fill the background white (red,green,blue)

background = background.convert()  #convert surface for faster blitting
clock = pygame.time.Clock()  #create pygame clock object

mainloop = True
FPS = 60  # desired max. framerate in frames per second.


def quarantine():
    return True if random.randint(0, 10) < 9 else False


def sick():
    return True if random.randint(0, 10) < 1 else False


barriers = [
    collision.Poly(
        collision.Vector(0, 0),
        [collision.Vector(0, 0),
         collision.Vector(1, 0),
         collision.Vector(1, HEIGHT),
         collision.Vector(0, HEIGHT)]),
    collision.Poly(
        collision.Vector(WIDTH, 0),
        [collision.Vector(0, 0),
         collision.Vector(10, 0),
         collision.Vector(10, HEIGHT),
         collision.Vector(0, HEIGHT)]),
    collision.Poly(
        collision.Vector(0, -10),
        [collision.Vector(0, 0),
         collision.Vector(WIDTH, 0),
         collision.Vector(WIDTH, 10),
         collision.Vector(0, 10)]),
    collision.Poly(
        collision.Vector(0, HEIGHT),
        [collision.Vector(0, 0),
         collision.Vector(WIDTH, 0),
         collision.Vector(WIDTH, 10),
         collision.Vector(0, 10)]),
]

humans = [
    Human(background, quarantine(), sick(), random.randint(0, WIDTH), random.randint(0, HEIGHT), WIDTH, HEIGHT,
          barriers) for x in range(0, 60)
]

while mainloop:
    milliseconds = clock.tick(FPS)  # milliseconds passed since last frame
    seconds = milliseconds / 1000.0  # seconds passed since last frame (float)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            mainloop = False  # pygame window closed by user
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                mainloop = False  # user pressed ESC

    background.fill((0, 0, 0))
    for human in humans:
        human.collide(humans)

    for human in humans:
        human.update(seconds)
        human.render()

    screen.blit(background, (0, 0))  #draw background on screen (overwriting all)

    pygame.display.flip()  # flip the screen 30 times a second
