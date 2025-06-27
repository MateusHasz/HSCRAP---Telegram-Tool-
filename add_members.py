import os
import json
import time
import random
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.errors import PeerFloodError, UserPrivacyRestrictedError, UserAlreadyParticipantError

# Carregar configurações de variáveis de ambiente
api_id = os.environ.get("TELEGRAM_API_ID")
api_hash = os.environ.get("TELEGRAM_API_HASH")
phone = os.environ.get("TELEGRAM_PHONE_NUMBER")

if not all([api_id, api_hash, phone]):
    print("Por favor, defina as variáveis de ambiente TELEGRAM_API_ID, TELEGRAM_API_HASH e TELEGRAM_PHONE_NUMBER.")
    print("Exemplo: export TELEGRAM_API_ID=\"1234567\"")
    print("Exemplo: export TELEGRAM_API_HASH=\"abcdef1234567890abcdef1234567890\"")
    print("Exemplo: export TELEGRAM_PHONE_NUMBER=\"+5511987654321\"")
    exit(1)

client = TelegramClient(phone, int(api_id), api_hash)

async def main():
    await client.start()
    print("Cliente conectado.")

    # Solicitar o nome de usuário ou ID do grupo de destino
    target_group_input = input("Digite o nome de usuário ou ID do grupo de destino (ex: @meugrupo ou -123456789): ")

    try:
        if target_group_input.startswith("@"):
            target_entity = await client.get_entity(target_group_input)
        else:
            target_entity = await client.get_entity(int(target_group_input))
    except Exception as e:
        print(f"Erro ao obter a entidade do grupo de destino: {e}")
        return

    if not hasattr(target_entity, 'participants_count'):
        print("A entidade fornecida não é um grupo ou canal válido para adicionar membros.")
        return

    print(f"Adicionando membros ao grupo: {target_entity.title} ({target_entity.id})")

    # Carregar membros do arquivo members.json
    try:
        with open("members.json", "r", encoding="utf-8") as f:
            members_to_add = json.load(f)
    except FileNotFoundError:
        print("Arquivo members.json não encontrado. Por favor, execute extract_members.py primeiro.")
        return

    print(f"Total de membros a adicionar: {len(members_to_add)}")

    added_count = 0
    for member_info in members_to_add:
        user_id = member_info["id"]
        username = member_info["username"]
        first_name = member_info["first_name"]

        try:
            user_to_add = await client.get_input_entity(user_id)
            await client(InviteToChannelRequest(target_entity, [user_to_add]))
            print(f"Adicionado: {first_name} (@{username or user_id})")
            added_count += 1
            # Pequeno atraso para evitar flood
            time.sleep(random.uniform(5, 15)) 

        except PeerFloodError:
            print("Erro: Flood detectado. Sua conta pode estar limitada. Aguarde um tempo e tente novamente.")
            print("Pausa longa para evitar banimento.")
            time.sleep(random.uniform(600, 1200)) # Pausa de 10 a 20 minutos
            continue
        except UserPrivacyRestrictedError:
            print(f"Não foi possível adicionar {first_name} (@{username or user_id}): Restrição de privacidade do usuário.")
        except UserAlreadyParticipantError:
            print(f"{first_name} (@{username or user_id}) já é participante do grupo.")
        except Exception as e:
            print(f"Erro ao adicionar {first_name} (@{username or user_id}): {e}")
        
        # Atraso maior a cada X membros para simular comportamento humano
        if added_count % 10 == 0 and added_count > 0:
            print(f"Adicionados {added_count} membros. Fazendo uma pausa maior...")
            time.sleep(random.uniform(60, 180)) # Pausa de 1 a 3 minutos

    print(f"Processo de adição concluído. Total de membros adicionados: {added_count}")
    await client.run_until_disconnected()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())


