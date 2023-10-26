from typing import Tuple, List

import event
import card_events
import constants
import res
import random

def get_inner_box(x, y, width, height, border_thickness=1):
    return x + border_thickness, y + border_thickness, width - (2 * border_thickness), height - (2 * border_thickness)


class UserBox:
    def __init__(self, x, y, starting_balance, avatar_resource=None):
        self.x = x
        self.y = y
        self.balance = starting_balance
        if avatar_resource:
            self.avatar_resource = avatar_resource
        else:
            self.avatar_resource = random.choice(res.default_avatars)
        self.card_deal_slot = 0
        self.bet_amount = None

    def get_draw_self_event(self):
        events = [event.DrawUserBox(self.x, self.y),
                  self.write_balance(self.balance)
                  ]
        if self.avatar_resource:
            events.append(event.DrawResourceEvent(self.avatar_resource,
                                                  self.x + constants.USER_AVATAR_AREA_X_OFFSET + 1,
                                                  self.y + constants.USER_AVATAR_AREA_Y_OFFSET + 1))
        return \
            event.SimultaniousDrawEvent(events)

    def get_deal_card_event(self, card):
        dest_x = self.x + (self.card_deal_slot * (constants.CARD_WIDTH - 1))
        dest_y = self.y
        self.card_deal_slot = (self.card_deal_slot + 1) % 2
        return card_events.CardDealEvent(card, constants.DESIGN_WIDTH // 2, 0, dest_x, dest_y,
                                         constants.USER_CARD_DEAL_PACE)

    def write_balance(self, amount):
        return event.DrawTextEvent(f"{amount}",
                                   *get_inner_box(self.x + constants.USER_BAL_AREA_X_OFFSET,
                                                  self.y + constants.USER_BAL_AREA_Y_OFFSET,
                                                  constants.USER_BAL_AREA_WIDTH,
                                                  constants.USER_BAL_AREA_HEIGHT),
                                   constants.USER_BAL_AREA_FONT_COLOUR)

    def increment_balance(self, amount):
        self.balance += amount

        surface = event.text_to_surface(f"+{amount}", constants.BALANCE_INCREMENT_COLOUR, None)
        x = self.x + constants.USER_BAL_AREA_X_OFFSET + constants.USER_BAL_AREA_WIDTH // 2 + 1 - surface.get_width() // 2
        y = self.y + constants.USER_BAL_AREA_Y_OFFSET
        return event.ConcatenationEvent([self.write_balance(self.balance),
                                         event.FadeAndGlideEvent(surface,
                                                                 x,
                                                                 y,
                                                                 x,
                                                                 y - constants.FADE_DISTANCE,
                                                                 constants.FADE_TIME
                                                                 )])

    def write_probability(self, probability):
        return event.DrawTextEvent(f"{round(probability * 100)}%" if probability is not None else "",
                                   *get_inner_box(self.x + constants.USER_PROB_AREA_X_OFFSET,
                                                  self.y + constants.USER_PROB_AREA_Y_OFFSET,
                                                  constants.USER_PROB_AREA_WIDTH,
                                                  constants.USER_PROB_AREA_HEIGHT),
                                   constants.USER_PROB_AREA_FONT_COLOUR, constants.BACKGROUND_COLOUR)

    def bet(self, amount):
        if self.bet_amount is None:
            self.bet_amount = 0
        self.bet_amount += amount
        self.balance -= amount
        return event.ConcatenationEvent([
                                            self.write_balance(self.balance),
                                         event.GlideEvent(self.x + constants.USER_BAL_AREA_X_OFFSET +
                                                          constants.USER_BAL_AREA_WIDTH // 2 - res.chip_resource.get_width() // 2,
                                                          self.y + constants.USER_BAL_AREA_Y_OFFSET,
                                                          self.x + constants.USER_BET_AREA_X_OFFSET +
                                                          constants.USER_BET_AREA_WIDTH // 2 - res.chip_resource.get_width() // 2,
                                                          self.y + constants.USER_BET_AREA_Y_OFFSET +
                                                          constants.USER_BET_AREA_HEIGHT,
                                                          constants.COMMUNITY_CARD_DEAL_PACE,
                                                          res.chip_resource, leave=False),

                                         self.write_bet_amount(self.bet_amount)
                                         ])

    def get_chip_area_coords(self):
        return self.x + constants.USER_AVATAR_AREA_X_OFFSET + 1 + (constants.USER_AVATAR_AREA_WIDTH
                                                                   - res.CHIP_WIDTH) // 2, \
               self.y + constants.USER_AVATAR_AREA_Y_OFFSET + 1 + (constants.USER_AVATAR_AREA_HEIGHT
                                                                   - res.CHIP_HEIGHT) // 2

    def get_card_positions(self):
        return (self.x + constants.USER_CARD_AREA_X_OFFSET, self.y + constants.USER_CARD_AREA_Y_OFFSET), \
               (self.x + constants.USER_CARD_AREA_X_OFFSET + constants.CARD_WIDTH,
                self.y + constants.USER_CARD_AREA_Y_OFFSET)

    def muck_cards(self):
        return event.MassGlideAndStayAnimation([self.get_card_positions()[0],
                                                self.get_card_positions()[1]],
                                               [constants.MUCK_POSITION] * 2,

                                               [res.card_back_resource] * 2,
                                               constants.MUCK_PACE)

    def increment_to_balance(self, final_balance):
        return self.increment_balance(final_balance - self.balance)

    def write_bet_amount(self, amount):
        self.bet_amount = amount
        return event.DrawTextEvent(f"{self.bet_amount}",
                                      *get_inner_box(self.x + constants.USER_BET_AREA_X_OFFSET + 1,
                                                      self.y + constants.USER_BET_AREA_Y_OFFSET,
                                                      constants.USER_BET_AREA_WIDTH-1,
                                                      constants.USER_BET_AREA_HEIGHT),
                                      constants.USER_BET_AREA_FONT_COLOUR,
                                      constants.BACKGROUND_COLOUR)

    def get_wait_event(self, mean_wait_time):
        return event.UserWaitEvent(self.x, self.y, random.expovariate(1/mean_wait_time))

def deal_players(cards: List[Tuple[Tuple[int, int]]], user_boxes: List[UserBox]):
    card1_events = []
    card2_events = []
    for i, (card1, card2) in enumerate(cards):
        card1_events.append(user_boxes[i].get_deal_card_event(card1))
        card2_events.append(user_boxes[i].get_deal_card_event(card2))

    events = card1_events + card2_events
    return event.StaggeredEvent(events, constants.HOLE_DEAL_STAGGER_TIME)
