import os
import re
from googleapiclient.discovery import build

def extrair_musicas_da_playlist(url_playlist: str) -> list:
    match = re.search(r"list=([a-zA-Z0-9_-]+)", url_playlist)
    if not match:
        print("Erro: URL de playlist inválida.")
        return []
    
    playlist_id = match.group(1)
    api_key = os.getenv("YOUTUBE_API_KEY")
    
    if not api_key:
        print("Erro: Chave da API do YouTube não encontrada no .env.")
        return []

    try:
        youtube = build("youtube", "v3", developerKey=api_key)
        
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=20 
        )
        response = request.execute()
        
        musicas = []
        for item in response.get("items", []):
            titulo = item["snippet"]["title"]
            canal = item["snippet"]["videoOwnerChannelTitle"]
            
            artista = canal.replace(" - Topic", "").replace("VEVO", "")
            
            musicas.append({
                "titulo": titulo,
                "artista": artista
            })
            
        return musicas

    except Exception as e:
        print(f"Erro ao acessar API do YouTube: {e}")
        return []