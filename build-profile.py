from dotenv import load_dotenv
import os
from src.graphql_client import GithubReleaseFetcher
from src.file_writer import FileWriter

if __name__ == "__main__":
    load_dotenv()  # take environment variables from .env.
    TOKEN = os.environ.get("LOWSUGARCOKE_TOKEN", "")
    fetcher = GithubReleaseFetcher(TOKEN)
    releases = fetcher.fetch_releases()
    print(releases)
    writer = FileWriter(__file__)
    writer.write_to_file(releases)
