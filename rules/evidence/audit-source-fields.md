# 条文核查报告 —— 全库 `source` 字段审计：**292 处只指向网站首页**

- **核查日期**：2026-10-07
- **核查背景**：第 54 轮发现 `EP-009` 的 `source` 指向与该文件无关的网址；
  第 66 轮发现 `AQ-003`／`AQ-004` 把**农业行业标准**指向**生态环境部**。
  ⇒ 本轮把 `source` 字段作为**独立审计对象**全面排查。
- **结论**：⚠️ **447 个 `source` 中有 292 个（65%）只写到网站首页**，
  **读者据此无法定位到所引文件**。**另有 2 处主机与发文件机构不匹配**（已另案更正）。
  ⚠️ **本轮不伪造深链接** —— 只记录问题与哪些可以修（见第四、五节）。

---

## 一、审计工具与两次改进（**过程本身值得记录**）

### 1.1 第一版：覆盖太窄，结论几乎无意义

第一版 `audit-source-hosts.mjs` 只内置 8 个部门主机，**判定 0 处可疑**。
但我随后做了**覆盖率检查**（`inventory-source-hosts.mjs`），结果是：

- `source` 共 **447** 个；
- **只有 94 个（21%）**落在审计已知的主机内；
- **实际出现 34 个不同主机**。

⇒ ⚠️ **"0 处可疑"是因为 79% 的来源根本没被检查**，
**而这个假阴性只能靠再写一个覆盖率脚本才发现。**
**教训：审计脚本必须先自证覆盖范围，否则它的"通过"没有意义。**

### 1.2 第二版：覆盖 403/447（90%），报出 24 处

补齐主机后，审计判定 **403** 个来源（**90%**），报出 **24 处可疑配对**。
逐条复核后分成两类（见第三节）——**其中只有 2 类是真实缺陷，其余是我的正则误报**。

---

## 二、⚠️ 主问题：**292 个 `source` 只写到网站首页**

### 2.1 数量与分布

| 类别 | 数量 |
|---|---|
| `source` 总数 | **447** |
| **具体页面**（含路径或查询串） | **155** |
| ⚠️ **仅网站首页** | **292（65%）** |

**涉及 45 个插件**，其中**整包全部为首页**的有：

| 插件 | 条数 | 首页主机 |
|---|---|---|
| `dsh-bid-qual-check`、`dsh-bid-ca-precheck`、`dsh-tender-extract`、`dsh-tender-matrix` | 8+6+7+7 | `https://www.gov.cn/` |
| `dsh-fmea-table-check`、`dsh-spc-gbt-adapter`、`dsh-guard-plan-qc`、`dsh-learning-gap-check` | 8+7+6+7 | `https://openstd.samr.gov.cn/` |
| `dsh-drill-script-check` | 8 | `https://www.mem.gov.cn/` |
| `dsh-soilwater-check`、`dsh-eia-guide-check` | 8+7 | `https://www.mee.gov.cn/` |
| `dsh-paper-doc-adapter`、`dsh-review-reply-check`、`dsh-essay-rubric-check` | 8+7+6 | `https://www.moe.gov.cn/` |
| `dsh-origin-rvc-check`、`dsh-customs-doc-check` | 7+7 | `http://www.customs.gov.cn/` |
| `dsh-ppap-check` | 7 | `https://www.aiag.org/` |
| `dsh-sop-sync-check` | 7 | `https://www.iatfglobaloversight.org/` |
| `dsh-lc-doc-check` | 8 | `https://iccwbo.org/` |
| `dsh-rulefile-check` | 7 | `https://github.com/` |
| 其余（`dsh-contract-stance`、`dsh-evidence-check`、`dsh-pleading-draft`、`dsh-protest-deadline`、`dsh-repair-order-qc`、`dsh-warranty-calc`、`dsh-railway-window`、`dsh-hs-classify`、`dsh-ota-review-check`、`dsh-permit-report-check`、`dsh-pipeline-check`、`dsh-policy-brief-draft`、`dsh-soe-decision-check`、`dsh-gongwen-flow-check`、`dsh-gongwen-word-check`、`dsh-aqua-input-check`、`dsh-export-ctl-check`、`dsh-hazchem-check`、`dsh-lawcite-adapter`、`dsh-demurrage-ledger`、`dsh-forecast-penalty`、`dsh-site-log-check` 等） | 各 1–8 | 见各包 |

### 2.2 ⚠️ 为什么这仍是问题 —— 但**不是"引文不实"**

必须把两件事分开：

