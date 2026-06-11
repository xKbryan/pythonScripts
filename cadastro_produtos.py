import sqlite3
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk


BANCO_DADOS = "estoque.db"


def conectar_banco():
    return sqlite3.connect(BANCO_DADOS)


conexao = conectar_banco()
cursor = conexao.cursor()

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        quantidade INTEGER NOT NULL,
        estoque_minimo INTEGER NOT NULL,
        validade TEXT,
        cor TEXT,
        textura TEXT,
        peso REAL,
        unidade_medida TEXT,
        aplicacao TEXT
    )
    """
)


def adicionar_colunas_produtos():
    colunas_necessarias = {
        "validade": "TEXT",
        "cor": "TEXT",
        "textura": "TEXT",
        "peso": "REAL",
        "unidade_medida": "TEXT",
        "aplicacao": "TEXT",
    }

    cursor.execute("PRAGMA table_info(produtos)")
    colunas_existentes = {coluna[1] for coluna in cursor.fetchall()}

    for nome_coluna, tipo_coluna in colunas_necessarias.items():
        if nome_coluna not in colunas_existentes:
            cursor.execute(f"ALTER TABLE produtos ADD COLUMN {nome_coluna} {tipo_coluna}")

    conexao.commit()


adicionar_colunas_produtos()

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS movimentacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto_id INTEGER NOT NULL,
        tipo TEXT NOT NULL,
        quantidade INTEGER NOT NULL,
        responsavel TEXT NOT NULL,
        data_operacao TEXT NOT NULL,
        FOREIGN KEY (produto_id) REFERENCES produtos (id)
    )
    """
)

conexao.commit()


def texto_obrigatorio(campo, nome_campo):
    valor = campo.get().strip()

    if not valor:
        messagebox.showerror("Erro", f"Informe o campo {nome_campo}.")
        campo.focus()
        return None

    return valor


def inteiro_obrigatorio(campo, nome_campo):
    valor = texto_obrigatorio(campo, nome_campo)

    if valor is None:
        return None

    try:
        numero = int(valor)
    except ValueError:
        messagebox.showerror("Erro", f"O campo {nome_campo} deve ser um numero inteiro.")
        campo.focus()
        return None

    if numero < 0:
        messagebox.showerror("Erro", f"O campo {nome_campo} nao pode ser negativo.")
        campo.focus()
        return None

    return numero


def real_opcional(campo, nome_campo):
    valor = campo.get().strip()

    if not valor:
        return None

    try:
        numero = float(valor.replace(",", "."))
    except ValueError:
        messagebox.showerror("Erro", f"O campo {nome_campo} deve ser um numero.")
        campo.focus()
        return None

    if numero < 0:
        messagebox.showerror("Erro", f"O campo {nome_campo} nao pode ser negativo.")
        campo.focus()
        return None

    return numero


def carregar_produtos():
    adicionar_colunas_produtos()
    lista_produtos.delete(*lista_produtos.get_children())
    combo_produto["values"] = []

    cursor.execute(
        """
        SELECT
            id,
            nome,
            quantidade,
            estoque_minimo,
            validade,
            cor,
            textura,
            peso,
            unidade_medida,
            aplicacao
        FROM produtos
        ORDER BY nome
        """
    )

    produtos = cursor.fetchall()
    opcoes_combo = []

    for produto in produtos:
        lista_produtos.insert("", tk.END, values=produto)
        opcoes_combo.append(f"{produto[0]} - {produto[1]}")

    combo_produto["values"] = opcoes_combo


def carregar_historico():
    lista_historico.delete(*lista_historico.get_children())

    cursor.execute(
        """
        SELECT
            movimentacoes.id,
            produtos.nome,
            movimentacoes.tipo,
            movimentacoes.quantidade,
            movimentacoes.responsavel,
            movimentacoes.data_operacao
        FROM movimentacoes
        INNER JOIN produtos ON produtos.id = movimentacoes.produto_id
        ORDER BY movimentacoes.id DESC
        """
    )

    for movimentacao in cursor.fetchall():
        lista_historico.insert("", tk.END, values=movimentacao)


def limpar_campos_produto():
    for campo in campos_produto:
        campo.delete(0, tk.END)

    entrada_nome.focus()


