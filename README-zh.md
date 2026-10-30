# dsh-rulefile-check — 规则库文件自检核对

[English](README.md) · [简体中文](README-zh.md) · [Español](README-es.md) · [Português](README-pt.md) · [हिन्दी](README-hi.md)

<!-- topblock:v1 -->
> **这是什么**　规则库文件自检核对。输出一份「哪一行、哪一栏、差什么」的清单。
> **给谁用**　规则库维护者、开发者。
> **你交什么**　一个规则库文件（YAML）；不改原件。
> **它不做什么**　不判合规、不认定责任、不替代审核人；只列材料内部能逐条指认的差异。
> **怎么开始**　命令行安装（暂未单独上架）：
> `dsh plugin --profile <name> add dsh-rulefile-check`
<!-- /topblock:v1 -->

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)
[![dshfind](https://dshfind.com/api/badge/PerryLink/dsh-rulefile-check?metric=downloads)](https://dshfind.com/en/plugins/PerryLink/dsh-rulefile-check?ref=badge)

`dsh-rulefile-check` 读取一份规则库——库头加每条规则一行——按本插件家族强制的条款引用纪律核对这份规则库：规则编号在库内是否唯一、依据字段是否都写全、摘录是否短于最小长度、来源是否写成 http(s) 链接、依据类型为 `derived-from-principle` 或 `institutional-configuration` 的规则有没有填定级、检查类型是否为引擎所支持、库头是否声明名称、适用插件与版本。

## Install

```sh
dsh plugin --profile <name> add dsh-rulefile-check
dsh --profile <name> --dump-config | grep 'dsh-rulefile-check'
```

## 实际输出长什么样

![dsh-rulefile-check 工作流图：文档 → 规则包 → 核对结果。](docs/assets/dsh-rulefile-check-flow.svg)

*工作流概览：文档 → 规则包 → 核对结果。下面的示例使用实际命令面。*


本插件对自己 `RF-001` 测试夹具的**真实输出**，不是示意图。规则库不伪造引文，因此每条发现都会同时写明所引条款，以及该条款原文本次未取得。

## 它回答什么问题

### 示例

下表是示例集：第一行是详细走查，其余行是简短案例。


#### 详细输出

**工具** `rulefile_check`

**输入**

~~~json
{"rows":[{"规则编号":"XX-001"},{"规则编号":"XX-001"}]}
~~~
 
**输出**

~~~json
{
  "id": "dsh-rulefile-check.RF-001.de02f9e1",
  "ruleId": "RF-001",
  "severity": "warn",
  "locator": {
    "row": 2,
    "field": "ruleId"
  },
  "found": "第 2 行「ruleId」的值「XX-001」与第 1 行重复",
  "expected": "「ruleId」在材料内应唯一",
  "fix": "核对是否重复登记或抄错；本条只核对唯一性"
}
~~~

*来源 `dsh-rulefile-check/tests/fixtures/RF-001/RF-001-unsafe.json`*

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

**边界（中文译文，以英文原文为准）：** 本插件核对一份 **规则库**（rule pack）是否符合本插件家族所强制执行的引用纪律——规则 id 是否唯一，每个依据字段是否齐备，摘录是否具有真实长度，来源是否为链接，派生依据或本机构配置依据是否带有严重级，检查类型是否为引擎支持的类型，以及规则库是否声明其名称、插件与版本。

> ### ⚠️ 这里核对的是形式，不是内容——而且它自己就这么说（以英文原文为准）
>
> **所核对的这套纪律是自定的，不是国家标准。**「摘录必须是逐字引文」与「由原则推论的检查不得标为 `error`」是本插件家族在 `shared/ruleset.ts` 中强制执行的规则；它们的依据是学术诚实这一一般原则——绝不把描述包装成引文，绝不把推论包装成要求——**而不是任何法规或标准**。每条规则的 `basis` 都如实写明这一点，这也是此处每条规则都是 `warn` 或 `info` 的原因。
>
> **它无法判断一条引文是否贴切。** 它核对的是字段是否填写、摘录是否够长、来源*看起来是否像*链接，以及是否写明了严重级。它会欣然通过一条引用了**真实但无关条款**的规则——这正是形式核对已在文档中写明的局限，也是为什么自动核对永远不能取代人工通读。
>
> 有两条规则值得说明。`RF-003` 的八个字符下限，是加载期强制在台账一侧的呼应——但**长度是必要条件，不是充分条件**：二十个字符的*描述*仍然不是引文，本插件分不出两者的差别。而 `RF-005` 只能确认严重级字段存在：严重级是否真的未超过上限由加载器强制执行，它会以 `strongest permitted severity` 直接拒绝违规的规则库。`RF-006` 的 kind 取值清单出厂为**空**，因为引擎支持哪些 kind 取决于引擎版本——若把本家族自己的清单硬编码进去，就意味着引擎每新增一种 kind 都要改这个插件。

## Compatibility

| 项目 | 状态 |
|---|---|
| Harness | 对等版本范围 `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` —— 已实测同时接受 `0.2.0-rc.2` 与 `0.2.1-rc.2`。**已声明 `engines.dsh`**：0.2.1 起由宿主单独裁决，范围为 `>=0.2.1-0 <0.3.0` |
| Node | `^22.19.0 || >=24.0.0` |
| 平台 | 全平台（纯 ESM；无原生代码、无联网、不调用模型） |
| 工具模式 | `native` / `ptc` 均可；批量校验整个目录时建议 `ptc`，schema 成本只付一次 |

## What it does

规则表、字段说明与行为细节见 [README.md](README.md#what-it-does)（英文主版本）。本插件只列出材料与所引条款之间的字面差异，并对无法执行的检查在 `skipped` 中逐项说明。

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

## PerryLink DSH Plugin Family

完整清单（62 个核查器 + 通用插件）见 [按材料选核查器](https://perrylink.github.io/zh/checkers/choose/)；本仓只是其中一个。

## License

[Apache License 2.0](LICENSE) © 2026 dsh-rulefile-check contributors.
