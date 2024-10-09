"""The module defines the UserRepositories class, which formulates the GraphQL query string
to extract repositories created by the user based on a given user ID."""

from typing import Dict, Any, List
from app.github_query.github_graphql.query import (
    QueryNode,
    PaginatedQuery,
    QueryNodePaginator,
)
from app.github_query.queries.constants import (
    NODE_USER,
    FIELD_NAME,
    FIELD_TOTAL_COUNT,
    FIELD_SIZE,
    FIELD_END_CURSOR,
    FIELD_HAS_NEXT_PAGE,
    NODE_REPOSITORIES,
    NODE_LANGUAGES,
    NODE_EDGES,
    NODE_NODE,
    NODE_NODES,
    NODE_PAGE_INFO,
    ARG_LOGIN,
    ARG_FIRST,
    ARG_IS_FORK,
    ARG_OWNER_AFFILIATIONS,
    ARG_ORDER_BY,
    ARG_FIELD,
    ARG_DIRECTION,
)


class UserRepositories(PaginatedQuery):
    """
    UserRepositories is a class for querying a user's repositories including details like language statistics,
    fork count, stargazer count, etc. It extends PaginatedQuery to handle potentially large numbers of repositories.
    """

    def __init__(
        self,
        login: str,
        is_fork: bool = False,
        ownership: str = "[OWNER]",
        pg_size: int = 10,
        repo_order_field: str = "CREATED_AT",
        repo_order_dir: str = "DESC",
        lag_order_field: str = "SIZE",
        lag_order_dir: str = "DESC",
    ) -> None:
        """
        Initializes a query for a user's repositories with various filtering and ordering options.
        """
        super().__init__(
            fields=[
                QueryNode(
                    NODE_USER,
                    args={ARG_LOGIN: login},
                    fields=[
                        QueryNodePaginator(
                            NODE_REPOSITORIES,
                            args={
                                ARG_FIRST: pg_size,
                                ARG_IS_FORK: is_fork,
                                ARG_OWNER_AFFILIATIONS: ownership,
                                ARG_ORDER_BY: {
                                    ARG_FIELD: repo_order_field,
                                    ARG_DIRECTION: repo_order_dir,
                                },
                            },
                            fields=[
                                FIELD_TOTAL_COUNT,
                                QueryNode(
                                    NODE_NODES,
                                    fields=[
                                        QueryNode(
                                            NODE_LANGUAGES,
                                            args={
                                                ARG_FIRST: 100,
                                                ARG_ORDER_BY: {
                                                    ARG_FIELD: lag_order_field,
                                                    ARG_DIRECTION: lag_order_dir,
                                                },
                                            },
                                            fields=[
                                                FIELD_TOTAL_COUNT,
                                                QueryNode(
                                                    NODE_EDGES,
                                                    fields=[
                                                        FIELD_SIZE,
                                                        QueryNode(
                                                            NODE_NODE,
                                                            fields=[FIELD_NAME],
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                                QueryNode(
                                    NODE_PAGE_INFO,
                                    fields=[FIELD_END_CURSOR, FIELD_HAS_NEXT_PAGE],
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
