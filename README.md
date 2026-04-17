# GrandSummonersPerfect

Plataforma companion premium para Grand Summoners, focada em transformar dados fragmentados em decisao pratica para composicoes, tiers, bosses e progressao.

## O que este projeto entrega

- Database de units e equips com filtros contextuais
- Tierlists contextuais (overall, beginner, sustain, nuke, arena, mode-specific, equips)
- Boss solver com leitura de mecanicas e recomendacao por estilo
- Team builder com classificacao de comp e recomendacoes por roster
- Hubs por modo de jogo, guides, AI presets e progression paths
- Painel admin para fluxo editorial e ingestao/sync de fontes publicas
- Sync automatico de dados externos no startup (sheet + base de units externa)

## Stack

### Frontend

- Next.js (App Router)
- TypeScript
- Tailwind CSS
- Framer Motion

### Backend

- FastAPI
- Pydantic v2
- Repositorio in-memory com seeds + stores JSON locais para workflow editorial/sync

## Estrutura do monorepo

```text
.
├── backend/
│   ├── app/
│   │   ├── core/               # config global
│   │   ├── data/               # mock_data seed
│   │   ├── db/                 # json store utilitario
│   │   ├── ingestion/          # estrutura de ingestao (camada base)
│   │   ├── models/             # enums e schemas pydantic
│   │   ├── repositories/       # memory repo + filtros + lookup
│   │   ├── routers/            # APIs public e admin
│   │   ├── services/           # recomendacao, tierlist, sync, editorial, external db
│   │   └── sql/                # schema SQL de referencia
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── public/
│   └── src/
│       ├── app/                # rotas pages (home, units, tierlists, admin, etc.)
│       ├── components/         # cards/layout/ui/filtros
│       ├── lib/                # client API + types
│       └── styles/
├── docs/
│   ├── IMPLEMENTATION_AUDIT.md
│   └── PROJECT_CONTEXT.md
└── scripts/
    └── verify_mvp.sh
```

## Setup local

### 1) Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2) Frontend

```bash
cd frontend
npm install
echo 'NEXT_PUBLIC_API_URL=http://localhost:8000' > .env.local
npm run dev
```

## Endpoints principais

### Public API (`/api/v1/public`)

- `GET /home`
- `GET /search`
- `GET /units`
- `GET /units/{slug_or_id}`
- `GET /equips`, `GET /equips/{slug_or_id}`
- `GET /bosses`, `GET /bosses/{slug_or_id}`
- `POST /bosses/{slug_or_id}/solve`
- `GET /comps`, `GET /comps/{slug_or_id}`
- `GET /tierlists`, `GET /tierlists/{slug}`
- `GET /modes`, `GET /modes/{mode}`
- `GET /guides`, `GET /guides/{slug}`
- `GET /ai-presets`
- `GET /progression-paths`
- `POST /team-builder/recommend`
- `POST /team-builder/classify`

### Admin API (`/api/v1/admin`)

- Overview/review queue:
  - `GET /overview`
  - `GET /review-queue`
- Curadoria editorial:
  - `GET /sources`
  - `GET /source-mappings`
  - `GET /tierlists/drafts`
  - `POST /publish`
  - `GET /editorial-history`
- Sync e ingestao:
  - `POST /sources/import`
  - `POST /sync/run`
  - `GET /sync/status`
  - `POST /sync/images`
  - `POST /sync/gsinfo-units`
  - `GET /sync/gsinfo-units/status`

## Fluxo de dados (resumo)

1. Startup backend chama sync runtime.
2. Sync consulta sheet publica (GViz JSON) e detecta mudancas via hash de registros.
3. Se mudou, aplica upsert em tierlist/community + placeholders necessarios.
4. Sync de imagens tenta mapear units para paths do GSInfo.
5. Base externa de units (GSInfo bundle parser) e atualizada para permitir fallback detalhado de unit.

## Funcionalidades de /units

- Busca textual (`q`) por nome/slug/tags/passivas/contexto
- Filtros por role/element/race/damage/tier/tag etc.
- Ordenacao (`sort_by`, `sort_dir`)
- Paginacao (`page`, `page_size`)
- Inclusao opcional de units externas (`include_external=true`)
- Fallback de detalhe para units externas quando nao houver unit local

## Observacoes de fonte e legalidade

- Projeto nao oficial/community companion.
- Dados e assets de Grand Summoners pertencem aos respectivos proprietarios.
- O sistema referencia fontes publicas para curadoria e sincronizacao.

## Qualidade e verificacao

Execute no root:

```bash
bash scripts/verify_mvp.sh
```

O script roda:

- testes backend (`pytest`)
- build frontend (`next build`)
- smoke checks de API e rotas principais web

## Documentacao adicional

- Auditoria de implementacao: `docs/IMPLEMENTATION_AUDIT.md`
- Contexto tecnico completo para IA/devs: `docs/PROJECT_CONTEXT.md`
