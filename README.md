# extract-projects-wiki

> 基于 repo-to-wiki 技能，快速扫描本地项目或 GitHub 仓库，生成双轨知识库（Wiki）和 AI 编程规则文件（CLAUDE.md + AGENTS.md）

**适用场景**：
- 📦 接手老旧项目，需要快速理解代码结构和业务逻辑
- 🤖 为项目生成 AI 友好的编程规则文件，提升 AI 编码助手输出质量
- 📚 从已有项目抽取可复用的开发规范、架构模式、业务规则
- 🔍 分析开源项目，生成结构化的技术文档和架构说明

---

## ✨ 核心能力

| 能力 | 说明 |
|------|------|
| **双轨知识库** | 生成 human（给人读）和 ai（给 AI 读）两套 Wiki 文档 |
| **AI 规则文件** | 生成 CLAUDE.md、AGENTS.md、.cursorrules 等 AI 编程规则 |
| **多技术栈支持** | 支持 Java/Spring Boot、Python/Django、Node.js/Express、Go/Gin 等主流框架 |
| **GitHub 集成** | 支持直接扫描 GitHub 仓库（含私有仓库） |
| **渐进式披露** | 主文件精简，详细信息通过链接引用，优化上下文使用 |

---

## 🚀 快速开始

### 方式一：使用 Claude Code（推荐）

1. **安装 repo-to-wiki skill**

```bash
# 在 Claude Code 中安装 skill
claude skill install repo-to-wiki
```

2. **扫描本地项目**

```
分析这个项目 /path/to/your/project，生成 Wiki 和 AI 规则文件
```

3. **扫描 GitHub 仓库**

```
https://github.com/username/repo 帮我生成 AI 编程规则和项目文档
```

### 方式二：直接运行脚本

```bash
# 进入技能目录
cd skills/repo-to-wiki

# 扫描本地项目
python3 scripts/main.py /path/to/your/project

# 扫描 GitHub 仓库
python3 scripts/main.py https://github.com/username/repo

# 指定输出目录
python3 scripts/main.py /path/to/project --output ./output

# 只生成 Wiki 文档
python3 scripts/main.py /path/to/project --wiki-only

# 只生成规则文件
python3 scripts/main.py /path/to/project --rules-only
```

---

## 📁 输出结构

执行完成后，将生成以下文件结构：

```
{output_dir}/
├── wiki/                        # 双轨知识库
│   ├── human/                   # 给人读的文档
│   │   ├── PROJECT_WIKI.md      # 项目综合手册
│   │   ├── BUSINESS_QA.md       # 业务问卷（核心业务流程）
│   │   └── ARCHITECTURE.md      # 技术架构文档
│   └── ai/                      # 给 AI 读的结构化知识
│       ├── _index.json          # AI 路由总控
│       ├── L0_profile.md        # 技术约束（技术栈、框架版本）
│       ├── L1_architecture.md   # 系统架构（模块划分、依赖关系）
│       ├── L2_modules.md        # 模块分析（核心类、职责）
│       └── L3_business.md       # 业务逻辑（业务规则、领域概念）
├── CLAUDE.md                    # Claude Code 主规则文件
├── AGENTS.md                    # 通用 AI 协作规范
├── CLAUDE.local.md              # 本地配置模板（个人偏好）
├── .claude/rules/               # 模块化规则（按技术栈）
├── .cursorrules                 # Cursor 规则（可选）
└── .copilot-instructions.md     # Copilot 规则（可选）
```

---

## 📋 输出物说明

### 1. CLAUDE.md — AI 编程行为准则

**定位**：定义 AI 编程助手的思维模式、编码风格、开发流程

**核心内容**：
- ✅ 核心思维总则（任务分析、最小改动、可读性优先）
- ✅ 编码通用规范（命名、注释、异常处理）
- ✅ 代码修改与重构规则
- ✅ 单元测试与校验规范
- ✅ 问题排查与调试流程
- ✅ 输出格式约束

**示例**：
```markdown
## 一、核心思维总则

### 1.1 任务分析优先
任何任务优先**高层架构分析**，再拆解子步骤：
1. 理解需求和约束边界
2. 分析对现有架构的影响
3. 确定改动范围和风险
4. 拆解实施步骤
5. 逐步执行和验证

> ⚠️ **禁止**：不分析直接写代码
```

### 2. AGENTS.md — AI 协作操作手册

**定位**：项目专属的开发规范，AI 进入项目后的"入职材料"

**核心内容**：
- ✅ 技术栈全景（后端、前端、基础设施）
- ✅ 常用命令速查（开发、测试、构建、部署）
- ✅ 目录结构与模块边界
- ✅ 架构约束（分层规则、技术选型）
- ✅ 安全红线（数据安全、输入校验、密钥管理）
- ✅ API 设计规范
- ✅ Git 工作流
- ✅ 测试规范
- ✅ 经验教训（AI 犯过的错误记录）

