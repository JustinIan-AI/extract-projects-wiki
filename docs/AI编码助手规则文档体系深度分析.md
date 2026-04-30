# AI 编码助手规则文档设计深度分析

> **分析日期**：2026-04-29
> **分析范围**：gstack-main、everything-claude-code-1.10.0、BMAD-METHOD-main
> **分析目标**：对比不同仓库的规则设计技巧，为团队规则体系选型提供参考

---

## 一、规则文档体系概述

### 1.1 核心概念定义

#### CLAUDE.md
| 维度 | 说明 |
|------|------|
| **定位** | Claude Code 专用配置文件，为 Claude 提供项目级上下文 |
| **加载时机** | 每次对话开始时自动加载 |
| **作用域** | 仓库根目录（团队共享）/ 父目录（monorepo）/ 主文件夹（全局） |
| **官方支持** | Anthropic Claude 官方维护 |

#### AGENTS.md
| 维度 | 说明 |
|------|------|
| **定位** | 通用 AI 编码代理指令格式，跨平台兼容 |
| **加载时机** | AI 代理自动扫描，嵌套文件优先 |
| **作用域** | 支持多层级嵌套（monorepo 场景） |
| **生态** | Agentic AI Foundation（Linux Foundation 旗下），60,000+ 项目采用 |

#### 关键区别

| 对比维度 | CLAUDE.md | AGENTS.md |
|---------|-----------|-----------|
| **提出者** | Anthropic Claude | OpenAI Codex 社区 → Agentic AI Foundation |
| **支持范围** | 仅 Claude 系列 | 25+ 种 AI 编码工具（通用生态） |
| **文件命名** | 单数形式 `CLAUDE.md` | 复数形式 `AGENTS.md` |
| **嵌套支持** | 通常单文件 | 原生支持多层级 |
| **生态成熟度** | 官方支持，快速迭代 | 开放标准，社区驱动 |

### 1.2 规则文档层级架构

```
项目根目录
├── CLAUDE.md                    # 项目级上下文（必选）
├── AGENTS.md                    # 通用代理指令（可选，跨工具兼容）
└── .claude/
    ├── rules/                   # 永久性规则（按语言/领域分层）
    │   ├── common/             # 通用规则
    │   │   ├── coding-style.md
    │   │   ├── git-workflow.md
    │   │   ├── testing.md
    │   │   ├── security.md
    │   │   └── ...
    │   ├── typescript/         # 语言特定规则
    │   ├── python/
    │   └── golang/
    ├── skills/                 # 工作流技能（按场景）
    ├── commands/               # 斜杠命令
    ├── hooks/                  # 触发式钩子
    └── agents/                 # 子代理定义
```

---

## 二、三个仓库规则体系对比

### 2.1 gstack-main

#### 规则架构特点

| 特征 | 实现方式 | 评价 |
|------|----------|------|
| **规则文件** | CLAUDE.md + AGENTS.md 双文件 | ✅ 兼容多种 AI 工具 |
| **规则深度** | 25.99 KB CLAUDE.md，极详细 | ✅ 上下文完整 |
| **SKILL 系统** | SKILL.md.tmpl → SKILL.md 生成流程 | ✅ 模板驱动，保证一致性 |
| **命令规范** | 内置测试命令、构建命令、CI 流程 | ✅ 开发体验好 |
| **特殊机制** | Dev symlink awareness、Slop-scan 集成 | ✅ 针对 AI 生成代码质量检测 |

#### 核心设计亮点

```markdown
## Platform-agnostic design

Skills must NEVER hardcode framework-specific commands, file patterns, or directory
structures. Instead:

1. Read CLAUDE.md for project-specific config
2. If missing, AskUserQuestion
3. Persist the answer to CLAUDE.md so we never have to ask again
```

**设计理念**：平台无关性 + 渐进式上下文获取

#### SKILL 生成流程

```bash
# 1. 编辑模板文件
edit SKILL.md.tmpl

# 2. 运行生成
bun run gen:skill-docs

# 3. 提交两者
git add SKILL.md.tmpl SKILL.md
```

**优势**：解决 merge conflict 问题，模板为唯一真相源

---

### 2.2 everything-claude-code-1.10.0

#### 规则架构特点

