"""The module defines the RepositoryCommits class, which formulates the GraphQL query string
to extract all the commits made to a repository's default branch."""

from typing import Dict, Optional
from app.github_query.github_graphql.query import (
    QueryNode,
    PaginatedQuery,
    QueryNodePaginator,
)


class RepositoryCommits(PaginatedQuery):
    """
    RepositoryCommits is a subclass of PaginatedQuery specifically designed to fetch commits to a given repository.
    It includes authoredDate, changedFilesIfAvailable, additions, deletions,  and message.
    It locates the repository base on the owner GitHub ID and the repository's name.
    """

    def __init__(self) -> None:
        """Initializes a paginated query for repository commits with specific fields and pagination controls."""
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
                                                                # Date when the commit was authored
                                                                "authoredDate",
                                                                # Number of files changed, if available
                                                                "changedFilesIfAvailable",
                                                                # Number of additions made in the commit
                                                                "additions",
                                                                # Number of deletions made in the commit
                                                                "deletions",
                                                                # Commit message
                                                                "message",
                                                                QueryNode(
                                                                    # Parent commits of the commit, limited to 2
                                                                    "parents (first: 2)",
                                                                    fields=[
                                                                        "totalCount"  # Total number of parent commits
                                                                    ],
                                                                ),
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
                                                                ),
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
    def commits_list(
        raw_data: Dict[str, Dict], cumulative_commits: Optional[Dict[str, Dict]] = None
    ) -> Dict[str, Dict]:
        """
        Processes the raw data from the GraphQL query to accumulate commit data per author.

        Args:
            raw_data: The raw data returned from the GraphQL query.
            cumulative_commits: Optional cumulative commits dictionary to accumulate results.

        Returns:
            A dictionary of cumulative commit data per author, with details like total additions, deletions,
            file changes, and commits.
        """
        nodes = (
            raw_data.get("repository", {})
            .get("defaultBranchRef", {})
            .get("target", {})
            .get("history", {})
            .get("nodes", [])
        )
        if cumulative_commits is None:
            cumulative_commits = {}

        # Process each commit node to accumulate data
        for node in nodes:
            # Consider only commits with less than 2 parents (usually mainline commits)
            if node.get("parents", {}).get("totalCount", 0) < 2:
                name = node.get("author", {}).get("name", "")
                login = node.get("author", {}).get("user", {}).get("login", "")
                additions = node.get("additions", 0)
                deletions = node.get("deletions", 0)
                files = node.get("changedFilesIfAvailable", 0)
                if name not in cumulative_commits:
                    if login:
                        cumulative_commits[name] = {
                            login: {
                                "total_additions": additions,
                                "total_deletions": deletions,
                                "total_files": files,
                                "total_commits": 1,
                            }
                        }
                    else:
                        cumulative_commits[name] = {
                            "total_additions": additions,
                            "total_deletions": deletions,
                            "total_files": files,
                            "total_commits": 1,
                        }
                else:  # name in cumulative_commits
                    if login:
                        if login in cumulative_commits[name]:
                            cumulative_commits[name][login][
                                "total_additions"
                            ] += additions
                            cumulative_commits[name][login][
                                "total_deletions"
                            ] += deletions
                            cumulative_commits[name][login]["total_files"] += files
                            cumulative_commits[name][login]["total_commits"] += 1
                        else:  # login not in cumulative_commits[name]
                            cumulative_commits[name][login] = {
                                "total_additions": additions,
                                "total_deletions": deletions,
                                "total_files": files,
                                "total_commits": 1,
                            }
                    else:  # no login
                        if "total_additions" in cumulative_commits[name]:
                            cumulative_commits[name]["total_additions"] += additions
                            cumulative_commits[name]["total_deletions"] += deletions
                            cumulative_commits[name]["total_files"] += files
                            cumulative_commits[name]["total_commits"] += 1
                        else:
                            cumulative_commits[name]["total_additions"] = additions
                            cumulative_commits[name]["total_deletions"] = deletions
                            cumulative_commits[name]["total_files"] = files
                            cumulative_commits[name]["total_commits"] = 1
        return cumulative_commits
