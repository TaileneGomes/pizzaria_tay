import tkinter as tk
from tkinter import messagebox
import re
import mysql.connector

# Conectar ao MySQL
tgs = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='',
    database='pizzaria_tay'
)

# Função para inserir um cliente no banco de dados
def inserir_cliente(nome, telefone, email):
    cursor = tgs.cursor()
    try:
        cursor.execute('''
            INSERT INTO clientes (nome, telefone, email)
            VALUES (%s, %s, %s)
        ''', (nome, telefone, email))
        tgs.commit()
        messagebox.showinfo("Cliente Cadastrado", "Cliente cadastrado com sucesso!")
    except mysql.connector.Error as err:
        messagebox.showerror("Erro", f"Erro ao inserir cliente: {err}")
    finally:
        cursor.close()

# Função para validar email
def validar_email(email):
    if re.match(r'^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$', email):
        return True
    else:
        return False

# Função para validar e cadastrar um cliente
def cadastrar_cliente():
    nome = entry_nome.get().strip()
    telefone = entry_telefone.get().strip()
    email = entry_email.get().strip()

    if nome == "" or telefone == "" or email == "":
        messagebox.showerror("Erro", "Por favor, preencha todos os campos.")
    elif not validar_email(email):
        messagebox.showerror("Erro", "Por favor, insira um email válido.")
    else:
        inserir_cliente(nome, telefone, email)

# Configurações da janela principal
root = tk.Tk()
root.title("Cadastro de Clientes")
root.geometry("400x300")
root.configure(bg="#99ccff")  # Cor de fundo

# Widgets
label_titulo = tk.Label(root, text="Cadastro de Clientes", font=("Arial", 18), bg="#3399ff")
label_titulo.pack(pady=10)

label_nome = tk.Label(root, text="Nome:", bg="#99ccff")
label_nome.pack(pady=5)

entry_nome = tk.Entry(root)
entry_nome.pack(pady=5)

label_telefone = tk.Label(root, text="Telefone:", bg="#99ccff")
label_telefone.pack(pady=5)

entry_telefone = tk.Entry(root)
entry_telefone.pack(pady=5)

label_email = tk.Label(root, text="Email:", bg="#99ccff")
label_email.pack(pady=5)

entry_email = tk.Entry(root)
entry_email.pack(pady=5)

button_cadastrar = tk.Button(root, text="Cadastrar Cliente", command=cadastrar_cliente)
button_cadastrar.pack(pady=20)

root.mainloop()
