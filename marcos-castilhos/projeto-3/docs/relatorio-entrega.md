# Relatório de Entrega — Projeto Individual 3: Automação com n8n e Agentes de IA

> **Aluno(a):** Marcos Antonio Teles de Castilhos
> **Matrícula:** 221008300
> **Data de entrega:** 05/05/2026

---

## 1. Resumo do Projeto

O projeto consiste em um pipeline de automação financeira operado via Telegram. O sistema recebe transcrições de áudio e mensagens de texto, utilizando modelos LLM (Groq Whisper e Llama 3) não como chatbots geradores de conteúdo, mas como parsers semânticos estritos. A IA atua no meio do fluxo para estruturar inputs estocásticos (linguagem natural) em um schema JSON determinístico, permitindo a orquestração condicional de persistência no Google Sheets ou acionamento de fallbacks de erro.

---

## 2. Problema Escolhido

 Pessoalmente, o registro manual de despesas pessoais cotidianas tem levado à desorganização financeira. A necessidade de abrir planilhas ou aplicativos específicos desencoraja o registro no momento do gasto. O fluxo resolve isso transformando o aplicativo de mensagens padrão do usuário em um terminal de entrada rápido, capaz de interpretar intenções ambíguas.

---

## 3. Desenho do Fluxo

A arquitetura atua como uma máquina de estados:
![alt text](/projeto-3/image.png)


### 3.1 Nós utilizados

| Nó | Tipo | Função no fluxo |
|----|------|-----------------|
|Telegram Trigger | Gatilho | Recebe o payload cru (texto ou áudio)|
| IF | Lógica | Bifurca o fluxo validando a existência do objeto de voz.|
| Telegram Get: file| Get | Baixa o áudio enviado no chat |
| Code | Transformação | Faz o spoofing do MIME Type de .oga para .ogg para compatibilidade de API. |
| HTTP Request | Integração | Consome a API do Groq (Whisper) para transcrição de áudio em texto. |
| Groq LLM Chain | Agente IA | Recebe a transcrição do áudio ou texto puro e aplica o System Prompt para forçar um JSON estruturado. |
| Edit Fields | Transformação | Faz mapeamento manual dos campos do JSON. |
| IF | Lógica | Roteia o fluxo baseado no artefato status (sucesso ou erro). |
| Google Sheets | Persistência | Realiza o append da linha com os dados limpos. |

---

## 4. Papel do Agente de IA

A IA atua estritamente como um compilador e validador de dados.

  Modelo/serviço utilizado: Groq (openai)Whisper (Speech2Text) e llama-3.3-70b-versatile (Extração).

  Tipo de decisão tomada pela IA: Classificação de categorias financeiras, extração de entidades (valor monetário) e inferência de datas baseadas no contexto de execução.

  Como a decisão da IA afeta o fluxo: Ela gera um artefato status limitando-se a "sucesso" ou "erro". O orquestrador usa esse metadado gerado pela IA para abrir ou fechar as válvulas de persistência no banco de dados.

---

## 5. Lógica de Decisão

Condição 1 (Status = Sucesso): O agente encontrou todos os parâmetros necessários. O fluxo realiza o parse das variáveis, aciona o Google Sheets para inserir a linha e envia uma confirmação visual via Telegram.

Condição 2 (Status = Erro): Ocorreu ambiguidade (ex: ausência de valor monetário explícito). O fluxo de inserção é abortado imediatamente (Fail Fast) e a mensagem de erro formatada pela IA é enviada de volta ao usuário pedindo correção.

---

## 6. Integrações

| Serviço | Finalidade |
|---------|------------|
| Telegram API | Interface de entrada (Microfone/Teclado) e output de logs/confirmações.|
| Groq API | Motor cognitivo (Velocidade na transcrição e parseamento via Llama). |
|Google Sheets | Banco de dados analítico. |


---

## 7. Persistência e Rastreabilidade

A rastreabilidade do sistema é garantida em duas camadas distintas:

