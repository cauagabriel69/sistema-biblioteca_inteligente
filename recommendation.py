import pickle
from pathlib import Path
import re

import numpy as np

try:
    from langchain_ollama import (
        OllamaEmbeddings,
        ChatOllama
    )
except ImportError:
    OllamaEmbeddings = None
    ChatOllama = None

from library import LibraryDB


class FallbackEmbeddings:

    def __init__(self, dim=768):
        self.dim = dim

    def _vectorize(self, text):
        vec = np.zeros(self.dim, dtype=float)
        for token in re.findall(r"\w+", text.lower()):
            vec[abs(hash(token)) % self.dim] += 1.0
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        return vec.tolist()

    def embed_query(self, text):
        return self._vectorize(text)


class FallbackLLM:

    def invoke(self, prompt):
        route_match = re.search(r"Rota utilizada:\s*(.+)", prompt)
        route = route_match.group(1).strip() if route_match else "personalizada"
        criteria_match = re.search(r"Critérios:\s*(.+)", prompt)
        criteria = criteria_match.group(1).strip() if criteria_match else "sem critérios definidos"
        category_match = re.search(r"Categoria:\s*(.+)", prompt)
        category = category_match.group(1).strip() if category_match else "desconhecida"

        content = (
            f"Recomendação local gerada sem conexão ao Ollama. "
            f"Rota: {route}. "
            f"Categoria: {category}. "
            f"Critérios: {criteria}."
        )

        return type("Response", (), {"content": content})()