| | 状态 |
|---|---|
| **`excerpt` 是否伪造引文** | ✅ **没有** —— 全库 `excerpt` 的形态是如实的 |
| **所引原文是否核对过** | ✅ **相当一部分核对过**，且**核对记录在 `rules/evidence/*.md` 里，并附了具体网址** |
| ⚠️ **规则自身的 `source` 能否定位到文件** | ❌ **292 处不能** |

⇒ 即：**证据报告里有深链接，但规则字段里只有首页。**
**两者不一致** —— 规则的 `source` 本应让读者**不必翻证据报告就能找到出处**。

⚠️ **也有一类首页是"确实没有更深的链接"**：
`dsh-ppap-check`（AIAG）、`dsh-sop-sync-check`（IATF）、`dsh-lc-doc-check`（ICC）、
`dsh-rulefile-check`（本项目自己的仓库）——
这些**文件本身需购买或不对外**，**首页可能已是能给出的最好出处**。
**但即便如此，也应写明"该文件需购买／不对外，此为发布机构首页"，而不是留一个光首页。**

---

## 三、第二版审计报出的 24 处：**逐条复核后的分类**

| 类别 | 处数 | 判定 |
|---|---|---|
| ⚠️ **主机与发件机构不匹配**（真缺陷） | **2** | `AQ-003`／`AQ-004` **农业标准→生态环境部**（**已于第 66 轮更正**） |
| ⚠️ **首页而非具体页**（真缺陷，见第二节） | **22** | 其中 `dsh-origin-rvc-check` 7 处、`dsh-paper-doc-adapter` 8 处、`dsh-review-reply-check` 7 处 |
| **我的正则误报** | 已排除 | 例：`dsh-icd-rule-check` `IC-003` 的 `《疾病分类与代码国家临床版 2.0》` 引的是
**国家中医药管理局**网站的具体页 —— ⚠️ **该文件确由卫生健康委与国家中医药管理局联合下发**，
**用中医药管理局的页面作 `source` 是正当的**，是我的 `expect` 正则太窄。 |
| **本机构配置类条目** | 已排除 | `EG-003`、`PD-004` 等的 `document` 是"**本机构口径**" —— **这类条目本就没有国家标准可引**，
`source` 指向该部门首页是**示意其主管领域**，**不改判**。 |

⚠️ **因此第二版的 24 处里，真正的缺陷是"首页"这一类（22 处）与"主机错配"（2 处）**，
**而不是它字面报出的"依据与机构不符"**。**审计给的是线索，分类靠人读。**

---

## 四、✅ 哪些可以立刻修（**本轮已确认可用**）

`rules/evidence/*.md` 里现成存着 **64 个主机的深链接**，可直接用于升级 `source`。
其中与本轮相关的、**已确认的具体页面**包括：

| 主机 | 已确认的深链接（例） |
|---|---|
| `openstd.samr.gov.cn` | `…/bzgk/std/newGbInfo?hcno=72487561F0A0B469A6C105FBD3652545`（GB/T 7826）、`…?hcno=6E8ABBDFAD27C0DA8BAC21295B04B032`（GB/T 4091）、`…?hcno=B04BA7B024E7439B35C21493F4F7C3F9`（GB/T 17989.2） |
| `std.samr.gov.cn` | 行业标准详情页（`…/hb/search/stdHBDetailed?id=…`）、国家标准详情页（`…/gb/search/gbDetailed?id=…`） |
| `www.nhc.gov.cn` 之外的卫生类 | `hncis.hnwsjk.cn/bingan/upload/files/2024/6/…pdf` |
| `www.mem.gov.cn` | `…/gk/zfxxgkpt/fdzdgknr/202012/t20201207_374134.shtml`（应急预案管理办法） |
| `gf.cabr-fire.com` | `…/m/article-37836.htm` 等按节页面 |
| `www.court.gov.cn` | `…/zixun/xiangqing/212721.html`（民事诉讼证据规定） |

⚠️ **但本轮未做批量替换**，理由见下节 —— **升级 `source` 是"声称该页就是出处"，
必须逐条确认该页确实载有该文件，不能拿一个"同主机的任意深链接"顶上。**

---

## 五、⚠️ 本轮**不做**批量替换的理由（如实标注）

1. **`source` 是"出处声明"**，与 `excerpt` 同等性质 ——
   **换成一个我没打开过的深链接，等于把"首页"换成"看似精确却未经确认的页面"**，
   性质比首页更坏（这正是第 62 轮"标准号看似精确实为作废"的同一类错误）；
2. **292 处无法在本轮逐条确认**；
3. ⇒ **本轮的正确产出是"把问题量化并分类"，而不是"用一个脚本把首页批量换成猜测的深链接"。**

