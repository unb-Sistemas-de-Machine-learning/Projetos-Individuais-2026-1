from github_client import get_full_profile
from analyzer import analyze_profile

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
    print(f"Nível:     {analysis['nivel']}")
    print(f"Tipo:      {analysis['tipo']}")
    print(f"Linguagens: {', '.join(analysis['linguagens'])}")
    print(f"Resumo:    {analysis['resumo']}")
    print("=" * 40)
