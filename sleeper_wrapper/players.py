from .base_api import BaseApi
from typing import  Optional, List

class Players(BaseApi):


	def __init__(self):
		pass

	def get_all_players(self):
		return self._call("https://api.sleeper.app/v1/players/nfl")

	def get_trending_players(self,sport, add_drop, hours=24, limit=25 ):
		return self._call("https://api.sleeper.app/v1/players/{}/trending/{}?lookback_hours={}&limit={}".format(sport, add_drop, hours, limit))


	def get_players_ownership(
			self,
			season_type: str,
			season: int,
			week: Optional[int] = None
	) -> List[dict]:

		"""
			Retrieve ownership and rostering information for NFL players.

			Args:
				season_type (str): Type of season: 'pre', 'regular', 'post', or 'off'.
				season (int): 4-digit season year (e.g., 2022).
				week (Optional[int], optional): Week number to filter results. Defaults to None.

			Returns:
				List[dict]: List of player ownership/rostering info objects.

			Example:
				Players().get_player_ownership('regular', 2024, 5)
        """

		# Construct URL based on whether week is provided
		url = f"https://api.sleeper.com/players/nfl/research/{season_type}/{season}"
		if week is not None:
			url += f"/{week}"

		return self._call(url)

