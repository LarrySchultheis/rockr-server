from flask import request
from rockr import db, auth, app, db_manager
from rockr.models import (
    User,
    MatchProfile,
    UserInstrument,
    UserMusicalInterest,
    UserGoal,
)


# input should be an array of instrument ids, array of music interest ids, and array of goal ids,
# most likely inputted through what the logged in user has, but also individually to test it on its own
def match_algorithm(instrumentids, musicinterestids, goalids):
    # List to store the matched tuples
    matches_tuple_list = []

    # numbers for the match score percentage, for us to edit these more easily.
    instrument_multiplier = 0.4
    music_interest_multiplier = 0.3
    goals_multiplier = 0.3

    # Get all the users for the Algorithm to sort through, that are not admins, are active, and are not bands
    match_users = User.query.filter_by(
        is_admin=False, is_active=True, is_band=False
    ).all()
    # Loop through the returned users
    for matched_user in match_users:
        # Find the ID of each one to look through the User Tables
        match_user_id = matched_user.id

        # variables for the match score totals For each User
        instrument_score = 0.0
        music_interest_score = 0.0
        goals_score = 0.0
        match_score = 0.0

        # numbers for the number of matches found.
        instrument_match_count = 0.0
        music_interest_match_count = 0.0
        goals_match_count = 0.0

        # In case the instrument IDs inputted array is empty, default score to 0.0
        if len(instrumentids) == 0:
            instrument_score = 0.0
            instrument_match_count = 0.0
        else:
            # Loop through the Instrument IDs inputted, query to see if one with the matched user's ID and Instrument ID shows up
            # Increment for each one found, then divide the total matched by the length and multiply by the multiplier
            # just get the first one to make there less to loop through, reducing time.
            for instrumentid in instrumentids:
                match_instruments = UserInstrument.query.filter_by(
                    id=match_user_id, instrument_id=instrumentid
                ).first()
                if match_instruments is None:
                    instrument_match_count = instrument_match_count + 0.0
                else:
                    instrument_match_count = instrument_match_count + 1.0
            # Get the percentage total
            instrument_score = instrument_match_count / len(instrumentids)
            instrument_score = instrument_score * instrument_multiplier

        # In case the Music Interest IDs inputted array is empty, default score to 0.0
        if len(musicinterestids) == 0:
            music_interest_score = 0.0
            music_interest_match_count = 0.0
        else:
            # Loop through the Music Interest IDs inputted, query to see if one with the matched user's ID and Music Interest ID shows up
            # Increment for each one found, then divide the total matched by the length and multiply by the multiplier
            # just get the first one to make there less to loop through, reducing time.
            for musicinterestid in musicinterestids:
                match_music_interest = UserMusicalInterest.query.filter_by(
                    id=match_user_id, interest_id=musicinterestid
                ).first()
                if match_music_interest is None:
                    music_interest_match_count = music_interest_match_count + 0.0
                else:
                    music_interest_match_count = music_interest_match_count + 1.0
            # Get the percentage total
            music_interest_score = music_interest_match_count / len(musicinterestids)
            music_interest_score = music_interest_score * music_interest_multiplier

        # In case the goal IDs inputted array is empty, default score to 0.0
        if len(goalids) == 0:
            goals_score = 0.0
            goals_match_count = 0.0
        else:
            # Loop through the Goal IDs inputted, query to see if one with the matched user's ID and goal ID shows up
            # Increment for each one found, then divide the total matched by the length and multiply by the multiplier
            # just get the first one to make there less to loop through, reducing time.
            for goalid in goalids:
                match_goal = UserGoal.query.filter_by(
                    id=match_user_id, goal_id=goalid
                ).first()
                if match_goal is None:
                    goals_match_count = goals_match_count + 0.0
                else:
                    goals_match_count = goals_match_count + 1.0
            # Get the percentage total
            goals_score = goals_match_count / len(goalids)
            goals_score = goals_score * goals_multiplier

        # total them up after getting the individual scores
        match_score = instrument_score + music_interest_score + goals_score
        # create tuple of the user information to be returned, making the match score first so it can be sorted easily
        match_tuple = (
            match_score,
            matched_user.id,
            matched_user.username,
            matched_user.first_name,
            matched_user.last_name,
        )
        # append to the list
        matches_tuple_list.append(match_tuple)

    # after matches are found, sort by match_score. Since match_score is the first tuple element, makes sorting easier
    matches_tuple_list.sort(reverse=True)
    return matches_tuple_list
