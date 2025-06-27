import os
import json
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

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

    # Solicitar o nome de usuário ou ID do grupo
    group_input = input("Digite o nome de usuário ou ID do grupo (ex: @meugrupo ou -123456789): ")

    try:
        if group_input.startswith("@"):
            entity = await client.get_entity(group_input)
        else:
            entity = await client.get_entity(int(group_input))
    except Exception as e:
        print(f"Erro ao obter a entidade do grupo: {e}")
        return

    if not hasattr(entity, 'participants_count'):
        print("A entidade fornecida não é um grupo ou canal válido para extração de membros.")
        return

    print(f"Extraindo membros do grupo: {entity.title} ({entity.id})")

    all_participants = []
    offset = 0
    limit = 100

    while True:
        participants = await client(GetParticipantsRequest(
            entity,
            ChannelParticipantsSearch(''),
            offset,
            limit,
            hash=0
        ))
        if not participants.users:
            break
        all_participants.extend(participants.users)
        offset += len(participants.users)

    with open('members.json', 'w', encoding='utf-8') as f:
        members_data = []
        for user in all_participants:
            member_info = {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.username,
                'phone': user.phone
            }
            members_data.append(member_info)
        json.dump(members_data, f, ensure_ascii=False, indent=4)

    print(f"Total de membros extraídos: {len(all_participants)}")
    print("Membros salvos em members.json")

    await client.run_until_disconnected()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())


