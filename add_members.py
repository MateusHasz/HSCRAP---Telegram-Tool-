import json
import time
import random
import logging
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.errors import PeerFloodError, UserPrivacyRestrictedError, UserAlreadyParticipantError, FloodWaitError

# Configuração de logging
logging.basicConfig(filename='add_members_log.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

async def add_members(api_id, api_hash, phone):
    client = TelegramClient(phone, int(api_id), api_hash)

    try:
        await client.start()
        print("Cliente conectado.")
        logging.info("Cliente Telegram conectado com sucesso.")
    except Exception as e:
        print(f"Erro ao conectar o cliente Telegram: {e}")
        logging.error(f"Erro ao conectar o cliente Telegram: {e}")
        return

    # Solicitar o nome de usuário ou ID do grupo de destino
    target_group_input = input("Digite o nome de usuário ou ID do grupo de destino (ex: @meugrupo ou -123456789): ")

    try:
        if target_group_input.startswith("@"):
            target_entity = await client.get_entity(target_group_input)
        else:
            target_entity = await client.get_entity(int(target_group_input))
    except Exception as e:
        print(f"Erro ao obter a entidade do grupo de destino: {e}")
        logging.error(f"Erro ao obter a entidade do grupo de destino '{target_group_input}': {e}")
        return

    if not hasattr(target_entity, 'participants_count'):
        print("A entidade fornecida não é um grupo ou canal válido para adicionar membros.")
        logging.warning(f"Entidade '{target_group_input}' não é um grupo ou canal válido.")
        return

    print(f"Adicionando membros ao grupo: {target_entity.title} ({target_entity.id})")
    logging.info(f"Iniciando adição de membros ao grupo: {target_entity.title} ({target_entity.id})")

    # Carregar membros do arquivo members.json (pendentes)
    try:
        with open("members.json", "r", encoding="utf-8") as f:
            all_members = json.load(f)
    except FileNotFoundError:
        print("Arquivo members.json não encontrado. Por favor, execute extract_members.py primeiro.")
        logging.error("Arquivo members.json não encontrado.")
        return
    except json.JSONDecodeError:
        print("Erro ao ler members.json. Verifique se o arquivo está formatado corretamente.")
        logging.error("Erro de decodificação JSON em members.json.")
        return

    # Carregar membros já adicionados
    try:
        with open("added_members.json", "r", encoding="utf-8") as f:
            added_members_list = json.load(f)
    except FileNotFoundError:
        added_members_list = []
        logging.info("Arquivo added_members.json não encontrado. Criando um novo.")
    except json.JSONDecodeError:
        print("Erro ao ler added_members.json. Criando um novo arquivo.")
        logging.warning("Erro de decodificação JSON em added_members.json. Criando um novo.")
        added_members_list = []

    added_member_ids = {member["id"] for member in added_members_list}

    members_to_add = [member for member in all_members if member["id"] not in added_member_ids]

    print(f"Total de membros a adicionar (excluindo já adicionados): {len(members_to_add)}")
    logging.info(f"Membros a adicionar (após filtragem de duplicatas): {len(members_to_add)}")

    added_count = 0
    failed_count = 0
    for member_info in members_to_add:
        user_id = member_info["id"]
        username = member_info["username"]
        first_name = member_info["first_name"]

        if user_id in added_member_ids:
            print(f"Membro {first_name} (@{username or user_id}) já foi adicionado anteriormente. Pulando.")
            logging.info(f"Membro {first_name} (@{username or user_id}) já adicionado. Pulando.")
            continue

        try:
            user_to_add = await client.get_input_entity(user_id)
            await client(InviteToChannelRequest(target_entity, [user_to_add]))
            print(f"Adicionado: {first_name} (@{username or user_id})")
            logging.info(f"Adicionado: {first_name} (@{username or user_id})")
            added_count += 1
            
            # Adicionar à lista de membros adicionados
            added_members_list.append(member_info)
            with open("added_members.json", "w", encoding="utf-8") as f:
                json.dump(added_members_list, f, ensure_ascii=False, indent=4)

            # Pequeno atraso para evitar flood
            time.sleep(random.uniform(5, 15)) 

        except PeerFloodError:
            print("Erro: Flood detectado. Sua conta pode estar limitada. Aguarde um tempo e tente novamente.")
            logging.error(f"PeerFloodError detectado. Pausando por 10-20 minutos.")
            time.sleep(random.uniform(600, 1200)) # Pausa de 10 a 20 minutos
            failed_count += 1
            continue
        except UserPrivacyRestrictedError:
            print(f"Não foi possível adicionar {first_name} (@{username or user_id}): Restrição de privacidade do usuário.")
            logging.warning(f"Falha ao adicionar {first_name} (@{username or user_id}): Restrição de privacidade.")
            failed_count += 1
        except UserAlreadyParticipantError:
            print(f"{first_name} (@{username or user_id}) já é participante do grupo.")
            logging.info(f"{first_name} (@{username or user_id}) já é participante.")
            # Se já é participante, considere como adicionado para não tentar novamente
            added_members_list.append(member_info)
            with open("added_members.json", "w", encoding="utf-8") as f:
                json.dump(added_members_list, f, ensure_ascii=False, indent=4)
        except FloodWaitError as e:
            wait_time = e.seconds + random.uniform(10, 30) # Adiciona um pouco mais de tempo
            print(f"Erro: FloodWaitError detectado. Aguardando {wait_time:.0f} segundos.")
            logging.warning(f"FloodWaitError detectado. Aguardando {wait_time:.0f} segundos.")
            time.sleep(wait_time)
            failed_count += 1
            continue
        except Exception as e:
            print(f"Erro inesperado ao adicionar {first_name} (@{username or user_id}): {e}")
            logging.error(f"Erro inesperado ao adicionar {first_name} (@{username or user_id}): {e}")
            failed_count += 1
        
        # Atraso maior a cada X membros para simular comportamento humano
        if added_count % 10 == 0 and added_count > 0:
            print(f"Adicionados {added_count} membros. Fazendo uma pausa maior...")
            logging.info(f"Adicionados {added_count} membros. Fazendo uma pausa maior.")
            time.sleep(random.uniform(60, 180)) # Pausa de 1 a 3 minutos

    # Atualizar members.json (lista de pendentes) após a execução
    remaining_members = [member for member in all_members if member["id"] not in added_member_ids]
    with open("members.json", "w", encoding="utf-8") as f:
        json.dump(remaining_members, f, ensure_ascii=False, indent=4)

    final_message = f"Processo de adição concluído. Total de membros adicionados nesta sessão: {added_count}. " \
                    f"Membros restantes para adicionar: {len(remaining_members)}. " \
                    f"Membros que falharam ao adicionar: {failed_count}."
    print(final_message)
    logging.info(final_message)

    await client.run_until_disconnected()

if __name__ == '__main__':
    print("Este script deve ser executado via run.py para gerenciamento de credenciais.")