**示例**：
```markdown
## 5. 安全红线（CRITICAL）

### 5.1 数据安全
- 所有数据库查询 MUST 按 tenantId 过滤，防止数据越权
- 用户敏感字段（密码、token、手机号）MUST 脱敏后返回

### 5.2 输入校验
- 所有外部输入 MUST 经过 schema 校验（使用 zod / joi）
- NEVER 直接拼接用户输入到 SQL/命令中
```

### 3. Wiki 文档

#### human/PROJECT_WIKI.md
项目综合手册，包含：
- 项目背景与目标
- 核心功能清单
- 快速开始指南
- 技术栈说明
- 部署流程

#### human/BUSINESS_QA.md
业务问卷，从代码中提取的核心业务流程：
- 用户管理流程
- 订单处理流程
- 支付结算流程
- 权限控制逻辑

#### human/ARCHITECTURE.md
技术架构文档：
- 系统架构图
- 模块划分与职责
- 技术选型说明
- 性能与安全考虑

---

## 🎯 典型使用场景

### 场景一：接手老旧项目

**问题**：刚加入团队，需要快速理解一个运行了 3 年的老项目

**解决方案**：
```bash
# 扫描项目
python3 scripts/main.py /path/to/legacy-project

# 输出后，按以下顺序阅读：
# 1. wiki/human/PROJECT_WIKI.md — 了解项目全貌
# 2. wiki/human/BUSINESS_QA.md — 理解核心业务
# 3. wiki/human/ARCHITECTURE.md — 掌握技术架构
# 4. CLAUDE.md + AGENTS.md — 建立 AI 编程规范
```

### 场景二：为项目配置 AI 编程助手

**问题**：团队开始使用 Claude Code/Cursor，希望统一 AI 输出质量

**解决方案**：
```bash
# 生成 AI 规则文件
python3 scripts/main.py /path/to/project --rules-only

# 将生成的文件提交到项目根目录：
# - CLAUDE.md
# - AGENTS.md
# - .claude/rules/
# - .cursorrules（如使用 Cursor）
```

### 场景三：分析开源项目

**问题**：想学习一个优秀的开源项目，但代码量太大无从下手

**解决方案**：
```bash
# 直接扫描 GitHub 仓库
python3 scripts/main.py https://github.com/awesome/project

# 阅读生成的文档：
# - wiki/human/ARCHITECTURE.md — 架构设计思路
# - wiki/ai/L2_modules.md — 核心模块分析
# - wiki/ai/L3_business.md — 业务逻辑提炼
```

---

## 🔧 配置选项

### 命令行参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--output` | 指定输出目录 | `--output ./output` |
| `--wiki-only` | 只生成 Wiki 文档 | `--wiki-only` |
| `--rules-only` | 只生成规则文件 | `--rules-only` |
| `--tools` | 指定生成的规则工具 | `--tools claude,cursor` |
| `--depth` | 分析深度（fast/standard/deep/full） | `--depth standard` |
| `--force` | 强制重新扫描，忽略缓存 | `--force` |

### 支持的技术栈

| 语言 | 框架 | 自动生成规则 |
|------|------|-------------|
| Java | Spring Boot, MyBatis, JPA | ✅ |
| Python | Django, Flask, FastAPI | ✅ |
| JavaScript/TypeScript | Express, NestJS, Next.js, Vue | ✅ |
| Go | Gin, Echo, Fiber | ✅ |
| Rust | Actix, Axum, Rocket | ✅ |
| Node.js | Koa, Fastify | ✅ |

---

## 📊 输出物质量保障

### 1. 双轨知识库设计

**human/ 目录**（给人读）：
- 叙事性文档，适合快速浏览
- 包含业务背景、架构决策、使用指南
- 渐进式披露，主文件 < 150 行

**ai/ 目录**（给 AI 读）：
- 结构化数据，便于 AI 精确检索
- L0-L3 分层，按需加载
- 包含技术约束、模块边界、业务规则

### 2. 渐进式披露原则

主文件（CLAUDE.md、AGENTS.md）控制在 100-150 行，详细信息通过链接引用：

```markdown
## 七、指令预算约束

> ⚠️ 本文件核心规则控制在 **150 行以内**

### 渐进式披露
- 项目技术细节 → 参考 `AGENTS.md`
- 详细架构规范 → [./docs/architecture.md]
- 详细测试规范 → [./docs/testing-guide.md]
- 安全合规说明 → [./docs/security.md]
```

### 3. 规则迭代机制

生成的规则文件包含迭代机制说明：

