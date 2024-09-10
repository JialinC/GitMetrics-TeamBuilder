"""The module defines the RepositoryContributors class, which formulates the GraphQL query string
to extract all contibutors to a repository's default branch."""

from typing import Dict, Set, Optional
from app.github_query.github_graphql.query import (
    QueryNode,
    PaginatedQuery,
    QueryNodePaginator,
)


class RepositoryContributors(PaginatedQuery):
    """
    RepositoryContributors is a subclass of PaginatedQuery specifically designed to fetch contributors' information to
    of a given repository's default branch.
    It locates the repository base on the owner GitHub ID and the repository's name.
    """

    def __init__(self):
        super().__init__(
            fields=[
                QueryNode(
                    "repository",
                    args={
                        "owner": "$owner",
                        "name": "$repo_name",
                    },  # Query arguments for specifying the repository
                    fields=[
                        QueryNode(
                            "defaultBranchRef",  # Points to the default branch of the repository
                            fields=[
                                QueryNode(
                                    "target",
                                    fields=[
                                        QueryNode(
                                            "... on Commit",  # Inline fragment on Commit type
                                            fields=[
                                                QueryNodePaginator(
                                                    "history",  # Paginated history of commits
                                                    args={
                                                        "first": "$pg_size"
                                                    },  # Pagination control arguments
                                                    fields=[
                                                        "totalCount",  # Total number of commits in the history
                                                        QueryNode(
                                                            "nodes",  # List of commit nodes
                                                            fields=[
                                                                QueryNode(
                                                                    "author",  # Author of the commit
                                                                    fields=[
                                                                        "name",  # Name of the author
                                                                        "email",  # Email of the author
                                                                        QueryNode(
                                                                            "user",  # User associated with the author
                                                                            fields=[
                                                                                "login"  # Login of the user
                                                                            ],
                                                                        ),
                                                                    ],
                                                                )
                                                            ],
                                                        ),
                                                        QueryNode(
                                                            "pageInfo",  # Information about pagination
                                                            fields=[
                                                                "endCursor",
                                                                "hasNextPage",
                                                            ],
                                                        ),
                                                    ],
                                                )
                                            ],
                                        )
                                    ],
                                )
                            ],
                        )
                    ],
                )
            ]
        )

    @staticmethod
    def extract_unique_author(
        raw_data: Dict[str, Dict], unique_authors: Optional[Dict[str, Set[str]]] = None
    ) -> Dict[str, Set[str]]:
        """
        Processes the raw data from the GraphQL query to extract unique authors from the repository's commit history.

        Args:
            raw_data: The raw data returned from the GraphQL query.
            unique_authors: An optional dictionary to accumulate unique authors' names and logins.

        Returns:
            A dictionary containing sets of unique author names and logins.
        """
        nodes = (
            raw_data.get("repository", {})
            .get("defaultBranchRef", {})
            .get("target", {})
            .get("history", {})
            .get("nodes", [])
        )
        if unique_authors is None:
            unique_authors = {"name": set(), "login": set()}

        # Process each commit node to accumulate unique author data
        for node in nodes:
            author = node["author"]
            name = author["name"]
            login = author["user"]["login"] if author["user"] else None

            if name:
                unique_authors["name"].add(name)
            if login:
                unique_authors["login"].add(login)

        return unique_authors
