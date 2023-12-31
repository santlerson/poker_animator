RENDER_FRAMERATE = 240
TARGET_FRAMERATE = 24
TIMING_FACTOR = TARGET_FRAMERATE / RENDER_FRAMERATE

DESIGN_SIZE = (240, 135)

DESIGN_WIDTH, DESIGN_HEIGHT = DESIGN_SIZE

BACKGROUND_COLOUR = (51, 145, 48)  # green
# BACKGROUND_COLOUR = (0, 128, 128)  #cyan

RENDER_SCALING = 1

DISPLAY_SIZE = (int(DESIGN_SIZE[0] * RENDER_SCALING), int(DESIGN_SIZE[1] * RENDER_SCALING))

CARD_WIDTH, CARD_HEIGHT = 15, 24

COMMUNITY_Y_OFFSET = 22
COMMUNITY_X_OFFSET = 86
COMMUNITY_OFFSET_PER_CARD = 18

COMMUNITY_POSITIONS = [
    (COMMUNITY_X_OFFSET + COMMUNITY_OFFSET_PER_CARD * i, COMMUNITY_Y_OFFSET) for i in range(5)
]

COMMUNITY_SLOTS_BORDER_COLOUR = (255, 255, 255)

MUCK_POSITION = COMMUNITY_X_OFFSET - COMMUNITY_OFFSET_PER_CARD, COMMUNITY_Y_OFFSET
# COMMUNITY_MUCK_SOURCE = MUCK_POSITION[0] + COMMUNITY_Y_OFFSET, 0
COMMUNITY_MUCK_SOURCE = DESIGN_WIDTH//2, 0
# COMMUNITY_SOURCES = [
#     (
#         x + COMMUNITY_Y_OFFSET
#         if x + COMMUNITY_Y_OFFSET < DESIGN_WIDTH and i <= 2
#         else x - COMMUNITY_Y_OFFSET // 3
#         , 0
#     ) for i, (x, y) in enumerate(COMMUNITY_POSITIONS)
# ]
COMMUNITY_SOURCES = [(DESIGN_WIDTH//2,0)] * len(COMMUNITY_POSITIONS)

# DURATIONS
COMMUNITY_CARD_DEAL_PACE = (0.5 * DESIGN_WIDTH) / 1000  # pixels per millisecond
USER_CARD_DEAL_PACE = DESIGN_WIDTH / 1000  # pixels per millisecond

# USER_CARD_SLOT_WIDTH = CARD_WIDTH + 1
USER_CARD_AREA_WIDTH, USER_CARD_AREA_HEIGHT = 2 * CARD_WIDTH, CARD_HEIGHT + 1

USER_BET_AREA_X_OFFSET, USER_BET_AREA_Y_OFFSET = USER_CARD_AREA_WIDTH - 1, 0
USER_BET_AREA_WIDTH, USER_BET_AREA_HEIGHT = 27, 11

USER_PROB_AREA_X_OFFSET, USER_PROB_AREA_Y_OFFSET = 0, USER_CARD_AREA_HEIGHT - 1
USER_PROB_AREA_WIDTH, USER_PROB_AREA_HEIGHT = 30, 11

USER_BAL_AREA_X_OFFSET, USER_BAL_AREA_Y_OFFSET = 0, USER_PROB_AREA_Y_OFFSET + USER_PROB_AREA_HEIGHT - 1
USER_BAL_AREA_WIDTH, USER_BAL_AREA_HEIGHT = 30, 11

USER_AVATAR_AREA_X_OFFSET, USER_AVATAR_AREA_Y_OFFSET = USER_BET_AREA_X_OFFSET, USER_BET_AREA_Y_OFFSET + \
                                                       USER_BET_AREA_HEIGHT - 1
USER_AVATAR_AREA_WIDTH, USER_AVATAR_AREA_HEIGHT = USER_BET_AREA_WIDTH, 35

USER_BAL_AREA_FONT_COLOUR = (255, 255, 255)

USER_PROB_AREA_FONT_COLOUR = (255, 255, 255)

USER_BET_AREA_FONT_COLOUR = (255, 255, 255)

BALANCE_INCREMENT_COLOUR = (0, 255, 0)

USER_BOX_POSITIONS = [
    (179, 22),
    (179, 78),
    (92, 78),
    (5, 78),
    (5, 22)
]
USER_BOX_POSITIONS_ACCORDING_TO_PLAYER_COUNT = {
    2: [
        USER_BOX_POSITIONS[1],
        USER_BOX_POSITIONS[3]
    ],
    3: [
        USER_BOX_POSITIONS[0],
        USER_BOX_POSITIONS[2],
        USER_BOX_POSITIONS[4]
    ],
    4: [
        USER_BOX_POSITIONS[0],
        USER_BOX_POSITIONS[1],
        USER_BOX_POSITIONS[3],
        USER_BOX_POSITIONS[4]
    ],
    5: USER_BOX_POSITIONS

}

FADE_DISTANCE = 25

FADE_TIME = 500

TARGET_TABLE = 0
TARGET_ABOVE_TABLE = 1

HOLE_DEAL_STAGGER_TIME = 275


USER_CARD_AREA_X_OFFSET=0
USER_CARD_AREA_Y_OFFSET=0

POT_BOX_X=92
POT_BOX_Y=48
POT_BOX_WIDTH=56
POT_BOX_HEIGHT=28

POT_TEXT_X = 122 -92 + POT_BOX_X
POT_TEXT_Y = 57 - 48 + POT_BOX_Y
POT_TEXT_WIDTH, POT_TEXT_HEIGHT = 24 , 10
POT_TEXT_COLOUR = (255, 255, 255)

BLIND_EXCHANGE_PACE = 0.5 * DESIGN_WIDTH / 1000
MUCK_PACE = 0.5 * DESIGN_WIDTH / 1000

BANNER_X, BANNER_Y = 20,4

USER_WAIT_COLOUR = (39, 83, 140)

MAXIMAL_MEAN_WAIT_TIME = 8*1000
FOLD_WAIT_PERCENTAGE = 0.25