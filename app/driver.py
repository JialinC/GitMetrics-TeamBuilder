import argparse
import csv
from app.metrics_miner.user_metrics_miner import UserMetricsMiner
from app.team_builder.team_builder import TeamBuilder
from app.github_query.github_graphql.client import Client
from app.github_query.github_graphql.authentication import (
    PersonalAccessTokenAuthenticator,
)


def parse_arguments():
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="A command-line tool for mining user metrics and forming teams."
    )
    parser.add_argument(
        "--auth-token", required=True, help="GitHub authentication token"
    )
    parser.add_argument(
        "--languages",
        nargs="+",
        required=True,
        help="Space-separated list of programming languages",
    )
    parser.add_argument(
        "--n-teams", type=int, required=True, help="Number of teams to form"
    )
    parser.add_argument(
        "--size-min", type=int, required=True, help="Minimum size of each team"
    )
    parser.add_argument(
        "--size-max", type=int, required=True, help="Maximum size of each team"
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--usernames", nargs="*", help="Space-separated list of GitHub usernames"
    )
    group.add_argument("--csv-file", help="CSV file containing GitHub usernames")
    return parser.parse_args()


def read_usernames_from_csv(csv_file):
    """
    Read usernames from a CSV file.

    Args:
        csv_file (str): Path to the CSV file.

    Returns:
        list: List of usernames.
    """
    usernames = []
    with open(csv_file, newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            usernames.extend(row)
    return usernames


def main():
    """
    Main execution logic.
    """
    args = parse_arguments()

    # Read usernames from CSV if provided
    if args.csv_file:
        usernames = read_usernames_from_csv(args.csv_file)
    else:
        usernames = args.usernames

    if not usernames:
        print(
            "No usernames provided. Please provide usernames via --usernames or --csv-file."
        )
        return

    # Initialize GitHub client
    clt = Client(
        host="api.github.com",
        is_enterprise=False,
        authenticator=PersonalAccessTokenAuthenticator(token=args.auth_token),
    )

    miner = UserMetricsMiner(clt)
    data = []
    for username in usernames:
        data.append(miner.mine(username, args.languages))

    teams = TeamBuilder(data).form_teams(
        n_teams=args.n_teams, size_min=args.size_min, size_max=args.size_max
    )

    max_team_number = len(teams)
    width = len(str(max_team_number))
    for i, team in enumerate(teams, start=1):
        print(f"team {str(i).rjust(width)}: {', '.join(team)}")


if __name__ == "__main__":
    main()