```markdown
## 九、规则迭代机制

### 触发添加规则
- AI 重复犯同一个错误 2 次以上
- Code Review 中经常出现同类反馈

### 触发删除规则
- 该规则对应的技术已不再使用
- 规则从未被触发（说明可能是冗余的）
```

---

## 📚 示例输出

查看 [samples/](samples/) 目录获取完整示例：

- [samples/CLAUDE.md](samples/CLAUDE.md) — AI 编程行为准则模板
- [samples/AGENTS.md](samples/AGENTS.md) — AI 协作操作手册模板
- [samples/Karpathy-CLAUDE.md](samples/Karpathy-CLAUDE.md) — Karpathy 风格示例

---

## 🤝 与 nexus-mapper 的关系

本项目内置了 [nexus-mapper](skills/nexus-mapper/) 子技能，用于：

1. **AST 解析**：使用 Tree-sitter 解析代码，提取类、方法、依赖关系
2. **文件树生成**：生成过滤后的项目文件树
3. **Git 历史分析**：提取代码变更热点、耦合关系

**产出物流向**：
```
nexus-mapper 产出 → scan_engine 处理 → knowledge_extractor 分析 → report_generator 生成
    ↓                    ↓                    ↓                    ↓
ast_nodes.json    →  技术栈识别      →  业务流程推断    →  Wiki 文档
file_tree.txt     →  模块划分        →  架构模式识别    →  规则文件
```

---

## 🛠️ 开发指南

### 项目结构

```
extract-projects-wiki/
├── skills/repo-to-wiki/       # 核心技能
│   ├── scripts/               # Python 脚本
│   │   ├── main.py            # 统一入口
│   │   ├── scan_engine.py     # 项目扫描
│   │   ├── knowledge_extractor.py  # 知识提取
│   │   ├── report_generator.py     # Wiki 生成
│   │   └── rule_generator.py       # 规则生成
│   ├── assets/                # 模板文件
│   │   ├── rules/             # 按技术栈分类的规则模板
│   │   └── wiki/              # Wiki 文档模板
│   ├── references/            # 参考文档
│   └── tests/                 # 测试用例
├── docs/                      # 项目文档
├── samples/                   # 输出示例
└── README.md                  # 本文件
```

### 添加新技术栈支持

1. 在 `assets/rules/` 下创建新语言目录
2. 编写 api-design.md、architecture.md、testing.md
3. 在 `scan_engine.py` 的 `_detect_tech_stack()` 中添加检测逻辑

---

## 📝 最佳实践

### 1. 规则文件放置位置

```
your-project/
├── CLAUDE.md              # 放在项目根目录，Claude Code 自动加载
├── AGENTS.md              # 放在项目根目录，通用 AI 工具加载
├── .claude/
│   └── rules/             # 模块化规则目录
└── .cursorrules           # Cursor 专属规则
```

### 2. 本地配置隔离

个人临时偏好放在 `CLAUDE.local.md`（已加入 .gitignore）：

```markdown
# CLAUDE.local.md
## 个人偏好
- 优先使用函数式编程风格
- 注释使用中文
```

### 3. 持续迭代规则

定期回顾规则文件，基于实际使用反馈进行优化：

```bash
# 查看规则文件使用情况
git log --oneline CLAUDE.md AGENTS.md

# 收集团队反馈，更新规则
# 触发条件：AI 重复犯错、Code Review 高频问题
```

---

## ❓ 常见问题

### Q: 生成的规则文件太长了怎么办？

A: 遵循渐进式披露原则，将详细信息移到子文档：
- 主文件（CLAUDE.md/AGENTS.md）控制在 100-150 行
- 详细规范放在 `docs/` 目录，通过链接引用

### Q: 如何验证生成的规则是否有效？

A: 使用实际任务测试：
1. 让 AI 基于规则执行典型任务
2. 检查输出是否符合预期
3. 记录 Bad Case，针对性优化规则

### Q: 老旧项目没有 Git 历史怎么办？

A: 降级为文件树分析：
- 跳过 Git 热点分析
- 基于目录结构和文件命名推断模块
- 在输出中标注 `evidence gap`

### Q: 支持私有 GitHub 仓库吗？

A: 支持，需要提供访问令牌：
```bash
# 设置环境变量
export GITHUB_TOKEN=your_token

# 扫描私有仓库
python3 scripts/main.py https://github.com/private/repo
```

---

## 📄 License

MIT

---

## 🙏 致谢

- [repo-to-wiki](../repo-to-wiki/) — 核心技能
- [nexus-mapper](../repo-to-wiki/skills/nexus-mapper/) — AST 解析与知识库生成
- [darwin-skill](../darwin-skill-master/) — Skill 质量评估框架
- [skill-creator](../.trae/skills/skill-creator/) — Skill 开发指南

---

**最后更新**：2026-04-30
