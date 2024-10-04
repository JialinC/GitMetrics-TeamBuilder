# Standard library imports
from datetime import datetime
from collections import Counter

# Third-party imports s
# import pandas as pd

# Local application imports
import app.github_query.utils.helper as helper
from app.github_query.github_graphql.client import Client, QueryFailedException

# User profiles queries
from app.github_query.queries.profiles import UserProfileStats

# User contributions queries
from app.github_query.queries.contributions import UserRepositories

# Time range contributions queries
from app.github_query.queries.time_range_contributions import (
    UserContributionsCollection,
)


class UserMetricsMiner:
    """
    Helps mining user GitHub metrics data.
    """

    def __init__(self, client: Client):
        self._client = client
        self.exceptions = []
        self.profile_stats = {}

    def fetch_user_profile_stats(self, login):
        """
        Fetch user profile stats.

        Args:
            login (str): The user login.

        Returns:
            Counter: A counter of user contributions.
        """
        try:
            response = self._client.execute(
                query=UserProfileStats(), substitutions={"user": login}
            )
            profile_stats = UserProfileStats.profile_stats(response)
            setattr(self, "profile_stats", profile_stats)
        except QueryFailedException:
            self.exceptions.append(login + " DNE")
            return

    def fetch_user_contributions(self, login, start, end):
        """
        Fetch user contributions between start and end dates.

        Args:
            login (str): The user login.
            start (datetime): The start date.
            end (datetime): The end date.

        Returns:
            Counter: A counter of user contributions.
        """
        contributions = Counter({"res_con": 0, "commit": 0, "pr_review": 0})
        period_end = helper.add_by_days(start, 365)

        while start < end:
            if period_end > end:
                period_end = end
            response = self._client.execute(
                query=UserContributionsCollection(),
                substitutions={"user": login, "start": start, "end": period_end},
            )
            queried_contribution = (
                UserContributionsCollection.user_contributions_collection(response)
            )
            for key in contributions:
                contributions[key] += queried_contribution[key]
            start = period_end
            period_end = helper.add_by_days(start, 365)

        return contributions

    def fetch_user_repositories(self, attribute_name, login, is_fork, ownership):
        """
        Helper method to fetch user repositories and handle exceptions.

        Args:
            attribute_name (str): The name of the attribute to store the results.
            login (str): The user login to substitute in the query.
            is_fork (bool): Whether the repository is a fork.
            ownership (str): The ownership type of the repository.
        """
        try:
            repositories = []
            for response in self._client.execute(
                query=UserRepositories(),
                substitutions={
                    "user": login,
                    "pg_size": 100,
                    "is_fork": is_fork,
                    "ownership": ownership,
                    "order_by": {"field": "CREATED_AT", "direction": "ASC"},
                },
            ):
                repositories += UserRepositories.user_repositories(response)
            setattr(self, attribute_name, repositories)
        except QueryFailedException:
            self.exceptions.append(f"{login} {attribute_name}")
            return

    def mine(self, login: str):
        """
        Collect GitHub metric data for a user.
        Args:
            login: user GitHub account
        """
        # For this specific purpose, we can straightly use UserProfileStats query.
        # Beacuse we only care user contributions till now instead of a specific time range.
        # UserProfileStats query is enough to provide all the necessary information and it is faster.

        self.fetch_user_profile_stats(login)
        created_at = self.profile_stats["created_at"]
        print(created_at)
        # B = commitComments + issueComments + gistComments + repositoryDiscussionComments + repositoryDiscussions
        # C = PullRequestReviewContributions + pullRequests
        # D = Issues

        # lifespan bc['lifespan'] = pre_class_metrics['lifeSpan']
        now = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        gh_start = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
        print(gh_start)
        gh_end = datetime.now()  # datetime.strptime(now, "%Y-%m-%dT%H:%M:%SZ")
        print(gh_end)
        # Calculate the GtiHub account life span (lifespan)
        lifetime = gh_end - gh_start
        print(lifetime)

        # Fetch user repos using the helper method.
        # This still need to be fetched separately because general profile stats do not provide this info.
        # E = A lang numbers + C langs numbers + B lang numbers + D langs numbers bc['E']
        # F = A lang size + C lang size + B lang size + D lang size= bc['F']
        # G = ABCD_count = ['repoACount', 'repoBCount', 'repoCCount', 'repoDCount']
        # self.fetch_user_repositories("repo_A", login, False, "OWNER")
        # self.fetch_user_repositories("repo_B", login, True, "OWNER")
        # self.fetch_user_repositories("repo_C", login, False, "COLLABORATOR")
        # self.fetch_user_repositories("repo_D", login, True, "COLLABORATOR")

        # A = RestrictedContributionsCount + CommitContributionsbc
        # Fetch user number of private contributions and commits.
        # This can be done with time range contributions query.
        # Main logic
        # end = gh_end
        # start = gh_start
        # cumulated_contributions_collection = self.fetch_user_contributions(
        #     login, start, end
        # )
        # print(cumulated_contributions_collection)

    # def fetch_contributions(self, query_class, method_name, attribute_name, login):
    #     """
    #     Helper method to fetch various types of contributions and handle exceptions.
    #     When only need counts, this can be used to fetch all kinds of contributions.
    #     For contribution specific information, use the corresponding fetch method.

    #     Args:
    #         query_class (type): The class of the query to execute.
    #         method_name (str): The name of the method to call on the query class.
    #         attribute_name (str): The name of the attribute to store the results.
    #         login (str): The user login to substitute in the query.
    #     """
    #     try:
    #         setattr(self, attribute_name, [])
    #         for response in self._client.execute(
    #             query=query_class(), substitutions={"user": login, "pg_size": 100}
    #         ):
    #             method = getattr(query_class, method_name)
    #             getattr(self, attribute_name).extend(method(response))
    #     except QueryFailedException:
    #         self.exceptions.append(f"{login} {attribute_name}")
    #         return

    # def fetch_comments(self, query_class, method_name, attribute_name, login):
    #     """
    #     Helper method to fetch comments and handle exceptions.

    #     Args:
    #         query_class (type): The class of the query to execute.
    #         method_name (str): The name of the method to call on the query class.
    #         attribute_name (str): The name of the attribute to store the results.
    #         login (str): The user login to substitute in the query.
    #     """
    #     try:
    #         setattr(self, attribute_name, [])
    #         for response in self._client.execute(
    #             query=query_class(), substitutions={"user": login, "pg_size": 100}
    #         ):
    #             method = getattr(query_class, method_name)
    #             getattr(self, attribute_name).extend(method(response))
    #     except QueryFailedException:
    #         self.exceptions.append(f"{login} {attribute_name}")
    #         return