| 特征 | 实现方式 | 评价 |
|------|----------|------|
| **规则分层** | common + 语言特定两层结构 | ✅ 可扩展性强 |
| **规则数量** | 10 个 common 规则 + 12 种语言规则 | ✅ 覆盖全面 |
| **多语言支持** | rules/zh/、rules/cpp/ 等 | ✅ 国际化 |
| **文档格式** | 安装脚本 `./install.sh` | ✅ 一键配置 |
| **Rules vs Skills** | 明确区分：Rules=标准，Skills=参考 | ✅ 职责清晰 |

#### 规则文件组织

```
rules/
├── common/          # 通用规则（必须安装）
│   ├── coding-style.md
│   ├── git-workflow.md
│   ├── testing.md
│   ├── performance.md
│   ├── patterns.md
│   ├── hooks.md
│   ├── agents.md
│   └── security.md
├── typescript/
├── python/
├── golang/
└── ...
```

#### 规则优先级机制

```markdown
## Rule Priority

When language-specific rules and common rules conflict, 
**language-specific rules take precedence** (specific overrides general).

- rules/common/ defines universal defaults
- rules/golang/ overrides where Go idioms differ
```

---

### 2.3 BMAD-METHOD-main

#### 规则架构特点

| 特征 | 实现方式 | 评价 |
|------|----------|------|
| **规则文件** | 仅 AGENTS.md（2.72 KB） | ⚠️ 较为简单 |
| **规则内容** | 提交规范 + 质量检查 | ⚠️ 覆盖有限 |
| **Skill 验证** | tools/skill-validator.md | ✅ 专业领域 |
| **多工具支持** | .codex/AGENTS.md | ✅ Codex 兼容 |

#### 核心规则

```markdown
## Rules

- Use Conventional Commits for every commit.
- Before pushing, run `npm ci && npm run quality` on `HEAD`
- Skill validation rules are in `tools/skill-validator.md`
- Deterministic skill checks run via `npm run validate:skills`
```

**设计理念**：最小化规则 + 强制性检查

---

## 三、规则设计技巧汇总

### 3.1 层级设计技巧

| 仓库 | 层级设计 | 实现方式 |
|------|----------|----------|
| gstack | 项目级 + 技能级 | CLAUDE.md（全局）+ SKILL.md.tmpl（模板） |
| ECC | common + 语言特定 | rules/common/ + rules/{lang}/ |
| BMAD | 仅项目级 | AGENTS.md 单一文件 |

### 3.2 规则粒度设计

| 仓库 | 粒度策略 | 文件数量 |
|------|----------|----------|
| gstack | 模板驱动，生成式 | 1 个模板 → N 个 SKILL.md |
| ECC | 按维度拆分 | 10 common + 12 lang = 22+ |
| BMAD | 聚合式 | 1 个 AGENTS.md |

### 3.3 规则内容设计模式

#### 模式 1：渐进式上下文获取（gstack）

```markdown
Skills must NEVER hardcode framework-specific commands.

1. Read CLAUDE.md for project-specific config
2. If missing, AskUserQuestion
3. Persist the answer to CLAUDE.md
```

#### 模式 2：分层继承（ECC）

```markdown
# typescript/coding-style.md
> This file extends ../common/coding-style.md with TypeScript specific content.

<!-- TypeScript 特定规则 -->
```

#### 模式 3：强制验证（BMAD）

```markdown
Before pushing, run `npm ci && npm run quality`
```

### 3.4 规则触发机制

