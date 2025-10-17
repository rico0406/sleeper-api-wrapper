from typing import List, Dict, Tuple, Optional, Any
from .base_api import BaseApi
from .stats import Stats


class League(BaseApi):
    def __init__(self, league_id):
        self.league_id = league_id
        self._base_url = "https://api.sleeper.app/v1/league/{}".format(self.league_id)
        self._league = self._call(self._base_url)

    def get_league(self):
        return self._league

    def get_rosters(self):
        return self._call("{}/{}".format(self._base_url, "rosters"))

    def get_users(self):
        return self._call("{}/{}".format(self._base_url, "users"))

    def get_matchups(self, week):
        return self._call("{}/{}/{}".format(self._base_url, "matchups", week))

    def get_playoff_winners_bracket(self):
        return self._call("{}/{}".format(self._base_url, "winners_bracket"))

    def get_playoff_losers_bracket(self):
        return self._call("{}/{}".format(self._base_url, "losers_bracket"))

    def get_transactions(self, week):
        return self._call("{}/{}/{}".format(self._base_url, "transactions", week))

    def get_traded_picks(self):
        return self._call("{}/{}".format(self._base_url, "traded_picks"))

    def get_all_drafts(self):
        return self._call("{}/{}".format(self._base_url, "drafts"))

    def map_users_to_team_name(self, users):
        """ returns dict {user_id:team_name}"""
        users_dict = {}

        # Maps the user_id to team name for easy lookup
        for user in users:
            try:
                users_dict[user["user_id"]] = user["metadata"]["team_name"]
            except:
                users_dict[user["user_id"]] = user["display_name"]
        return users_dict

    def get_standings(self, rosters, users):
        users_dict = self.map_users_to_team_name(users)

        roster_standings_list = []
        for roster in rosters:
            wins = roster["settings"]["wins"]
            points = roster["settings"]["fpts"]
            name = roster["owner_id"]
            losses = roster["settings"]["losses"]
            if name is not None:
                roster_tuple = (wins, losses, points, users_dict[name])
            else:
                roster_tuple = (wins, losses, points, None)
            roster_standings_list.append(roster_tuple)

        roster_standings_list.sort(reverse=1)

        clean_standings_list = []
        for item in roster_standings_list:
            clean_standings_list.append((item[3], str(item[0]), str(item[1]), str(item[2])))

        return clean_standings_list

    def map_rosterid_to_ownerid(self, rosters):
        """returns: dict {roster_id:[owner_id,pts]} """
        result_dict = {}
        for roster in rosters:
            roster_id = roster["roster_id"]
            owner_id = roster["owner_id"]
            result_dict[roster_id] = owner_id

        return result_dict

    def get_scoreboards(
            self,
            rosters: List[Dict],
            matchups: List[Dict],
            users: List[Dict]
    ) -> Optional[Dict[int, List[Tuple[str, float]]]]:
        """
        Returns a list of matchups in a JSON-like format containing both teams'
        names and scores for each game.

        Args:
            rosters (List[Dict]): List of roster objects from Sleeper API.
            matchups (List[Dict]): List of matchup objects from Sleeper API.
            users (List[Dict]): List of user objects from Sleeper API.

		Returns:
            Optional[List[Dict[str, object]]]:
                A list of dictionaries, each representing one matchup with keys:
                - "matchup_id" (int)
                - "team_a_name" (str)
                - "team_a_points" (float)
                - "team_b_name" (str)
                - "team_b_points" (float)

                Returns None if there are no matchups.

        Notes:
            - The score for each team is obtained directly from the `points` field in the matchup object.
            - If the `points` field is None, it defaults to 0.
            - Teams without a mapped owner will show "Team name not available".
        """


        if len(matchups) == 0:
            return None

        roster_id_dict = self.map_rosterid_to_ownerid(rosters)

        # Get the users to team name stats
        users_dict = self.map_users_to_team_name(users)

        # map roster_id to points
        scoreboards_dict = {}

        for team in matchups:
            matchup_id = team["matchup_id"]
            current_roster_id = team["roster_id"]
            owner_id = roster_id_dict[current_roster_id]
            if owner_id is not None:
                team_name = users_dict[owner_id]
            else:
                team_name = "Team name not available"

            team_score = team["points"]
            if team_score is None:
                team_score = 0

            team_score_tuple = (team_name, team_score)
            if matchup_id not in scoreboards_dict:
                scoreboards_dict[matchup_id] = [team_score_tuple]
            else:
                scoreboards_dict[matchup_id].append(team_score_tuple)
        return scoreboards_dict

    def get_scoreboards_json(
            self, rosters: List[Dict],
            matchups: List[Dict],
            users: List[Dict]
    ) -> List[Dict[str, Any]]:
        """
        Returns the scoreboard in a JSON-friendly format.

        Args:
            rosters (List[Dict]): List of roster objects from Sleeper API.
            matchups (List[Dict]): List of matchup objects from Sleeper API.
            users (List[Dict]): List of user objects from Sleeper API.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing a matchup with:
                - matchup_id (int)
                - team_a_name (str)
                - team_a_points (float)
                - team_b_name (str)
                - team_b_points (float)

        Notes:
            - Uses get_scoreboards() internally to preserve original logic.
            - If there is a matchup with only one team (e.g., bye week), team_b fields will be None.
        """
        raw_scoreboards = self.get_scoreboards(rosters, matchups, users)
        if not raw_scoreboards:
            return []

        json_friendly_list = []
        for matchup_id, teams in raw_scoreboards.items():
            team_a_name = teams[0][0]
            team_a_points = teams[0][1]
            if len(teams) > 1:
                team_b_name = teams[1][0]
                team_b_points = teams[1][1]
            else:
                team_b_name = None
                team_b_points = None

            json_friendly_list.append({
                "matchup_id": matchup_id,
                "team_a_name": team_a_name,
                "team_a_points": team_a_points,
                "team_b_name": team_b_name,
                "team_b_points": team_b_points
            })

        return json_friendly_list


    def get_close_games(self, scoreboards, close_num):
        """ -Notes: Need to find a better way to compare scores rather than abs value of the difference of floats. """
        close_games_dict = {}
        for key in scoreboards:
            team_one_score = scoreboards[key][0][1]
            team_two_score = scoreboards[key][1][1]

            if abs(team_one_score - team_two_score) < close_num:
                close_games_dict[key] = scoreboards[key]
        return close_games_dict

    def get_team_score(self, starters, score_type, week):
        total_score = 0
        stats = Stats()
        week_stats = stats.get_week_stats("regular", 2019, week)
        for starter in starters:
            if stats.get_player_week_stats(week_stats, starter) is not None:
                try:
                    total_score += stats.get_player_week_stats(week_stats, starter)[score_type]
                except KeyError:
                    total_score += 0

        return total_score

    def empty_roster_spots(self):
        pass

    def get_negative_scores(self, week):
        pass

    def get_rosters_players(self):
        pass
