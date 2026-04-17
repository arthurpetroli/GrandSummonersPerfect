# PROJECT_CONTEXT

Documento de contexto tecnico completo para orientar qualquer IA ou desenvolvedor sobre arquitetura, fluxo de dados, comportamento de APIs, convencoes e operacao deste repositorio.

Use este arquivo como referencia principal antes de pedir implementacoes.

## 1. Visao do produto

GrandSummonersPerfect e um companion web para Grand Summoners orientado a decisao:

- encontrar unit/equip/comps por contexto
- resolver boss por mecanica e estilo (safe, nuke, auto)
- montar times com substitutes baseados no roster
- consultar tierlists contextuais com explicabilidade
- apoiar progressao com caminhos e guias

Nao e uma wiki estatica; combina database, curadoria editorial e recomendacao pratica.

## 2. Estado atual da arquitetura

### 2.1 Frontend

- Next.js App Router em `frontend/src/app`
- API client em `frontend/src/lib/api.ts`
- Tipos compartilhados do client em `frontend/src/lib/types.ts`
- Componentes reutilizaveis em `frontend/src/components`

Pontos relevantes:

- `/units` suporta busca textual, paginacao, ordenacao, inclusao de units externas
- `/units/[slug]` abre detalhe local e fallback externo
- `/admin` controla sync/import/publish e status

### 2.2 Backend

- FastAPI em `backend/app/main.py`
- Rotas:
  - public: `backend/app/routers/public.py`
  - admin: `backend/app/routers/admin.py`
- Repositorio principal in-memory (seed): `backend/app/repositories/memory_repo.py`
- Serviços principais:
  - recomendacao: `backend/app/services/recommendation.py`
  - tierlist enrich/group: `backend/app/services/tierlist.py`
  - ingestao/sync sheet+imagens: `backend/app/services/ingestion_service.py`
  - base externa de units GSInfo: `backend/app/services/gsinfo_unit_db.py`
  - runtime startup sync: `backend/app/services/sync_runtime.py`
  - editorial workflow: `backend/app/services/editorial.py`

### 2.3 Persistencia atual

- Gameplay principal (units/equips/bosses/comps/tierlists) fica no `memory_repo` carregado de `mock_data`.
- Curadoria/sync usa stores JSON locais em `backend/data/*.json`.
- Banco SQL real ainda nao e path principal runtime (schema de referencia existe em `backend/app/sql/schema.sql`).

## 3. Fluxo de sync e ingestao

### 3.1 Startup

`backend/app/main.py` chama `run_startup_sync_once()` no evento startup.

O startup tenta:

1. `sync_if_stale(force=False)` (sheet + imagem)
2. `sync_gsinfo_unit_database()` (parser de units externas)

Falhas externas nao derrubam o boot.

### 3.2 Sheet community (tier)

- Fonte principal: planilha publica (gid de tier comunitaria)
- Endpoint usado: GViz JSON, nao export CSV simples
- Pipeline:
  - leitura tabela
  - extracao de bloco “Recently added units”
  - normalizacao de tier
  - mapeamento para entity_id (unit/equip)
  - quando nao mapeia, cria id externa placeholder
  - hash dos registros para detectar alteracao real
  - upsert em tierlist `community-recent-added-tier`

Estado salvo em `sync_state.json`:

- `last_tier_sync_at`
- `last_image_sync_at`
- `tier_sync`
- `image_sync`
- `last_sync_signature`

### 3.3 Imagens de units

- Parser varre bundle JS publico do GSInfo para localizar `image.detail*` e `image.thumb*`.
- Atualiza `image_url` e `image_thumb_url` nos units locais.
- Se nao achar match e unit nao tiver imagem, usa fallback de logo.

### 3.4 Base externa de units

- `gsinfo_unit_db.py` parseia objetos de unit no bundle JS.
- Salva store local `gsinfo_units_store.json` com dados de detail:
  - nome, slug, elemento, raca
  - skill/arts/true arts
  - passivas
  - review fields (strengths/limitations)
  - metricas (damage, artgen, buffs, defense, heal, break)
  - urls de imagem

Usos:

- fallback em `/public/units/{slug}`
- resultados extras em `/public/search` e `/public/units?include_external=true&q=...`

## 4. Contrato das rotas principais

### 4.1 Public units list

`GET /api/v1/public/units`

Query suportada:

- filtros: `server_region`, `mode`, `role`, `element`, `race`, `damage_type`, `slot`, `tier`, `tierlist_slug`, `focus`, `min_value`, `tag`, `tags_any`
- busca: `q`
- composicao com externo: `include_external`
- ordenacao: `sort_by`, `sort_dir`
- paginacao: `page`, `page_size`

Resposta:

