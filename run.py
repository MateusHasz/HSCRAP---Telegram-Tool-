import os
import sys
import json
import asyncio
from extract_members import extract_members
from add_members import add_members
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.shortcuts import radiolist_dialog

CREDENTIALS_FILE = "telegram_credentials.json"

def load_credentials():
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_credentials(credentials):
    with open(CREDENTIALS_FILE, "w", encoding="utf-8") as f:
        json.dump(credentials, f, ensure_ascii=False, indent=4)

def get_user_input(prompt_text, sensitive=False):
    if sensitive:
        import getpass
        return getpass.getpass(prompt_text)
    return prompt(prompt_text)

def add_new_account():
    print("\n--- Adicionar Nova Conta Telegram ---")
    account_name = get_user_input("Digite um nome para esta conta (ex: MinhaContaPrincipal): ")
    api_id = get_user_input("Digite seu API ID (my.telegram.org/apps): ")
    api_hash = get_user_input("Digite seu API Hash: ", sensitive=True)
    phone = get_user_input("Digite seu número de telefone (ex: +5511987654321): ")

    credentials = load_credentials()
    credentials[account_name] = {
        "api_id": api_id,
        "api_hash": api_hash,
        "phone": phone
    }
    save_credentials(credentials)
    print(f"Conta \'{account_name}\' salva com sucesso.")

def select_account():
    credentials = load_credentials()
    if not credentials:
        print("Nenhuma conta salva. Por favor, adicione uma nova conta primeiro.")
        return None

    print("\n--- Selecionar Conta Telegram ---")
    accounts = list(credentials.keys())
    
    # Usar radiolist_dialog para seleção interativa
    values = [(name, name) for name in accounts]
    
    if not values:
        print("Nenhuma conta disponível para seleção.")
        return None

    selected_name = radiolist_dialog(
        title="Selecionar Conta",
        text="Escolha a conta que deseja usar:",
        values=values
    ).run()

    if selected_name:
        print(f"Conta \'{selected_name}\' selecionada.")
        return credentials[selected_name]
    else:
        print("Nenhuma conta selecionada.")
        return None

def main():
    while True:
        print("\n--- Menu Principal ---")
        menu_options = [
            ("1", "Adicionar nova conta Telegram"),
            ("2", "Selecionar e usar conta existente"),
            ("3", "Sair")
        ]
        
        choice = radiolist_dialog(
            title="Menu Principal",
            text="Escolha uma opção:",
            values=menu_options
        ).run()

        if choice == '1':
            add_new_account()
        elif choice == '2':
            selected_account = select_account()
            if selected_account:
                api_id = selected_account["api_id"]
                api_hash = selected_account["api_hash"]
                phone = selected_account["phone"]

                while True:
                    print("\n--- Operações da Conta ---")
                    op_options = [
                        ("1", "Extrair membros de um grupo"),
                        ("2", "Adicionar membros a um grupo"),
                        ("3", "Voltar ao menu principal")
                    ]
                    op_choice = radiolist_dialog(
                        title="Operações da Conta",
                        text="Escolha uma operação:",
                        values=op_options
                    ).run()

                    if op_choice == '1':
                        print("Executando script de extração de membros...")
                        asyncio.run(extract_members(api_id, api_hash, phone))
                        break
                    elif op_choice == '2':
                        print("Executando script de adição de membros...")
                        asyncio.run(add_members(api_id, api_hash, phone))
                        break
                    elif op_choice == '3':
                        break
                    else:
                        print("Opção inválida. Por favor, tente novamente.")
        elif choice == '3':
            print("Saindo...")
            break
        else:
            print("Opção inválida. Por favor, tente novamente.")

if __name__ == '__main__':
    main()


