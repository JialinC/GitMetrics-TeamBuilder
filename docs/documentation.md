<table>
<tr>
<th>GraphQL</th>
<th>Python</th>
</tr>
<tr>
<td>

```
query {
  viewer {
    login
  }
}
```

</td>
<td>

```python
class UserLoginViewer(Query):
    def __init__(self):
        super().__init__(
            fields=[
                QueryNode(
                    NODE_VIEWER,
                    fields=["login"]
                )
            ]
        )
```

</td>
</tr>
</table>

<table>
<tr>
<th>GraphQL</th>
<th>Python</th>
</tr>
<tr>
<td>

```
query {
    user(login: login) {
        login
        name
        id
        email
        createdAt
    }
}
```

</td>
<td>

```python
class UserLogin(Query):
    def __init__(self, login: str) -> None:
        super().__init__(
            fields=[
                QueryNode(
                    NODE_USER,
                    args={
                        ARG_LOGIN: login
                    },
                    fields=[
                        FIELD_LOGIN,
                        FIELD_NAME,
                        FIELD_ID,
                        FIELD_EMAIL,
                        FIELD_CREATED_AT,
                    ],
                )
            ]
        )
```

</td>
</tr>
</table>

<table>
<tr>
<th>GraphQL</th>
<th>Python</th>
</tr>
<tr>
<td>

```
query {
    user(login: login) {
        login
        name
        email
        createdAt
        issues { totalCount }
        pullRequests { totalCount }
        repositories { totalCount }
        gistComments { totalCount }
        issueComments { totalCount }
        commitComments { totalCount }
        repositoryDiscussionComments { totalCount }
    }
}
```

</td>
<td>

```python
class UserProfileStats(Query):
    def __init__(self, login: str) -> None:
        super().__init__(
            fields=[
                QueryNode(
                    NODE_USER,
                    args={ARG_LOGIN: login},
                    fields=[
                        FIELD_LOGIN,
                        FIELD_NAME,
                        FIELD_EMAIL,
                        FIELD_CREATED_AT,
                        QueryNode(NODE_ISSUES, fields=[FIELD_TOTAL_COUNT]),
                        QueryNode(NODE_PULL_REQUESTS, fields=[FIELD_TOTAL_COUNT]),
                        QueryNode(NODE_REPOSITORIES, fields=[FIELD_TOTAL_COUNT]),
                        QueryNode(NODE_GIST_COMMENTS, fields=[FIELD_TOTAL_COUNT]),
                        QueryNode(NODE_ISSUE_COMMENTS, fields=[FIELD_TOTAL_COUNT]),
                        QueryNode(NODE_COMMIT_COMMENTS, fields=[FIELD_TOTAL_COUNT]),
                        QueryNode(NODE_REPOSITORY_DISCUSSION_COMMENTS, fields=[FIELD_TOTAL_COUNT],),
                    ],
                )
            ]
        )
```

</td>
</tr>
</table>

<table>
<tr>
<th>GraphQL</th>
<th>Python</th>
</tr>
<tr>
<td>

```
query {
    user(login: "login") {
        repositories(
            first: 10,
            isFork: false,
            ownerAffiliations: [OWNER],
            orderBy: {field: UPDATED_AT, direction: DESC}
        ) {
            totalCount
            nodes {
                languages(first: 100, orderBy: {field: SIZE, direction: DESC}) {
                    totalCount
                    edges {
                        size
                        node { name }
                    }
                }
            }
            pageInfo { endCursor hasNextPage }
        }
    }
}
```

</td>
<td>

```python
class UserRepositories(PaginatedQuery):
    def __init__(
        self,
        login: str,
        pg_size: int = 10,
        is_fork: bool = False,
        ownership: str = "[OWNER]",
        repo_order_field: str = "CREATED_AT",
        repo_order_dir: str = "DESC",
        lag_order_field: str = "SIZE",
        lag_order_dir: str = "DESC",
    ) -> None:
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
```

</td>
</tr>
</table>

<table>
<tr>
<th>GraphQL</th>
<th>Python</th>
</tr>
<tr>
<td>

```
query {
    user(login: "login") {
        contributionsCollection(from: "2021-01-01T00:00:00Z", to: "2021-12-31T23:59:59Z") {
            startedAt
            endedAt
            restrictedContributionsCount
            totalCommitContributions
            totalIssueContributions
            totalPullRequestContributions
            totalPullRequestReviewContributions
            totalRepositoryContributions
        }
    }
}
```

</td>
<td>

```python
class UserContributionsCollection(Query):
    def __init__(
        self,
        login: str,
        start: str,
        end: str,
    ) -> None:
        super().__init__(
            fields=[
                QueryNode(
                    NODE_USER,
                    args={ARG_LOGIN: login},
                    fields=[
                        QueryNode(
                            NODE_CONTRIBUTIONS_COLLECTION,
                            args={
                                ARG_FROM: start,
                                ARG_TO: end,
                            },
                            fields=[
                                FIELD_STARTED_AT,
                                FIELD_ENDED_AT,
                                FIELD_RESTRICTED_CONTRIBUTIONS_COUNT,
                                FIELD_TOTAL_COMMIT_CONTRIBUTIONS,
                                FIELD_TOTAL_ISSUE_CONTRIBUTIONS,
                                FIELD_TOTAL_PULL_REQUEST_CONTRIBUTIONS,
                                FIELD_TOTAL_PULL_REQUEST_REVIEW_CONTRIBUTIONS,
                                FIELD_TOTAL_REPOSITORY_CONTRIBUTIONS,
                            ],
                        ),
                    ],
                )
            ]
        )
```

</td>
</tr>
</table>

<table>
<tr>
<th>GraphQL</th>
<th>Python</th>
</tr>
<tr>
<td>

```
query {
    rateLimit(dryRun: true) {
        cost
        limit
        remaining
        resetAt
        used
    }
}
```

</td>
<td>

```python
class RateLimit(Query):
    def __init__(self, dryrun: bool) -> None:
        super().__init__(
            fields=[
                QueryNode(
                    NODE_RATE_LIMIT,
                    args={ARG_DRYRUN: dryrun},
                    fields=[
                        FIELD_COST,
                        FIELD_LIMIT,
                        FIELD_REMAINING,
                        FIELD_RESET_AT,
                        FIELD_USED,
                    ],
                )
            ]
        )
```

</td>
</tr>
</table>

<table>
<tr>
<th>GraphQL</th>
<th>Python</th>
</tr>
<tr>
<td>

```
query {
    user(login: "login") {
        login
    }
    rateLimit(dryRun: true) {
        cost
        remaining
        resetAt
    }
}
```

</td>
<td>

```python
class QueryCost(Query):
    def __init__(self, query: str, dryrun: bool) -> None:
        if not query:
            raise ValueError("Test query must not be empty")

        super().__init__(
            fields=[
                query,
                QueryNode(
                    NODE_RATE_LIMIT,
                    args={ARG_DRYRUN: dryrun},
                    fields=[
                        FIELD_COST,
                        FIELD_REMAINING,
                        FIELD_RESET_AT,
                    ],
                ),
            ]
        )
```

</td>
</tr>
</table>

<table>
<tr>
<th>GraphQL</th>
<th>Python</th>
</tr>
<tr>
<td>

```

```

</td>
<td>

```python

```

</td>
</tr>
</table>