| 触发方式 | 适用场景 | 仓库示例 |
|----------|----------|----------|
| 自动加载 | 通用上下文 | CLAUDE.md、AGENTS.md |
| 斜杠命令 | 工作流触发 | /qa、/ship、/review |
| 钩子机制 | 事件响应 | hooks/*.json |
| 子代理 | 任务委托 | agents/*.md |

---

## 四、规则文档管理与更新策略

### 4.1 规则生命周期

```
创建 → 验证 → 部署 → 监控 → 迭代
  │        │        │        │
  └────────┴────────┴────────┴────→ 持续改进
```

### 4.2 更新策略对比

| 策略 | 描述 | 优势 | 劣势 | 适用仓库 |
|------|------|------|------|----------|
| **模板生成** | SKILL.md.tmpl → SKILL.md | 解决 merge conflict | 需要构建流程 | gstack |
| **分层叠加** | common + lang rules | 可扩展 | 可能冲突 | ECC |
| **最小化** | 仅核心规则 | 简单 | 可能不够用 | BMAD |

### 4.3 团队协作模式

#### 模式 A：集中式管理（推荐）

```
团队负责人
    │
    ├── 维护核心规则（common/）
    │
    └── 审核语言特定规则（{lang}/）

团队成员
    │
    ├── 贡献语言特定规则
    │
    └── 提出规则改进建议
```

#### 模式 B：分布式管理

```
每个语言/模块
    │
    └── 维护自己的 rules/{module}/

定期同步到 common/
```

### 4.4 规则版本管理

```bash
# 分支策略
main (稳定规则)
    │
    ├── feature/new-rules-{topic}
    │
    └── chore/update-rules-{version}

# 提交规范
feat: add {lang}-specific testing rules
chore: update common rules to v2.1.0
fix: resolve conflict between common and {lang} rules
```

### 4.5 规则质量保障

| 检查项 | 实现方式 | 自动化程度 |
|--------|----------|------------|
| 语法正确性 | Markdown lint | ✅ 全自动 |
| 规则冲突检测 | 层级优先级检查 | ⚠️ 手动 |
| 规则有效性验证 | 测试用例覆盖 | ✅ 可自动化 |
| 规则覆盖率 | 规则覆盖的功能点 | ⚠️ 手动 |

---

## 五、关键发现与建议

### 5.1 关键发现

1. **gstack 的模板驱动机制**解决了 SKILL.md 的 merge conflict 问题，是大型项目的最佳实践

2. **ECC 的分层规则结构**提供了可扩展的规则体系，适合多语言项目

3. **BMAD 的强制验证**确保了规则落地，但覆盖面有限

4. **CLAUDE.md 和 AGENTS.md 可以共存**，前者提供项目上下文，后者提供跨工具兼容性

### 5.2 选型建议矩阵

| 项目特征 | 推荐方案 | 理由 |
|----------|----------|------|
| 单语言项目 | CLAUDE.md + rules/common/ | 简单有效 |
| 多语言项目 | CLAUDE.md + rules/common + rules/{lang}/ | 层级清晰 |
| 超大型项目 | CLAUDE.md + AGENTS.md + SKILL 模板 + 分层 rules | 全面覆盖 |
| 工具无关项目 | AGENTS.md（优先）+ CLAUDE.md | 跨工具兼容 |

### 5.3 规则文档最佳实践

1. **必选文件**：CLAUDE.md（项目上下文）
2. **推荐文件**：AGENTS.md（跨工具兼容）
3. **可选文件**：rules/（按需分层）
4. **强制机制**：质量检查（CI 集成）
5. **更新节奏**：每季度评审 + 按需更新

---

## 六、附录

### A. 参考资料

- [AGENTS.md 官方规范](https://agents.md/)
- [CLAUDE.md 官方指南](https://claude.com/blog/using-claude-md-files)
- [Claude Code 最佳实践](https://www.claudedirectory.org/blog/claude-md-guide)

### B. 规则文件清单

| 仓库 | 规则文件 | 大小 | 类型 |
|------|----------|------|------|
| gstack-main | CLAUDE.md | 25.99 KB | 项目上下文 |
| gstack-main | AGENTS.md | 2.55 KB | 跨工具兼容 |
| gstack-main | SKILL.md | 37.59 KB | 技能定义 |
| ECC | CLAUDE.md | 2.72 KB | 项目上下文 |
| ECC | AGENTS.md | 7.89 KB | 代理指令 |
| ECC | rules/ | 10+ 文件 | 分层规则 |
| BMAD | AGENTS.md | 2.72 KB | 核心规则 |

### C. 术语表

| 术语 | 定义 |
|------|------|
| CLAUDE.md | Claude Code 专用配置文件 |
| AGENTS.md | 通用 AI 代理指令格式 |
| SKILL | 工作流技能定义 |
| Hook | 触发式自动化钩子 |
| Sub-agent | 子代理，用于任务委托 |
| Rules | 永久性编码标准 |
