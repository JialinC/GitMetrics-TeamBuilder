"""The module defines the UserRepositories class, which formulates the GraphQL query string
to extract repositories created by the user based on a given user ID."""

from typing import Dict, Any, List
from app.github_query.utils.helper import (
    created_before,
    created_after,
    in_time_period,
)
from app.github_query.github_graphql.query import (
    QueryNode,
    PaginatedQuery,
    QueryNodePaginator,
)


class UserRepositories(PaginatedQuery):
    """
    UserRepositories is a class for querying a user's repositories including details like language statistics,
    fork count, stargazer count, etc. It extends PaginatedQuery to handle potentially large numbers of repositories.
    """

    def __init__(self) -> None:
        """
        Initializes a query for a user's repositories with various filtering and ordering options.
        """
        super().__init__(
            fields=[
                QueryNode(
                    "user",
                    args={"login": "$user"},
                    fields=[
                        QueryNodePaginator(
                            "repositories",
                            args={
                                "first": "$pg_size",
                                "isFork": "$is_fork",
                                "ownerAffiliations": "$ownership",
                                "orderBy": "$order_by",
                            },
                            fields=[
                                "totalCount",
                                QueryNode(
                                    "nodes",
                                    fields=[
                                        "name",
                                        "isEmpty",
                                        "createdAt",
                                        "updatedAt",
                                        "forkCount",
                                        "stargazerCount",
                                        QueryNode("watchers", fields=["totalCount"]),
                                        QueryNode("primaryLanguage", fields=["name"]),
                                        QueryNode(
                                            "languages",
                                            args={
                                                "first": 100,
                                                "orderBy": {
                                                    "field": "SIZE",
                                                    "direction": "DESC",
                                                },
                                            },
                                            fields=[
                                                "totalSize",
                                                QueryNode(
                                                    "edges",
                                                    fields=[
                                                        "size",
                                                        QueryNode(
                                                            "node", fields=["name"]
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                                QueryNode(
                                    "pageInfo", fields=["endCursor", "hasNextPage"]
                                ),
                            ],
                        ),
                    ],
                )
            ]
        )

    @staticmethod
    def user_repositories(raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extracts and returns the list of repositories from the raw GraphQL query response data.

        Args:
            raw_data: The raw data returned by the GraphQL query.

        Returns:
            A list of dictionaries, each containing data about a single repository.
        """
        repositories = raw_data.get("user", {}).get("repositories", {}).get("nodes", [])
        return repositories

    @staticmethod
    def cumulated_repository_stats(
        repo_list: List[Dict[str, Any]],
        repo_stats: Dict[str, int],
        lang_stats: Dict[str, int],
        start: str,
        end: str,
        direction: str,
    ) -> None:
        """
        Aggregates statistics for repositories created before, after a certain time or in between a time range.

        Args:
            repo_list: List of repositories to be analyzed.
            repo_stats: Dictionary accumulating various statistics like total count, fork count, etc.
            lang_stats: Dictionary accumulating language usage statistics.
            start: String representing the start time for consideration of repositories.
            end: String representing the end time for consideration of repositories.
            direction: Specify whether to aggregates statistics for repositories created before,
            after a certain time or in between a time range.

        Returns:
            None: Modifies the repo_stats and lang_stats dictionaries in place.
        """
        for repo in repo_list:
            created_at = repo["createdAt"]
            if direction == "before" and not created_before(created_at, start):
                continue
            elif direction == "after" and not created_after(created_at, start):
                continue
            elif direction == "between" and not in_time_period(created_at, start, end):
                continue

            languages = repo["languages"]
            if languages["totalSize"] == 0:
                continue
            repo_stats["total_count"] = repo_stats.get("total_count", 0) + 1
            repo_stats["fork_count"] = (
                repo_stats.get("fork_count", 0) + repo["forkCount"]
            )
            repo_stats["stargazer_count"] = (
                repo_stats.get("stargazer_count", 0) + repo["stargazerCount"]
            )
            repo_stats["watchers_count"] = (
                repo_stats.get("watchers_count", 0) + repo["watchers"]["totalCount"]
            )
            repo_stats["total_size"] = (
                repo_stats.get("total_size", 0) + languages["totalSize"]
            )
            language_list_sorted = sorted(
                languages["edges"], key=lambda s: s["size"], reverse=True
            )
            if language_list_sorted:
                for language in language_list_sorted:
                    name = language["node"]["name"]
                    size = language["size"]
                    lang_stats[name] = lang_stats.get(name, 0) + int(size)
