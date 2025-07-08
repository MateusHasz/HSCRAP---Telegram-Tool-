import os
import sys
import json
import asyncio
from extract_members import extract_members
from add_members import add_members

CREDENTIALS_FILE = "telegram_credentials.json"

def load_credentials():
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_credentials(credentials):
    with open(CREDENTIALS_FILE, "w", encoding="utf-8") as f:
        json.dump(credentials, f, ensure_ascii=False, indent=4)

def get_user_input(prompt, sensitive=False):
    if sensitive:
        import getpass
        return getpass.getpass(prompt)
    return input(prompt)

def add_new_account():
    print("\n--- Adicionar Nova Conta Telegram ---")
    account_name = input("Digite um nome para esta conta (ex: MinhaContaPrincipal): ")
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
    for i, name in enumerate(accounts):
        print(f"{i + 1}. {name}")

    while True:
        try:
            choice = int(input("Escolha o número da conta que deseja usar: "))
            if 1 <= choice <= len(accounts):
                selected_name = accounts[choice - 1]
                print(f"Conta \'{selected_name}\' selecionada.")
                return credentials[selected_name]
            else:
                print("Escolha inválida. Por favor, digite um número válido.")
        except ValueError:
            print("Entrada inválida. Por favor, digite um número.")

def main():
    while True:
        print("\n--- Menu Principal ---")
        print("1. Adicionar nova conta Telegram")
        print("2. Selecionar e usar conta existente")
        print("3. Sair")

        choice = input("Escolha uma opção: ")

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
                    print("1. Extrair membros de um grupo")
                    print("2. Adicionar membros a um grupo")
                    print("3. Voltar ao menu principal")

                    op_choice = input("Escolha uma operação: ")

                    if op_choice == '1':
                        print("Executando script de extração de membros...")
                        asyncio.run(extract_members(api_id, api_hash, phone))
                        break # Retorna ao menu principal após a conclusão
                    elif op_choice == '2':
                        print("Executando script de adição de membros...")
                        asyncio.run(add_members(api_id, api_hash, phone))
                        break # Retorna ao menu principal após a conclusão
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


