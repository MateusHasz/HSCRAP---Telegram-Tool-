import json
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty

# Removendo a importação de prompt_toolkit
# from prompt_toolkit.shortcuts import radiolist_dialog, checkboxlist_dialog

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

    print("\nSelecione os grupos/canals para extrair membros:")
    
    group_options = []
    for i, g in enumerate(groups):
        group_options.append((g, g.title))
        print(f"{i + 1}. {g.title}") # Adicionado para exibir as opções no console

    if not group_options:
        print("Nenhum grupo ou canal encontrado para extração.")
        await client.run_until_disconnected()
        return

    # Substituindo checkboxlist_dialog por input simples
    while True:
        try:
            choice_str = input("Escolha os números dos grupos/canais separados por vírgula (ex: 1,3,5): ")
            choices = [int(c.strip()) for c in choice_str.split(',')]
            selected_group_entities = []
            for c in choices:
                if 1 <= c <= len(groups):
                    selected_group_entities.append(groups[c - 1])
                else:
                    print(f"Opção inválida: {c}. Por favor, digite números válidos.")
                    selected_group_entities = [] # Limpa a seleção se houver erro
                    break
            if selected_group_entities:
                break
        except ValueError:
            print("Entrada inválida. Por favor, digite números separados por vírgula.")

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