def cadastrar_produto():
    nome = texto_obrigatorio(entrada_nome, "Nome do Produto")
    quantidade = inteiro_obrigatorio(entrada_quantidade, "Quantidade")
    estoque_minimo = inteiro_obrigatorio(entrada_minimo, "Estoque Minimo")
    peso = real_opcional(entrada_peso, "Peso")

    if nome is None or quantidade is None or estoque_minimo is None:
        return

    if entrada_peso.get().strip() and peso is None:
        return

    validade = entrada_validade.get().strip()
    cor = entrada_cor.get().strip()
    textura = entrada_textura.get().strip()
    unidade = entrada_unidade.get().strip()
    aplicacao = entrada_aplicacao.get().strip()

    cursor.execute(
        """
        INSERT INTO produtos (
            nome,
            quantidade,
            estoque_minimo,
            validade,
            cor,
            textura,
            peso,
            unidade_medida,
            aplicacao
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            nome,
            quantidade,
            estoque_minimo,
            validade,
            cor,
            textura,
            peso,
            unidade,
            aplicacao,
        ),
    )

    conexao.commit()
    carregar_produtos()
    limpar_campos_produto()
    verificar_estoque(exibir_mensagem_sucesso=False)
    messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso!")


def obter_produto_selecionado():
    valor = combo_produto.get().strip()

    if not valor:
        messagebox.showerror("Erro", "Selecione um produto.")
        combo_produto.focus()
        return None

    try:
        return int(valor.split(" - ")[0])
    except ValueError:
        messagebox.showerror("Erro", "Produto selecionado invalido.")
        combo_produto.focus()
        return None


def registrar_movimentacao(tipo):
    produto_id = obter_produto_selecionado()
    quantidade = inteiro_obrigatorio(entrada_qtd_movimento, "Quantidade da Movimentacao")
    responsavel = texto_obrigatorio(entrada_responsavel, "Responsavel")

    if produto_id is None or quantidade is None or responsavel is None:
        return

    if quantidade == 0:
        messagebox.showerror("Erro", "A quantidade da movimentacao deve ser maior que zero.")
        entrada_qtd_movimento.focus()
        return

    cursor.execute("SELECT quantidade FROM produtos WHERE id = ?", (produto_id,))
    resultado = cursor.fetchone()

    if resultado is None:
        messagebox.showerror("Erro", "Produto nao encontrado.")
        return

    quantidade_atual = resultado[0]

    if tipo == "Saida" and quantidade > quantidade_atual:
        messagebox.showerror("Erro", "Nao existe quantidade suficiente em estoque.")
        entrada_qtd_movimento.focus()
        return

    if tipo == "Entrada":
        nova_quantidade = quantidade_atual + quantidade
    else:
        nova_quantidade = quantidade_atual - quantidade

    data_operacao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    cursor.execute(
        "UPDATE produtos SET quantidade = ? WHERE id = ?",
        (nova_quantidade, produto_id),
    )

    cursor.execute(
        """
        INSERT INTO movimentacoes (
            produto_id,
            tipo,
            quantidade,
            responsavel,
            data_operacao
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (produto_id, tipo, quantidade, responsavel, data_operacao),
    )

    conexao.commit()
    entrada_qtd_movimento.delete(0, tk.END)
    entrada_responsavel.delete(0, tk.END)
    carregar_produtos()
    carregar_historico()
    verificar_estoque(exibir_mensagem_sucesso=False)
    messagebox.showinfo("Sucesso", f"Movimentacao de {tipo.lower()} registrada.")


def verificar_estoque(exibir_mensagem_sucesso=True):
    cursor.execute(
        """
        SELECT nome, quantidade, estoque_minimo
        FROM produtos
        WHERE quantidade < estoque_minimo
        ORDER BY nome
        """
    )

    produtos_abaixo_minimo = cursor.fetchall()

    if produtos_abaixo_minimo:
        mensagem = "Produtos abaixo do estoque minimo:\n\n"

        for nome, quantidade, estoque_minimo in produtos_abaixo_minimo:
            mensagem += f"- {nome}: {quantidade} em estoque (minimo: {estoque_minimo})\n"

        messagebox.showwarning("Alerta de Estoque", mensagem)
    elif exibir_mensagem_sucesso:
        messagebox.showinfo("Estoque", "Todos os produtos estao acima do estoque minimo.")


def criar_campo(frame, texto, linha, coluna):
    tk.Label(frame, text=texto).grid(row=linha, column=coluna, sticky="w", padx=5, pady=2)
    entrada = tk.Entry(frame, width=25)
    entrada.grid(row=linha + 1, column=coluna, padx=5, pady=2)
    return entrada


janela = tk.Tk()
janela.title("Sistema de Controle de Estoque")
janela.geometry("1050x700")

abas = ttk.Notebook(janela)
abas.pack(fill="both", expand=True, padx=10, pady=10)

aba_cadastro = ttk.Frame(abas)
aba_movimentacao = ttk.Frame(abas)
aba_historico = ttk.Frame(abas)

abas.add(aba_cadastro, text="Cadastro de Produtos")
abas.add(aba_movimentacao, text="Movimentacao de Estoque")
abas.add(aba_historico, text="Historico")

frame_cadastro = tk.LabelFrame(aba_cadastro, text="Dados do Produto")
frame_cadastro.pack(fill="x", padx=10, pady=10)

entrada_nome = criar_campo(frame_cadastro, "Nome do Produto", 0, 0)
entrada_quantidade = criar_campo(frame_cadastro, "Quantidade", 0, 1)
entrada_minimo = criar_campo(frame_cadastro, "Estoque Minimo", 0, 2)
entrada_validade = criar_campo(frame_cadastro, "Validade", 2, 0)
entrada_cor = criar_campo(frame_cadastro, "Cor", 2, 1)
entrada_textura = criar_campo(frame_cadastro, "Textura", 2, 2)
entrada_peso = criar_campo(frame_cadastro, "Peso", 4, 0)
entrada_unidade = criar_campo(frame_cadastro, "Unidade de Medida", 4, 1)
entrada_aplicacao = criar_campo(frame_cadastro, "Aplicacao", 4, 2)

campos_produto = [
    entrada_nome,
    entrada_quantidade,
    entrada_minimo,
    entrada_validade,
    entrada_cor,
    entrada_textura,
    entrada_peso,
    entrada_unidade,
    entrada_aplicacao,
]

tk.Button(frame_cadastro, text="Cadastrar Produto", command=cadastrar_produto).grid(
    row=6,
    column=0,
    padx=5,
    pady=10,
    sticky="w",
)

tk.Button(frame_cadastro, text="Verificar Estoque Minimo", command=verificar_estoque).grid(
    row=6,
    column=1,
    padx=5,
    pady=10,
    sticky="w",
)

colunas_produtos = (
    "ID",
    "Nome",
    "Quantidade",
    "Minimo",
    "Validade",
    "Cor",
    "Textura",
    "Peso",
    "Unidade",
    "Aplicacao",
)

lista_produtos = ttk.Treeview(aba_cadastro, columns=colunas_produtos, show="headings")

for coluna in colunas_produtos:
    lista_produtos.heading(coluna, text=coluna)
    lista_produtos.column(coluna, width=100)

lista_produtos.pack(fill="both", expand=True, padx=10, pady=10)

frame_movimentacao = tk.LabelFrame(aba_movimentacao, text="Entrada e Saida de Materiais")
frame_movimentacao.pack(fill="x", padx=10, pady=10)

tk.Label(frame_movimentacao, text="Produto").grid(row=0, column=0, sticky="w", padx=5, pady=2)
combo_produto = ttk.Combobox(frame_movimentacao, width=40, state="readonly")
combo_produto.grid(row=1, column=0, padx=5, pady=2)

entrada_qtd_movimento = criar_campo(frame_movimentacao, "Quantidade", 0, 1)
entrada_responsavel = criar_campo(frame_movimentacao, "Responsavel", 0, 2)

tk.Button(
    frame_movimentacao,
    text="Registrar Entrada",
    command=lambda: registrar_movimentacao("Entrada"),
).grid(row=2, column=0, padx=5, pady=10, sticky="w")

tk.Button(
    frame_movimentacao,
    text="Registrar Saida",
    command=lambda: registrar_movimentacao("Saida"),
).grid(row=2, column=1, padx=5, pady=10, sticky="w")

colunas_historico = ("ID", "Produto", "Tipo", "Quantidade", "Responsavel", "Data")
lista_historico = ttk.Treeview(aba_historico, columns=colunas_historico, show="headings")

for coluna in colunas_historico:
    lista_historico.heading(coluna, text=coluna)
    lista_historico.column(coluna, width=150)

lista_historico.pack(fill="both", expand=True, padx=10, pady=10)

carregar_produtos()
carregar_historico()

janela.mainloop()
