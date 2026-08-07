# Research Notes: Configurações Globais

## Decisão 1: Configuração singleton

**Decision**: Usar um único registro global de configuração.

**Rationale**: A spec não pede multi-tenancy por usuário.

## Decisão 2: Token protegido em repouso

**Decision**: Armazenar token criptografado com chave fora do banco.

**Rationale**: Atende requisitos de segurança e evita exposição em texto plano.

## Decisão 3: Exibição mascarada por padrão

**Decision**: Mostrar token mascarado e revelar apenas por ação explícita.

**Rationale**: Reduz risco de exposição acidental.
