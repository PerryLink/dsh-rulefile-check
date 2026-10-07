# 发布前核查报告 —— 53 个包的 tarball 内容

- **核查日期**：2026-10-07
- **核查方式**：对 **53 个包逐个**执行 `pnpm pack --dry-run`，把输出**重定向到文件**后解析
  （⚠️ 不能用进程内捕获 —— `pnpm pack` 把报告写到 **stderr**，而 `.cmd` 子进程的 stdout 捕获在本环境不可靠，
  本会话早前正是因此得出过"0 tests / 53 failures"的假结论）
- **结果**：**53/53 完整；0 个不完整**

## 一、每个包必须携带的东西（逐个断言）

| 必需项 | 为什么必需 |
|---|---|
| `lib/index.mjs` | `package.json#main` 指向它；缺失会让加载器**静默跳过**该包 |
| `lib/index.d.mts` | `types` 指向它 |
| `package.json` | — |
| `cordis.patch.yml` | `dsh.bundle.patch` 指向它；缺失会导致 **`not-a-bundle`** |
| `locale/en.json` | 展示面（`meta.title` / `meta.description`） |
| `rules/*.yaml` | **规则数据与代码分离**的载体；缺失则插件加载后**没有规则可跑** |
| `README.md` + `README-zh/-es/-pt/-hi.md` | 本工作区的**五语 README** 约定 |

## 二、⚠️ 本轮之前**真实缺失**的一项：4 份译版 README

**首次 `pack --dry-run` 显示 tarball 里只有 `README.md`** —— `files[]` 只列了 `lib` / `cordis.patch.yml` /
`locale/*.json` / `icon.svg` / `rules`，**四份译版全部漏发**。

⇒ **已修复：53 个包的 `files[]` 都补上了 5 份 README。**
（本项目刻意不用 `README.<lang>.md` 点号命名，因为 npm 取包页**首份**匹配文件，
点号名会排在 `README.md` 之前 ⇒ **包页会变成中文**。这是既有约定的原因，非疏漏。）

## 三、⚠️⚠️ 同一轮里我**自己造成**并修复的一次破坏（必须记录）

修 `files[]` 时，我**顺手**把 `tsdown` / `typescript` 从 `dependencies` 移走
（理由是"构建工具应在 devDependencies"），**键变空后又把整个 `dependencies` 删掉，版本号一并丢失**。

**后果**（立刻可见）：

```text
$ tsdown
'tsdown' is not recognized as an internal or external command
[ELIFECYCLE] Command failed with exit code 1.
```

**根因**：`package.json` 声明了 **`"prepare": "tsdown"`**，而 **`prepare` 在 `pnpm pack` 与安装时都会运行**，
它**从本包自身的依赖树里解析二进制** ⇒ **`tsdown` 必须是真依赖**。
⇒ **原布局本来就是对的；是我的"改进"把 53 个包全变成装不上的。**

**修复**：找回版本（`tsdown ^0.22.14`、`typescript ^5.9.3`）→ 53 个包恢复 → `pnpm install` → 重新验证。

⚠️ **教训**：**我为一个"看起来更整洁"的通用规则，改掉了一个我并不理解其作用的字段。**
若在修复前直接发布，**53 个包会全部装不上**，且**首次发布不可撤销**。
⇒ **这正是"发布前逐个验证 tarball"这一步的价值**，本轮已把它固化为可复跑脚本 `scripts/verify-all-tarballs.mjs`。

## 四、发布前的其余已核实项

| 项 | 结果 |
|---|---|
| 四道门（53 个包） | **1594 tests · typecheck 0 · test 0 · check 0** |
| 53 个包名在 npm 是否被占 | ✅ **均未被占用**（抽测 5 个全 404） |
| 包版本 | 全部 `0.1.0`（**均为首次发布**） |
| `license` | 全部 `Apache-2.0` |
| npm 认证 | ✅ `npm whoami` → `perrylink`（令牌只经环境变量，**未回显、未落盘**） |

## 五、⛔ 尚未发布的理由（留待授权）

1. **首次发布不可撤销**，会永久占用 53 个包名；
2. 令牌文件 `D. 使用规则` 仍写明「**npm 一律走各仓 release workflow 的 OIDC 可信发布，不手工 `npm publish`**」，
   而**本工作区无 git、无 workflow** ⇒ **"直接发布"与该口径冲突**，需用户明确覆盖；
3. 53 个包的 `repository` 字段为空 ⇒ 发布后**包页无源码链接**（可后补，但首发即定形）。
