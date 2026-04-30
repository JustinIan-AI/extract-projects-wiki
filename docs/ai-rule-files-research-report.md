# AI 编程规则文档调研报告

## AGENTS.md × CLAUDE.md × 团队实践方法

最近天天刷到盛赞Katpathy大神的CLAUDE.md，我去学习了下核心就是四条约束：

https://x.com/karpathy/status/2015883857489522876

https://github.com/forrestchang/andrej-karpathy-skills

![1777517643109](image/ai-rule-files-research-report/1777517643109.png)

1. Think Before Coding
2. Simplicity First
3. Surgical Changes
4. Goal-Driven Execution
   但这属于方法论级别的，到底与我们实际应用过程中的rules有哪些关系？AGENTS.md、CLAUDE.md之间如何共生？我把我的调研结论和操作方法分享给大家

---

## 目录

1. [背景：为什么规则文档变得重要](#1-背景)
2. [AGENTS.md：定义、边界与最佳实践](#2-agentsmd)
   - [2.1 定义](#21-定义)
   - [2.2 边界](#22-边界)
   - [2.3 最佳实践](#23-最佳实践)
3. [CLAUDE.md：定义、边界与最佳实践](#3-claudemd)
   - [3.1 定义](#31-定义)
   - [3.2 边界](#32-边界)
   - [3.3 最佳实践](#33-最佳实践)
4. [两者关系与工具支持对比](#4-对比与关系)
5. [团队 AGENTS.md 通用模板](#5-团队模板仅供参考)
6. [规范抽取方法论](#6-规范抽取方法论)
   - [6.1 规范抽取工作坊](#61-规范抽取工作坊)
   - [6.2 Monorepo 项目的规范抽取策略](#62-monorepo-项目的规范抽取策略)
   - [6.3 引入私域知识：参考项目方法](#63-引入私域知识参考项目方法)
   - [6.4 项目扫描工具](#64-项目扫描工具)
7. [常见误区](#7-常见误区)
8. [总结](#8-总结)
9. [附录：团队实践方法供参考](#附录团队实践方法供参考)

---

## 1. 背景

### 1.1 Specs驱动下的事实性约束标准

`AGENTS.md` 和 `CLAUDE.md` 是放在代码仓库中的 Markdown 文件，在 AI 开始工作前**自动加载**，相当于为每次会话提供一份项目入职材料。

> **类比**：README.md 是给人类看的项目说明，AGENTS.md/CLAUDE.md 是给 AI 看的操作手册。

### 1.2 生态现状（截止2026年4月）

| 指标                       | 数据                                      |
| -------------------------- | ----------------------------------------- |
| AGENTS.md 采用的开源仓库数 | 60,000+                                   |
| 支持 AGENTS.md 的工具数    | 60+                                       |
| AGENTS.md 标准管理方       | Linux Foundation（Agentic AI Foundation） |
| CLAUDE.md 标准管理方       | Anthropic                                 |

---

## 2. AGENTS.md

### 2.1 定义

AGENTS.md 是由 **OpenAI 首创、Linux Foundation 旗下 Agentic AI Foundation 管理的开放标准**，是一种放置于代码仓库中、专门面向 AI 编程 Agent 的规范配置文件。

**核心作用**：

- 统一不同 AI 工具的项目上下文认知
- 规范 AI 的行为边界
- 让 AI 能像资深开发者一样精准参与项目协作

**支持工具（主流）**：OpenAI Codex、Cursor、GitHub Copilot、Windsurf、Aider、Gemini CLI、Claude Code（兼容回退）等 60+ 种工具

### 2.2 边界

#### 文件位置与生效规则

```
项目根目录/
├── AGENTS.md            ← 全局规则，对所有 AI 工具生效
├── src/
│   └── AGENTS.md        ← 对 src/ 目录内的任务生效（就近原则）
├── tests/
│   └── AGENTS.md        ← 对 tests/ 目录内的任务生效
└── docs/
    └── AGENTS.md        ← 对 docs/ 目录内的任务生效
```

**优先级规则（从高到低）**：

1. 用户在对话中的直接提示词（最高优先级，可覆盖文件规则）
2. 距离当前操作文件最近的 `AGENTS.md`（子目录级）
3. 项目根目录的 `AGENTS.md`（全局项目级）

#### 内容边界：该写什么 / 不该写什么

**✅ 应该写（AI 无法从代码中推断的内容）**：

- 构建、测试、运行命令（`npm run dev`、`make test` 等）
- 非默认的技术选型（"使用 Zustand，不用 Redux"）
- 分层架构约束（"禁止 Controller 层直接调用 Repository"）
- 私域组件/内部库的使用方式（AI 训练数据中不存在的内容）
- 安全红线（"所有 DB 查询必须过滤 tenantId"）
- 代码审查重点（"PR 必须包含测试用例"）

**❌ 不应该写（冗余、会消耗"指令预算"的内容）**：

- 语言本身的通用规范（"写干净的代码"、"使用有意义的变量名"）
- Linter/Formatter 已经自动检查的规则（ESLint、Prettier 等）
- README 中人类读者需要的项目介绍性文字
- 频繁变动的内容（版本号、日期等）
- 详细的 API 文档（给链接即可）

> ⚠️ **指令预算约束**：研究表明前沿 LLM 只能合理遵循约 150-200 条指令，系统提示词已占用部分额度。**核心原则是无情的优先级排序，而非全面性**。超过此上限，AI 会开始选择性忽略规则，适得其反。

### 2.3 最佳实践

#### 实践一：渐进式披露（最重要）

主文档控制在 **100-150 行**，只做高层级索引，具体细节推送到独立参考文档并通过链接引用。

```markdown
# 项目架构规范
详细说明见 [架构文档](./docs/architecture.md)

# 测试规范
完整测试清单见 [测试规范](./docs/testing-guide.md)
```

> 📊 量化数据：渐进式披露可带来 10-15% 的全方位提升（代码准确性、完整性、规范复用率）

#### 实践二：过程化工作流

将任务拆分为带编号的多步骤指引，大幅降低任务遗漏率。

```markdown
## 新增 API 端点流程
1. 在 `src/routes/` 创建路由文件
2. 在 `src/services/` 实现业务逻辑
3. 在 `src/repositories/` 封装数据访问
4. 在 `tests/` 补充单元测试
5. 更新 `docs/api.md` 接口文档
```

#### 实践三：决策表消歧义

针对有多种可行路径的场景，用决策表提前消除架构分歧。

```markdown
## 状态管理选择
| 场景 | 推荐方案 | 禁止方案 |
|------|----------|----------|
| 组件本地状态 | useState/useReducer | - |
| 跨组件共享状态 | Zustand | Redux、MobX |
| 服务端状态 | React Query | 自己写 fetch |
```

#### 实践四：真实代码片段

提供 3-10 行生产环境真实代码模板，引导 AI 模仿现有模式。

```markdown
## API 响应格式（必须遵循）
\`\`\`typescript
// ✅ 正确格式
return res.json({ code: 0, data: result, message: 'success' });

// ❌ 禁止格式
return res.json(result);
\`\`\`
```

#### 实践五：禁令必须搭配替代方案

仅告知 AI "不要做什么" 会导致其过度探索，必须同步给出可行方案。

```markdown
# ❌ 错误写法
NEVER use raw SQL queries.

# ✅ 正确写法
NEVER use raw SQL queries. Use the QueryBuilder from `src/db/query-builder.ts` instead.
```

#### 实践六：Bad Case 驱动迭代

不要试图一次写完，从实际使用中 AI 犯的错误出发，持续补充规则。这是最高效的迭代方式。

```markdown
## 经验教训（AI 犯过的错误记录）
- 本项目使用 ESM，NEVER 用 `require()`，统一使用 `import`
- 数据库迁移文件 NEVER 直接修改，只能新增
- 前端路由统一通过 `useNavigate`，NEVER 使用 `window.location`
```

---

## 3. CLAUDE.md

### 3.1 定义

CLAUDE.md 是由 **Anthropic 为 Claude Code 设计的专属配置文件**，是功能最丰富的 AI 编程规则文件格式。

与 AGENTS.md 的本质区别在于：**CLAUDE.md 不只是一个文本文件，它是一套具备工程能力的配置体系**——支持模块化导入、路径限定规则、Hooks 联动、自动记忆等高级功能。

### 3.2 边界

#### 文件位置与五级层次结构

```
~/.claude/CLAUDE.md               ← Level 1: 全局用户配置（跨所有项目生效）
项目根目录/
├── CLAUDE.md                     ← Level 2: 项目级配置（最常用）
├── CLAUDE.local.md               ← Level 3: 个人本地配置（加入 .gitignore，不提交）
├── src/
│   └── CLAUDE.md                 ← Level 4: 子目录配置（Monorepo 专用）
└── .claude/
    └── rules/
        ├── testing.md            ← Level 5: 模块化规则文件
        └── api-design.md
```

**优先级（从高到低）**：

1. `CLAUDE.local.md`（当前目录的个人私有配置）
2. `CLAUDE.md`（当前目录的项目配置）
3. 父目录的 `CLAUDE.md`（Monorepo 场景向上查找）
4. `~/.claude/CLAUDE.md`（全局用户配置，最低优先级）

#### 独有能力（AGENTS.md 不具备）

| 功能                     | 说明                                       | 语法                    |
| ------------------------ | ------------------------------------------ | ----------------------- |
| **模块化导入**     | 将规则文件拆分引用，避免主文件臃肿         | `@path/to/rules.md`   |
| **路径限定规则**   | 规则只对特定路径的文件生效                 | YAML frontmatter 中定义 |
| **Hooks 联动**     | 在特定事件后自动触发检查命令               | `.claude/hooks/`      |
| **自动记忆**       | `/remember` 指令将经验自动写入 CLAUDE.md | Claude Code 内置命令    |
| **`/init` 命令** | 自动分析项目并生成初版 CLAUDE.md           | Claude Code 内置命令    |

#### `@` 导入示例

```markdown
# CLAUDE.md 主文件

@.claude/rules/testing.md
@.claude/rules/api-design.md
@docs/architecture.md

## 本文件包含的核心规则（控制在 50 行以内）
...
```

### 3.3 最佳实践

#### 实践一：用 `/init` 生成初稿，然后大刀阔斧删减

```bash
# 在 Claude Code 中执行
/init
```

Claude Code 会分析项目结构，自动生成一份初版 CLAUDE.md。**但生成的内容往往包含大量冗余**，需要删减 60-70% 的样板文字，只保留真正会改变 AI 行为的规则。

#### 实践二：遵循"是什么 → 为什么 → 怎么做"结构

```markdown
# CLAUDE.md

## 技术栈（是什么）
- 后端：Node.js 22 + Express + TypeScript
- 数据库：PostgreSQL 16 + Prisma ORM
- 前端：React 19 + Vite + TailwindCSS

## 关键架构决策（为什么）
- 使用 Prisma 而非原生 SQL：团队不熟悉 SQL 优化，统一走 ORM 降低维护成本
- 禁止 Redux：项目状态简单，Zustand 已足够，避免引入复杂度

## 常用命令（怎么做）
\`\`\`bash
npm run dev          # 启动开发服务器
npm run test         # 运行测试套件
npm run build        # 生产构建
npm run db:migrate   # 执行数据库迁移
\`\`\`
```

#### 实践三：分层配置策略

```
共享规则（提交 Git）：
  CLAUDE.md → 项目规范，全员遵守

个人偏好（不提交 Git）：
  CLAUDE.local.md → 个人快捷方式、本地路径配置

全局习惯（跨项目）：
  ~/.claude/CLAUDE.md → 个人一贯的工作风格
```

#### 实践四：规则必须可测试

每条规则加入后，立即验证：

1. 新开一个 Claude Code 会话
2. 给一个应该触发该规则的任务
3. 观察 Claude 是否遵循
4. 不遵循 → 规则表述不清，重写；遵循 → 规则有效，保留

#### 实践五：与 Hooks 联动，强制执行关键规则

对于不能依赖 AI 自觉的关键规则（如安全扫描、格式检查），用 Hooks 确定性强制执行，不消耗指令预算：

```json
// .claude/hooks/post-edit.json
{
  "command": "npm run lint && npm run test",
  "trigger": "after_file_edit"
}
```

在 CLAUDE.md 中声明：

```markdown
## 自动化检查（由 Hooks 执行，无需 AI 手动处理）
- 代码格式：prettier（保存时自动格式化）
- Lint 检查：ESLint（编辑后自动运行）
```

---

## 4. 对比与关系

### 4.1 核心差异对比

| 维度                     | AGENTS.md               | CLAUDE.md                          |
| ------------------------ | ----------------------- | ---------------------------------- |
| **适用工具**       | 60+ 种（跨平台通用）    | 仅 Claude Code                     |
| **标准管理方**     | Linux Foundation        | Anthropic                          |
| **文件格式**       | 纯 Markdown，无特殊语法 | 支持 YAML frontmatter、`@import` |
| **多层级支持**     | 是（就近原则）          | 是（五级层次）                     |
| **高级功能**       | 无                      | Hooks、自动记忆、路径限定          |
| **适合场景**       | 多工具团队、开源项目    | 全员使用 Claude Code 的团队        |
| **开源项目采用率** | 60,000+                 | Claude Code 用户为主               |

### 4.2 推荐组合策略

```
场景 A：团队只用 Claude Code
→ 只维护 CLAUDE.md，充分利用其高级功能

场景 B：团队使用多种 AI 工具（Claude Code + Cursor + Copilot）
→ 通用规则写在 AGENTS.md
→ CLAUDE.md 通过 @AGENTS.md 导入，再叠加 Claude 专属功能
→ 一套规则，多工具共享

场景 C：开源项目
→ 只维护 AGENTS.md（兼容性最广）

场景 D：个人开发者
→ ~/.claude/CLAUDE.md 配置全局偏好
→ 项目根目录 CLAUDE.md 配置项目特定规则
```

**最佳实践（场景 B）的文件结构**：

```markdown
# CLAUDE.md

@AGENTS.md          ← 导入通用规则（所有工具共享）

## Claude Code 专属配置
（这里放 Claude Code 独有的功能配置）
```

---

## 5. 团队模板（仅供参考)

以下提供一个**通用团队 AGENTS.md 模板**，可根据实际项目填充。

```markdown
# AGENTS.md — [项目名称] AI 协作规范
> 版本：v1.0 | 最后更新：YYYY-MM-DD | 维护人：[团队负责人]

---

## 🏗️ 技术栈

### 后端
- 语言：[如：Node.js 22 / Python 3.12 / Go 1.22]
- 框架：[如：Express / FastAPI / Gin]
- ORM/数据访问：[如：Prisma / SQLAlchemy / GORM]
- 数据库：[如：PostgreSQL 16 / MySQL 8]

### 前端（如有）
- 框架：[如：React 19 / Vue 3 / Next.js 15]
- 状态管理：[如：Zustand / Pinia]
- UI 组件库：[如：TailwindCSS + shadcn/ui]
- 构建工具：[如：Vite / Turbopack]

### 基础设施
- 容器：[如：Docker + Kubernetes]
- CI/CD：[如：GitHub Actions / Jenkins / Harness]
- 代码仓库结构：[monorepo / multi-repo]

---

## ⚡ 常用命令

\`\`\`bash
# 开发
[启动命令，如：npm run dev / python manage.py runserver]

# 测试
[测试命令，如：npm run test / pytest / go test ./...]

# 构建
[构建命令，如：npm run build / make build]

# 数据库
[迁移命令，如：npm run db:migrate / alembic upgrade head]

# 代码检查
[lint 命令，如：npm run lint / ruff check .]
\`\`\`

---

## 📁 目录结构

\`\`\`
[项目名]/
├── src/
│   ├── routes/         # [路由层说明]
│   ├── services/       # [业务逻辑层说明]
│   ├── repositories/   # [数据访问层说明]
│   └── models/         # [数据模型说明]
├── tests/              # [测试文件组织方式]
├── docs/               # [文档目录]
└── scripts/            # [脚本目录]
\`\`\`

---

## 📐 架构约束

### 分层规则（MUST 遵守）
- Routes 层 ONLY 负责参数校验和路由转发，业务逻辑 MUST 在 Service 层
- Service 层 NEVER 直接操作数据库，MUST 通过 Repository 层
- Repository 层 ONLY 包含数据访问逻辑，NEVER 包含业务判断

### 技术选型约束
- [示例：状态管理 MUST 使用 Zustand，NEVER 引入 Redux]
- [示例：HTTP 请求 MUST 使用 axios，NEVER 使用 fetch 原生 API]
- [示例：日期处理 MUST 使用 dayjs，NEVER 使用 moment.js（已废弃）]

### 安全红线（CRITICAL）
- [示例：所有数据库查询 MUST 按 tenantId 过滤，防止数据越权]
- [示例：NEVER 在日志中输出用户密码、token、手机号等敏感字段]
- [示例：所有外部输入 MUST 经过 schema 校验（使用 zod / joi）]

---

## 🎨 代码风格

### 命名规范
- 文件名：[如：kebab-case（user-service.ts）]
- 类名：[如：PascalCase（UserService）]
- 函数/变量：[如：camelCase（getUserById）]
- 常量：[如：UPPER_SNAKE_CASE（MAX_RETRY_COUNT）]
- 数据库表名：[如：snake_case（user_orders）]

### 代码示例（MUST 参考现有风格）
\`\`\`typescript
// ✅ 正确示例：[说明这段代码体现了什么规范]
[粘贴项目中的真实代码片段，3-10行]

// ❌ 错误示例：[说明这段代码违反了什么规范]
[粘贴反例]
\`\`\`

---

## ✅ 测试规范

- 测试框架：[如：Jest / Vitest / pytest]
- 最低覆盖率要求：[如：核心业务逻辑 80%]
- 测试文件位置：[如：与源文件同目录 / 统一在 tests/ 目录]
- 测试命名规范：[如：describe('UserService', () => { it('should return user by id') })]
- MUST 为以下内容写测试：[如：所有 Service 层公共方法、所有 API 端点]
- NEVER 在测试中连接真实数据库：[如：使用 jest.mock() 或内存数据库]

---

## 🔀 Git 工作流

- 分支命名：[如：feature/[JIRA-ID]-brief-description]
- Commit 格式：[如：遵循 Conventional Commits：feat/fix/docs/refactor/test]
- PR 要求：[如：MUST 包含测试用例 / MUST 通过 CI 检查 / MUST 至少 1 人 Review]
- NEVER 直接向 main/master 分支推送

---

## 🚫 项目特定禁止项

> 这里记录项目历史中踩过的坑和不可触碰的约束

- [示例：NEVER 修改 migrations/ 目录下的已有文件，只能新增]
- [示例：NEVER 在 Controller 层写超过 20 行的业务逻辑]
- [示例：NEVER 使用 `any` 类型，除非有明确注释说明原因]
- [示例：NEVER 在 main 分支直接提交，ALWAYS 走 PR 流程]

---

## 📚 经验教训

> AI 在本项目中曾经犯过的错误，防止重蹈覆辙

- [示例：本项目的 API 路径统一用 `/api/v2/`，NEVER 用 `/api/v1/`（旧版已废弃）]
- [示例：环境变量通过 `config/index.ts` 统一导出，NEVER 直接用 `process.env.xxx`]

---

## 🔗 参考文档

- 架构设计文档：[链接]
- API 接口文档：[链接]
- 数据库 ER 图：[链接]
- 部署流程文档：[链接]
```

---

## 6. 规范抽取方法论

### 6.1 规范抽取工作坊（建议 2-3 人、90 分钟）

这是从现有项目中提炼团队规范、填充 AGENTS.md 的核心方法。

**参与者**：技术负责人 + 1-2 名熟悉项目的资深开发

#### Step 1：扫描代码库（20分钟）

让 AI（或人工）分析以下几个维度：

```bash
# 用 Claude Code 执行（效率最高）
# 在项目根目录打开 Claude Code，输入：

"请分析这个项目的技术栈、目录结构、常用命令（package.json 或 Makefile），
以及代码风格特点，生成一份项目概览。"
```

人工补充检查：

- `package.json` / `Makefile` / `pyproject.toml` → 提取构建/测试/运行命令
- `.eslintrc` / `prettier.config` / `tsconfig.json` → 了解已自动化的检查（这些**不需要**写进 AGENTS.md）
- 目录结构 → 理解分层架构

#### Step 2：Code Review 痛点收集（30分钟）

这是最有价值的一步——**从历史 PR 评论中提炼规则**。

```
收集渠道：
① 查看最近 3 个月 GitHub/GitLab 上的 PR 评论
② 提问团队成员：「你最常在 Code Review 中反复纠正什么？」
③ 查看 Jira/Linear 中的 Bug 标签，找出重复出现的问题类型

提炼规则的判断标准：
✅ 超过 2 次被评论同一问题 → 必须写进规则
✅ 新人入职时必须被告知的事项 → 写进规则
✅ 引发过线上故障的操作习惯 → 写进规则（用 CRITICAL 标注）
❌ 只有 1 次的单点问题 → 不写，避免噪音
```

**收集表格模板**：

| 问题描述                         | 频率        | 优先级 | 转化为规则                                       |
| -------------------------------- | ----------- | ------ | ------------------------------------------------ |
| 直接操作 DOM 而不通过 React 状态 | 每周 2-3 次 | 高     | NEVER 直接操作 DOM，状态变更 MUST 通过 setState  |
| 忘记处理 async 函数的错误        | 每月 5 次   | 中     | 所有 async 函数 MUST 使用 try-catch 或 .catch()  |
| 在 console.log 遗留调试信息      | 每周 1 次   | 低     | NEVER 在 PR 中提交 console.log，使用 logger 工具 |

#### Step 3：架构红线确认（20分钟）

与架构师/技术负责人确认以下问题：

```
必问清单：
□ 哪些技术/库是明确禁用的？（原因是什么？）
□ 分层架构有哪些绝对不能违反的规则？
□ 有哪些安全约束是必须强制执行的？（如多租户隔离、数据脱敏）
□ 有哪些历史遗留问题是 AI 不知道的？（如某个目录不能碰）
□ 有哪些接口/工具是内部私有的，外部 AI 训练数据中不存在的？
```

#### Step 4：初稿生成与精炼（20分钟）

将以上信息填入模板，然后执行"删减原则"：

```
对每一条规则问自己：
"如果删掉这条规则，Claude/AI 的输出会变差吗？"

→ 会变差：保留
→ 不会（因为 AI 本来就会做）：删除
→ 不确定：用 Claude Code 测试一下
```

#### Step 5：真实代码片段补充（10分钟）

从现有代码库中拷贝 3-5 个最典型的"正确写法"示例，放入 AGENTS.md 的对应章节。

> 研究数据：提供真实代码片段，可提升 AI 代码复用率 20%。

### 6.2 Monorepo 项目的规范抽取策略

对于包含多个子项目的 monorepo，采用分层抽取：

```
根目录 AGENTS.md（80-100行）：
  ├── 通用构建/测试命令
  ├── 跨模块架构约束
  ├── 全局安全规则
  └── Git 工作流规范

packages/backend/AGENTS.md（50-70行）：
  ├── 后端特定技术栈
  ├── API 设计规范
  └── 数据库操作规范

packages/frontend/AGENTS.md（50-70行）：
  ├── 前端组件规范
  ├── 状态管理规则
  └── 样式规范

packages/shared/AGENTS.md（30-40行）：
  ├── 公共类型定义规范
  └── 工具函数规范
```

### 6.3 引入私域知识：参考项目方法

对于 AI 训练数据中不存在的内部组件库、私有工具，采用 **git submodule 引入源码** 的方式：

```bash
# 将内部组件库的源码引入项目
git submodule add [内部组件库地址] reference-projects/internal-ui

# 在 AGENTS.md 中声明
```

```markdown
## 内部私有依赖
本项目依赖以下内部组件库（AI 训练数据中不存在，请参考源码）：
- `@company/ui-kit`：位于 `reference-projects/internal-ui/`
- `@company/request`：位于 `reference-projects/internal-request/`

使用这些组件前，MUST 先阅读对应的 README 和 examples 目录。
```

## 6.4 项目扫描工具

---

## 7. 常见误区

### 误区一：越详细越好

> ❌ 误区：写了 500 行，覆盖所有可能的情况
>
> ✅ 正确：上限 200 行，超出部分拆分为链接子文档。超过 150-200 条指令后，AI 开始选择性忽略规则，优先级高的规则反而被淹没。

### 误区二：把 README 内容复制进去

> ❌ 误区："本项目是电商平台，用于管理商品、订单、用户……"
>
> ✅ 正确：README 回答"是什么"，AGENTS.md 只回答"怎么开发"。

### 误区三：只写禁止项，不给替代方案

> ❌ 误区：`NEVER use Redux`
>
> ✅ 正确：`NEVER use Redux. Use Zustand from the existing setup in src/store/`

### 误区四：规则缺乏执行力，靠 AI 自觉

> ❌ 误区：写了"禁止提交 console.log"，但没有 lint 规则
>
> ✅ 正确：关键规则 = 规则文件声明 + 自动化检查脚本。规则优先级：**自动化检查 > 写在文件中 > 口头约定**

### 误区五：写完不维护

> ❌ 误区：一次性写完，之后从不更新
>
> ✅ 正确：建立触发机制——AI 犯错 → 立即添加规则；规则超过 200 行 → 立即删减。把规则文件当作代码一样 Code Review。

### 误区六：文档放错位置

> ❌ 误区：重要规则放在 `_docs/` 子目录下的独立文件中，不在 AGENTS.md 中引用
>
> ✅ 正确：AI 对不同位置文档的发现率差异极大——
>
> - AGENTS.md 本身：100%
> - AGENTS.md 中引用的链接：90%+
> - 根目录 README.md：80%
> - 孤立文档（`_docs/` 等）：<10%

---

## 8. 总结

### 核心结论

1. **AGENTS.md 是跨工具通用标准**，适合多工具团队和开源项目，纯 Markdown，上手成本最低
2. **CLAUDE.md 是 Claude Code 专属的增强版本**，支持 Hooks、模块化导入等工程化能力，适合全员使用 Claude Code 的团队
3. **最佳组合**：通用规则写 AGENTS.md，CLAUDE.md 通过 `@AGENTS.md` 导入并叠加增强功能
4. **质量比数量重要**：写好等于升级模型，写坏不如不写
5. **规则文件是活文档**：从 Bad Case 出发驱动迭代，才是最高效的维护方式

## 附录.团队实践方法供参考

### 9.1 落地路线图（建议分三个阶段）

```
第一阶段（第1-2周）：破冰
  目标：建立基础文件，消除最高频的 AI 返工问题
  行动：
  ① 选 1 个核心项目试点
  ② 执行"规范抽取工作坊"（见第6章）
  ③ 生成初版 AGENTS.md（控制在 80 行以内）
  ④ 全员试用 1 周，记录 AI 犯错的 Bad Case

第二阶段（第3-4周）：迭代
  目标：基于实际使用反馈，精炼规则
  行动：
  ① 将 Bad Case 转化为新规则
  ② 删除从未被触发的规则
  ③ 将超过 15 行的章节拆分为独立子文档
  ④ 推广至其他项目

第三阶段（持续）：制度化
  目标：将规则文件纳入工程规范
  行动：
  ① 纳入 Git 仓库（AGENTS.md 提交，CLAUDE.local.md 加入 .gitignore）
  ② 建立"规则更新触发条件"：AI 犯错 → 添加规则
  ③ 每月 Review 一次，删除过时规则
  ④ 在 onboarding 流程中包含规则文件讲解
```

### 9.2 规则更新的触发机制

```
触发更新的信号：
  ✅ AI 重复犯同一个错误（超过 2 次）→ 必须加规则
  ✅ Code Review 中经常出现同类反馈 → 必须加规则
  ✅ 新人入职时问的常见问题 → 适合加规则
  
触发删除的信号：
  🗑️ 该规则对应的技术已不再使用（如迁移了框架）
  🗑️ AI 从未违反过这条规则（说明可能是多余的或 AI 本来就知道）
  🗑️ 文件超过 200 行 → 必须删减或拆分
```

---
