# dsh-rulefile-check — Rule pack self-check against the citation discipline and severity ceilings

`dsh-rulefile-check` reads one rule pack — the pack header plus one row per rule — and checks that pack against the citation discipline its plugin family enforces: that every rule id is unique within the pack, that both basis fields are filled in, that no excerpt is shorter than the minimum length, that every source is written as an http(s) link, that a rule whose basis kind is `derived-from-principle` or `institutional-configuration` carries a severity, that the check kind is one the engine supports, and that the pack header declares its name, plugin and version.

## What it answers

| You ask | What it answers |
|---|---|
| The same rule id appears on two rules in the pack. | `RF-001` reports the repeated id, because a duplicate makes `issue.id` point at two different rules and the hit can no longer be traced back. Comparison ignores whitespace. It can only see one pack at a time: it does not compare two packs with each other or look anything up in a register. |
| A rule carries only `document` and says nothing about the clause. | `RF-002` checks that at least one of the two basis fields is filled in, so a rule whose `document` is present passes. It does not judge whether the cited clause really exists or whether it relates to the rule. |
| The excerpt is a one-sentence description of the clause rather than a quotation. | `RF-003` requires the excerpt to exist and to be at least eight characters long. Length is necessary, not sufficient: a twenty-character description is still not a quotation, and this rule cannot tell the difference — it does not compare the excerpt against the original clause. |
| The source reads `某某网站` instead of a link. | `RF-004` reports it, because the source field has to look like an http(s) link. It checks the form only: it does not visit the link, does not tell you whether the link works, and does not tell you whether the page really contains the clause being cited. |
| A rule derived from a principle is filed as `error`. | `RF-005` confirms that a rule whose basis kind is `derived-from-principle` or `institutional-configuration` states a severity at all. Whether that severity actually respects the ceiling is enforced by the loader, which rejects such a pack outright with `strongest permitted severity`; this check only covers the field being present and cannot replace the loader. |
| The pack writes a `check.kind` the engine does not know — and does it declare its `packName` and `version`? | `RF-006` reports the unknown `check.kind`, because such a rule is silently not executed. Its list of supported kinds ships empty, since which kinds exist depends on the engine version, so an unconfigured pack puts that rule in `skipped` instead of passing it; it only compares against the list you supply. `RF-007` checks the header for `packName`, `plugin` and `version` together, because without them you cannot tell which plugin a pack belongs to, or which revision, when you swap it in. Neither rule verifies that the declared values match the plugin actually in use. |

## Standards it follows

This rule pack cites no public standard: every rule's basis is the plugin family's own self-imposed citation discipline, its engine contract and its pack contract, so the entries below name the family's internal contracts rather than any statute or national standard.

| Document | Number | Cited by rules |
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

| Surface | Status |
|---|---|
| Harness | Peer range `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verified to accept both `0.2.0-rc.2` and `0.2.1-alpha.1`. `engines.dsh` is deliberately not declared: it has no reader and cannot reject a host |
| Node | `^22.19.0 || >=24.0.0` |
| Platforms | All (plain ESM; no native code, no network, no model call) |
| Tool mode | Works in `native`, `ptc` and `both`; for a whole rule pack use `ptc` |

## What it does

Registers the `rulefile_check` tool. It reads one rule inventory — the pack header plus one row per rule —
applies a versioned rule pack, and returns a report.

| Rule | Check | Severity | Basis |
|---|---|---|---|
| `RF-001` | rule ids are unique | warn | self-imposed discipline |
| `RF-002` | basis fields are present | warn | self-imposed discipline |
| `RF-003` | the excerpt has real length | warn | self-imposed discipline |
| `RF-004` | the source is a link | warn | self-imposed discipline |
| `RF-005` | a derived basis carries a severity | warn | self-imposed discipline |
| `RF-006` | the check kind is supported (off by default) | warn | engine contract |
| `RF-007` | the pack declares name, plugin and version | warn | pack contract |

## Install

```sh
dsh plugin --profile <name> add dsh-rulefile-check
dsh --profile <name> --dump-config | grep 'dsh-rulefile-check'
```

## Configuration

| Key | Type | Default | Description |
|---|---|---|---|
| `rulesFile` | string | `rules/rulefile-check.yaml` | Rule-pack path, relative to the package root |
| `disabledRules` | string[] | `[]` | Rule ids to stop running; each appears in `skipped` |
| `onlyRules` | string[] | `[]` | Run only these rule ids; empty runs every rule |
| `skipNotes` | string | `""` | Note appended to every `skipped` reason |
| `timeoutMs` | number | `120000` | Cooperative tool timeout budget |

Rule-level parameters worth knowing:

- `RF-003` `minLength` — the excerpt floor, eight characters by default (the same figure the loader uses).
- `RF-004` `pattern` — the source shape, `^https?://[^\s]+$` by default.
- `RF-006` `values` — **your engine's supported check kinds.** Empty means the rule does not run; fill it from
  the engine's dispatch table rather than from this plugin.

