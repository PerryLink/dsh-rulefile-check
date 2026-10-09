# dsh-rulefile-check — Autoverificação do ficheiro de regras segundo a disciplina de citações e os tetos de severidade

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-rulefile-check` lê um ficheiro de regras —o cabeçalho do ficheiro mais uma linha por regra— e confronta-o com a disciplina de citações que a sua família de plugins impõe: que cada id de regra seja único dentro do ficheiro, que os dois campos de fundamento estejam preenchidos, que nenhum extrato seja mais curto do que o comprimento mínimo, que toda a fonte esteja escrita como ligação http(s), que uma regra cujo tipo de fundamento seja `derived-from-principle` ou `institutional-configuration` traga uma severidade, que o tipo de verificação seja um que o motor aceite, e que o cabeçalho do ficheiro declare o nome, o plugin e a versão.

## Como é a saída

![Terminal demo of dsh-rulefile-check: real output over its RF-001 fixture](https://raw.githubusercontent.com/PerryLink/dsh-rulefile-check/main/docs/assets/dsh-rulefile-check-demo.png)

Saída real deste plugin sobre o seu próprio fixture de teste `RF-001` — não é uma simulação. O pacote de regras não inventa citações, por isso cada achado nomeia a cláusula aplicada e avisa que o seu texto não foi obtido.

## O que ele responde

| Você pergunta | O que ele responde |
|---|---|
| O mesmo id de regra aparece em duas regras do ficheiro. | `RF-001` reporta o id repetido, porque uma duplicação faz com que `issue.id` aponte para duas regras diferentes e a ocorrência deixa de ser rastreável. A comparação ignora espaços em branco. Só vê um ficheiro de cada vez: não compara dois ficheiros entre si nem consulta qualquer registo. |
| Uma regra traz apenas `document` e não diz nada sobre a cláusula. | `RF-002` verifica que pelo menos um dos dois campos de fundamento esteja preenchido, pelo que uma regra com `document` presente passa. Não julga se a cláusula citada existe realmente nem se tem relação com a regra. |
| O extrato é uma descrição da cláusula numa frase, não uma citação. | `RF-003` exige que o extrato exista e tenha pelo menos oito caracteres. O comprimento é necessário, não suficiente: uma descrição de vinte caracteres continua a não ser uma citação, e esta regra não distingue — não confronta o extrato com a cláusula original. |
| A fonte diz «某某网站» em vez de uma ligação. | `RF-004` reporta-o, porque o campo da fonte tem de se parecer com uma ligação http(s). Verifica apenas a forma: não visita a ligação, não lhe diz se a ligação funciona nem se a página contém realmente a cláusula citada. |
| Uma regra derivada de um princípio está classificada como `error`. | `RF-005` confirma que uma regra cujo tipo de fundamento seja `derived-from-principle` ou `institutional-configuration` indique alguma severidade. Que essa severidade respeite de facto o teto é imposto pelo carregador, que rejeita esse ficheiro com `strongest permitted severity`; esta verificação só cobre a presença do campo e não pode substituir o carregador. |
| O ficheiro escreve um `check.kind` que o motor não conhece — e declara o seu `packName` e a sua `version`? | `RF-006` reporta o `check.kind` desconhecido, porque essa regra não é executada em silêncio. A sua lista de tipos aceites vem vazia, já que quais tipos existem depende da versão do motor, pelo que um ficheiro por configurar deixa essa regra em `skipped` em vez de a aprovar; só compara com a lista que você fornecer. `RF-007` verifica em conjunto `packName`, `plugin` e `version` no cabeçalho, porque sem eles não se consegue saber a que plugin pertence um ficheiro, nem que revisão, ao substituí-lo. Nenhuma das duas confirma que os valores declarados correspondam ao plugin realmente em uso. |

## Normas que segue

Este ficheiro de regras não cita qualquer norma pública: o fundamento de cada regra é a disciplina de citações que a própria família de plugins se impõe, o seu contrato de motor e o seu contrato de ficheiro, pelo que as entradas abaixo nomeiam compromissos internos da família e não qualquer lei ou norma nacional.

| Documento | Número | Regras que o citam |
|---|---|---|
| 本插件家族的条款引用纪律（自定纪律，非国家标准） | 无编号（本规则库自定） | RF-001, RF-002, RF-003, RF-004, RF-005 |
| 本插件家族的检查引擎契约（自定纪律，非国家标准） | 无编号（本规则库自定） | RF-006 |
| 本插件家族的规则库契约（自定纪律，非国家标准） | 无编号（本规则库自定） | RF-007 |

**Boundary:** this plugin checks a **规则库** (a rule pack) for the citation discipline this plugin family
enforces — that rule ids are unique, that every basis field is present, that an excerpt has real length, that a
source is a link, that a derived or locally configured basis carries a severity, that the check kind is one the
engine supports, and that the pack declares its name, plugin and version.

> ### ⚠️ This checks form, not content — and it says so
>
> **The discipline being checked is self-imposed, not a national standard.** "An excerpt must be a verbatim
> quotation" and "a principle-derived check may not be an `error`" are rules this plugin family enforces in
> `shared/ruleset.ts`; their basis is the general principle of intellectual honesty — never dress a description
> up as a quotation, never dress an inference up as a requirement — **not any statute or standard**. Every
> rule's `basis` says exactly that, which is why every rule here is `warn` or `info`.
>
> **It cannot tell whether a citation is apt.** It checks that fields are filled, that an excerpt is long
> enough, that a source *looks like* a link, and that a severity is stated. It will happily pass a rule that
> cites **a real but irrelevant clause** — that is the documented limit of a form check, and it is why
> automated checking never replaces a human read-through.
>
> Two rules deserve a note. `RF-003`'s floor of eight characters is the ledger-side echo of the load-time guard
> — but **length is necessary, not sufficient**: a twenty-character *description* is still not a quotation, and
> this plugin cannot tell the difference. And `RF-005` can only confirm a severity field is present: whether a
> severity actually respects the ceiling is enforced by the loader, which rejects a violating pack outright with
> `strongest permitted severity`. `RF-006`'s kind vocabulary ships **empty**, because which kinds an engine
> supports depends on the engine version — hard-coding this family's own list would mean editing this plugin
> every time the engine gains a kind.

## Compatibility

| Superfície | Estado |
|---|---|
| Harness | Faixa de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificada para aceitar tanto `0.2.0-rc.2` quanto `0.2.1-alpha.1`. **`engines.dsh` não é declarado**: não tem leitor e não pode recusar nenhum host |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sem código nativo, sem rede, sem chamada ao modelo) |
| Modo de ferramenta | Funciona em `native`, `ptc` e `both`; para um diretório inteiro use `ptc` |

## What it does

A tabela de regras, os campos e o comportamento detalhado estão em [README.md](README.md#what-it-does) (versão principal em inglês). O plugin apenas lista divergências literais frente às cláusulas citadas e indica em `skipped` cada verificação que não pôde ser executada.

## Install

```sh
dsh plugin --profile <name> add dsh-rulefile-check
dsh --profile <name> --dump-config | grep 'dsh-rulefile-check'
```

## Configuration

Todos os parâmetros ajustáveis ficam no esquema Schemastery de `src/config.ts`, portanto mudam pelo `cordis.yml` sem editar código; os limites por regra ficam no pacote de regras sob `rules/`.

| Chave | Tipo | Padrão | Descrição |
|---|---|---|---|
| `rulesFile` | string | `rules/rulefile-check.yaml` | Caminho do pacote de regras, relativo à raiz do pacote |
| `disabledRules` | string[] | `[]` | Ids de regras a desativar; cada uma aparece em `skipped` |
| `onlyRules` | string[] | `[]` | Executar apenas estas regras; vazio executa todas |
| `skipNotes` | string | `""` | Nota acrescentada a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Orçamento de tempo limite cooperativo da ferramenta |

## Material format

Aceita JSON ou YAML. O exemplo completo de campos está em [README.md](README.md#material-format) (versão principal em inglês). Os campos são opcionais na camada de leitura e validados pelo motor, de modo que uma exportação parcial gera achados sobre o que falta em vez de falhar.

## Rule sources

Os dados das regras ficam separados do código: cada regra traz documento, número, cláusula na numeração própria da fonte, trecho literal e URL de origem. O carregador impõe que o trecho seja citação real de pelo menos oito caracteres e que uma verificação baseada apenas em princípio geral (`kind: derived-from-principle`, teto `warn`) ou em política local (`kind: institutional-configuration`, teto `info`) nunca seja declarada `error`.

Os limites verificados e as conclusões deliberadamente **não** afirmadas estão em [README.md](README.md#rule-sources) (versão principal em inglês) e em `rules/evidence/`.

## Troubleshooting

- **O plugin instala mas a ferramenta não aparece**: confirme que `main` resolve para `lib/index.mjs` e que `pnpm run build` o gerou.
- **`dsh plugin add` recusa o pacote**: a faixa de peers cobre `0.1.x` e `0.2.x`; fora dela, conceda isenção explícita com `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`.
- **Uma regra não executou**: leia o arranjo `skipped`.
- **`check` informa `manifest-peers` como falha**: problema conhecido do `dsh-plugin-dev`; o runtime aplica a compatibilidade na instalação.
- **Os horários parecem deslocados**: toda a aritmética é de hora local sobre as cadeias fornecidas.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-rulefile-check
```

O último comando copia o kit compartilhado de `../_shared` para `src/shared/`; execute-o novamente após cada alteração compartilhada.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-rulefile-check contributors.
