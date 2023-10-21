from abc import abstractmethod
from typing import List, Union, Tuple
import res
import pygame
import constants

COMPLETE = 0
CONTINUE = 1
SKIP_FRAME = 2

PERMANENT = True
TEMPORARY = False


def text_to_surface(text, color, background_colour=constants.BACKGROUND_COLOUR, title=False):
    return (res.title_font if title else res.font).render(text, True, color, background_colour)


class Event:
    @abstractmethod
    def draw(self, above_table, table, time):
        pass


class GlideEvent(Event):
    def __init__(self, start_x, start_y, finish_x, finish_y, pace, image, leave=True, clear_source=False):
        self.start_x = start_x
        self.start_y = start_y
        self.finish_x = finish_x
        self.finish_y = finish_y
        self.image = image
        self.start_time = None
        self.leave = leave
        distance = ((finish_x - start_x) ** 2 + (finish_y - start_y) ** 2) ** 0.5
        self.duration = distance * constants.TIMING_FACTOR / pace
        self.clear_source = clear_source

    def draw(self, above_table, table, time):
        if self.start_time is None:
            self.start_time = time
            if self.clear_source:
                above_table.fill((0, 0, 0, 0), pygame.Rect(self.start_x, self.start_y, self.image.get_width(),
                                          self.image.get_height()), pygame.BLEND_RGBA_MULT)
                return SKIP_FRAME, PERMANENT
        elapsed = time - self.start_time

        if elapsed < self.duration:
            x = self.start_x + (self.finish_x - self.start_x) * min(elapsed, self.duration) / self.duration
            y = self.start_y + (self.finish_y - self.start_y) * min(elapsed, self.duration) / self.duration
            above_table.blit(self.image, (x, y))
            return CONTINUE, TEMPORARY
        elif self.leave:
            x = self.finish_x
            y = self.finish_y
            above_table.blit(self.image, (x, y))
            return COMPLETE, (PERMANENT if self.leave else TEMPORARY)
        else:
            return COMPLETE, TEMPORARY


class DrawEvent(Event):
    pass


class DrawResourceEvent(DrawEvent):
    def __init__(self, image, x, y, target=constants.TARGET_TABLE):
        self.image = image
        self.x = x
        self.y = y
        self.target = target

    def draw(self, above_table, table, time):
        (table if self.target == constants.TARGET_TABLE else above_table).blit(self.image, (self.x, self.y))
        return COMPLETE, PERMANENT


