# Relatório de Entrega — Projeto Individual 1

> **Aluno(a):** Alex Gabriel Alves Faustino  
> **Matrícula:** 200056603  
> **Data de entrega:** 29/03/2026  

---

## 1. Resumo do Projeto

O projeto consiste no desenvolvimento de um agente inteligente desenhado para resolver o problema da organização puramente técnica de músicas nas plataformas de vídeo. Através de um pipeline sequencial, o agente consome uma playlist pública do YouTube, limpa e padroniza os metadados dos vídeos, e extrai as letras das canções utilizando a API do Genius. Em seguida, as letras são submetidas a um LLM (Google Gemini via biblioteca `google.generativeai`) que realiza uma análise de sentimento e categoriza cada faixa emocionalmente. No código atual, o modelo padrão utilizado é `gemini-2.5-flash` (definido em `src/agent.py`). O resultado é um relatório em terminal que agrupa as músicas pelo seu perfil emocional.

---

## 2. Combinação Atribuída

| Item | Valor |
|------|-------|
| **Domínio** | Cultura |
| **Função do agente** | Análise de sentimento |
| **Restrição obrigatória** | Integração com API externa |

---

## 3. Modelagem do Agente

### 3.1 Entrada (Input)
A entrada é uma string contendo a URL pública de uma playlist do YouTube.

Exemplo: https://youtube.com/playlist?list=PLynH9_8UlJrO5QIH8Ct-a_ElmiN9_ag8k&si=z5fvrZqvmIQIXDCe

### 3.2 Processamento (Pipeline)
Entrada (URL) → [Extração YouTube] → [Regex Clean] → [Extração Genius] → [Classificação LLM] → Saída

### 3.3 Decisão
A decisão do agente reside na análise semântica do LLM. O modelo atua sob um prompt restritivo, com o parâmetro `temperature` configurado para `0.0` para forçar respostas determinísticas e exatas. A configuração desativa os filtros de assédio e conteúdo explícito para garantir que a análise poética de gêneros como o Rap e o Trap não sofra interrupções.

### 3.4 Saída (Output)
A saída é um relatório textual impresso no terminal, apresentando as categorias de sentimentos mapeadas como cabeçalhos e listando os títulos e artistas pertinentes sob cada uma.

Exemplo:

[MELANCOLIA / TRISTEZA]
  - Mas Que Nada - KVSH

[AGRESSIVIDADE / TENSÃO]
  - Liderança - Major RD
  - Iphone Branco - Borges
  - 60K (Remix) - Major RD
  - Favela Sinistra - Trilha Sonora do Gueto
  - The Plot In You - Forgotten (Official Music Video) - Fearless Records
  - Three Days Grace - Animal I Have Become (Official Video) - ThreeDaysGrace
  - Architects - "Seeing Red" - Architects

---

## 4. Implementação

### 4.1 Tecnologias utilizadas

| Tecnologia | Versão | Finalidade |
|------------|--------|------------|
| Python | 3.11 | Linguagem principal, executada via ambiente virtual |
| google-generativeai | não fixada | Comunicação e orquestração do LLM Gemini 
| lyricsgenius | não fixada | Integração com a API de letras do Genius
| google-api-python-client | 2.118.0 | Extração nativa de itens de playlists do YouTube |

### 4.2 Estrutura do código

```
projeto-1/
├── src/
│   ├── main.py
│   ├── agent.py
│   └── tools/
│       ├── __init__.py
│       ├── youtube.py
│       └── lyrics.py
├── .env.example
├── .gitignore
└── requirements.txt
```

### 4.3 Como executar

#### 1. instalar dependências

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### 2. Configurar variáveis de ambiente

Crie um arquivo `.env` contendo as chaves abaixo:

```
GENIUS_API_KEY=seu_token_genius
YOUTUBE_API_KEY=seu_token_youtube
GEMINI_API_KEY=sua_chave_gemini
```

#### 3. Executar o orquestrador

```bash
python src/main.py
```

---

## 5. Avaliação e Testes

### 5.1 Métricas definidas

| Métrica | Descrição | Resultado obtido |
|---------|-----------|------------------|
| Resiliência a Dados | Capacidade de buscar letras apesar de títulos "sujos" de vídeos musicais. | Elevada (resolvido com Regex). |
| Bypass de Segurança | Evitar cortes na inferência por falsos positivos em filtros de safety. | Configurado para minimizar bloqueios, mas o comportamento final depende das políticas do serviço e pode variar. |

### 5.2 Exemplos de teste

#### Teste 1: Contorno de Filtro de Segurança
- **Entrada:** Música "Iphone Branco" - Borges (Letra explícita).
- **Saída esperada:** Classificação textual da emoção, sem bloqueio.
- **Saída obtida:** Categoria retornada com sucesso.
- **Resultado:** Sucesso.

#### Teste 2: Metadados Sujos
- **Entrada:** Vídeo "Three Days Grace - Animal I Have Become (Official Video)".
- **Saída esperada:** Encontrar a letra correta no Genius limpando o texto.
- **Saída obtida:** Letra localizada e classificada.
- **Resultado:** Sucesso.

### 5.3 Análise dos resultados
O agente demonstrou alta capacidade de resolução arquitetural. Os principais obstáculos foram contornar as limitações rígidas das APIs externas: metadados poluídos devolvidos pelo YouTube e bloqueios de segurança aplicados pelo LLM a letras de músicas.

---

## 6. Diferenciais implementados

- [ ] RAG com base externa
- [ ] Múltiplos agentes
- [x] Uso de ferramentas (tools)
- [ ] Memória persistente
- [ ] Explicabilidade
- [x] Análise crítica de limitações

---

## 7. Limitações e Trabalhos Futuros

O sistema atual apresenta limitações em faixas puramente instrumentais (pois dependem de letras) ou músicas de nicho extremado não cadastradas na plataforma Genius. Trabalhos futuros poderiam envolver a transcrição de áudio em tempo real (Speech-to-Text) para suprir a base de letras. Como também aproveitar o relatório gerado pelo agente para criar novas playlists com base na classificação.

---

## 8. Referências

1. Google AI Studio Documentation.
2. Documentação da API do YouTube Data v3.
3. Documentação LyricsGenius.

---

## 9. Checklist de entrega

- [x] Documento de engenharia preenchido
- [x] Código funcional no repositório
- [x] Relatório de entrega preenchido
- [x] Pull Request aberto