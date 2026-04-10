import os
import google.generativeai as genai

def configurar_gemini():
    chave_api = os.getenv("GEMINI_API_KEY")
    if chave_api:
        genai.configure(api_key=chave_api)

def classificar_sentimento_llm(letra: str) -> str:
    """Lê a letra da música e classifica o sentimento."""
    configurar_gemini()
    
    generation_config = {
      "temperature": 0.0, # Temperatura 0 força o modelo a ser determinístico e direto
      "top_p": 0.95,
      # max_output_tokens removido! O modelo tem espaço livre para gerar a resposta.
    }
    
    # Filtros de segurança relaxados para não bloquear as letras
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
    ]
    
    modelo = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        generation_config=generation_config
    )
    
    prompt = f"""
    Você é um especialista em análise musical e psicologia das emoções.
    Leia a letra da música abaixo e classifique-a em APENAS UMA destas categorias:
    
    - Alegria / Euforia
    - Melancolia / Tristeza
    - Calmaria / Relaxamento
    - Agressividade / Tensão
    - Romantismo / Paixão
    - Motivação / Inspiração
    
    Regra estrita: Responda APENAS com o nome exato da categoria. Não adicione nenhuma explicação, introdução ou pontuação extra.
    
    Letra:
    \"\"\"
    {letra}
    \"\"\"
    """
    
    try:
        resposta = modelo.generate_content(prompt, safety_settings=safety_settings)
        
        # Se a resposta gerou texto válido, retorna ele limpo
        if resposta.text:
            return resposta.text.strip()
            
        # Caso contrário, pega o real motivo do bloqueio para debug
        motivo = resposta.candidates[0].finish_reason.name if resposta.candidates else "Sem Motivo"
        return f"Bloqueado ({motivo})"
        
    except Exception as e:
        # Agora o erro real vai aparecer no seu console em vez de ficar oculto!
        print(f"\n[ERRO INTERNO NO LLM]: {e}")
        return "Erro de Classificação"