import os
import time
from dotenv import load_dotenv
from tools.youtube import extrair_musicas_da_playlist
from tools.lyrics import buscar_letra
from agent import classificar_sentimento_llm

def executar_agente(url_playlist: str):
    load_dotenv()
    
    print("="*50)
    print("🤖 INICIANDO AGENTE DE ANÁLISE MUSICAL")
    print("="*50)
    
    print(f"\n[1] Lendo playlist do YouTube...")
    musicas = extrair_musicas_da_playlist(url_playlist)
    
    if not musicas:
        print("Nenhuma música para processar. Encerrando.")
        return

    playlist_categorizada = []
    
    print("\n[2] Buscando letras e analisando sentimentos...")
    for idx, musica in enumerate(musicas, 1):
        artista = musica['artista']
        titulo = musica['titulo']
        print(f"  -> Processando {idx}/{len(musicas)}: {titulo} ({artista})")
        
        letra = buscar_letra(artista, titulo)
        
        if letra:
            sentimento = classificar_sentimento_llm(letra)
        else:
            sentimento = "Sem dados (Letra não encontrada)"
            
        playlist_categorizada.append({
            "titulo": titulo,
            "artista": artista,
            "sentimento": sentimento
        })
        
        # Pequeno delay para evitar Rate Limit nas APIs
        time.sleep(1)

    print("\n" + "="*50)
    print("📊 RESULTADO FINAL: PLAYLIST CATEGORIZADA")
    print("="*50)
    
    resultados_agrupados = {}
    for item in playlist_categorizada:
        cat = item['sentimento']
        if cat not in resultados_agrupados:
            resultados_agrupados[cat] = []
        resultados_agrupados[cat].append(f"{item['titulo']} - {item['artista']}")
        
    for categoria, lista_musicas in resultados_agrupados.items():
        print(f"\n[{categoria.upper()}]")
        for m in lista_musicas:
            print(f"  - {m}")

if __name__ == "__main__":
    URL_TESTE = input("Cole a URL da playlist pública do YouTube: ")
    executar_agente(URL_TESTE)