- `items`
- `count`
- `page`, `page_size`, `total_pages`
- `sort_by`, `sort_dir`
- `source_type` por item da pagina

### 4.2 Public unit detail

`GET /api/v1/public/units/{slug_or_id}`

- tenta local primeiro
- fallback para unit externa no store GSInfo

Resposta:

- `item`
- `substitutes`
- `synergies`
- `external_source` (quando fallback externo)

### 4.3 Public search

`GET /api/v1/public/search?q=...`

Retorna blocos:

- `units`, `equips`, `bosses`, `guides`, `comps`
- `external_units`

### 4.4 Admin sync

- `POST /api/v1/admin/sync/run`
- `GET /api/v1/admin/sync/status`
- `POST /api/v1/admin/sync/images`
- `POST /api/v1/admin/sync/gsinfo-units`
- `GET /api/v1/admin/sync/gsinfo-units/status`

### 4.5 Admin ingest/publish/editorial

- `POST /api/v1/admin/sources/import`
- `POST /api/v1/admin/publish`
- `GET /api/v1/admin/tierlists/drafts`
- `GET /api/v1/admin/source-mappings`
- `GET /api/v1/admin/editorial-history`

## 5. Modelos e convencoes

### 5.1 Enums

Arquivo: `backend/app/models/enums.py`

- `ServerRegion`: GLOBAL, JP, BOTH
- `UnitRole`: DPS, SUPPORT, TANK, HEALER, BREAKER
- `DamageType`: PHYSICAL, MAGIC, HYBRID
- `EquipSlotType`: WEAPON, ARMOR, SUPPORT, HEAL
- `TierGrade`: SSS, SS, S, A, B, C
- `ContentMode`: STORY, ARENA, DUNGEON_OF_TRIALS, CREST_PALACE, SUMMONERS_ROAD, MAGICAL_MINES, GRAND_CRUSADE, RAID, COLLAB
- `CompStyle`: SUSTAIN, NUKE, AUTO_FARM, ARENA, BREAKER, SUPPORT_CENTRIC

### 5.2 UnitProfile

Arquivo: `backend/app/models/schemas.py`

Campos relevantes para frontend:

- core: `id`, `slug`, `name`, `rarity`, `element`, `race`, `role`, `damage_type`, `equip_slots`, `tags`
- kit: `skill`, `arts`, `true_arts`, `super_arts`, `passives`
- analise: `strengths`, `limitations`, `best_use`, `weak_in`, `team_dependencies`, `equip_dependencies`, `values`
- sync/assets: `image_url`, `image_thumb_url`, `source_updated_at`, `source_refs`
- opcional externo: `external_metrics` (frontend type)

## 6. /units: comportamento esperado

### 6.1 Lista

Se usuario pesquisar um nome nao presente no seed local (ex: Abaddon):

- com `include_external=true` e `q=abaddon`, rota `/units` deve trazer item externo
- card mostra badge external
- click abre `/units/abaddon`

### 6.2 Detalhe

`/units/[slug]` deve:

- mostrar dados locais quando existir local
- mostrar dados externos com aviso de origem quando fallback
- exibir imagem (thumb/detail) ou placeholder

## 7. Testes e validacao

### 7.1 Backend

Rode:

```bash
cd backend
pytest -q
```

### 7.2 Frontend

Rode:

```bash
cd frontend
npm run build
```

### 7.3 E2E smoke local

```bash
bash scripts/verify_mvp.sh
```

## 8. Variaveis de ambiente

### Frontend

- `NEXT_PUBLIC_API_URL` (default no client: `http://localhost:8000`)

### Backend

- `DATABASE_URL` (planejado para persistencia SQL futura)
- `PERSISTENCE_ENABLED` (`true/false`, atualmente base runtime principal continua in-memory)

## 9. Arquivos criticos para IA/dev

Quando uma IA for trabalhar neste projeto, sugerir leitura inicial desta ordem:

1. `docs/PROJECT_CONTEXT.md`
2. `README.md`
3. `backend/app/routers/public.py`
4. `backend/app/routers/admin.py`
5. `backend/app/repositories/memory_repo.py`
6. `backend/app/services/ingestion_service.py`
7. `backend/app/services/gsinfo_unit_db.py`
8. `frontend/src/lib/api.ts`
9. `frontend/src/app/units/page.tsx`
10. `frontend/src/app/units/[slug]/page.tsx`

## 10. Limites atuais e proxima evolucao recomendada

### Limites

- gameplay data principal ainda seeded/in-memory
- sync da sheet ainda focado em blocos especificos e placeholders
- falta banco SQL como fonte unica de verdade

### Proxima evolucao

- migrar ingestao e editorial para Postgres
- criar historico diff por unit/tier
- autocomplete cliente-side para `/units`
- comparador side-by-side de units
- cache e job scheduling robusto para sync periodico
