import sqlite3
from pathlib import Path

DEFAULT_BOOKS = [
    ("1984", "George Orwell", "Distopia"),
    ("A Revolução dos Bichos", "George Orwell", "Distopia"),
    ("Admirável Mundo Novo", "Aldous Huxley", "Distopia"),
    ("Fahrenheit 451", "Ray Bradbury", "Distopia"),
    ("Jogos Vorazes", "Suzanne Collins", "Distopia"),

    ("Duna", "Frank Herbert", "Ficção Científica"),
    ("Fundação", "Isaac Asimov", "Ficção Científica"),
    ("Eu, Robô", "Isaac Asimov", "Ficção Científica"),
    ("Neuromancer", "William Gibson", "Cyberpunk"),
    ("Androides Sonham com Ovelhas Elétricas?", "Philip K. Dick", "Ficção Científica"),

    ("O Hobbit", "J.R.R. Tolkien", "Fantasia"),
    ("O Senhor dos Anéis", "J.R.R. Tolkien", "Fantasia"),
    ("O Silmarillion", "J.R.R. Tolkien", "Fantasia"),
    ("Harry Potter e a Pedra Filosofal", "J.K. Rowling", "Fantasia"),
    ("As Crônicas de Nárnia", "C.S. Lewis", "Fantasia"),
    ("Eragon", "Christopher Paolini", "Fantasia"),
    ("A Roda do Tempo", "Robert Jordan", "Fantasia"),
    ("Mistborn", "Brandon Sanderson", "Fantasia"),

    ("Dom Casmurro", "Machado de Assis", "Romance"),
    ("Memórias Póstumas de Brás Cubas", "Machado de Assis", "Romance"),
    ("Orgulho e Preconceito", "Jane Austen", "Romance"),
    ("Jane Eyre", "Charlotte Brontë", "Romance"),
    ("Anna Kariênina", "Liev Tolstói", "Romance"),
    ("O Morro dos Ventos Uivantes", "Emily Brontë", "Romance"),

    ("Crime e Castigo", "Dostoiévski", "Clássico"),
    ("Os Irmãos Karamázov", "Dostoiévski", "Clássico"),
    ("Guerra e Paz", "Liev Tolstói", "Clássico"),
    ("Os Miseráveis", "Victor Hugo", "Clássico"),
    ("Dom Quixote", "Miguel de Cervantes", "Clássico"),
    ("Madame Bovary", "Gustave Flaubert", "Clássico"),
    ("O Conde de Monte Cristo", "Alexandre Dumas", "Clássico"),

    ("Drácula", "Bram Stoker", "Terror"),
    ("Frankenstein", "Mary Shelley", "Terror"),
    ("O Iluminado", "Stephen King", "Terror"),
    ("It: A Coisa", "Stephen King", "Terror"),
    ("O Chamado de Cthulhu", "H.P. Lovecraft", "Terror"),

    ("Sherlock Holmes", "Arthur Conan Doyle", "Mistério"),
    ("Assassinato no Expresso do Oriente", "Agatha Christie", "Mistério"),
    ("E Não Sobrou Nenhum", "Agatha Christie", "Mistério"),
    ("O Nome da Rosa", "Umberto Eco", "Mistério"),
    ("Garota Exemplar", "Gillian Flynn", "Suspense"),

    ("O Código Da Vinci", "Dan Brown", "Suspense"),
    ("Anjos e Demônios", "Dan Brown", "Suspense"),
    ("O Silêncio dos Inocentes", "Thomas Harris", "Suspense"),
    ("A Garota no Trem", "Paula Hawkins", "Suspense"),

    ("O Pequeno Príncipe", "Antoine de Saint-Exupéry", "Infantil"),
    ("Alice no País das Maravilhas", "Lewis Carroll", "Infantil"),
    ("Pinóquio", "Carlo Collodi", "Infantil"),
    ("Peter Pan", "J.M. Barrie", "Infantil"),

    ("O Alquimista", "Paulo Coelho", "Ficção"),
    ("Cem Anos de Solidão", "Gabriel García Márquez", "Ficção"),
    ("A Metamorfose", "Franz Kafka", "Ficção"),
    ("O Apanhador no Campo de Centeio", "J.D. Salinger", "Ficção"),
    ("O Grande Gatsby", "F. Scott Fitzgerald", "Ficção"),
    ("Ulisses", "James Joyce", "Ficção"),

    ("O Caçador de Pipas", "Khaled Hosseini", "Drama"),
    ("A Menina que Roubava Livros", "Markus Zusak", "Drama"),
    ("A Culpa é das Estrelas", "John Green", "Drama"),
    ("Extraordinário", "R.J. Palacio", "Drama"),

    ("A República", "Platão", "Filosofia"),
    ("Assim Falou Zaratustra", "Friedrich Nietzsche", "Filosofia"),
    ("Meditações", "Marco Aurélio", "Filosofia"),
    ("O Mundo de Sofia", "Jostein Gaarder", "Filosofia"),
    ("O Estrangeiro", "Albert Camus", "Filosofia"),

    ("A Arte da Guerra", "Sun Tzu", "Estratégia"),
    ("O Príncipe", "Nicolau Maquiavel", "Política"),
    ("Da Guerra", "Carl von Clausewitz", "Estratégia"),
    ("A Riqueza das Nações", "Adam Smith", "Economia"),
    ("O Capital", "Karl Marx", "Economia"),

    ("Cosmos", "Carl Sagan", "Ciência"),
    ("Uma Breve História do Tempo", "Stephen Hawking", "Ciência"),
    ("O Gene Egoísta", "Richard Dawkins", "Ciência"),
    ("A Origem das Espécies", "Charles Darwin", "Ciência"),
    ("O Andar do Bêbado", "Leonard Mlodinow", "Ciência"),

    ("Sapiens", "Yuval Noah Harari", "História"),
    ("Homo Deus", "Yuval Noah Harari", "História"),
    ("Armas, Germes e Aço", "Jared Diamond", "História"),
    ("O Diário de Anne Frank", "Anne Frank", "História"),
    ("A História da Humanidade", "H.G. Wells", "História"),

    ("Steve Jobs", "Walter Isaacson", "Biografia"),
    ("Longa Caminhada para a Liberdade", "Nelson Mandela", "Biografia"),
    ("Einstein: Sua Vida e Universo", "Walter Isaacson", "Biografia"),
    ("Leonardo da Vinci", "Walter Isaacson", "Biografia"),
    ("Eu Sou Malala", "Malala Yousafzai", "Biografia"),

    ("Pai Rico, Pai Pobre", "Robert Kiyosaki", "Finanças"),
    ("Os Segredos da Mente Milionária", "T. Harv Eker", "Finanças"),
    ("O Investidor Inteligente", "Benjamin Graham", "Finanças"),
    ("Hábitos Atômicos", "James Clear", "Desenvolvimento Pessoal"),
    ("Como Fazer Amigos e Influenciar Pessoas", "Dale Carnegie", "Desenvolvimento Pessoal"),

    ("Os 7 Hábitos das Pessoas Altamente Eficazes", "Stephen Covey", "Desenvolvimento Pessoal"),
    ("Trabalhe 4 Horas por Semana", "Tim Ferriss", "Produtividade"),
    ("Deep Work", "Cal Newport", "Produtividade"),
    ("Essencialismo", "Greg McKeown", "Produtividade"),
    ("Mindset", "Carol Dweck", "Psicologia"),

    ("Rápido e Devagar", "Daniel Kahneman", "Psicologia"),
    ("O Homem em Busca de Sentido", "Viktor Frankl", "Psicologia"),
    ("Inteligência Emocional", "Daniel Goleman", "Psicologia"),
    ("Psicologia das Massas", "Gustave Le Bon", "Psicologia"),
    ("A Interpretação dos Sonhos", "Sigmund Freud", "Psicologia"),

    ("A Máquina do Tempo", "H.G. Wells", "Ficção Científica"),
    ("Vinte Mil Léguas Submarinas", "Júlio Verne", "Aventura"),
    ("Viagem ao Centro da Terra", "Júlio Verne", "Aventura"),
    ("A Ilha Misteriosa", "Júlio Verne", "Aventura"),
    ("O Fim da Eternidade", "Isaac Asimov", "Ficção Científica"),
    ("Encontro com Rama", "Arthur C. Clarke", "Ficção Científica"),
    ("Solaris", "Stanislaw Lem", "Ficção Científica"),
    ("Snow Crash", "Neal Stephenson", "Cyberpunk"),
    ("Altered Carbon", "Richard K. Morgan", "Cyberpunk"),
    ("Ready Player One", "Ernest Cline", "Ficção Científica"),

    ("O Último Desejo", "Andrzej Sapkowski", "Fantasia"),
    ("A Espada do Destino", "Andrzej Sapkowski", "Fantasia"),
    ("O Nome do Vento", "Patrick Rothfuss", "Fantasia"),
    ("O Temor do Sábio", "Patrick Rothfuss", "Fantasia"),
    ("A Guerra dos Tronos", "George R.R. Martin", "Fantasia"),
    ("A Fúria dos Reis", "George R.R. Martin", "Fantasia"),
    ("O Caminho dos Reis", "Brandon Sanderson", "Fantasia"),
    ("Elantris", "Brandon Sanderson", "Fantasia"),
    ("A Cor da Magia", "Terry Pratchett", "Fantasia"),
    ("American Gods", "Neil Gaiman", "Fantasia"),

    ("A Cabana", "William P. Young", "Drama"),
    ("Comer, Rezar, Amar", "Elizabeth Gilbert", "Drama"),
    ("Pequenas Mulheres", "Louisa May Alcott", "Drama"),
    ("A Cor Púrpura", "Alice Walker", "Drama"),
    ("A Estrada", "Cormac McCarthy", "Drama"),

    ("O Processo", "Franz Kafka", "Clássico"),
    ("O Castelo", "Franz Kafka", "Clássico"),
    ("A Peste", "Albert Camus", "Clássico"),
    ("O Vermelho e o Negro", "Stendhal", "Clássico"),
    ("As Vinhas da Ira", "John Steinbeck", "Clássico"),

    ("O Médico e o Monstro", "Robert Louis Stevenson", "Terror"),
    ("A Volta do Parafuso", "Henry James", "Terror"),
    ("Coraline", "Neil Gaiman", "Terror"),
    ("Entrevista com o Vampiro", "Anne Rice", "Terror"),
    ("Hell House", "Richard Matheson", "Terror"),

    ("O Talismã", "Stephen King", "Suspense"),
    ("Misery", "Stephen King", "Suspense"),
    ("O Colecionador", "John Fowles", "Suspense"),
    ("Antes de Dormir", "S.J. Watson", "Suspense"),
    ("A Paciente Silenciosa", "Alex Michaelides", "Suspense"),

    ("Morte no Nilo", "Agatha Christie", "Mistério"),
    ("Os Crimes ABC", "Agatha Christie", "Mistério"),
    ("A Filha do Tempo", "Josephine Tey", "Mistério"),
    ("O Falcão Maltês", "Dashiell Hammett", "Mistério"),
    ("O Sono Eterno", "Raymond Chandler", "Mistério"),

    ("O Menino do Pijama Listrado", "John Boyne", "História"),
    ("SPQR", "Mary Beard", "História"),
    ("Os Canhões de Agosto", "Barbara Tuchman", "História"),
    ("Pós-Guerra", "Tony Judt", "História"),
    ("A Segunda Guerra Mundial", "Antony Beevor", "História"),

    ("O Livro dos Cinco Anéis", "Miyamoto Musashi", "Estratégia"),
    ("Sobre a Guerra", "Sun Bin", "Estratégia"),
    ("A Política", "Aristóteles", "Política"),
    ("Leviatã", "Thomas Hobbes", "Política"),
    ("Do Contrato Social", "Jean-Jacques Rousseau", "Política"),

    ("Além do Bem e do Mal", "Friedrich Nietzsche", "Filosofia"),
    ("Crítica da Razão Pura", "Immanuel Kant", "Filosofia"),
    ("Ética", "Baruch Spinoza", "Filosofia"),
    ("O Ser e o Nada", "Jean-Paul Sartre", "Filosofia"),
    ("Discurso do Método", "René Descartes", "Filosofia"),

    ("O Corpo Fala", "Pierre Weil", "Psicologia"),
    ("Em Busca de Sentido", "Viktor Frankl", "Psicologia"),
    ("Influência", "Robert Cialdini", "Psicologia"),
    ("O Animal Social", "Elliot Aronson", "Psicologia"),
    ("A Coragem de Não Agradar", "Ichiro Kishimi", "Psicologia"),

    ("A Física do Futuro", "Michio Kaku", "Ciência"),
    ("O Gene", "Siddhartha Mukherjee", "Ciência"),
    ("Breves Respostas para Grandes Questões", "Stephen Hawking", "Ciência"),
    ("O Universo Numa Casca de Noz", "Stephen Hawking", "Ciência"),
    ("Bilhões e Bilhões", "Carl Sagan", "Ciência"),

    ("A Startup Enxuta", "Eric Ries", "Negócios"),
    ("De Zero a Um", "Peter Thiel", "Negócios"),
    ("Good to Great", "Jim Collins", "Negócios"),
    ("O Jeito Harvard de Ser Feliz", "Shawn Achor", "Negócios"),
    ("Rework", "Jason Fried", "Negócios"),

    ("O Milagre da Manhã", "Hal Elrod", "Desenvolvimento Pessoal"),
    ("Quem Pensa Enriquece", "Napoleon Hill", "Desenvolvimento Pessoal"),
    ("A Única Coisa", "Gary Keller", "Produtividade"),
    ("O Poder do Hábito", "Charles Duhigg", "Produtividade"),
    ("Faça Tempo", "Jake Knapp", "Produtividade"),

    ("Elon Musk", "Ashlee Vance", "Biografia"),
    ("Benjamin Franklin", "Walter Isaacson", "Biografia"),
    ("Churchill", "Andrew Roberts", "Biografia"),
    ("Alex Ferguson: Minha Autobiografia", "Alex Ferguson", "Biografia"),
    ("Open", "Andre Agassi", "Biografia"),

    ("A Bíblia", "Diversos Autores", "Religião"),

    ("Watchmen", "Alan Moore", "HQ"),
    ("Maus", "Art Spiegelman", "HQ"),
    ("Sandman", "Neil Gaiman", "HQ"),
    ("V de Vingança", "Alan Moore", "HQ"),
    ("Batman: O Cavaleiro das Trevas", "Frank Miller", "HQ")
]

