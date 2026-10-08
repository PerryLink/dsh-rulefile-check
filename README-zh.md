# dsh-rulefile-check — 规则库文件自检核对

`dsh-rulefile-check` 读取一份规则库——库头加每条规则一行——按本插件家族强制的条款引用纪律核对这份规则库：规则编号在库内是否唯一、依据字段是否都写全、摘录是否短于最小长度、来源是否写成 http(s) 链接、依据类型为 `derived-from-principle` 或 `institutional-configuration` 的规则有没有填定级、检查类型是否为引擎所支持、库头是否声明名称、适用插件与版本。

## 它回答什么问题

| 你会问 | 它怎么答 |
|---|---|
| 同一个规则编号在库里出现在两条规则上。 | `RF-001` 会报出重复的编号，因为编号重复会让 `issue.id` 指向两条不同的规则，命中信息再也追溯不回去。比较时忽略空白字符。它一次只看一份规则库：不把两份库互相对比，也不去任何登记库查询。 |
| 某条规则只写了 `document`，条款一个字没写。 | `RF-002` 核对的是两个依据字段里至少填了一个，所以 `document` 填了的规则会通过。它不判断所引条款是否真实存在、是否与规则相关。 |
| 摘录写的是一句对条款的描述，不是逐字引文。 | `RF-003` 要求摘录存在且不少于八个字符。长度只是必要条件、不是充分条件：写满二十字的描述照样不是引文，本条分不出来——它不拿摘录去和条款原文比对。 |
| 来源栏写的是「某某网站」，不是链接。 | `RF-004` 会报出，因为来源栏必须写成 http(s) 链接的样子。它只核对形式：不访问该链接、不告诉你链接能不能打开、也不告诉你该页面是否真含所引条款。 |
| 一条由原则推论的规则，定级填成了 `error`。 | `RF-005` 核对的是依据类型为 `derived-from-principle` 或 `institutional-configuration` 的规则到底有没有填定级。定级是否真的没超过上限由加载器强制——它会直接拒绝这样的规则库并抛 `strongest permitted severity`；本条只覆盖字段齐备，不能代替加载器判断。 |
| 规则库里写了一个引擎不认识的 `check.kind`——库头又有没有声明 `packName` 与 `version`？ | `RF-006` 会报出不认识的 `check.kind`，因为这样的规则会静默不执行。它核对的支持取值清单出厂为空，因为有哪些 kind 取决于引擎版本，所以未配置时该条进 `skipped`，而不是通过；它只拿你提供的清单比对。`RF-007` 一并核对库头的 `packName`、`plugin` 与 `version`，因为没有它们，替换规则库时就无法确认它属于哪个插件、是哪一版。两条都不核对填的值是否与实际使用的插件相符。 |

## 依据的标准

本规则库不引用任何公开标准：每条规则的依据都是本插件家族自定的引用纪律、引擎契约与规则库契约，因此下表列的是家族内部约定，而不是任何法律法规或国家标准。

| 文件 | 文号 | 引用它的规则 |
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

| 项目 | 状态 |
|---|---|
| Harness | 对等版本范围 `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` —— 已实测同时接受 `0.2.0-rc.2` 与 `0.2.1-alpha.1`。**刻意不声明 `engines.dsh`**：它没有任何读取者，也无法拒装任何宿主 |
| Node | `^22.19.0 || >=24.0.0` |
| 平台 | 全平台（纯 ESM；无原生代码、无联网、不调用模型） |
| 工具模式 | `native` / `ptc` / `both` 均可；批量校验整个目录时建议 `ptc`，schema 成本只付一次 |

## What it does

规则表、字段说明与行为细节见 [README.md](README.md#what-it-does)（英文主版本）。本插件只列出材料与所引条款之间的字面差异，并对无法执行的检查在 `skipped` 中逐项说明。

## Install

```sh
dsh plugin --profile <name> add dsh-rulefile-check
dsh --profile <name> --dump-config | grep 'dsh-rulefile-check'
```

## Configuration

全部可调参数都在 `src/config.ts` 的 Schemastery schema 中，只改 `cordis.yml` 即可生效，无需改代码；逐条阈值在 `rules/` 下的规则库文件里。

| 键 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `rulesFile` | string | `rules/rulefile-check.yaml` | 规则库文件路径，相对插件包根目录 |
| `disabledRules` | string[] | `[]` | 要停用的规则 id 列表；每条都会出现在 `skipped` 中 |
| `onlyRules` | string[] | `[]` | 只执行这些规则 id；留空表示执行全部规则 |
| `skipNotes` | string | `""` | 附加到每条 `skipped` 说明后的备注 |
| `timeoutMs` | number | `120000` | 工具协作式超时预算（毫秒） |

## Material format

支持 JSON 与 YAML。完整字段示例见 [README.md](README.md#material-format)（英文主版本）。字段在读取层是可选的，由检查引擎校验，因此部分导出的材料会产生"缺项"类差异，而不是让程序崩溃。

## Rule sources

规则数据与代码分离，每条规则都带文件名、文号、按原文自身编号体系的条款号、逐字摘录与来源地址。加载期强制：摘录必须是真实引文且不少于八个字符；依据仅为原则性条款（`kind: derived-from-principle`，严重级上限 `warn`）或本机构配置（`kind: institutional-configuration`，上限 `info`）的检查不得标为 `error`。夸大依据的规则库会在加载期失败，而不会产出一份看起来很有底气的报告。

核验中确认的边界与"刻意没有作出的结论"见 [README.md](README.md#rule-sources)（英文主版本）与随包的 `rules/evidence/` 目录。

## Troubleshooting

- **插件装上了但工具不出现**：确认 `main` 指向 `lib/index.mjs` 且 `pnpm run build` 已生成该文件；`main` 写错会让加载器静默跳过该条目。
- **`dsh plugin add` 报版本不兼容**：peer 范围覆盖 `0.1.x` 与 `0.2.x`；若运行时在其之外，可显式豁免：`dsh plugin --profile <name> allow-version <包名@版本> --dsh-version <runtime> --accept-risk`
- **某条规则没有执行**：查看 `skipped` 数组，其中写明了规则 id 与原因。
- **`check` 报 `manifest-peers` 失败**：静态检查器比对的是一份早于 0.2 世代的硬编码 peer 范围；安装期的 peer 校验以运行时为准。这是 `dsh-plugin-dev` 的已知上游问题。
- **时间看起来偏移**：全部计算都是对输入字符串做墙上时钟运算，不做时区换算。

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-rulefile-check
```

第 4 项把 `../_shared` 的共享件同步进 `src/shared/`；每次改动共享件后都要重跑。

## License

[Apache License 2.0](LICENSE) © 2026 dsh-rulefile-check contributors.