**建议的后续做法**：按插件分批做 ——
**每轮挑 1–2 个插件，打开其证据报告里的深链接确认该页确载该文件，再逐条升级 `source`**；
对**确实没有公开深链接的**（AIAG／IATF／ICC 等），
**在 `source` 处写明"该文件需购买／不对外，此为发布机构首页"**。

---

## 六、复现方法

```sh
node scripts/inventory-source-hosts.mjs    # 34 个主机及其条数（含覆盖率）
node scripts/audit-source-hosts.mjs        # 判定 403/447，报出可疑配对
node scripts/audit-bare-sources.mjs        # 292 处首页按插件列出
node scripts/harvest-deep-links.mjs        # 证据报告里现成的 64 个主机深链接
```

## 六之二、⚠️ 第 68 轮的执行结果：**升级了 3 个包，并抓出一个假深链接**

### 已升级（每一条都**打开确认过页面内容**）

| 插件 | 条数 | 升级后的 `source` | 打开确认的内容 |
|---|---|---|---|
| `dsh-fmea-table-check` | **8** | `…/bzgk/std/newGbInfo?hcno=72487561F0A0B469A6C105FBD3652545` | **GB/T 7826-2012**，名称「系统可靠性分析技术 失效模式和影响分析（FMEA）程序」，**状态 现行**，发布 2012-11-05、实施 2013-02-15，CCS L05 |
| `dsh-spc-gbt-adapter` | **7** | `…/bzgk/gb/newGbInfo?hcno=B04BA7B024E7439B35C21493F4F7C3F9` | **GB/T 17989.2-2020**，**状态 现行**，发布 2020-03-06、实施 2020-10-01 |
| `dsh-learning-gap-check` | **7** | `…/bzgk/std/newGbInfo?hcno=D49E0CDA27AE25C80AF34FDA534B5E9A` | **GB/T 19025-2023**，**状态 现行**，发布并实施 2023-03-17，CCS A00、ICS 03.120.10 |

**全库效果**：具体页面 **155 → 177**，首页 **292 → 270**。

### ⚠️⚠️ 并抓出一个**假深链接** —— 它正好证明"批量替换"是危险的

证据报告里存着一个指向 `openstd.samr.gov.cn` 的"深链接"，被当作 **GB/T 7826** 的出处：

```
https://openstd.samr.gov.cn/bzgk/std/newGbInfo?hcno=EB1CC0500D91490B5D219823AC1F3D16
```

**打开它，页面显示的是 `GB/T 18894-2016`《电子文件归档与电子档案管理规范》** ——
⚠️ **与 GB/T 7826 毫无关系**。而该链接**出现在 4 个包的证据报告里**
（`dsh-archive-check`、`dsh-hazplan-check`、`dsh-power-ticket-check`、本报告）。

⇒ **已全部更正为核实的 GB/T 7826-2012 页面**（4 处）。

**这件事的意义**：若按上一轮设想的"从证据报告里把深链接批量搬到 `source`"，
**这个假链接会被复制进 4 个包的 `source` 字段**，而且**看起来比首页精确得多** ——
**这正是上一轮报告第二节所担心的错误，本轮真的发生了。**
⇒ **"逐条打开确认"不是多余的谨慎，而是必需的步骤。**

---

## 七、后续动作

- [x] **量化问题**：447 个 `source` 中 **292 个（65%）为首页**、155 个为具体页面。
- [x] **修正审计工具**：第一版覆盖率仅 21%，第二版达 90%；
      **并确立"审计脚本必须先自证覆盖范围"这一要求**。
- [x] **分类 24 处报项**：真缺陷 2 类（主机错配 2 处、首页 22 处），其余为**正则误报**。
- [x] **记录了 64 个主机的现成深链接**（`harvest-deep-links.mjs`），供后续分批升级使用。
- [x] **已升级 3 个包、共 22 条 `source`**；全库具体页面 155 → **177**。
- [x] **已更正 4 处假深链接**（点开发现指向 GB/T 18894-2016 而非 GB/T 7826）。
- [ ] **待做**：其余 `openstd.samr.gov.cn` 首页仍有 **25 处**
      （`dsh-gongwen-word-check` 5、`dsh-guard-plan-qc` 6、`dsh-lawcite-adapter` 6、
      `dsh-hazchem-check` 4、`dsh-lc-doc-check`／`dsh-customs-doc-check`／
      `dsh-demurrage-ledger`／`dsh-forecast-penalty` 各 1 等）——
      **每一条都须先打开确认页面确载该标准，再写进 `source`**。
- [ ] ⚠️ **并应把 `audit-bare-sources.mjs` 纳入常规审计** ——
      `source` 是出处声明，**270 处不可定位在本项目中不应长期存在**。
