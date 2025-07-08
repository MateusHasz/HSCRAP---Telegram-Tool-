import json
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
from prompt_toolkit.shortcuts import radiolist_dialog, checkboxlist_dialog

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

    print("\nSelecione os grupos/canais para extrair membros:")
    
    group_options = []
    for i, g in enumerate(groups):
        group_options.append((g, g.title))

    if not group_options:
        print("Nenhum grupo ou canal encontrado para extração.")
        await client.run_until_disconnected()
        return

    selected_group_entities = checkboxlist_dialog(
        title="Selecionar Grupos/Canais",
        text="Escolha os grupos/canais para extrair membros (use espaço para selecionar/desselecionar, Enter para confirmar):",
        values=group_options
    ).run()

    if not selected_group_entities:
        print("Nenhum grupo/canal selecionado. Operação cancelada.")
        await client.run_until_disconnected()
        return

    all_extracted_members = []
    extracted_member_ids = set()

    for target_group in selected_group_entities:
        print(f"Extraindo membros do grupo: {target_group.title} ({target_group.id})")

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
            for user in participants.users:
                if user.id not in extracted_member_ids:
                    member_info = {
                        "id": user.id,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "username": user.username,
                        "phone": user.phone
                    }
                    all_extracted_members.append(member_info)
                    extracted_member_ids.add(user.id)
            offset += len(participants.users)

    with open("members.json", "w", encoding="utf-8") as f:
        json.dump(all_extracted_members, f, ensure_ascii=False, indent=4)

    print(f"Total de membros extraídos (sem duplicatas): {len(all_extracted_members)}")
    print("Membros salvos em members.json")

    await client.run_until_disconnected()

if __name__ == '__main__':
    print("Este script deve ser executado via run.py para gerenciamento de credenciais.")


