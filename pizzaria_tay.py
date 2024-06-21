import tkinter as tk
from tkinter import messagebox
import datetime
import mysql.connector

# Conectar ao MySQL
tgs = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='',
    database='pizzaria_tay'
)

# Verificar se o banco de dados existe
cursor = tgs.cursor()
cursor.execute('SELECT COUNT(*) FROM information_schema.SCHEMATA WHERE SCHEMA_NAME = "pizzaria_tay";')
num_results = cursor.fetchone()[0]

# Se o banco de dados não existe, criá-lo
if num_results == 0:
    cursor.execute('CREATE DATABASE pizzaria_tay;')
    tgs.commit()

    # Reconectar especificando o banco de dados recém-criado
    tgs = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='',
        database='pizzaria_tay'
    )
    cursor = tgs.cursor()

    # Criar tabelas
    cursor.execute('''
        CREATE TABLE pedidos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            data DATE NOT NULL,
            tamanho VARCHAR(255),
            quantidade INT,
            valor_total DECIMAL(10,2) NOT NULL
        )
    ''')
    #Criar contatos
    cursor.execute('''
        CREATE TABLE clientes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            endereco VARCHAR(255) NOT NULL,
            telefone VARCHAR(20) NOT NULL
        )
    ''')

    tgs.commit()

# Função para inserir um pedido no banco de dados
def inserir_pedido(data, tamanho, quantidade, valor_total):
    cursor.execute('''
        INSERT INTO pedidos (data, tamanho, quantidade, valor_total)
        VALUES (%s, %s, %s, %s)
    ''', (data, tamanho, quantidade, valor_total))
    tgs.commit()

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

            # Inserir pedido no banco de dados
            inserir_pedido(data_atual, tamanho, quantidade, total)

            messagebox.showinfo("Pedido Confirmado", "Seu pedido foi realizado com sucesso!")
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira uma quantidade válida (número positivo).")

# Configurações da janela principal
root = tk.Tk()
root.title("Pizzaria da Tay")
root.geometry("400x600")
root.configure(bg="#99ccff")  # Cor de fundo

# Variáveis
tamanhos = ["Pequena", "Média", "Grande"]
precos = {"Pequena": 18.00, "Média": 30.00, "Grande": 50.00}

ingredientes = ["Queijo Extra", "Pepperoni", "Bacon"]
precos_ingredientes = {"Queijo Extra": 6.00, "Pepperoni": 8.00, "Bacon": 11.00}

bordas = ["Catupiry", "Chocolate Branco", "Chocolate Preto"]
precos_bordas = {"Catupiry": 10.00, "Chocolate Branco": 12.00, "Chocolate Preto": 15.00}

var_tamanho = tk.StringVar(value=tamanhos[0])
var_ingredientes = {ingrediente: tk.BooleanVar() for ingrediente in ingredientes}
var_bordas = {borda: tk.BooleanVar() for borda in bordas}

# Widgets
label_titulo = tk.Label(root, text="Pizzaria da Tay", font=("Arial", 18), bg="#3399ff")
label_titulo.grid(row=0, column=0, columnspan=2, pady=10, padx=20)

label_precos = tk.Label(root, text="Preços: Pequena: R$18.00, Média: R$30.00, Grande: R$50.00", bg="#99ccff")
label_precos.grid(row=1, column=0, columnspan=2, pady=5, padx=20)

label_tamanho = tk.Label(root, text="Tamanho da Pizza:", bg="#99ccff")
label_tamanho.grid(row=2, column=0, pady=5, padx=20, sticky='e')

optionmenu_tamanho = tk.OptionMenu(root, var_tamanho, *tamanhos)
optionmenu_tamanho.grid(row=2, column=1, pady=5, padx=20, sticky='w')

label_quantidade = tk.Label(root, text="Quantidade:", bg="#99ccff")
label_quantidade.grid(row=3, column=0, pady=5, padx=20, sticky='e')

entry_quantidade = tk.Entry(root)
entry_quantidade.grid(row=3, column=1, pady=5, padx=20, sticky='w')

label_ingredientes = tk.Label(root, text="Ingredientes Adicionais:", font=("Arial", 14), bg="#99ccff")
label_ingredientes.grid(row=4, column=0, columnspan=2, pady=10, padx=20)

for i, ingrediente in enumerate(ingredientes):
    checkbutton = tk.Checkbutton(root, text=ingrediente, variable=var_ingredientes[ingrediente], bg="#99ccff")
    checkbutton.grid(row=5 + i, column=0, columnspan=2, pady=2, padx=20, sticky='w')

label_bordas = tk.Label(root, text="Opções de Borda:", font=("Arial", 14), bg="#99ccff")
label_bordas.grid(row=8, column=0, columnspan=2, pady=10, padx=20)

for j, borda in enumerate(bordas):
    checkbutton = tk.Checkbutton(root, text=borda, variable=var_bordas[borda], bg="#99ccff")
    checkbutton.grid(row=9 + j, column=0, columnspan=2, pady=2, padx=20, sticky='w')

button_pedir = tk.Button(root, text="Pedir", command=lambda: [calcular_total(), confirmar_pedido()])
button_pedir.grid(row=12, column=0, columnspan=2, pady=20, padx=20)

label_total = tk.Label(root, text="Total a Pagar: R$0.00", font=("Arial", 14), bg="#99ccff")
label_total.grid(row=13, column=0, columnspan=2, pady=10, padx=20)

root.mainloop()