class DrawTextEvent(DrawEvent):
    def __init__(self, text,
                 x, y, width,
                 height, colour, background_colour=constants.BACKGROUND_COLOUR,
                 title=False, target=constants.TARGET_TABLE):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.colour = colour
        self.title = title
        self.background_colour = background_colour
        self.target = target

    def draw(self, above_table, table, time):
        surface = text_to_surface(self.text, self.colour, self.background_colour, self.title)
        text_width, text_height = surface.get_size()
        if text_width > self.width:
            new_surface = pygame.Surface((self.width, text_height))
            new_surface.blit(surface, (0, 0),
                             ((text_width - self.width + 1) // 2, 0, self.width - (text_width - self.width) // 2,
                              text_height))
            surface = new_surface
            text_width = self.width
        if text_height > self.height:
            new_surface = pygame.Surface((text_width, self.height))
            new_surface.blit(surface, (0, 0), (0, (text_height - self.height + 1) // 2, text_width,
                                               self.height - (text_height - self.height - 2) // 2))
            surface = new_surface
            text_height = self.height
        target_surface = table if self.target == constants.TARGET_TABLE else above_table
        target_surface.fill(self.background_colour, pygame.Rect(self.x, self.y, self.width, self.height))
        target_surface.blit(surface,
                            (self.x + (self.width - text_width) // 2, self.y + (self.height - text_height) // 2))
        return COMPLETE, PERMANENT


class ConcatenationEvent(Event):
    def __init__(self, events: List[Event]):
        self.events = events
        self.i = 0

    def draw(self, above_table, table, time):
        for j in range(self.i):
            self.events[j].draw(above_table, table, time)
        completion_status, permanence = self.events[self.i].draw(above_table, table, time)
        if completion_status == COMPLETE:
            if self.i < len(self.events) - 1:
                self.i += 1
                return CONTINUE, permanence
            elif self.i == len(self.events) - 1:
                return COMPLETE, permanence
            else:
                return CONTINUE, permanence
        else:
            return CONTINUE, permanence


class DelayEvent(Event):
    def __init__(self, delay):
        self.delay = delay * constants.TIMING_FACTOR
        self.start_time = None

    def draw(self, above_table, table, time):
        if self.start_time is None:
            self.start_time = time
        elapsed = time - self.start_time
        if elapsed >= self.delay:
            return COMPLETE, PERMANENT
        else:
            return CONTINUE, TEMPORARY


class DrawBoxEvent(DrawEvent):
    def __init__(self, x, y, width, height, border_colour, fill_colour=None, target=constants.TARGET_TABLE):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.border_colour = border_colour
        self.fill_colour = fill_colour
        self.target = target

    def draw(self, above_table, table, time):
        target_surface = table if self.target == constants.TARGET_TABLE else above_table
        pygame.draw.rect(target_surface, self.border_colour, pygame.Rect(self.x, self.y, self.width, self.height), 1)
        if self.fill_colour:
            pygame.draw.rect(target_surface, self.fill_colour,
                             pygame.Rect(self.x + 1, self.y + 1, self.width - 1, self.height - 1))
        return COMPLETE, PERMANENT


class SimultaniousDrawEvent(DrawEvent):
    def __init__(self, events: List[Union[DrawEvent]]):
        self.events = events

    def draw(self, above_table, table, time):
        for event in self.events:
            event.draw(above_table, table, time)
        return COMPLETE, PERMANENT


class DrawCommunitySlots(SimultaniousDrawEvent):
    def __init__(self):
        super().__init__([
            DrawBoxEvent(slot_x, slot_y, constants.CARD_WIDTH,
                         constants.CARD_HEIGHT, constants.COMMUNITY_SLOTS_BORDER_COLOUR)
            for slot_x, slot_y in constants.COMMUNITY_POSITIONS
        ]+[
            DrawBoxEvent(constants.MUCK_POSITION[0], constants.MUCK_POSITION[1],
                         constants.CARD_WIDTH, constants.CARD_HEIGHT,
                         constants.COMMUNITY_SLOTS_BORDER_COLOUR)
        ])


class DrawPotBox(SimultaniousDrawEvent):
    def __init__(self):
        super().__init__([
            DrawBoxEvent(constants.POT_BOX_X, constants.POT_BOX_Y
                         , constants.POT_BOX_WIDTH,
                         constants.POT_BOX_HEIGHT,
                         constants.COMMUNITY_SLOTS_BORDER_COLOUR),
            DrawResourceEvent(res.large_chip_resource,
                              constants.POT_BOX_X + 2,
                              constants.POT_BOX_Y + 1
                              )

        ])


class DrawUserBox(SimultaniousDrawEvent):
    def __init__(self, x, y):
        super().__init__([
            DrawBoxEvent(x, y, constants.CARD_WIDTH, constants.CARD_HEIGHT + 1,
                         constants.COMMUNITY_SLOTS_BORDER_COLOUR),
            DrawBoxEvent(x + constants.CARD_WIDTH - 1, y, constants.CARD_WIDTH + 1, constants.CARD_HEIGHT + 1,
                         constants.COMMUNITY_SLOTS_BORDER_COLOUR),
            DrawBoxEvent(x + constants.USER_BET_AREA_X_OFFSET, y + constants.USER_BET_AREA_Y_OFFSET,
                         constants.USER_BET_AREA_WIDTH,
                         constants.USER_BET_AREA_HEIGHT, constants.COMMUNITY_SLOTS_BORDER_COLOUR),
            DrawBoxEvent(x + constants.USER_PROB_AREA_X_OFFSET, y + constants.USER_PROB_AREA_Y_OFFSET,
                         constants.USER_PROB_AREA_WIDTH, constants.USER_PROB_AREA_HEIGHT,
                         constants.COMMUNITY_SLOTS_BORDER_COLOUR),
            DrawBoxEvent(x + constants.USER_BAL_AREA_X_OFFSET, y + constants.USER_BAL_AREA_Y_OFFSET,
                         constants.USER_BAL_AREA_WIDTH, constants.USER_BAL_AREA_HEIGHT,
                         constants.COMMUNITY_SLOTS_BORDER_COLOUR),
            DrawBoxEvent(x + constants.USER_AVATAR_AREA_X_OFFSET, y + constants.USER_AVATAR_AREA_Y_OFFSET,
                         constants.USER_AVATAR_AREA_WIDTH, constants.USER_AVATAR_AREA_HEIGHT,
                         constants.COMMUNITY_SLOTS_BORDER_COLOUR),

        ])


class FadeAndGlideEvent(Event):
    def __init__(self, image, start_x, start_y, end_x, end_y, duration):
        self.image = image
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.duration = duration * constants.TIMING_FACTOR
        self.start_time = None

    def draw(self, above_table, table, time):
        if self.start_time is None:
            self.start_time = time
        elapsed = time - self.start_time
        if elapsed > self.duration:
            return COMPLETE, TEMPORARY
        else:
            x = self.start_x + (self.end_x - self.start_x) * elapsed / self.duration
            y = self.start_y + (self.end_y - self.start_y) * elapsed / self.duration
            # elapsed / self.duration should be percentage transparancy
            image = self.image.copy()
            image.fill((255, 255, 255, 255 - 255 * elapsed / self.duration), None, pygame.BLEND_RGBA_MULT)
            above_table.blit(image, (x, y))
            return CONTINUE, TEMPORARY


class MassGlideAndStayAnimation(Event):
    def __init__(self, start_coords: List[Tuple[int, int]],
                 finish_coords: List[Tuple[int, int]], surfaces, pace):
        self.all_complete = False
        self.started = False
        self.start_coords = start_coords
        self.events = [
            GlideEvent(start_x, start_y, finish_x, finish_y, pace, surface)
            for (start_x, start_y), (finish_x, finish_y), surface in zip(start_coords, finish_coords, surfaces)
        ]
        self.dimensions = [(surface.get_width(), surface.get_height()) for surface in surfaces]

    def draw(self, above_table, table, time):
        if not self.started:
            for (width, height), (x, y) in zip(self.dimensions, self.start_coords):
                # fill with alpha
                above_table.fill((0, 0, 0, 0), pygame.Rect(x, y, width, height), pygame.BLEND_RGBA_MULT)
            self.started = True
            return SKIP_FRAME, PERMANENT
        self.all_complete = True
        for event in self.events:
            completeness, _ = event.draw(above_table, table, time)
            self.all_complete = (self.all_complete and (completeness == COMPLETE))
        if self.all_complete:
            return COMPLETE, PERMANENT
        else:
            return CONTINUE, TEMPORARY


class StaggeredEvent(Event):
    def __init__(self, events: List[Event], stagger_time):
        self.events = events
        self.stagger_time = stagger_time * constants.TIMING_FACTOR
        self.start_time = None

    def draw(self, above_table, table, time):
        if self.start_time is None:
            self.start_time = time
            self.done = [False for _ in self.events]
        elapsed = time - self.start_time
        anything_been_done = False
        for i, event in enumerate(self.events):
            if elapsed > i * self.stagger_time:  # or not anything_been_done:
                completeness, _ = event.draw(above_table, table, time)
                self.done[i] = (completeness == COMPLETE)
                if not anything_been_done:
                    anything_been_done = not (completeness == COMPLETE)
            else:
                continue
        if all(self.done):
            return COMPLETE, PERMANENT
        else:
            return CONTINUE, TEMPORARY
