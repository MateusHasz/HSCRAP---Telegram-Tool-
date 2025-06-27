# Guia de Uso: HSCRAP - Telegram Tool

Este guia detalha como usar a ferramenta Python para extrair membros de grupos do Telegram e adicioná-los a outros grupos, com foco na execução em Termux no Android.

## Pré-requisitos

1.  **Termux**: Instale o Termux na sua no F-Droid.
2.  **Python**: O Python 3 deve estar instalado no seu Termux. Você pode instalá-lo com `pkg install python`.
3.  **Telethon**: A biblioteca Telethon é essencial para interagir com a API do Telegram. Será instalada automaticamente.
4.  **Credenciais da API do Telegram**: Você precisará do seu `api_id` e `api_hash`. Obtenha-os em [my.telegram.org/apps](https://my.telegram.org/apps).
5.  **Número de Telefone**: O número de telefone associado à sua conta do Telegram, incluindo o código do país (ex: `+5511987654321`).

## Configuração do Ambiente

### 1. Instalar dependências

Navegue até o diretório onde você salvou os scripts (`extract_members.py`, `add_members.py` e `run.py`) e instale as dependências:

```bash
pip install -r requirements.txt
```

## Uso da Aplicação

Para iniciar a aplicação, execute o script `run.py`:

```bash
python run.py
```

O script `run.py` agora oferece um menu para gerenciar suas contas do Telegram e executar as operações de extração e adição de membros:

### Menu Principal:

1.  **Adicionar nova conta Telegram**: Permite que você insira seu `api_id`, `api_hash` e número de telefone e salve essas credenciais com um nome de sua escolha. As credenciais serão armazenadas em um arquivo `telegram_credentials.json`.
2.  **Selecionar e usar conta existente**: Lista todas as contas salvas e permite que você escolha qual delas deseja usar para a sessão atual. Após selecionar uma conta, você terá acesso às operações de extração e adição de membros.
3.  **Sair**: Encerra a aplicação.

### Operações da Conta (após selecionar uma conta):

1.  **Extrair membros de um grupo**: Ao selecionar esta opção, o script listará todos os grupos e canais que sua conta participa. Você poderá então escolher o grupo/canal desejado digitando o número correspondente. Após a execução, os membros serão salvos em um arquivo `members.json` no mesmo diretório.
2.  **Adicionar membros a um grupo**: O script pedirá que você digite o nome de usuário ou o ID numérico do grupo de destino. Ele lerá os membros do arquivo `members.json` e tentará adicioná-los um por um automaticamente.
3.  **Voltar ao menu principal**: Retorna ao menu de seleção de contas.

## Proteções Anti-Spam e Limitações

O script `add_members.py` inclui algumas proteções para minimizar o risco de sua conta ser banida ou limitada por spam:

*   **Atrasos Aleatórios**: Pequenos atrasos aleatórios são inseridos entre cada adição de membro para simular um comportamento mais humano.
*   **Pausas Maiores**: Após cada 10 membros adicionados, uma pausa mais longa (1 a 3 minutos) é aplicada.
*   **Tratamento de `PeerFloodError`**: Se o Telegram detectar um comportamento de flood (`PeerFloodError`), o script fará uma pausa muito longa (10 a 20 minutos) para evitar o banimento da conta. É crucial respeitar essas pausas.
*   **Tratamento de `UserPrivacyRestrictedError`**: Membros com restrições de privacidade que impedem a adição direta serão ignorados.
*   **Tratamento de `UserAlreadyParticipantError`**: Membros que já estão no grupo de destino serão ignorados.

**Importante:** Mesmo com essas proteções, o uso excessivo ou abusivo da ferramenta pode levar a limitações ou banimento da sua conta pelo Telegram. Use com moderação e responsabilidade. Não adicione um grande número de membros de uma vez. É recomendável adicionar um pequeno número de membros por dia e aumentar gradualmente, observando o comportamento da sua conta.
**Mais atualizações e funções em breve**
