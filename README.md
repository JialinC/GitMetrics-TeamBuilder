# GitHub Metrics Team Builder

GitHub Metrics Team Builder is a convenient tool for querying a group of users' GitHub metrics and forming software engineering teams using the collected metrics and a constrained k-means algorithm. The related research is published in this paper: [Utilizing the Constrained K-Means Algorithm and Pre-Class GitHub Contribution Statistics for Forming Student Teams](https://dl.acm.org/doi/abs/10.1145/3649217.3653634).

## Installation

1. **Clone the Repository**:

   ```sh
   git clone https://github.com/JialinC/GitMetrics-TeamBuilder.git
   cd GitMetrics-TeamBuilder
   ```

2. **Create and Activate Virtual Environment**:
   **For Windows**:

   ```sh
   python -m venv venv
   .\venv\Scripts\activate
   ```

   **For macOS/Linux**:

   ```sh
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install the Package:**:
   ```sh
   pip install .
   ```

## Usage

Once the package is installed, you can use the `team` command to query GitHub metrics and form teams.

### Command-Line Arguments

- `--auth-token`: GitHub authentication token (required)
- `--languages`: Space-separated list of programming languages that you interested from each user (required)
- `--n-teams`: Number of teams to form (required)
- `--size-min`: Minimum size of each team (required)
- `--size-max`: Maximum size of each team (required)
- `--usernames`: Space-separated list of GitHub usernames (mutually exclusive with `--csv-file`)
- `--csv-file`: CSV file containing GitHub usernames (mutually exclusive with `--usernames`)

## Example

### Using Space-Separated Usernames

```sh
team --auth-token YOUR_AUTH_TOKEN --usernames user1 user2 user3 --languages Python Java C++ --n-teams 3 --size-min 1 --size-max 1
```

### Using a CSV File for Usernames

```sh
team --auth-token YOUR_AUTH_TOKEN --csv-file usernames.csv --languages Python Java C++ --n-teams 4 --size-min 2 --size-max 3
```

## Documentation

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or suggestions, please open an issue or contact us at [jcui9@ncsu.edu](mailto:jcui9@ncsu.edu).
