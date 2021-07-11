import collections
import datetime
import os
import random

import github
from github.GithubException import GithubException
from jinja2 import Template

GITHUB_TOKEN = os.environ.get("GHT")

gh = github.Github(GITHUB_TOKEN)


def align(number: int):
    """ Align the number regarding to template """

    return " " + str(number) + " " * (11 - len(str(number)))


def align_username(user_name: str):
    """ Align the username regarding to template """

    if len(user_name) <= 5:
        return str(user_name) + "@github.com"
    elif len(user_name) <= 7:
        return str(user_name) + "@github"
    elif len(user_name) <= 10:
        return str(user_name) + "@git"
    elif len(user_name) > 16:
        return user_name[:17]
    else:
        return user_name


class UserStats:
    """ Interactes with GihHub Api and fetch required data """

    def __init__(self, username: str):
        self.user = gh.get_user(username)
        self.user_repos = self.user.get_repos()
        self.name = self.user.name
        self.bio = self.user.bio
        self.web = self.user.blog
        self.stars = sum([repo.stargazers_count for repo in self.user_repos])
        self.forks = sum([repo.forks_count for repo in self.user_repos])
        self.commits = self.get_commits()
        self.repos_count = len(list(self.user_repos))
        self.followers = self.user.followers
        self.issues_created = len(
            list(gh.search_issues("", author=username, type="issue"))
        )
        self.pr_created = len(list(gh.search_issues(
            "", author=username, type="pr"
        )))
        self.watching_repos = len(list(self.user.get_watched()))
        self.gists = len(list(self.user.get_gists()))
        self.hireable = self.user.hireable
        self.created_at = self.user.created_at

    def get_commits(self):
        repos = []
        for repo in self.user_repos:
            if repo.fork:
                repos.append(0)
            else:
                try:
                    repos.append(repo.get_commits().totalCount)
                except GithubException:
                    repos.append(0)

        return sum(repos)


def get_stats(username: str):
    """ Returns the stats data of the given username """

    stats = collections.namedtuple(
        "UserStats",
        field_names=[
            "username",
            "name",
            "bio",
            "website",
            "stars",
            "forks",
            "commits",
            "repo",
            "followers",
            "pic",
            "issues",
            "pr",
            "watch",
            "gists",
            "hire",
            "uptime",
        ],
    )

    user = UserStats(username)

    return stats(
        align_username(username),
        user.name,
        user.bio,
        user.web,
        align(user.stars),
        align(user.forks),
        align(user.commits),
        align(user.repos_count),
        align(user.followers),
        user.user.avatar_url,
        align(user.issues_created),
        align(user.pr_created),
        user.watching_repos,
        align(user.gists),
        user.hireable,
        (datetime.datetime.now() - user.created_at).days,
    )

THEMES = {
    "ubuntu": {
        "name": "ubuntu",
        "back": "#300a24",
        "fore": "#ffffff",
        "green": "#ffffff",
        "purple": "#ffffff",
        "orange": "#ffffff",
        "cyan": "#ffffff",
        "username": "#5cbe09",
    },
    "default": {
        "name": "default",
        "back": "#272822",
        "fore": "#f8f8f2",
        "green": "#a6e22e",
        "purple": "#ae81ff",
        "orange": "#cc6633",
        "cyan": "#8be9fd",
        "username": "#f70202",
    },
    "dracula": {
        "name": "dracula",
        "back": "#282A36",
        "fore": "#F8F8F2",
        "green": "#50fa7b",
        "purple": "#bd93f9",
        "orange": "#ffb86c",
        "cyan": "#8be9fd",
        "username": "#E356A7",
    },
    "monokai": {
        "name": "monokai",
        "back": "#2e2e2e",
        "fore": "#d6d6d6",
        "green": "#b4d273",
        "purple": "#9e86c8",
        "orange": "#e87d3e",
        "cyan": "#8be9fd",
        "username": "#f92672",
    },
    "atom": {
        "name": "atom",
        "back": "#161719",
        "fore": "#c5c8c6",
        "green": "#94fa36",
        "purple": "#b9b6fc",
        "orange": "#f5ffa8",
        "cyan": "#85befd",
        "username": "#fd5ff1",
    },
    "github": {
        "name": "github",
        "back": "#f4f4f4",
        "fore": "#3e3e3e",
        "green": "#87d5a2",
        "purple": "#e94691",
        "orange": "#2e6cba",
        "cyan": "#666666",
        "username": "#de0000",
    },
    "googledark": {
        "name": "googledark",
        "back": "#202124",
        "fore": "#E8EAED",
        "green": "#34A853",
        "purple": "#A142F4",
        "orange": "#FBBC05",
        "cyan": "#EA4335",
        "username": "#4285F4",
    },
    "googlelight": {
        "name": "googlelight",
        "back": "#FFFFFF",
        "fore": "#5F6368",
        "green": "#34A853",
        "purple": "#A142F4",
        "orange": "#EA4335",
        "cyan": "#24C1E0",
        "username": "#4285F4",
    },
    "powershell": {
        "name": "powershell",
        "back": "#052454",
        "fore": "#F6F6F7",
        "green": "#1CFE3C",
        "purple": "#D33682",
        "orange": "#FEFE45",
        "cyan": "#EF2929",
        "username": "#F6F6F7",
    },
}


def get_theme(theme):
    default = THEMES.get("default")
    return THEMES.get(theme, default)


with open("template.svg", "r") as file_obj:
    template_string = file_obj.read()

with open("stats.svg", "w") as file_obj:
    template = Template(template_string)
    rendered_string = template.render(
        data=get_stats("yogeshwaran01"),
        theme=get_theme(random.choice(list(THEMES.keys())))
    )
    file_obj.write(rendered_string)
