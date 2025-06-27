import os
import sys
import subprocess

def set_environment_variables():
    print("\n--- Configuração de Credenciais do Telegram ---")
    api_id = input("Digite seu API ID (my.telegram.org/apps): ")
    api_hash = input("Digite seu API Hash: ")
    phone = input("Digite seu número de telefone (ex: +5511987654321): ")

    os.environ["TELEGRAM_API_ID"] = api_id
    os.environ["TELEGRAM_API_HASH"] = api_hash
    os.environ["TELEGRAM_PHONE_NUMBER"] = phone
    print("Credenciais configuradas para esta sessão.")

def main():
    set_environment_variables()

    while True:
        print("\n--- Menu Principal ---")
        print("1. Extrair membros de um grupo")
        print("2. Adicionar membros a um grupo")
        print("3. Sair")

        choice = input("Escolha uma opção: ")

        if choice == '1':
            print("Executando script de extração de membros...")
            subprocess.run([sys.executable, "extract_members.py"])
        elif choice == '2':
            print("Executando script de adição de membros...")
            subprocess.run([sys.executable, "add_members.py"])
        elif choice == '3':
            print("Saindo...")
            break
        else:
            print("Opção inválida. Por favor, tente novamente.")

if __name__ == '__main__':
    main()


