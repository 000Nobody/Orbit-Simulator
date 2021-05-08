import pygame
import sys
import random
import math
import numpy as np
from pygame.locals import KEYDOWN, KEYUP, MOUSEBUTTONDOWN, MOUSEBUTTONUP, QUIT

pygame.init()
clock = pygame.time.Clock()
pygame.display.set_caption("Orbital Simulator")

WINDOW_SIZE = (1920, 1080)
screen = pygame.display.set_mode(WINDOW_SIZE)
screen_rect = screen.get_rect()
display = pygame.Surface(WINDOW_SIZE)
display_rect = display.get_rect()

G = 6.67408 * (10 ** -11)  # Gravitational Constant
MASS_AREA_RATIO = 2 * (10 ** 9)  # mass in kilograms to area in pixels

planets = []
particles = []
planet_id = 0
mouse_down = False
ctrl_down = False


class Planet:
    def __init__(self, x, y, radius, mass, id):
        self.x = x
        self.y = y
        self.radius = radius
        self.volume = radius ** 3
        self.mass = mass
        self.id = id
        self.rect = pygame.Rect(
            self.x - self.radius / 1.5,
            self.y - self.radius / 1.5,
            self.radius * 1.5,
            self.radius * 1.5,
        )
        self.last_pos = (x, y)
        self.velocity = (0, 0)
        self.doneCreating = False
        self.color = random.choice(
            [
                (236, 37, 37),
                (236, 151, 37),
                (247, 219, 41),
                (41, 247, 72),
                (46, 231, 208),
                (46, 63, 231),
                (221, 53, 232),
                (255, 84, 180),
            ]
        )

    def update(self):
        self.getVelocity()
        self.collision()
        self.rect = pygame.Rect(
            self.x - self.radius / 1.5,
            self.y - self.radius / 1.5,
            self.radius * 1.5,
            self.radius * 1.5,
        )
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.mass = math.pi * (self.radius ** 2) * MASS_AREA_RATIO
        if not mouse_down:
            self.doneCreating = True
        if not self.doneCreating:
            self.create()
        if self.doneCreating and self.velocity[0] != 0 and self.velocity[1] != 0:
            particles.append(
                Particle(
                    self.x,
                    self.y,
                    [np.subtract(self.color, (35, 35, 35))],
                    1,
                    int(-self.velocity[0]),
                    1,
                    int(-self.velocity[1]),
                    1,
                    int(self.radius / 1.5),
                    0.4,
                    0,
                )
            )

    def create(self):
        if self.radius <= 200:
            self.radius += 0.35
        self.mass = math.pi * (self.radius ** 2) * MASS_AREA_RATIO
        self.volume = self.radius ** 3
        self.x, self.y = mx, my

    def getVelocity(self):
        if not self.doneCreating:
            self.current_pos = [mx, my]
            self.dpos = [
                (self.current_pos[0] - self.last_pos[0]) / 2,
                (self.current_pos[1] - self.last_pos[1]) / 2,
            ]  # dividing by two to make it less sensitive
            self.last_pos = [
                mx,
                my,
            ]  # Comparing mouse pos from one frame ago to current frame to get the velocity of the mouse movement
            self.velocity = self.dpos

        if self.doneCreating:
            for planet in planets:
                if self.id != planet.id and planet.doneCreating:
                    dx = planet.x - self.x
                    dy = planet.y - self.y
                    angle = math.atan2(dy, dx)  # Calculate angle between planets
                    d = math.sqrt((dx ** 2) + (dy ** 2))  # Calculate distance
                    if d == 0:
                        d = 0.000001  # Prevent division by zero error
                    f = (
                        G * self.mass * planet.mass / (d ** 2)
                    )  # Calculate gravitational force

                    self.velocity[0] += (math.cos(angle) * f) / self.mass
                    self.velocity[1] += (math.sin(angle) * f) / self.mass

    def collision(self):
        if self.doneCreating:
            for planet in planets:
                if (
                    self.id != planet.id
                    and planet.doneCreating
                    and self.rect.colliderect(planet.rect)
                    and self.mass > planet.mass
                ):
                    planets.remove(planet)
                    if self.radius <= 200:
                        self.volume += planet.volume
                        self.radius = self.volume ** (1. /3.)

    def draw(self):
        pygame.draw.circle(
            display, self.color, (int(self.x), int(self.y)), int(self.radius)
        )
        # pygame.draw.rect(display, (255, 255, 255), self.rect)


class Particle:
    def __init__(
        self,
        x,
        y,
        colors,
        min_xvel,
        max_xvel,
        min_yvel,
        max_yvel,
        min_radius,
        max_radius,
        shrink_rate,
        gravity,
    ):
        self.x = x
        self.y = y
        self.color = random.choice(colors)
        if min_xvel < max_xvel:
            self.xvel = random.randint(min_xvel, max_xvel) / 10
        else:
            self.xvel = random.randint(max_xvel, min_xvel) / 10
        if min_yvel < max_yvel:
            self.yvel = random.randint(min_yvel, max_yvel) / 10
        else:
            self.yvel = random.randint(max_yvel, min_yvel) / 10
        self.radius = random.randint(min_radius, max_radius)
        self.shrink_rate = shrink_rate
        self.gravity = gravity

    def update(self):
        self.x += self.xvel
        self.y += self.yvel
        self.radius -= self.shrink_rate
        self.yvel += self.gravity

    def draw(self):
        pygame.draw.circle(
            display, self.color, (int(self.x), int(self.y)), int(self.radius)
        )


def draw():
    display.fill((25, 25, 25))

    for particle in particles:
        particle.draw()

    for planet in planets:
        planet.draw()

    display_rect.center = screen_rect.center
    screen.blit(display, (0, 0))

    pygame.display.update()


while True:
    clock.tick(60)
    mx, my = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit()
            pygame.quit()

        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            mouse_down = True
            if not ctrl_down:
                planets.append(Planet(mx, my, 0, 0, planet_id))
                planet_id += 1

        if event.type == MOUSEBUTTONUP and event.button == 1:
            mouse_down = False

        if event.type == KEYDOWN and event.key == pygame.K_LCTRL:
            ctrl_down = True

        if event.type == KEYUP and event.key == pygame.K_LCTRL:
            ctrl_down = False

        if event.type == KEYDOWN and event.key == pygame.K_TAB:
            planets.clear()

    for planet in planets:
        if len(planets) >= 50:
            planets.remove(planet)
        if planet.x > 50000 or planet.x < -50000:
            planets.remove(planet)
        if planet.y > 50000 or planet.y < -50000:
            planets.remove(planet)
        if planet.velocity[0] > 1000 or planet.velocity[0] < -1000:
            planets.remove(planet)
        if planet.velocity[1] > 1000 or planet.velocity[1] < -1000:
            planets.remove(planet)
    
    for particle in particles:
        particle.update()
        if particle.radius <= 0:
            particles.remove(particle)
    for planet in planets:
        planet.update()
    draw()
