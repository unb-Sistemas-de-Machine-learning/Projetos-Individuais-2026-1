from openai import OpenAI

# Configuração apontando para o seu endereço local
client = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key="lm-studio")

def agente_justica_explicavel(texto_juridico):
    print("--- Processando Decisão Judicial... ---\n")
    
    prompt_sistema = (
        "Você é um assistente jurídico brasileiro, baseado na Constituição Federal. Sua missão é explicar sentenças para pessoas comuns. "
        "REGRA OBRIGATÓRIA (EXPLICABILIDADE): Para cada afirmação, você DEVE citar o trecho na lei "
        "original entre parênteses. Use uma linguagem clara e evite palavras difíceis."
    )

    try:
        completion = client.chat.completions.create(
            model="meta-llama-3-8b", # O LM Studio vai ignorar o nome e usar o que estiver carregado
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": texto_juridico}
            ],
            temperature=0.3,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Erro de conexão: Verifique se o LM Studio está com o servidor ligado! \n{e}"

if __name__ == "__main__":
    print("=== AGENTE JURÍDICO ONLINE (LM STUDIO) ===")
    print("Digite 'sair' para encerrar.\n")
    
    while True:
        entrada_usuario = input("Cole a sentença judicial aqui: ")
        
        if entrada_usuario.lower() == 'sair':
            print("Encerrando agente... Até mais!")
            break
            
        resultado = agente_justica_explicavel(entrada_usuario)
        print("\n" + "="*30)
        print("EXPLICAÇÃO DO AGENTE:")
        print(resultado)
        print("="*30 + "\n")