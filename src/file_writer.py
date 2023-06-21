import pathlib
import re


class FileWriter:
    def __init__(self, root):
        self.root = pathlib.Path(root).parent.resolve()

    def replace_chunk(self, content, marker, chunk, inline=False):
        r = re.compile(
            r"<!\-\- {} starts \-\->.*<!\-\- {} ends \-\->".format(
                marker, marker),
            re.DOTALL,
        )
        if not inline:
            chunk = "\n{}\n".format(chunk)
        chunk = "<!-- {} starts -->{}<!-- {} ends -->".format(
            marker, chunk, marker)
        return r.sub(chunk, content)

    def write_to_file(self, releases):
        readme = self.root / "README.md"
        project_releases = self.root / "releases.md"
        releases.sort(key=lambda r: r["published_at"], reverse=True)
        md = "\n\n".join(
            [
                "[{repo} {release}]({url}) - {published_day}".format(**release)
                for release in releases[:8]
            ]
        )
        readme_contents = readme.open().read()

        rewritten = self.replace_chunk(readme_contents, "recent_releases", md)

        # Write out full project-releases.md file
        project_releases_md = "\n".join(
            [
                (
                    "* **[{repo}]({repo_url})**: [{release}]({url}) {total_releases_md}- {published_day}\n"
                    "<br />{description}"
                ).format(
                    total_releases_md="- ([{} releases total]({}/releases)) ".format(
                        release["total_releases"], release["repo_url"]
                    )
                    if release["total_releases"] > 1
                    else "",
                    **release
                )
                for release in releases
            ]
        )
        project_releases_content = project_releases.open().read()
        project_releases_content = self.replace_chunk(
            project_releases_content, "recent_releases", project_releases_md
        )
        project_releases_content = self.replace_chunk(
            project_releases_content, "project_count", str(len(releases)), inline=True
        )
        project_releases_content = self.replace_chunk(
            project_releases_content,
            "releases_count",
            str(sum(r["total_releases"] for r in releases)),
            inline=True,
        )

        project_releases.open("w").write(project_releases_content)

        readme.open("w").write(rewritten)
