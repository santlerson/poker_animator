import event
import constants
import res






class MuckEvent(event.GlideEvent):
    def __init__(self, start_x, start_y, duration):
        super().__init__(start_x, start_y, constants.MUCK_POSITION[0], constants.MUCK_POSITION[1], duration, res.card_back_resource)

class CommunityMuckEvent(MuckEvent):
    def __init__(self):
        super().__init__(constants.COMMUNITY_MUCK_SOURCE[0], constants.COMMUNITY_MUCK_SOURCE[1], constants.COMMUNITY_CARD_DEAL_PACE)

class CardDealEvent(event.ConcatenationEvent):
    def __init__(self, card, start_x, start_y, finish_x, finish_y, pace):
        rank, suit = card
        image = res.card_resource_dict[(suit, rank)]
        deal_glide = event.GlideEvent(start_x, start_y, finish_x, finish_y, pace, res.card_back_resource, leave=False)
        reveal_draw = event.DrawResourceEvent(image, finish_x, finish_y, target=event.constants.TARGET_ABOVE_TABLE)
        super().__init__([deal_glide, reveal_draw])


class CommunityFlipOneCard(CardDealEvent):
    def __init__(self, card, community_index):
        source_x, source_y = constants.COMMUNITY_SOURCES[community_index]
        dest_x, dest_y = constants.COMMUNITY_POSITIONS[community_index]
        super().__init__(card, source_x, source_y, dest_x, dest_y, constants.COMMUNITY_CARD_DEAL_PACE)

class Flop(event.ConcatenationEvent):
    def __init__(self, cards):
        super().__init__([CommunityMuckEvent()]+[CommunityFlipOneCard(card, i) for i, card in enumerate(cards)])

class TurnOrRiver(event.ConcatenationEvent):
    def __init__(self, card, turn=True):
        super().__init__([CommunityMuckEvent(), CommunityFlipOneCard(card, 3 if turn else 4)])

