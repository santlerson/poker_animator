from typing import List, Tuple
import event, card_events, constants, res
import user_box
import json
import tqdm

(PREFLOP, FLOP, TURN, RIVER) = range(4)

def get_event_list_from_logs(log_path):
    bb_index = None
    sb_index = None
    old_bb_index = None
    old_sb_index = None
    event_list = []
    with open(log_path, 'r') as log_file:
        json_map = json.load(log_file, )
    starting_balance = json_map['parameters']['starting_balance']
    user_count = len(json_map['players'])
    user_box_positions = constants.USER_BOX_POSITIONS_ACCORDING_TO_PLAYER_COUNT[user_count]
    user_boxes = [
        user_box.UserBox(x,y, starting_balance, None)
        for x,y in user_box_positions
    ]
    user_box_draw_events = [
        box.get_draw_self_event() for box in user_boxes
    ]

    event_list.append(
        event.SimultaniousDrawEvent(
            [
                event.DrawCommunitySlots(),
                *user_box_draw_events,
                event.DrawPotBox(),
                event.DrawResourceEvent(res.banner, constants.BANNER_X, constants.BANNER_Y),
            ]
        )
    )
    event_list.append(
        event.SimultaniousDrawEvent([
            ub.write_bet_amount(0) for ub in user_boxes
        ])
    )
    for r in tqdm.tqdm(json_map['rounds']):
        folded = [False for _ in range(user_count)]

        old_bb_index, old_sb_index = bb_index, sb_index
        if old_bb_index is None:
            bb_chip_source = constants.DESIGN_HEIGHT//2, 0
        else:
            bb_chip_source = user_boxes[old_bb_index].get_chip_area_coords()
        if old_sb_index is None:
            sb_chip_source = constants.DESIGN_HEIGHT//2, 0
        else:
            sb_chip_source = user_boxes[old_sb_index].get_chip_area_coords()
        bb_index = r['bb']
        sb_index = r['sb']
        event_list.append(
            event.MassGlideAndStayAnimation(
                [
                    bb_chip_source,
                    sb_chip_source
                ],
                [
                    user_boxes[bb_index].get_chip_area_coords(),
                    user_boxes[sb_index].get_chip_area_coords()
                ],
                [res.big_blind_resource, res.small_blind_resource],
                constants.BLIND_EXCHANGE_PACE

            )
        )
        event_list.append(
            event.StaggeredEvent(
                [
                    user_boxes[bb_index].bet(r['bb_amount']),
                    user_boxes[sb_index].bet(r['sb_amount'])
                ],
                0
            )
        )

        pot_amount = r['bb_amount'] + r['sb_amount']
        event_list.append(
            event.DrawTextEvent(
                f"{pot_amount}",
                constants.POT_TEXT_X,
                constants.POT_TEXT_Y,
                constants.POT_TEXT_WIDTH,
                constants.POT_TEXT_HEIGHT,
                constants.POT_TEXT_COLOUR)
        )
        holes = r['hole_cards']
        hole_deal_events = []
        boxes_from_sb = user_boxes[sb_index:] + user_boxes[:sb_index]
        holes_from_sb = holes[sb_index:] + holes[:sb_index]
        for card_num in range(2):
            for ub, hole in zip(boxes_from_sb, holes_from_sb):
                if ub.balance or ub.bet_amount:
                    hole_deal_events.append(
                    ub.get_deal_card_event(tuple(hole[card_num]))
                    )
        event_list.append(
            event.StaggeredEvent(
                hole_deal_events, constants.HOLE_DEAL_STAGGER_TIME
            )
        )
        for stage_num, stage_json in enumerate(r["stages"]):
            if stage_num==PREFLOP:
                pass
            elif stage_num==FLOP:
                event_list.append(
                    card_events.Flop(
                        r['community_cards'][:3]
                    )
                )
            elif stage_num==TURN:
                event_list.append(
                    card_events.TurnOrRiver(
                        r['community_cards'][3],
                        turn=True
                    )
                )
            elif stage_num==RIVER:
                event_list.append(
                    card_events.TurnOrRiver(
                        r['community_cards'][4],
                        turn=False
                    )
                )
            probabilities = stage_json.get("probabilities", None)
            if probabilities is not None:
                this_time_probability = probabilities.pop(0)
                event_list.append(
                    event.SimultaniousDrawEvent(
                        [
                            ub.write_probability(this_time_probability[i])
                            for i, ub in enumerate(user_boxes)
                        ]
                    )
                )
            for action in stage_json["actions"]:
                if action.get("amount", -1)<0:
                    event_list.append(
                        user_boxes[action["player"]].muck_cards()
                    )
                    if probabilities:
                        this_time_probability = probabilities.pop(0)
                        event_list.append(
                            event.SimultaniousDrawEvent(
                                [ub.write_probability(this_time_probability[i]) for i, ub in enumerate(user_boxes)]
                            )
                        )
                    folded[action["player"]] = True
                else:
                    if action["amount"]>0:
                        event_list.append(
                            user_boxes[action["player"]].bet(action["amount"])
                        )
                        pot_amount+=action["amount"]
                        event_list.append(
                            event.DrawTextEvent(
                                f"{pot_amount}",
                                constants.POT_TEXT_X,
                                constants.POT_TEXT_Y,
                                constants.POT_TEXT_WIDTH,
                                constants.POT_TEXT_HEIGHT,
                                constants.POT_TEXT_COLOUR)
                        )

        for new_balance, ub in zip(r["new_balances"], user_boxes):
            if new_balance>ub.balance:
                event_list.append(
                    ub.increment_to_balance(new_balance)
                )
                pot_amount=0
                event_list.append(
                    event.DrawTextEvent(
                        f"{pot_amount}",
                        constants.POT_TEXT_X,
                        constants.POT_TEXT_Y,
                        constants.POT_TEXT_WIDTH,
                        constants.POT_TEXT_HEIGHT,
                        constants.POT_TEXT_COLOUR)
                )
        event_list.append(
            event.SimultaniousDrawEvent(
                [ub.write_probability(None) for ub in user_boxes] +
                   [
                        ub.write_bet_amount(0) for ub in user_boxes
                    ]

            )
        )
        all_card_positions =[]
        for ub, fold in zip(user_boxes, folded):
            if not fold:
                player_card_positions = ub.get_card_positions()
                all_card_positions+=player_card_positions
        for i, community_card in enumerate(r['community_cards']):
            all_card_positions.append(constants.COMMUNITY_POSITIONS[i])
        event_list.append(event.MassGlideAndStayAnimation(
            all_card_positions,
            [constants.MUCK_POSITION] * len(all_card_positions),
            [res.card_back_resource] * len(all_card_positions),
            constants.MUCK_PACE
            )
        )
        event_list.append(
            event.GlideEvent(
                *constants.MUCK_POSITION,
                constants.DESIGN_WIDTH//2,
                0,
                constants.COMMUNITY_CARD_DEAL_PACE,
                res.card_back_resource,
                False,
                clear_source=True
            )
        )


    return event_list




