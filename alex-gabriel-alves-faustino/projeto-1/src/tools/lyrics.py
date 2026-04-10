import os
import re
from dotenv import load_dotenv
import lyricsgenius
import traceback

def buscar_letra(artista: str, titulo: str) -> str:

    titulo_limpo = re.sub(r'[\(\[\{].*?[\)\]\}]', '', titulo).strip()
    
    titulo_limpo = titulo_limpo.replace('"', '').replace("'", "")
    
    termos_youtube = ['official video', 'lyric video', 'audio', 'music video', 'official audio']
    for termo in termos_youtube:
        titulo_limpo = re.compile(re.escape(termo), re.IGNORECASE).sub('', titulo_limpo)
    
    if " - " in titulo_limpo:
        titulo_limpo = titulo_limpo.split(" - ")[-1].strip()
        
    titulo_limpo = re.sub(r'\s+', ' ', titulo_limpo).strip()

    artista_limpo = re.split(r' feat\.? | ft\.? | & | x | X ', artista, flags=re.IGNORECASE)[0].strip()
    
    load_dotenv()

    token = os.getenv("GENIUS_API_KEY")
    if not token:
        print("Erro: GENIUS_API_KEY não encontrada no .env")
        return ""

    token = token.strip('"\'')

    try:
        genius = lyricsgenius.Genius(token, verbose=True, remove_section_headers=True)

        try:
            musica = genius.search_song(titulo_limpo, artista_limpo)
        except TypeError as te:
            print(f"Debug: search_song com artista falhou: {repr(te)}. Tentando sem artista...")
            traceback.print_exc()
            try:
                musica = genius.search_song(titulo_limpo)
            except Exception as e2:
                print(f"Debug: fallback sem artista também falhou: {repr(e2)}")
                traceback.print_exc()
                return ""

        if musica and getattr(musica, 'lyrics', None):
            letra = musica.lyrics
            letra = re.sub(r'\d*Embed$', '', letra)
            return letra[:3000]

        print(f"Info: Nenhuma letra encontrada para '{titulo_limpo}' de '{artista_limpo}'")
        return ""

    except Exception as e:
        print(f"Aviso: Falha na busca do Genius para '{titulo_limpo}' de '{artista_limpo}': {repr(e)}")
        traceback.print_exc()
        return ""