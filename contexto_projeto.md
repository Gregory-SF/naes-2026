# Contexto do sistema NAES Projetos

Sistema web (Django) para gestão de projetos, equipes, sprints e análise de commits do GitHub (NAES 2026).

## Perfis de acesso
- **Coordenadores**: cadastram, alteram e excluem. Acessam configurações globais, análise de commits e a administração da IA.
- **Professores**: apenas consultam.
- Cada registro (projeto, equipe, sprint) pertence a quem o cadastrou. Cada usuário só vê, altera e exclui os próprios registros.

## Telas e como usar
- **Projetos** (menu Projetos): lista com filtros por nome, status e ano. "Novo Projeto" pede nome, status, ano, dias de aula,
  link da organização no GitHub e os repositórios (nome, link e branch principal). Também é possível criar uma sprint junto.
  Só é possível excluir um projeto que não tenha equipes nem análises vinculadas.
- **Equipes** (menu Equipes): lista com filtros por nome, projeto e situação. Toda equipe pertence a um projeto ativo seu e precisa de
  1 Scrum Master, 1 Product Owner e ao menos 1 Desenvolvedor (alunos buscados por nome ou apelido do GitHub). Equipes não são excluídas,
  apenas inativadas, e só se não tiverem membros.
- **Sprints** (menu Sprints): lista com filtros por nome, projeto e período. Cada sprint tem nome, data de início e de fim e projetos vinculados.
- **Configurações globais** (menu Ações, coordenadores): token do GitHub e dias de aula.
- **Análise** (menu Ações, coordenadores): "Branches" cadastra ou busca branches de um repositório; "Iniciar análise" importa os commits
  de uma branch em um período (ou sprint); o status mostra o resultado.
- **IA**: "Meu consumo" mostra a cota mensal de tokens do usuário. Coordenadores veem também Requisições (auditoria),
  Configuração (modelo, chave e botão "Testar conexão") e IA por usuário (cota e permissão).
- **Assistente**: este chat. O histórico é individual e só as últimas 5 mensagens são enviadas à IA.

## Regras gerais
- Mensagens de sucesso e erro aparecem no topo da página após cadastrar, alterar ou excluir.
- Listas têm paginação que mantém os filtros aplicados.
- A cota mensal de tokens da IA é renovada todo dia 1º.
- A senha pode ser alterada em Ações > Alterar senha.
