from python_graphql_client import GraphqlClient
import json
import re
import os
import pathlib


class GithubReleaseFetcher:
    def __init__(self, oauth_token):
        self.client = GraphqlClient(endpoint="https://api.github.com/graphql")
        self.oauth_token = oauth_token

    def make_query(self, after_cursor=None, include_organization=False):
        organization_graphql = """
          user(login: "LowSugarCoke") {
            repositories(first: 100, privacy: PUBLIC) {
              pageInfo {
                hasNextPage
                endCursor
              }
              nodes {
                name
                description
                url
                releases(orderBy: {field: CREATED_AT, direction: DESC}, first: 1) {
                  totalCount
                  nodes {
                    name
                    publishedAt
                    url
                  }
                }
              }
            }
          }
        """
        return """
    query {
      ORGANIZATION
      viewer {
        repositories(first: 100, privacy: PUBLIC, after: AFTER) {
          pageInfo {
            hasNextPage
            endCursor
          }
          nodes {
            name
            description
            url
            releases(orderBy: {field: CREATED_AT, direction: DESC}, first: 1) {
              totalCount
              nodes {
                name
                publishedAt
                url
              }
            }
          }
        }
      }
    }
    """.replace(
            "AFTER", '"{}"'.format(after_cursor) if after_cursor else "null"
        ).replace(
            "ORGANIZATION", organization_graphql if include_organization else "",
        )

    def fetch_releases(self):
        repos = []
        releases = []
        repo_names = {"playing-with-actions"}  # Skip this one
        has_next_page = True
        after_cursor = None

        first = True

        while has_next_page:
            data = self.client.execute(
                query=self.make_query(
                    after_cursor, include_organization=first),
                headers={"Authorization": "Bearer {}".format(
                    self.oauth_token)},
            )
            first = False
            repo_nodes = data["data"]["viewer"]["repositories"]["nodes"]
            if "organization" in data["data"]:
                repo_nodes += data["data"]["organization"]["repositories"]["nodes"]
            for repo in repo_nodes:
                if repo["releases"]["totalCount"] and repo["name"] not in repo_names:
                    repos.append(repo)
                    repo_names.add(repo["name"])
                    releases.append(
                        {
                            "repo": repo["name"],
                            "repo_url": repo["url"],
                            "description": repo["description"],
                            "release": repo["releases"]["nodes"][0]["name"]
                            .replace(repo["name"], "")
                            .strip(),
                            "published_at": repo["releases"]["nodes"][0]["publishedAt"],
                            "published_day": repo["releases"]["nodes"][0][
                                "publishedAt"
                            ].split("T")[0],
                            "url": repo["releases"]["nodes"][0]["url"],
                            "total_releases": repo["releases"]["totalCount"],
                        }
                    )
            after_cursor = data["data"]["viewer"]["repositories"]["pageInfo"]["endCursor"]
            has_next_page = after_cursor
        return releases
