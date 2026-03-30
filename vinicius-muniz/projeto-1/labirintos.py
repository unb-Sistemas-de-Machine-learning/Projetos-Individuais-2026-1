import random

def gerar_labirinto(linhas=15, colunas=15):
    grid = [[0 for _ in range(colunas)] for _ in range(linhas)]

    for i in range(linhas):
        for j in range(colunas):
            if random.random() < 0.25:
                grid[i][j] = 1

    grid[0][0] = 0
    grid[linhas - 1][colunas - 1] = 0

    return grid


def labirinto_para_texto(grid, agent=None, goal=None):
    legenda = (
        "Legenda: 0 = caminho livre, 1 = parede, A = agente, G = objetivo\n"
    )
    linhas = []
    for i, row in enumerate(grid):
        cells = []
        for j, cell in enumerate(row):
            if agent and (i, j) == agent:
                cells.append("A")
            elif goal and (i, j) == goal:
                cells.append("G")
            else:
                cells.append(str(cell))
        linhas.append(" ".join(cells))
    return legenda + "\n".join(linhas)
