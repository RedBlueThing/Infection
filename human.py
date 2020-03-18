import pygame as pg
import collision
import enum
import random
import uuid

HUMAN_RADIUS = 7
SICK_COLOR = (255, 0, 0)
RECOVERED_COLOR = (0, 0, 255)
HEALTHY_COLOR = (0, 255, 0)
MAX_RECOVERY_SECONDS = 30


class Status(enum.Enum):

    Healthy = "healthy"
    Sick = "sick"
    Recovered = "recovered"


class Human:
    def __init__(self, surface, quarantine, sick, x, y, width, height, barriers=[]):

        self._status = Status.Healthy if not sick else Status.Sick
        self.recovering = False if not sick else True

        self.recovery_seconds = 0
        self.total_recovery_seconds = random.randrange(0, MAX_RECOVERY_SECONDS)
        self.surface = surface
        self.quarantine = quarantine
        self.direction = self.random_direction()
        self.position = collision.Vector(x, y)
        self.id = uuid.uuid4()
        self.width = width
        self.height = height
        self.barriers = barriers

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):

        if (self.status == Status.Healthy and status == Status.Sick):
            self.recovering = True

        self._status = status

    def collision_circle(self):
        return collision.Circle(self.position, HUMAN_RADIUS)

    def random_amount(self):

        sign = -1 if random.randrange(0, 2) else 1
        return random.randrange(1, 100) * sign

    def random_direction(self):

        return collision.Vector(self.random_amount(), self.random_amount()).normalize()

    def color(self):

        if (self.status == Status.Sick):
            return SICK_COLOR

        if (self.status == Status.Recovered):
            return RECOVERED_COLOR

        return HEALTHY_COLOR

    def velocity(self):

        if (self.quarantine):
            return collision.Vector(0, 0)

        return self.direction

    def bounce(self, normal):
        """
        r = self.direction - 2(self.direction . normal) * normal
        """
        dot_product = self.direction.dot(normal)
        self.direction = (self.direction - collision.Vector((2 * dot_product) * normal.x,
                                                            (2 * dot_product) * normal.y)).normalize()

    def direction(self):
        return self.direction

    def update_axis_and_overlap(self, axis, overlap, new_axis, new_overlap):

        overlap = overlap + new_overlap if overlap is not None else new_overlap
        axis = axis + new_axis if axis is not None else new_axis
        return (axis, overlap)

    def infectious(self):
        """
        If people who have recovered can pass on the disease then this should
        be self.status != Status.Healthy
        """

        if (self.status == Status.Sick):
            return True

        return False

    def collide(self, humans):

        shortest_colliding_axis = None
        overlap_v = None
        response = collision.Response()

        collide = False
        for other_human in humans:

            # check if this is another human
            if other_human.id == self.id:
                continue

            if (collision.collide(self.collision_circle(), other_human.collision_circle(), response)):
                shortest_colliding_axis, overlap_v = self.update_axis_and_overlap(shortest_colliding_axis, overlap_v,
                                                                                  response.overlap_n,
                                                                                  response.overlap_v)
                # Not sure if people who have recovered can pass it on?
                if (other_human.infectious() and self.status == Status.Healthy):
                    self.status = Status.Sick
                if (self.infectious() and other_human.status == Status.Healthy):
                    other_human.status = Status.Sick

                collide = True

        # Also check any barriers
        barrier_collide = False
        for barrier in self.barriers:
            if (collision.collide(self.collision_circle(), barrier, response)):
                shortest_colliding_axis, overlap_v = self.update_axis_and_overlap(shortest_colliding_axis, overlap_v,
                                                                                  response.overlap_n,
                                                                                  response.overlap_v)
                collide = True
                barrier_collide = True

        if (collide):
            self.position -= overlap_v
            self.bounce(shortest_colliding_axis.reverse())

    def update(self, seconds):

        if (self.recovering):
            self.recovery_seconds += seconds

        if (self.recovery_seconds >= self.total_recovery_seconds):
            self.status = Status.Recovered

        self.position += self.velocity()

    def render(self):

        pg.draw.circle(self.surface, self.color(), (self.position.x, self.position.y), HUMAN_RADIUS)
