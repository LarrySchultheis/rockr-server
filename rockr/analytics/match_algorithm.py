from rockr import db_manager
from rockr.models import (
    User,
    UserInstrument,
    UserMusicalInterest,
    UserGoal,
    UserMatch,
)

INSTRUMENT_MULTIPLIER = 0.4
INTEREST_MULTIPLIER = 0.3
GOAL_MULTIPLIER = 0.3


def match_algorithm(user_id):
    matches = []
    # delete all unseen matches for this user
    um = UserMatch.query.filter_by(user_id=user_id, seen=False)
    for m in um:
        db_manager.delete(m)

    user_instrument_ids = {
        i.instrument_id for i in UserInstrument.query.filter_by(user_id=user_id).all()
    }
    user_interest_ids = {
        i.interest_id
        for i in UserMusicalInterest.query.filter_by(user_id=user_id).all()
    }
    user_goal_ids = {g.goal_id for g in UserGoal.query.filter_by(user_id=user_id).all()}

    # user must have a complete match profile
    if (
        len(user_instrument_ids) < 1
        or len(user_interest_ids) < 1
        or len(user_goal_ids) < 1
    ):
        return []

    potential_match_users = User.query.filter(
        User.is_paused == False, User.id != user_id
    ).all()

    for user in potential_match_users:
        existing_match = UserMatch.query.filter_by(user_id=user_id, match_id=user.id).first()
        if existing_match:
            continue

        match_user_instrument_ids = {
            i.instrument_id
            for i in UserInstrument.query.filter_by(user_id=user.id)
        }
        match_user_interests_ids = {
            i.interest_id
            for i in UserMusicalInterest.query.filter_by(user_id=user.id)
        }
        match_user_goal_ids = {
            i.goal_id for i in UserGoal.query.filter_by(user_id=user.id).all()
        }

        if (
                len(match_user_instrument_ids) < 1
                or len(match_user_interests_ids) < 1
                or len(match_user_goal_ids) < 1
        ):
            continue

        # get counts
        common_instrument_match_count = len(
            user_instrument_ids & match_user_instrument_ids
        )
        common_interest_match_count = len(user_interest_ids & match_user_interests_ids)
        common_goals_match_count = len(user_goal_ids & match_user_goal_ids)

        # calculate scores
        instrument_score = (
            common_instrument_match_count * 1.0 / len(match_user_instrument_ids)
        ) * INSTRUMENT_MULTIPLIER
        interest_score = (
            common_interest_match_count * 1.0 / len(match_user_interests_ids)
        ) * INTEREST_MULTIPLIER
        goal_score = (
            common_goals_match_count * 1.0 / len(match_user_goal_ids)
        ) * GOAL_MULTIPLIER

        match_score = 1 - (instrument_score + interest_score + goal_score) / 100
        new_match = UserMatch(user_id=user_id, match_id=user.id)
        db_manager.insert(new_match)
        matches.append((new_match, match_score))

    return sorted(matches, key=lambda m: m[1], reverse=True)
