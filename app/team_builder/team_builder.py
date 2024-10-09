"""
This module contains the TeamBuilder class, which is used to form project teams based on GitHub metric data from 
users. The TeamBuilder class utilizes the KMeansConstrained algorithm to create teams with specified constraints on
team sizes.
"""

from k_means_constrained import KMeansConstrained
import numpy as np


class TeamBuilder:
    """
    Class to form project teams with GitHub metric data from users.
    """

    def __init__(self, data):
        """
        Initialize the TeamBuilder with data.

        Args:
            data (list of list): The input data where each row is a list containing an identifier and numerical metrics.
        """
        self.identifiers = [row[0] for row in data]
        self.numerical_data = np.array([row[1:] for row in data], dtype=float)
        self.normalized_data = None
        self._normalize_data()

    def _normalize_data(self):
        """
        Normalize the numerical data using z-score normalization.
        """
        means = np.mean(self.numerical_data, axis=0)
        std_devs = np.std(self.numerical_data, axis=0)
        self.normalized_data = (self.numerical_data - means) / std_devs

    def form_teams(self, n_teams, size_min=None, size_max=None, random_state=42):
        """
        Form teams using the KMeansConstrained algorithm.

        Args:
            n_teams (int): The number of teams to form.
            size_min (int, optional): The minimum size of each team.
            size_max (int, optional): The maximum size of each team.

        Returns:
            list of list: A list of teams, where each team is a list of identifiers.
        """
        kmeans = KMeansConstrained(
            n_clusters=n_teams,
            size_min=size_min,
            size_max=size_max,
            random_state=random_state,
        )
        kmeans.fit(self.normalized_data)
        labels = kmeans.labels_

        teams = [[] for _ in range(n_teams)]
        for identifier, label in zip(self.identifiers, labels):
            teams[label].append(identifier)

        return teams
