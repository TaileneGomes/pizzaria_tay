import tkinter as tk
from tkinter import ttk, messagebox
import datetime # Importa o módulo datetime para trabalhar com datas
import mysql.connector # Importa o módulo mysql.connector para conectar ao Mysql

# Conectar ao MySQL
try:
    tgs = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',  # Insira sua senha do MySQL aqui
        database='pizzaria_tay'
    )

    # Verifica se o banco de dados existe
    cursor = tgs.cursor()
    cursor.execute('SELECT COUNT(*) FROM information_schema.SCHEMATA WHERE SCHEMA_NAME = "pizzaria_tay";')
    num_results = cursor.fetchone()[0]

    # Se o banco de dados não existe, criá-lo
    if num_results == 0:
        cursor.execute('CREATE DATABASE pizzaria_tay;')
        tgs.commit()

        # Reconectar especificando o banco de dados recém-criado
        tgs = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',  # Insira sua senha do MySQL aqui
            database='pizzaria_tay'
        )
        cursor = tgs.cursor()

        # Criar tabelas
        cursor.execute('''
            CREATE TABLE pedidos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                cliente_id INT,
                data DATE NOT NULL,
                tamanho VARCHAR(255),
                quantidade INT,
                valor_total DECIMAL(10,2) NOT NULL,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE clientes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                endereco VARCHAR(255) NOT NULL,
                telefone VARCHAR(20) NOT NULL,
                email VARCHAR(255)
            )
        ''')

        tgs.commit()

except mysql.connector.Error as err:
    print(f"Erro ao conectar ao MySQL: {err}")

# Função para inserir um pedido no banco de dados
def inserir_pedido(cliente_id, data, tamanho, quantidade, valor_total):
    try:
        cursor.execute('''
            INSERT INTO pedidos (cliente_id, data, tamanho, quantidade, valor_total)
            VALUES (%s, %s, %s, %s, %s)
        ''', (cliente_id, data, tamanho, quantidade, valor_total))
        tgs.commit()
    except mysql.connector.Error as err:
        print(f"Erro ao inserir pedido no banco de dados: {err}")

# Função para inserir um cliente no banco de dados
def inserir_cliente(nome, endereco, telefone, email):
    try:
        cursor.execute('''
            INSERT INTO clientes (nome, endereco, telefone, email)
            VALUES (%s, %s, %s, %s)
        ''', (nome, endereco, telefone, email))
        tgs.commit()
    except mysql.connector.Error as err:
        print(f"Erro ao inserir cliente no banco de dados: {err}")

# Função para buscar clientes cadastrados
def buscar_clientes():
    cursor.execute('SELECT * FROM clientes')
    return cursor.fetchall()

# Função para buscar um cliente pelo nome
def buscar_cliente_por_nome(nome):
    cursor.execute('SELECT * FROM clientes WHERE nome = %s', (nome,))
    return cursor.fetchone()

# Função para calcular o total a pagar
def calcular_total():
    try:
        quantidade = int(entry_quantidade.get())
        if quantidade <= 0:
            raise ValueError("A quantidade deve ser um número positivo.")

        tamanho = var_tamanho.get()
        total = precos[tamanho] * quantidade
        
        for ingrediente, var in var_ingredientes.items():
            if var.get():
                total += precos_ingredientes[ingrediente] * quantidade

        for borda, var in var_bordas.items():
            if var.get():
                total += precos_bordas[borda] * quantidade
        
        label_total.config(text=f"Total a Pagar: R${total:.2f}")
    except ValueError as e:
        messagebox.showerror("Erro", str(e))

# Função para confirmar o pedido
def confirmar_pedido():
    resposta = messagebox.askyesno("Confirmar Pedido", "Você deseja confirmar o pedido?")
    if resposta:
        try:
            quantidade = int(entry_quantidade.get())
            tamanho = var_tamanho.get()
            total = precos[tamanho] * quantidade
            
            for ingrediente, var in var_ingredientes.items():
                if var.get():
                    total += precos_ingredientes[ingrediente] * quantidade

            for borda, var in var_bordas.items():
                if var.get():
                    total += precos_bordas[borda] * quantidade

            # Obter a data atual
            data_atual = datetime.datetime.now().date()

            # Buscar o cliente selecionado
            nome_cliente = var_cliente.get()
            cliente = buscar_cliente_por_nome(nome_cliente)
            
            if not cliente:
                raise ValueError("Cliente não encontrado.")
            
            cliente_id = cliente[0]

            # Inserir pedido no banco de dados
            inserir_pedido(cliente_id, data_atual, tamanho, quantidade, total)

            messagebox.showinfo("Pedido Confirmado", "Seu pedido foi realizado com sucesso!")
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
        except mysql.connector.Error as err:
            messagebox.showerror("Erro MySQL", f"Erro ao inserir pedido no banco de dados: {err}")

