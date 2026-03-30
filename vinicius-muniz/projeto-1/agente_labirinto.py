import os
import time
import json
from collections import deque
from dotenv import load_dotenv
from groq import Groq
from labirintos import gerar_labirinto, labirinto_para_texto

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MOVIMENTOS = {
    "cima":    (-1, 0),
    "baixo":   (1, 0),
    "esquerda": (0, -1),
    "direita":  (0, 1),
}

MAX_TENTATIVAS_LLM = 150


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def print_grid(grid, agent=None, goal=None, path=None):
    for i in range(len(grid)):
        row = ""
        for j in range(len(grid[0])):
            if (i, j) == agent:
                row += "A "
            elif (i, j) == goal:
                row += "G "
            elif path and (i, j) in path:
                row += "* "
            elif grid[i][j] == 1:
                row += "█ "
            else:
                row += ". "
        print(row)
    print()


# ===================== AGENTE BFS =====================

def bfs(grid, start, goal, visual=False):
    rows, cols = len(grid), len(grid[0])
    queue = deque([(start, [start])])
    visited = {start}
    movimentos = 0
    direcoes = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while queue:
        (x, y), path = queue.popleft()
        movimentos += 1

        if visual:
            clear()
            print("[BFS] Explorando...")
            print(f"   Movimentos explorados: {movimentos}")
            print_grid(grid, agent=(x, y), goal=goal)
            time.sleep(0.03)

        if (x, y) == goal:
            return path, movimentos

        for dx, dy in direcoes:
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols and grid[nx][ny] == 0 and (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append(((nx, ny), path + [(nx, ny)]))

    return None, movimentos


# ===================== AGENTE LLM (GROQ) =====================

def construir_prompt_unico(grid, posicao, goal, posicoes_visitadas, ultimo_feedback):
    rows, cols = len(grid), len(grid[0])
    x, y = posicao
    gx, gy = goal
    mapa = labirinto_para_texto(grid, agent=posicao, goal=goal)

    vizinhos = {}
    for nome, (dx, dy) in MOVIMENTOS.items():
        nx, ny = x + dx, y + dy
        if 0 <= nx < rows and 0 <= ny < cols:
            estado = "livre" if grid[nx][ny] == 0 else "parede"
            if estado == "livre" and (nx, ny) in posicoes_visitadas:
                estado = "livre (JÁ VISITADA)"
            vizinhos[nome] = f"({nx},{ny}) {estado}"
        else:
            vizinhos[nome] = "fora do mapa"

    visitadas_str = ", ".join(f"({r},{c})" for r, c in sorted(posicoes_visitadas))

    feedback_linha = ""
    if ultimo_feedback:
        feedback_linha = f"\nFEEDBACK DO TURNO ANTERIOR: {ultimo_feedback}\n"

    return f"""Labirinto {rows}x{cols}. Vá de (0,0) até ({gx},{gy}). Mova: cima/baixo/esquerda/direita. Só células 0.
{feedback_linha}
Posição: ({x},{y}) | Objetivo: ({gx},{gy}) | Falta: {gx-x} linhas, {gy-y} colunas
Visitadas: [{visitadas_str}]
Vizinhos: {json.dumps(vizinhos, ensure_ascii=False)}

{mapa}

PRIORIZE direções que aproximem do objetivo e NÃO foram visitadas.
Responda APENAS: {{"movimento":"<dir>","raciocinio":"<breve>"}}"""


def extrair_movimento(texto):
    try:
        inicio = texto.find("{")
        fim = texto.rfind("}") + 1
        if inicio != -1 and fim > inicio:
            dados = json.loads(texto[inicio:fim])
            return dados.get("movimento", "").lower(), dados.get("raciocinio", "")
    except (json.JSONDecodeError, AttributeError):
        pass
    return None, "Resposta inválida do LLM"


DIRECAO_NOME = {(-1, 0): "cima", (1, 0): "baixo", (0, -1): "esquerda", (0, 1): "direita"}


def bfs_para_celula_livre(grid, inicio, posicoes_visitadas):
    rows, cols = len(grid), len(grid[0])
    queue = deque([(inicio, [])])
    visited_bfs = {inicio}
    direcoes = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while queue:
        (x, y), caminho = queue.popleft()

        if (x, y) != inicio and (x, y) not in posicoes_visitadas:
            return caminho

        for dx, dy in direcoes:
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols and grid[nx][ny] == 0 and (nx, ny) not in visited_bfs:
                visited_bfs.add((nx, ny))
                queue.append(((nx, ny), caminho + [(dx, dy)]))

    return None


def agente_llm(grid, start, goal, visual=False):
    posicao = start
    path = [start]
    posicoes_visitadas = {start}
    rows, cols = len(grid), len(grid[0])
    ultimo_feedback = ""
    contagem_posicoes = {start: 1}
    fila_escape = []

    for tentativa in range(1, MAX_TENTATIVAS_LLM + 1):
        if visual:
            clear()
            if fila_escape:
                print("[LLM] Backtracking assistido...")
            else:
                print("[LLM] Pensando...")
            print(f"   Movimentos realizados: {tentativa - 1}")
            print_grid(grid, agent=posicao, goal=goal)

        if posicao == goal:
            return path, tentativa - 1

        if fila_escape:
            dx, dy = fila_escape.pop(0)
            nx, ny = posicao[0] + dx, posicao[1] + dy
            nome_dir = DIRECAO_NOME.get((dx, dy), "?")

            if visual:
                print(f"   Decisão: {nome_dir} (backtracking assistido)")
                print(f"   Raciocínio: BFS encontrou rota de escape")

            posicao = (nx, ny)
            path.append(posicao)
            posicoes_visitadas.add(posicao)
            contagem_posicoes[posicao] = contagem_posicoes.get(posicao, 0) + 1

            if visual:
                time.sleep(0.1)
            continue

        if contagem_posicoes.get(posicao, 0) >= 3:
            rota = bfs_para_celula_livre(grid, posicao, posicoes_visitadas)
            if rota:
                fila_escape = rota
                if visual:
                    print(f"   LOOP detectado! Ativando backtracking assistido ({len(rota)} passos)")
                    time.sleep(0.5)
                continue
            else:
                ultimo_feedback = "LOOP detectado e não há células livres não visitadas acessíveis."

        prompt = construir_prompt_unico(grid, posicao, goal, posicoes_visitadas, ultimo_feedback)
        ultimo_feedback = ""

        movimento, raciocinio = None, ""
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Você navega um labirinto. Responda APENAS JSON válido."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=80,
            )
            resposta_llm = response.choices[0].message.content.strip()
            movimento, raciocinio = extrair_movimento(resposta_llm)
        except Exception as e:
            raciocinio = f"Erro na API: {e}"

        if visual:
            print(f"   Decisão: {movimento}")
            print(f"   Raciocínio: {raciocinio}")

        if movimento and movimento in MOVIMENTOS:
            dx, dy = MOVIMENTOS[movimento]
            nx, ny = posicao[0] + dx, posicao[1] + dy

            if 0 <= nx < rows and 0 <= ny < cols and grid[nx][ny] == 0:
                posicao = (nx, ny)
                path.append(posicao)
                posicoes_visitadas.add(posicao)
                contagem_posicoes[posicao] = contagem_posicoes.get(posicao, 0) + 1
            else:
                ultimo_feedback = f"'{movimento}' BLOQUEADO (parede/fora). Tente outra direção."
        else:
            ultimo_feedback = f"Movimento inválido ('{movimento}'). Use: cima, baixo, esquerda, direita."

        if visual:
            time.sleep(0.3)

    return None, MAX_TENTATIVAS_LLM