Camada de Negócio (Google Sheets): Entradas processadas com sucesso são armazenadas de forma persistente como uma base de dados analítica. Cada linha representa uma decisão consolidada da IA.

Camada de Auditoria (n8n Executions): Todo o histórico de requisições, sejam elas bem-sucedidas ou falhas (entradas ambíguas), fica registrado no log de execuções do n8n. Isso permite rastrear o payload original do Telegram (o áudio ou texto cru), a transcrição intermediária gerada pelo Whisper e o JSON bruto retornado pelo LLM antes do roteamento do nó Switch, garantindo total observabilidade do processo.

---

## 8. Tratamento de Erros e Limites

Os mecanismos de contenção de falhas foram desenhados com a premissa do Fail Fast (Falha Rápida):

**Falhas da IA:** Para evitar que alucinações quebrem a inserção no banco de dados, o nó do LLM atua sob um contrato estrito (JSON Mode / Structured Outputs). Isso neutraliza o risco de a IA responder em texto livre, garantindo que o motor do n8n sempre receba as chaves esperadas (status, valor, categoria).

**Entradas inválidas:** Se o usuário enviar um áudio vago (ex: "fui ao shopping"), o System Prompt instrui a IA a não deduzir valores. A IA classifica o status como erro e preenche o campo mensagem_erro ("Esperava valor numérico"). O nó If atua como um disjuntor, barrando a persistência no Sheets e devolvendo o erro no Telegram.

**Fallback (baixa confiança):** Para contornar cenários onde o modelo não consegue decidir a classificação com clareza, foi imposta a diretriz de categorização forçada em Outros. Isso garante que o fluxo não quebre por incerteza semântica, delegando ao usuário a correção manual posterior, mas garantindo a captura do valor.

---

## 9. Diferenciais implementados

- [ ] Memória de contexto
- [X] Multi-step reasoning (cadeia de decisões) - O fluxo exige conversão de mídia em texto (Whisper) para então realizar a inferência semântica e extração de entidades (Llama 3).
- [ ] Integração com base de conhecimento
- [ ] Uso de embeddings / busca semântica

---

## 10. Limitações e Riscos

Ausência de Estado (Stateless): O bot não possui memória conversacional. Se o fluxo rejeita um input por falta de valor e o usuário responde na mensagem seguinte apenas com "foi 50 reais", o sistema falhará novamente, pois processa cada mensagem como um evento isolado sem contexto histórico.

Riscos de Classificação Estocástica: Dependendo da descrição do gasto ("Comprei cerveja no posto"), a IA pode oscilar na classificação entre Alimentação, Lazer ou Transporte.

Vulnerabilidade de API Externa: A latência ou o sucesso do fluxo dependem integralmente do tempo de resposta da API do Groq e do Telegram, além de estar sujeito a Rate Limits (limites de requisição) da camada gratuita.

---

## 11. Como executar

_Instruções para importar e rodar o workflow:_

```
# 1. Importar o arquivo workflow.json para o ambiente do n8n.
# 2. Configurar a credencial "Telegram API" criando um novo bot via @BotFather.
# 3. Configurar a credencial "Groq API" (ou OpenAI compatível) com uma API Key válida.
# 4. Configurar a credencial "Google Sheets" e atualizar o nó com o ID da sua planilha.
# 5. Ativar o workflow (Toggle Active).
# 6. Enviar uma mensagem de áudio ou texto para o bot no Telegram contendo um gasto e um valor.
```

---

## 12. Referências

1. [groq Speech to Text](https://console.groq.com/docs/speech-to-text)
2. [Telegram Bot Api](https://core.telegram.org/bots/api)
3. [n8n nodes](https://docs.n8n.io/workflows/components/nodes/)

---

## 13. Checklist de entrega

- [X] Workflow exportado do n8n (.json)
- [X] Código/scripts auxiliares incluídos
- [X] Demonstração do fluxo (vídeo ou prints)
- [X] Relatório de entrega preenchido
- [X] Pull Request aberto
