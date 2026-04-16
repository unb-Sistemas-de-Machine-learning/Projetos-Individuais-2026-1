import os
import requests

from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}


def get_profile(username):
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 404:
        print(f"Usuário {username} não encontrado.")
        return None

    data = response.json()

    return {
        "username": data["login"],
        "name": data.get("name", "Nome não informado."),
        "bio": data.get("bio", "Perfil sem biografia.."),
        "public_repos": data.get("public_repos", 0),
        "followers": data.get("followers", 0),
        "created_at": data.get("created_at", ""),
    }


def get_repositories(username):
    url = f"https://api.github.com/users/{username}/repos"
    params = {"per_page": 100, "type": "owner"}
    response = requests.get(url, headers=HEADERS, params=params)

    repository_list = response.json()
    repositories = []

    for repository in repository_list:
        repositories.append(
            {
                "name": repository["name"],
                "description": repository.get("description", ""),
                "language": repository.get("language", ""),
                "stargazers_count": repository.get("stargazers_count", 0),
                "forks_count": repository.get("forks_count", 0),
            }
        )

    return repositories


def get_languages(repositories):
    languages = {}

    for repository in repositories:
        language = repository.get("language")

        if language:
            languages[language] = languages.get(language, 0) + 1

    sorted_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)

    return sorted_languages


def get_pull_requests(username):
    url = f"https://api.github.com/search/issues"
    params = {"q": f"author:{username} type:pr", "per_page": 100}
    response = requests.get(url, headers=HEADERS, params=params)
    data = response.json()

    prs = data.get("items", [])
    total_opened = len(prs)
    total_merged = 0
    external_repositories = set()

    for pr in prs:
        repository_url = pr.get("repository_url", "")
        repository_name = "/".join(repository_url.split("/")[-2:])

        if not repository_name.startswith(username):
            external_repositories.add(repository_name)

        if pr.get("pull_request", {}).get("merged_at"):
            total_merged += 1

    return {
        "total_opened": total_opened,
        "total_merged": total_merged,
        "external_repositories": list(external_repositories),
    }


def get_full_profile(username):
    profile = get_profile(username)

    if not profile:
        return None

    repositories = get_repositories(username)
    languages = get_languages(repositories)
    pull_requests = get_pull_requests(username)

    return {
        **profile,
        "repositories": repositories,
        "languages": languages,
        "pull_requests": pull_requests,
    }
