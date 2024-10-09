"""
This module provides the `UserMetricsMiner` class, which is responsible for collecting and processing GitHub metric 
data for a user. The class utilizes various GitHub GraphQL queries to fetch user profile statistics, repositories,
and contributions over a specified time range.
"""

import logging
from datetime import datetime
from collections import Counter
from typing import List, Dict, Any, Set, Tuple
import numpy as np
import app.github_query.utils.helper as helper
from app.github_query.github_graphql.client import QueryFailedException
from app.github_query.queries.profiles import UserProfileStats
from app.github_query.queries.repositories import UserRepositories
from app.github_query.queries.time_range_contributions import (
    UserContributionsCollection,
)


class UserMetricsMiner:
    """
    Class to collect GitHub metric data for a user.
    """

    def __init__(self, client):
        self._client = client
        self.profile_stats = {}
        self.user_owned_repo = []
        self.commits = {}
        self.exceptions = []

    def fetch_user_profile_stats(self, login: str) -> None:
        """
        Fetch user profile stats.

        Args:
            login (str): The user login.

        Returns:
            None
        """
        try:
            response = self._client.execute(query=UserProfileStats(login=login))
            self.profile_stats = UserProfileStats.profile_stats(response)
        except QueryFailedException as e:
            logging.error("Query failed for user %s: %s", login, e)
            self.exceptions.append(login + " DNE")
            self.profile_stats = None

    def fetch_user_contributions(self, login: str, start: str, end: str) -> Counter:
        """
        Fetch user contributions between start and end dates.

        Args:
            login (str): The user login.
            start (str): The start date.
            end (str): The end date.

        Returns:
            None
        """
        contributions = Counter({"res_con": 0, "commit": 0, "pr_review": 0})
        period_end = helper.add_by_days(start, 365)

        try:
            while start < end:
                if period_end > end:
                    period_end = end
                response = self._client.execute(
                    query=UserContributionsCollection(
                        login=login, start=f'"{start}"', end=f'"{period_end}"'
                    )
                )
                queried_contribution = (
                    UserContributionsCollection.user_contributions_collection(response)
                )
                for key in contributions:
                    contributions[key] += queried_contribution[key]
                start = period_end
                period_end = helper.add_by_days(start, 365)
            self.commits = contributions
        except QueryFailedException as e:
            logging.error("Error fetching contributions for user %s: %s", login, e)
            self.exceptions.append(f"Error fetching contributions for {login}: {e}")
            self.commits = Counter({"res_con": 0, "commit": 0, "pr_review": 0})

    def fetch_user_repositories(self, login: str):
        """
        Fetch user repositories based on the given criteria.
        Args:
            login (str): The user login to substitute in the query.

        Returns:
            None
        """
        try:
            repositories = []
            for response in self._client.execute(query=UserRepositories(login=login)):
                repositories += UserRepositories.user_repositories(response)
            self.user_owned_repo = repositories
        except QueryFailedException as e:
            logging.error("Error fetching owned repo for user %s: %s", login, e)
            self.exceptions.append(f"Error fetching owned repo for {login}: {e}")
            self.user_owned_repo = []

    def calculate_lifetime(self, created_at: str) -> int:
        """
        Calculate the GitHub account life span.
        Args:
            created_at: The creation date of the GitHub account.
        Returns:
            The lifespan in days.
        """
        try:
            gh_start = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
            gh_end = datetime.now()
            return (gh_end - gh_start).days
        except ValueError as e:
            logging.error("Error parsing date %s: %s", created_at, e)
            return 0

    def calculate_language_statistics(self, langs: Set[str]):
        """
        Calculate language statistics for the user's repositories.

        Args:
            langs (Set[str]): A set of languages to calculate statistics for.

        Returns:
            Tuple[int, int]: A tuple containing the number of unique languages and the total size of popular languages.
        """
        user_langs = set()
        lang_size = self.calculate_repo_language_size(
            self.user_owned_repo, langs, user_langs
        )
        return len(user_langs), lang_size

    def calculate_repo_language_size(
        self, repos: List[Dict[str, Any]], langs: Set[str], lang_set: Set[str]
    ) -> int:
        """
        Calculate the size of languages in a repository.
        Args:
            repos: The list of repositories.
            pop_lang: The set of popular languages.
            l_set: The set to store all languages.
        Returns:
            The total size of popular languages.
        """
        size = 0
        for repo in repos:
            languages = repo["languages"]
            for language in languages["edges"]:
                lang = language["node"]["name"]
                lsize = language["size"]
                if lang in langs:
                    size += lsize
                lang_set.add(lang)
        return size

    def fetch_user_contributions_data(
        self, login: str, created_at: str
    ) -> Tuple[int, int, int, int, int]:
        """
        Fetch user contributions data.
        Args:
            login (str): user GitHub account
            created_at (str): The creation date of the GitHub account.
        Returns:
            A tuple containing commits, comments, pull requests, issues, and repositories count.
        """
        gh_start = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
        gh_end = datetime.now()
        end = gh_end.strftime("%Y-%m-%dT%H:%M:%SZ")
        start = gh_start.strftime("%Y-%m-%dT%H:%M:%SZ")
        self.fetch_user_contributions(login, start, end)
        commits = self.commits["commit"]
        comments = (
            self.profile_stats["commit_comments"]
            + self.profile_stats["issue_comments"]
            + self.profile_stats["gist_comments"]
            + self.profile_stats["repository_discussion_comments"]
        )
        pr = self.commits["pr_review"] + self.profile_stats["pull_requests"]
        issues = self.profile_stats["issues"]
        repoc = self.profile_stats["repositories"]
        return commits, comments, pr, issues, repoc

    def mine(self, login: str, pop_lang: Set[str]):
        """
        Mines user metrics by fetching and calculating various statistics.

        Args:
            login (str): The user's login.
            pop_lang (Set): The list of interested languages.

        Returns:
            list: A list of user metrics.
        """
        self.fetch_user_profile_stats(login)
        created_at = self.profile_stats["created_at"]

        lifetime = self.calculate_lifetime(created_at)
        self.fetch_user_repositories(login)

        l_count, pop_lang_size = self.calculate_language_statistics(pop_lang)
        commits, comments, pr, issues, repoc = self.fetch_user_contributions_data(
            login, created_at
        )

        return [
            login,
            lifetime,
            commits,
            comments,
            pr + issues,
            l_count,
            np.log10(pop_lang_size + 1),
            repoc,
        ]