## Material format

The tool accepts JSON or YAML:

```yaml
packName: 某某规则库
plugin: dsh-rulefile-check
version: '2026.1'
rows:
  - { 规则编号: XX-001, 规则标题: 示例规则标题, 定级: warn,
      依据类型: derived-from-principle, 依据文件: 《某某标准》, 条款号: 第 5.3 条,
      摘录: 该条文本次未取得：核查未获得该标准的逐字原文，本规则库不伪造引文。,
      来源: https://openstd.samr.gov.cn/, 检查类型: presence, 参数: 'field: title' }
```

Column names are matched case-insensitively and ignoring spaces, underscores and hyphens; the inventory's own
column names are kept, so a finding names the column it read.

## Rule sources

Rule data lives in `rules/rulefile-check.yaml`. Its header explains that the discipline it checks is this
family's own, not a standard's, and that the basis for it is the general principle of intellectual honesty. The
load-time guard still requires a document, clause, excerpt and source per rule, and still forbids a
principle-derived or locally configured check from being `error`.

## Troubleshooting

- **`RF-006` never runs.** Its vocabulary is empty. Fill it with the check kinds your engine actually supports;
  the plugin will not hard-code its own list.
- **`RF-005` passes a pack the loader then rejects.** That is expected: `RF-005` checks that a severity field is
  present, while the loader enforces the ceiling itself. The loader's error names the offending rule.
- **`RF-003` passes an excerpt I know is a paraphrase.** Length cannot detect that. Only a human comparison
  against the source can.
- **`RF-004` passes a link that 404s.** The check never fetches the URL; it verifies the shape only.
- **The plugin installs but the tool never appears.** Check that `main` resolves to `lib/index.mjs` and
  that `pnpm run build` produced it; a wrong `main` makes the loader skip the entry silently.
- **`dsh plugin add` refuses the package as incompatible.** The peer range covers `0.1.x` and `0.2.x`; if
  your runtime sits outside it, grant an explicit exemption:
  `dsh plugin --profile <name> allow-version dsh-rulefile-check@0.1.0 --dsh-version <runtime> --accept-risk`
- **`check` reports `manifest-peers` as failed.** The static checker compares against a hard-coded peer
  range that predates the 0.2 line. The runtime enforces peer compatibility at install time, so the
  declared range is the correct one; this is a known upstream issue in `dsh-plugin-dev`.

## Development

```sh
pnpm install
pnpm run typecheck   # tsc --noEmit
pnpm test            # vitest, the shared table-plugin suite plus paired fixtures
pnpm run build       # tsdown -> lib/index.mjs + lib/index.d.mts
node ../scripts/sync-shared.mjs dsh-rulefile-check   # refresh src/shared from ../_shared
```

The plugin is **data-only**: `src/model.ts` declares the table shape, the shared kit supplies the reader and
the check engine, and the rule pack declares every check.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-rulefile-check contributors.
