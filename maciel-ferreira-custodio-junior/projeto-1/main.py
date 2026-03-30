from github_client import get_full_profile
from analyzer import analyze_profile
from issue_finder import search_issues

username = input("Digite o username do GitHub: ")
profile = get_full_profile(username)

if profile:
    print(f"\nNome: {profile['name']}")
    print(f"Conta criada em: {profile['created_at']}")
    print(f"Repositórios públicos: {profile['public_repos']}")
    print(f"Seguidores: {profile['followers']}")
    print(f"Linguagens: {profile['languages'][:5]}")
    print(f"Total de PRs abertos: {profile['pull_requests']['total_opened']}")
    print(f"Total de PRs mergeados: {profile['pull_requests']['total_merged']}")
    print(
        f"Repos externos contribuídos: {profile['pull_requests']['external_repositories'][:5]}"
    )

    print("\nAnalisando perfil com IA...\n")
    analysis = analyze_profile(profile)

    print("=" * 40)
    print("        ANÁLISE DO PERFIL")
    print("=" * 40)
    print(f"Nível:      {analysis['level']}")
    print(f"Tipo:       {analysis['type']}")
    print(f"Linguagens: {', '.join(analysis['languages'])}")
    print(f"Resumo:     {analysis['summary']}")
    print("=" * 40)

    print("\nBuscando issues recomendadas...\n")

    keywords = analysis.get("keywords", [])
    all_issues, total = search_issues(
        analysis["languages"], analysis["level"], keywords=keywords
    )

    if not all_issues:
        print("Nenhuma issue encontrada.")
    else:
        per_page = 5
        page = 0

        while True:
            start = page * per_page
            end = start + per_page
            results = all_issues[start:end]

            if not results:
                print("Não há mais issues para carregar.")
                break

            print(f"Mostrando {end} de {total} issues encontradas\n")
            print("=" * 40)

            for i, entry in enumerate(results, start=1):
                issue = entry["issue"]
                repo = entry["repo"]
                labels = [label["name"] for label in issue.get("labels", [])]

                print(f"{i}. {issue['title']}")
                print(f"   Repositório:  {repo.get('full_name', 'N/A')}")
                print(f"   Labels:       {', '.join(labels) if labels else 'Nenhuma'}")
                print(f"   Estrelas:     {repo.get('stargazers_count', 0)}")
                print(f"   Score:        {entry['popularity_score']}")
                print(f"   Link:         {issue['html_url']}")
                print()

            print("=" * 40)

            if end >= total:
                print("Não há mais issues para carregar.")
                break

            remaining = min(per_page, total - end)
            continuar = (
                input(f"\nCarregar mais {remaining} issues? (s/n): ").strip().lower()
            )
            if continuar != "s":
                break

            page += 1
