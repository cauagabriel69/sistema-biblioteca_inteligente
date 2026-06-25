# Agente Inteligente de Recomendação Literária

Projeto de trabalho de lógica e IA agêntica aplicada. O sistema usa Streamlit para interface, um banco de dados SQLite para histórico e uma arquitetura de recomendação semântica com fallback local quando o Ollama não está disponível.

## Funcionalidades

- Interface web com Streamlit
- Recomendação literária personalizada
- Análise de perfil do usuário
- Routing agêntico para decidir entre: cold start, perfil fraco, exploração e recomendações personalizadas
- Uso de embeddings para semântica de livros
- Explicações em linguagem natural para cada recomendação
- Registro de histórico de leitura e feedback de aceitação

## Arquivos principais

- `app.py` - interface Streamlit e fluxo principal do front-end
- `library.py` - classe `LibraryDB` que gerencia o banco SQLite e o catálogo de livros
- `recommendation.py` - classe `RecommendationAPI` com o motor de recomendação e explicação
- `requirements.txt` - dependências do projeto
- `library.db` - banco de dados SQLite gerado em runtime
- `book_embeddings.pkl` - cache de embeddings gerado em runtime

## Tecnologias

- Python
- Streamlit
- SQLite
- Ollama / langchain-ollama
- NumPy
- Pandas

## Como executar

1. Crie e ative um ambiente virtual Python:

```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Execute a aplicação Streamlit:

```bash
streamlit run app.py
```

4. Abra o link exibido no terminal (normalmente `http://localhost:8501`).

## Observações

- Se o Ollama não estiver instalado ou disponível, o projeto usa um fallback local para embeddings e explicações.
- O modelo padrão selecionado é `llama3.2:1b` se não houver outros modelos detectados.
- Os dados de livro, histórico e logs são salvos localmente em `library.db`.

## Estrutura do agente

Fluxo principal:

1. Análise de perfil
2. Routing
3. Busca semântica / seleção de candidato
4. Tomada de decisão
5. Explicação
6. Validação humana / feedback

## Notas

- Não versionar arquivos de banco de dados e cache local.
- Para desenvolvedores, basta atualizar `requirements.txt` e instalar novamente.
