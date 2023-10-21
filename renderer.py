import pygame
import event
import os
import constants
import tqdm
from event_list_from_logs import get_event_list_from_logs
import sys


def get_events():
    return get_event_list_from_logs(sys.argv[1])


def main():
    pygame.init()
    # screen = pygame.display.set_mode(DISPLAY_SIZE)
    above_table = pygame.Surface(constants.DESIGN_SIZE, pygame.SRCALPHA, 32)
    table = pygame.Surface(constants.DESIGN_SIZE)
    table.fill(constants.BACKGROUND_COLOUR)
    clock = pygame.time.Clock()
    events = get_events()
    frame_num = 0
    if not os.path.exists('frames'):
        os.mkdir('frames')
    # empty contents of frames
    for file in os.listdir('frames'):
        os.remove(os.path.join('frames', file))
    bar = tqdm.tqdm(total=len(events))
    while events:

        above_table_copy = above_table.copy()
        table_copy = table.copy()
        if events:
            completeness, permanence = events[0].draw(above_table_copy, table_copy, pygame.time.get_ticks())
            if completeness == event.COMPLETE:
                events.pop(0)
                bar.update(1)
            if permanence == event.PERMANENT:
                above_table = above_table_copy
                table = table_copy
            if completeness == event.SKIP_FRAME:
                continue

        save_surface = table_copy.copy()
        save_surface.blit(above_table_copy, (0, 0))
        pygame.image.save(save_surface, f'frames/img-{frame_num:#0{16}}.png')
        clock.tick(constants.RENDER_FRAMERATE)
        frame_num += 1
    pygame.quit()


if __name__ == '__main__':
    main()