# Função para atualizar a lista de clientes na Treeview
def atualizar_lista_clientes():
    for i in treeview.get_children():
        treeview.delete(i)
    
    clientes = buscar_clientes()
    for cliente in clientes:
        treeview.insert("", "end", values=(cliente[1], cliente[2], cliente[3], cliente[4]))

# Função para cadastrar um novo cliente
def cadastrar_novo_cliente():
    nome = entry_nome_cliente.get().strip()
    endereco = entry_endereco_cliente.get().strip()
    telefone = entry_telefone_cliente.get().strip()
    email = entry_email_cliente.get().strip()

    if nome == "" or endereco == "" or telefone == "":
        messagebox.showerror("Erro", "Por favor, preencha todos os campos obrigatórios.")
    else:
        try:
            inserir_cliente(nome, endereco, telefone, email)
            messagebox.showinfo("Cliente Cadastrado", "Cliente cadastrado com sucesso!")
            atualizar_lista_clientes()
        except mysql.connector.Error as err:
            messagebox.showerror("Erro", f"Erro ao cadastrar cliente: {err}")

# Configurações da janela principal
root = tk.Tk()
root.title("Pizzaria da Tay")
root.geometry("600x600")
root.configure(bg="#99ccff")  # Cor de fundo

# Variáveis globais
tamanhos = ["Pequena", "Média", "Grande"]
precos = {"Pequena": 18.00, "Média": 30.00, "Grande": 50.00}

ingredientes = ["Queijo Extra", "Pepperoni", "Bacon"]
precos_ingredientes = {"Queijo Extra": 6.00, "Pepperoni": 8.00, "Bacon": 11.00}

bordas = ["Catupiry", "Chocolate Branco", "Chocolate Preto"]
precos_bordas = {"Catupiry": 10.00, "Chocolate Branco": 12.00, "Chocolate Preto": 15.00}

var_tamanho = tk.StringVar(value=tamanhos[0])
var_ingredientes = {ingrediente: tk.BooleanVar() for ingrediente in ingredientes}
var_bordas = {borda: tk.BooleanVar() for borda in bordas}

# Abas
notebook = ttk.Notebook(root)
notebook.pack(pady=10)

# Aba de Pedidos
frame_pedidos = ttk.Frame(notebook)
notebook.add(frame_pedidos, text='Pedidos')

label_titulo_pedidos = tk.Label(frame_pedidos, text="Pizzaria da Tay - Pedidos", font=("Arial", 18), bg="#3399ff")
label_titulo_pedidos.grid(row=0, column=0, columnspan=2, pady=10, padx=20)

label_precos = tk.Label(frame_pedidos, text="Preços: Pequena: R$18.00, Média: R$30.00, Grande: R$50.00", bg="#99ccff")
label_precos.grid(row=1, column=0, columnspan=2, pady=5, padx=20)

label_tamanho = tk.Label(frame_pedidos, text="Tamanho da Pizza:", bg="#99ccff")
label_tamanho.grid(row=2, column=0, pady=5, padx=20, sticky='e')

optionmenu_tamanho = tk.OptionMenu(frame_pedidos, var_tamanho, *tamanhos)
optionmenu_tamanho.grid(row=2, column=1, pady=5, padx=20, sticky='w')

label_quantidade = tk.Label(frame_pedidos, text="Quantidade:", bg="#99ccff")
label_quantidade.grid(row=3, column=0, pady=5, padx=20, sticky='e')

entry_quantidade = tk.Entry(frame_pedidos)
entry_quantidade.grid(row=3, column=1, pady=5, padx=20, sticky='w')

label_ingredientes = tk.Label(frame_pedidos, text="Ingredientes Adicionais:", font=("Arial", 14), bg="#99ccff")
label_ingredientes.grid(row=4, column=0, columnspan=2, pady=10, padx=20)

for i, ingrediente in enumerate(ingredientes):
    checkbutton = tk.Checkbutton(frame_pedidos, text=ingrediente, variable=var_ingredientes[ingrediente], bg="#99ccff")
    checkbutton.grid(row=5 + i, column=0, columnspan=2, pady=2, padx=20, sticky='w')