# ===================== EXECUÇÃO PRINCIPAL =====================

def exibir_resultado(nome, path, movimentos, grid, goal):
    if path:
        print(f"  [OK] {nome}: resolveu em {len(path) - 1} passos ({movimentos} movimentos explorados)")
        print_grid(grid, path=set(path), goal=goal)
    else:
        print(f"  [FALHA] {nome}: NAO conseguiu resolver ({movimentos} movimentos)")
        print()


def main():
    NUM_LABIRINTOS = 3
    start = (0, 0)
    goal = (6, 6)

    print("=" * 50)
    print("  LABIRINTO: BFS vs AGENTE LLM (Groq)")
    print("=" * 50)

    for i in range(NUM_LABIRINTOS):
        while True:
            grid = gerar_labirinto(7, 7)
            path_teste, _ = bfs(grid, start, goal, visual=False)
            if path_teste:
                break

        print(f"\n{'─' * 50}")
        print(f"  LABIRINTO {i + 1}")
        print(f"{'─' * 50}\n")

        print("Mapa gerado:")
        print_grid(grid, agent=start, goal=goal)

        input("Pressione ENTER para ver o BFS resolver...\n")

        path_bfs, mov_bfs = bfs(grid, start, goal, visual=True)
        clear()
        print(f"\n--- Resultado BFS (Labirinto {i + 1}) ---\n")
        exibir_resultado("BFS", path_bfs, mov_bfs, grid, goal)

        input("Pressione ENTER para ver o Agente LLM resolver...\n")

        path_llm, mov_llm = agente_llm(grid, start, goal, visual=True)
        clear()
        print(f"\n--- Resultado LLM (Labirinto {i + 1}) ---\n")
        exibir_resultado("Agente LLM", path_llm, mov_llm, grid, goal)

        print(f"{'─' * 40}")
        print(f"  COMPARACAO - Labirinto {i + 1}")
        print(f"{'─' * 40}")
        print(f"  BFS:        {len(path_bfs) - 1 if path_bfs else '—':>4} passos | {mov_bfs:>4} nós explorados")
        if path_llm:
            print(f"  Agente LLM: {len(path_llm) - 1:>4} passos | {mov_llm:>4} chamadas à API")
        else:
            print(f"  Agente LLM:    — falhou  | {mov_llm:>4} chamadas à API")
        print()

        if i < NUM_LABIRINTOS - 1:
            input("Pressione ENTER para o próximo labirinto...\n")

    print("\nTodos os labirintos foram processados!")


if __name__ == "__main__":
    main()
