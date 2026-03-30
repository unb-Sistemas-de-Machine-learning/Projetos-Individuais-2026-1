import os
import requests

from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

LABEL_PRIORITY = {
    "Iniciante": [
        "good first issue",
        "good-first-issue",
        "documentation",
        "beginner",
        "easy",
        "starter",
        "help wanted",
        "low priority",
        "design",
        "bug",
        "enhancement",
        "refactor",
        "testing",
        "frontend",
        "backend",
        "medium priority",
        "performance",
        "security",
        "critical",
        "high priority",
    ],
    "Intermediário": [
        "bug",
        "enhancement",
        "refactor",
        "testing",
        "help wanted",
        "medium priority",
        "frontend",
        "backend",
        "good first issue",
        "good-first-issue",
        "documentation",
        "beginner",
        "easy",
        "starter",
        "low priority",
        "design",
        "performance",
        "security",
        "critical",
        "high priority",
    ],
    "Avançado": [
        "performance",
        "security",
        "critical",
        "high priority",
        "help wanted",
        "bug",
        "enhancement",
        "refactor",
        "testing",
        "medium priority",
        "frontend",
        "backend",
        "good first issue",
        "good-first-issue",
        "documentation",
        "beginner",
        "easy",
        "starter",
        "low priority",
        "design",
    ],
}

OPEN_SOURCE_LICENSES = {
    "mit",
    "apache-2.0",
    "bsd-2-clause",
    "bsd-3-clause",
    "isc",
    "bsl-1.0",
    "artistic-2.0",
    "gpl-2.0",
    "gpl-3.0",
    "agpl-3.0",
    "lgpl-2.0",
    "lgpl-2.1",
    "lgpl-3.0",
    "mpl-2.0",
    "eclipse-pl-2.0",
    "unlicense",
    "cc0-1.0",
}


def is_open_source(repo_data):
    license_info = repo_data.get("license")
    if not license_info:
        return False
    spdx_id = license_info.get("spdx_id", "").lower()
    return spdx_id in OPEN_SOURCE_LICENSES


def normalize_dynamic(values):
    min_value = min(values) if values else 0
    max_value = max(values) if values else 1

    if max_value == min_value:
        return [1.0 for _ in values]

    return [(value - min_value) / (max_value - min_value) for value in values]


def get_recent_commits(owner, repository):
    url = f"https://api.github.com/repos/{owner}/{repository}/commits"
    since = datetime.now(timezone.utc).replace(day=1).isoformat()
    params = {"since": since, "per_page": 100}
    response = requests.get(url, headers=HEADERS, params=params)

    if response.status_code == 200:
        return len(response.json())

    return 0


def get_contributors_count(owner, repository):
    url = f"https://api.github.com/repos/{owner}/{repository}/contributors"
    params = {"per_page": 100, "anon": "false"}
    response = requests.get(url, headers=HEADERS, params=params)

    if response.status_code == 200:
        return len(response.json())

    return 0


def get_repo_data(owner, repository):
    url = f"https://api.github.com/repos/{owner}/{repository}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        return response.json()

    return {}


def get_label_priority(issue_labels, level):
    priority_list = LABEL_PRIORITY.get(level, [])
    issue_label_names = [label["name"].lower() for label in issue_labels]

    for i, priority_label in enumerate(priority_list):
        if priority_label.lower() in issue_label_names:
            return i

    return len(priority_list)


def search_issues(languages, nivel, keywords=None):
    issues = []
    repo_cache = {}

    keyword_query = " ".join(keywords) if keywords else ""

    for language in languages:
        query = f"is:issue is:open language:{language} {keyword_query}".strip()
        url = "https://api.github.com/search/issues"
        params = {
            "q": query,
            "sort": "updated",
            "order": "desc",
            "per_page": 20,
        }

        response = requests.get(url, headers=HEADERS, params=params)

        if response.status_code == 200:
            data = response.json()
            issues.extend(data.get("items", []))
        else:
            print(f"Erro ao buscar issues para {language}: {response.status_code}")

    seen = set()
    unique_issues = []
    for issue in issues:
        if issue["id"] not in seen:
            seen.add(issue["id"])
            unique_issues.append(issue)

    enriched = []
    for issue in unique_issues:
        repo_url = issue.get("repository_url", "")
        parts = repo_url.split("/")
        owner, repo = parts[-2], parts[-1]
        repo_key = f"{owner}/{repo}"

        if repo_key not in repo_cache:
            repo_data = get_repo_data(owner, repo)

            if not is_open_source(repo_data):
                repo_cache[repo_key] = None
            else:
                recent_commits = get_recent_commits(owner, repo)
                contributors = get_contributors_count(owner, repo)
                repo_cache[repo_key] = {
                    "repo_data": repo_data,
                    "recent_commits": recent_commits,
                    "contributors": contributors,
                }

        cached = repo_cache[repo_key]
        if cached is None:
            continue

        enriched.append(
            {
                "issue": issue,
                "repo": cached["repo_data"],
                "label_priority": get_label_priority(issue.get("labels", []), nivel),
                "raw": {
                    "stars": cached["repo_data"].get("stargazers_count", 0),
                    "forks": cached["repo_data"].get("forks_count", 0),
                    "recent_commits": cached["recent_commits"],
                    "contributors": cached["contributors"],
                },
            }
        )

    stars_normalized = normalize_dynamic([e["raw"]["stars"] for e in enriched])
    forks_normalized = normalize_dynamic([e["raw"]["forks"] for e in enriched])
    commits_normalized = normalize_dynamic(
        [e["raw"]["recent_commits"] for e in enriched]
    )
    contributors_normalized = normalize_dynamic(
        [e["raw"]["contributors"] for e in enriched]
    )

    # label_priority: menor índice = label mais relevante = maior score
    # inverte a normalização pra menor índice virar maior valor
    label_scores = [e["label_priority"] for e in enriched]
    label_normalized = normalize_dynamic(label_scores)
    label_normalized = [1 - v for v in label_normalized]

    for i, entry in enumerate(enriched):
        entry["popularity_score"] = round(
            (
                stars_normalized[i]
                + forks_normalized[i]
                + commits_normalized[i]
                + contributors_normalized[i]
                + label_normalized[i]
            )
            / 5,
            4,
        )

    enriched.sort(key=lambda x: -x["popularity_score"])

    return enriched, len(enriched)