label_bordas = tk.Label(frame_pedidos, text="Opções de Borda:", font=("Arial", 14), bg="#99ccff")
label_bordas.grid(row=8, column=0, columnspan=2, pady=10, padx=20)

for j, borda in enumerate(bordas):
    checkbutton = tk.Checkbutton(frame_pedidos, text=borda, variable=var_bordas[borda], bg="#99ccff")
    checkbutton.grid(row=9 + j, column=0, columnspan=2, pady=2, padx=20, sticky='w')

clientes = [cliente[1] for cliente in buscar_clientes()]
if clientes:
    var_cliente = tk.StringVar(value=clientes[0])
    optionmenu_cliente = tk.OptionMenu(frame_pedidos, var_cliente, *clientes)
else:
    var_cliente = tk.StringVar()
    optionmenu_cliente = tk.OptionMenu(frame_pedidos, var_cliente, "")
label_cliente = tk.Label(frame_pedidos, text="Selecione o Cliente:", bg="#99ccff")
label_cliente.grid(row=12, column=0, pady=5, padx=20, sticky='e')
optionmenu_cliente.grid(row=12, column=1, pady=5, padx=20, sticky='w')

button_pedir = tk.Button(frame_pedidos, text="Pedir", command=lambda: [calcular_total(), confirmar_pedido()])
button_pedir.grid(row=13, column=0, columnspan=2, pady=20, padx=20)

label_total = tk.Label(frame_pedidos, text="Total a Pagar: R$0.00", font=("Arial", 14), bg="#99ccff")
label_total.grid(row=14, column=0, columnspan=2, pady=10, padx=20)

# Aba de Clientes
frame_clientes = ttk.Frame(notebook)
notebook.add(frame_clientes, text='Clientes')

label_titulo_clientes = tk.Label(frame_clientes, text="Pizzaria da Tay - Clientes", font=("Arial", 18), bg="#3399ff")
label_titulo_clientes.grid(row=0, column=0, columnspan=2, pady=10, padx=20)

# Widgets para cadastro de clientes
label_nome_cliente = tk.Label(frame_clientes, text="Nome:", bg="#99ccff")
label_nome_cliente.grid(row=1, column=0, pady=5, padx=20, sticky='e')

entry_nome_cliente = tk.Entry(frame_clientes)
entry_nome_cliente.grid(row=1, column=1, pady=5, padx=20, sticky='w')

label_endereco_cliente = tk.Label(frame_clientes, text="Endereço:", bg="#99ccff")
label_endereco_cliente.grid(row=2, column=0, pady=5, padx=20, sticky='e')

entry_endereco_cliente = tk.Entry(frame_clientes)
entry_endereco_cliente.grid(row=2, column=1, pady=5, padx=20, sticky='w')

label_telefone_cliente = tk.Label(frame_clientes, text="Telefone:", bg="#99ccff")
label_telefone_cliente.grid(row=3, column=0, pady=5, padx=20, sticky='e')

entry_telefone_cliente = tk.Entry(frame_clientes)
entry_telefone_cliente.grid(row=3, column=1, pady=5, padx=20, sticky='w')

label_email_cliente = tk.Label(frame_clientes, text="Email:", bg="#99ccff")
label_email_cliente.grid(row=4, column=0, pady=5, padx=20, sticky='e')

entry_email_cliente = tk.Entry(frame_clientes)
entry_email_cliente.grid(row=4, column=1, pady=5, padx=20, sticky='w')

button_cadastrar_cliente = tk.Button(frame_clientes, text="Cadastrar Cliente", command=cadastrar_novo_cliente)
button_cadastrar_cliente.grid(row=5, column=0, columnspan=2, pady=20)

# Treeview para exibir clientes cadastrados
treeview = ttk.Treeview(frame_clientes, columns=('Nome', 'Endereço', 'Telefone', 'Email'), show='headings')
treeview.heading('Nome', text='Nome')
treeview.heading('Endereço', text='Endereço')
treeview.heading('Telefone', text='Telefone')
treeview.heading('Email', text='Email')
treeview.grid(row=6, column=0, columnspan=2, pady=10, padx=20)

# Atualizar a lista de clientes na inicialização
atualizar_lista_clientes()

# Iniciar a interface gráfica
root.mainloop()