class RecommendationAPI:

    def __init__(
        self,
        llm_model="llama3.2:1b"
    ):

        self.library = LibraryDB()

        self.llm_model = llm_model

        self.cache_file = "book_embeddings.pkl"

        self.recommended_ids = set()

        self.rejection_count = 0

        self.last_recommendation_id = None

        self.using_ollama = False

        self.embedding_model = None
        self.llm = None

        self._initialize_models()

        self._load_embeddings()

    def _initialize_models(self):
        try:
            if OllamaEmbeddings is None or ChatOllama is None:
                raise RuntimeError("O pacote langchain_ollama ou ollama não está disponível")

            self.embedding_model = OllamaEmbeddings(
                model="nomic-embed-text"
            )

            self.llm = ChatOllama(
                model=self.llm_model,
                temperature=0.7
            )

            self.using_ollama = True

        except Exception as error:
            self.embedding_model = FallbackEmbeddings()
            self.llm = FallbackLLM()
            self.using_ollama = False
            print(
                "Aviso: Ollama não disponível, usando fallback local de embeddings e explicações.",
                error
            )

    # ==================================================
    # CONFIGURAÇÃO
    # ==================================================

    def set_model(self, model):

        self.llm_model = model

        self.llm = ChatOllama(
            model=model,
            temperature=0.7
        )

    # ==================================================
    # EMBEDDINGS
    # ==================================================

    def _book_text(self, book):

        return (
            f"{book['title']} "
            f"{book['author']} "
            f"{book['category']}"
        )

    def _load_embeddings(self):

        def _expected_dim():
            if isinstance(self.embedding_model, FallbackEmbeddings):
                return self.embedding_model.dim
            try:
                return len(self.embedding_model.embed_query(""))
            except Exception:
                return None

        self.embeddings = {}
        rebuild_cache = False

        if Path(self.cache_file).exists():
            with open(
                self.cache_file,
                "rb"
            ) as f:
                self.embeddings = pickle.load(f)

            if self.embeddings:
                first_vector = next(iter(self.embeddings.values()))
                loaded_dim = len(first_vector) if hasattr(first_vector, "__len__") else None
                expected_dim = _expected_dim()

                if expected_dim is not None and loaded_dim != expected_dim:
                    rebuild_cache = True
                    print(
                        "Aviso: cache de embeddings tem dimensão diferente do modelo atual; reconstruindo embeddings."
                    )

            if not rebuild_cache:
                return

        self.embeddings = {}

        books = self.library.get_all_books()

        for book in books:
            try:
                self.embeddings[book["id"]] = self.embedding_model.embed_query(
                    self._book_text(book)
                )
            except Exception as error:
                self.embedding_model = FallbackEmbeddings()
                self.llm = FallbackLLM()
                self.using_ollama = False
                print(
                    "Aviso: falha ao gerar embeddings com Ollama, ativando fallback local.",
                    error
                )
                self.embeddings[book["id"]] = self.embedding_model.embed_query(
                    self._book_text(book)
                )

        with open(
            self.cache_file,
            "wb"
        ) as f:

            pickle.dump(
                self.embeddings,
                f
            )

    # ==================================================
    # UTILIDADES
    # ==================================================

    def _cosine_similarity(
        self,
        a,
        b
    ):

        a = np.array(a)
        b = np.array(b)

        return float(
            np.dot(a, b)
            /
            (
                np.linalg.norm(a)
                *
                np.linalg.norm(b)
            )
        )

    # ==================================================
    # ETAPA 1
    # ANÁLISE DE PERFIL
    # ==================================================

    def analyze_user_profile(self):

        history = self.library.get_read_history()

        liked = [
            h
            for h in history
            if h["rating"] >= 4
        ]

        profile = {
            "history": history,
            "liked": liked,
            "total_reads": len(history),
            "liked_count": len(liked)
        }

        return profile

    # ==================================================
    # ETAPA 2
    # ROUTING
    # ==================================================

    def route_decision(
        self,
        profile
    ):

        if profile["total_reads"] == 0:
            return "cold_start"

        if profile["liked_count"] < 2:
            return "sparse_profile"

        if self.rejection_count >= 2:
            return "exploration"

        return "personalized"

    # ==================================================
    # ETAPA 3
    # CANDIDATOS
    # ==================================================

    def get_candidates(self):

        books = self.library.get_all_books()

        history = self.library.get_read_history()

        read_titles = {
            h["title"].lower()
            for h in history
        }

        candidates = [
            b
            for b in books
            if (
                b["title"].lower()
                not in read_titles
                and
                b["id"]
                not in self.recommended_ids
            )
        ]

        return candidates

    # ==================================================
    # ETAPA 4
    # DECISÃO
    # ==================================================

    def choose_book(
        self,
        route,
        profile,
        candidates
    ):

        if not candidates:
            return None

        # -------------------
        # COLD START
        # -------------------

        if route == "cold_start":

            book = candidates[0]

            return {
                "book": book,
                "score": 0.0,
                "criteria": [
                    "Usuário sem histórico",
                    "Recomendação inicial"
                ]
            }

        # -------------------
        # PERFIL FRACO
        # -------------------

        if route == "sparse_profile":

            liked_titles = [
                h["title"]
                for h in profile["liked"]
            ]

            query = "\n".join(liked_titles)

            profile_embedding = (
                self.embedding_model.embed_query(
                    query
                )
            )

            scored = []

            for book in candidates:

                score = self._cosine_similarity(
                    profile_embedding,
                    self.embeddings[book["id"]]
                )

                scored.append(
                    (
                        score,
                        book
                    )
                )

            scored.sort(
                reverse=True,
                key=lambda x: x[0]
            )

            score, book = scored[0]

            return {
                "book": book,
                "score": score,
                "criteria": [
                    "Pouco histórico",
                    "Similaridade semântica"
                ]
            }

        # -------------------
        # EXPLORAÇÃO
        # -------------------

        if route == "exploration":

            available_categories = list(
                {
                    b["category"]
                    for b in candidates
                }
            )

            category = available_categories[
                self.rejection_count
                %
                len(available_categories)
            ]

            filtered = [
                b
                for b in candidates
                if b["category"] == category
            ]

            book = filtered[0]

            return {
                "book": book,
                "score": 0.50,
                "criteria": [
                    "Diversificação",
                    "Exploração de novos gêneros"
                ]
            }

        # -------------------
        # PERSONALIZADO
        # -------------------

        liked_titles = [
            h["title"]
            for h in profile["liked"]
        ]

        profile_embedding = (
            self.embedding_model.embed_query(
                "\n".join(liked_titles)
            )
        )

        scored = []

        for book in candidates:

            score = self._cosine_similarity(
                profile_embedding,
                self.embeddings[book["id"]]
            )

            scored.append(
                (
                    score,
                    book
                )
            )

        scored.sort(
            reverse=True,
            key=lambda x: x[0]
        )

        score, book = scored[0]

        return {
            "book": book,
            "score": score,
            "criteria": [
                "Histórico consistente",
                "Alta similaridade semântica",
                "Livro ainda não lido"
            ]
        }

    # ==================================================
    # ETAPA 5
    # EXPLICAÇÃO
    # ==================================================

    def explain_decision(
        self,
        route,
        book,
        criteria
    ):

        prompt = f"""
Você é um assistente literário.

Explique em até 3 frases.

Rota utilizada:
{route}

Livro:
{book['title']}

Autor:
{book['author']}

Categoria:
{book['category']}

Critérios:
{', '.join(criteria)}

Explique por que esta recomendação faz sentido.
"""

        if self.using_ollama:
            try:
                return self.llm.invoke(prompt).content.strip()
            except Exception as error:
                print(
                    "Aviso: falha ao chamar o ChatOllama, usando explicação local.",
                    error
                )
                self.llm = FallbackLLM()
                self.using_ollama = False

        return self.llm.invoke(prompt).content.strip()

    # ==================================================
    # WORKFLOW PRINCIPAL
    # ==================================================

    def recommend(self):

        profile = self.analyze_user_profile()

        route = self.route_decision(
            profile
        )

        candidates = self.get_candidates()

        decision = self.choose_book(
            route,
            profile,
            candidates
        )

        if decision is None:

            return {
                "success": False,
                "message": "Nenhum livro disponível."
            }

        explanation = self.explain_decision(
            route,
            decision["book"],
            decision["criteria"]
        )

        self.recommended_ids.add(
            decision["book"]["id"]
        )

        self.library.log_recommendation(
            route=route,
            book_title=decision["book"]["title"],
            similarity=decision["score"]
        )

        logs = self.library.get_recommendation_logs()

        if logs:
            self.last_recommendation_id = logs[0]["id"]

        return {

            "success": True,

            "route": route,

            "book": decision["book"],

            "score": round(
                decision["score"] * 100,
                1
            ),

            "criteria": decision["criteria"],

            "explanation": explanation,

            "workflow": [
                "Análise de Perfil",
                "Routing",
                "Busca Semântica",
                "Tomada de Decisão",
                "Explicação",
                "Validação Humana"
            ]
        }

    # ==================================================
    # FEEDBACK
    # ==================================================

    def feedback(
        self,
        liked
    ):

        if self.last_recommendation_id:

            self.library.save_feedback(
                self.last_recommendation_id,
                liked
            )

        if liked:

            self.rejection_count = 0

        else:

            self.rejection_count += 1

    # ==================================================
    # RESET
    # ==================================================

    def reset_session(self):

        self.recommended_ids.clear()

        self.rejection_count = 0

        self.last_recommendation_id = None

    # ==================================================
    # MÉTRICAS
    # ==================================================

    def get_agent_metrics(self):

        return self.library.get_metrics()
