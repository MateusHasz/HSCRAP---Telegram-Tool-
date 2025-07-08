import json
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty

async def extract_members(api_id, api_hash, phone):
    client = TelegramClient(phone, int(api_id), api_hash)

    await client.start()
    print("Cliente conectado.")

    chats = []
    last_date = None
    chunk_size = 200

    print("Obtendo seus grupos e canais...")
    while True:
        result = await client(GetDialogsRequest(
            offset_date=last_date,
            offset_id=0,
            offset_peer=InputPeerEmpty(),
            limit=chunk_size,
            hash=0
        ))
        chats.extend(result.chats)

        if not result.chats:
            break
        last_date = result.chats[-1].date

    groups = []
    for chat in chats:
        try:
            if hasattr(chat, 'megagroup') and chat.megagroup == True or hasattr(chat, 'channel') and chat.channel == True:
                groups.append(chat)
        except:
            continue

    print("\nSelecione o grupo/canal para extrair membros:")
    for i, g in enumerate(groups):
        print(f"{i}. {g.title}")

    while True:
        try:
            g_index = int(input("Digite o número do grupo/canal: "))
            if 0 <= g_index < len(groups):
                target_group = groups[g_index]
                break
            else:
                print("Número inválido. Por favor, tente novamente.")
        except ValueError:
            print("Entrada inválida. Por favor, digite um número.")

    print(f"Extraindo membros do grupo: {target_group.title} ({target_group.id})")

    all_participants = []
    offset = 0
    limit = 100

    while True:
        participants = await client(GetParticipantsRequest(
            target_group,
            ChannelParticipantsSearch(""),
            offset,
            limit,
            hash=0
        ))
        if not participants.users:
            break
        all_participants.extend(participants.users)
        offset += len(participants.users)

    with open("members.json", "w", encoding="utf-8") as f:
        members_data = []
        for user in all_participants:
            member_info = {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "phone": user.phone
            }
            members_data.append(member_info)
        json.dump(members_data, f, ensure_ascii=False, indent=4)

    print(f"Total de membros extraídos: {len(all_participants)}")
    print("Membros salvos em members.json")

    await client.run_until_disconnected()

if __name__ == '__main__':
    print("Este script deve ser executado via run.py para gerenciamento de credenciais.")