class LibraryDB:

    def __init__(self, db_path="library.db"):
        self.db_path = db_path
        self._ensure_database()

    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_database(self):

        with self._conn() as conn:

            c = conn.cursor()

            # =========================
            # LIVROS
            # =========================
            c.execute("""
            CREATE TABLE IF NOT EXISTS books(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT UNIQUE,
                author TEXT,
                category TEXT
            )
            """)

            # =========================
            # HISTÓRICO
            # =========================
            c.execute("""
            CREATE TABLE IF NOT EXISTS read_history(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                rating INTEGER,
                notes TEXT,
                read_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # =========================
            # LOG DE RECOMENDAÇÕES
            # =========================
            c.execute("""
            CREATE TABLE IF NOT EXISTS recommendation_log(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                route TEXT,
                book_title TEXT,
                similarity REAL,
                accepted INTEGER DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # =========================
            # TESTES
            # =========================
            c.execute("""
            CREATE TABLE IF NOT EXISTS test_results(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scenario TEXT,
                expected TEXT,
                obtained TEXT,
                success INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # =========================
            # POPULAR BANCO
            # =========================
            c.execute("SELECT COUNT(*) FROM books")

            if c.fetchone()[0] == 0:
                c.executemany(
                    """
                    INSERT INTO books(title, author, category)
                    VALUES(?,?,?)
                    """,
                    DEFAULT_BOOKS
                )

            conn.commit()

    # ==================================================
    # LIVROS
    # ==================================================

    def get_all_books(self):
        with self._conn() as conn:
            return [
                dict(r)
                for r in conn.execute(
                    "SELECT * FROM books ORDER BY title"
                ).fetchall()
            ]

    def search_books(self, title=None, author=None, category=None):

        query = "SELECT * FROM books WHERE 1=1"
        params = []

        if title:
            query += " AND title LIKE ?"
            params.append(f"%{title}%")

        if author:
            query += " AND author LIKE ?"
            params.append(f"%{author}%")

        if category:
            query += " AND category LIKE ?"
            params.append(f"%{category}%")

        query += " ORDER BY title"

        with self._conn() as conn:
            return [
                dict(r)
                for r in conn.execute(query, params).fetchall()
            ]

    def add_book(self, title, author, category):

        with self._conn() as conn:

            conn.execute(
                """
                INSERT INTO books(title, author, category)
                VALUES(?,?,?)
                """,
                (title, author, category)
            )

            conn.commit()

    def remove_book(self, title):

        with self._conn() as conn:

            conn.execute(
                "DELETE FROM books WHERE title=?",
                (title,)
            )

            conn.commit()

    # ==================================================
    # HISTÓRICO
    # ==================================================

    def add_to_history(self, title, rating, notes=""):

        with self._conn() as conn:

            conn.execute(
                """
                INSERT INTO read_history(
                    title,
                    rating,
                    notes
                )
                VALUES(?,?,?)
                """,
                (title, rating, notes)
            )

            conn.commit()

    def get_read_history(self):

        with self._conn() as conn:

            return [
                dict(r)
                for r in conn.execute(
                    """
                    SELECT *
                    FROM read_history
                    ORDER BY read_date DESC
                    """
                ).fetchall()
            ]

    def remove_from_history(self, history_id):

        with self._conn() as conn:

            conn.execute(
                """
                DELETE FROM read_history
                WHERE id=?
                """,
                (history_id,)
            )

            conn.commit()

    # ==================================================
    # RECOMENDAÇÕES
    # ==================================================

    def log_recommendation(
        self,
        route,
        book_title,
        similarity
    ):

        with self._conn() as conn:

            conn.execute(
                """
                INSERT INTO recommendation_log(
                    route,
                    book_title,
                    similarity
                )
                VALUES(?,?,?)
                """,
                (
                    route,
                    book_title,
                    similarity
                )
            )

            conn.commit()

    def save_feedback(
        self,
        recommendation_id,
        accepted
    ):

        with self._conn() as conn:

            conn.execute(
                """
                UPDATE recommendation_log
                SET accepted=?
                WHERE id=?
                """,
                (
                    int(accepted),
                    recommendation_id
                )
            )

            conn.commit()

    def get_recommendation_logs(self):

        with self._conn() as conn:

            return [
                dict(r)
                for r in conn.execute(
                    """
                    SELECT *
                    FROM recommendation_log
                    ORDER BY created_at DESC
                    """
                ).fetchall()
            ]

    # ==================================================
    # TESTES
    # ==================================================

    def add_test_result(
        self,
        scenario,
        expected,
        obtained,
        success
    ):

        with self._conn() as conn:

            conn.execute(
                """
                INSERT INTO test_results(
                    scenario,
                    expected,
                    obtained,
                    success
                )
                VALUES(?,?,?,?)
                """,
                (
                    scenario,
                    expected,
                    obtained,
                    int(success)
                )
            )

            conn.commit()

    def get_test_results(self):

        with self._conn() as conn:

            return [
                dict(r)
                for r in conn.execute(
                    """
                    SELECT *
                    FROM test_results
                    ORDER BY created_at DESC
                    """
                ).fetchall()
            ]

    # ==================================================
    # MÉTRICAS
    # ==================================================

    def get_metrics(self):

        with self._conn() as conn:

            total_books = conn.execute(
                "SELECT COUNT(*) FROM books"
            ).fetchone()[0]

            total_reads = conn.execute(
                "SELECT COUNT(*) FROM read_history"
            ).fetchone()[0]

            total_recommendations = conn.execute(
                "SELECT COUNT(*) FROM recommendation_log"
            ).fetchone()[0]

            accepted = conn.execute(
                """
                SELECT COUNT(*)
                FROM recommendation_log
                WHERE accepted=1
                """
            ).fetchone()[0]

            tests = conn.execute(
                """
                SELECT COUNT(*)
                FROM test_results
                """
            ).fetchone()[0]

            passed = conn.execute(
                """
                SELECT COUNT(*)
                FROM test_results
                WHERE success=1
                """
            ).fetchone()[0]

            acceptance_rate = (
                accepted / total_recommendations * 100
                if total_recommendations > 0 else 0
            )

            success_rate = (
                passed / tests * 100
                if tests > 0 else 0
            )

            return {
                "books": total_books,
                "reads": total_reads,
                "recommendations": total_recommendations,
                "acceptance_rate": round(acceptance_rate, 1),
                "tests": tests,
                "success_rate": round(success_rate, 1)
            }
