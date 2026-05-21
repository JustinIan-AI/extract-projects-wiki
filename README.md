# make-your-harness

> 构建 AI 编程代理的生产级 Harness 工程 —— 五个子系统架构、记忆持久化、会话连续性、验证工作流、范围控制、生命周期管理

**适用场景**：
- 🏗️ 从零开始构建或扩展 AI 编程代理运行时
- 🤖 为项目创建 AGENTS.md/CLAUDE.md 规则文件
- 📊 提升代理跨会话的可靠性和工作质量
- 🔍 分析现有项目，生成结构化的技术文档（作为场景之一）
- 🧪 验证代理工作成果，确保代码质量

---

## ✨ 核心能力

| 能力 | 说明 |
|------|------|
| **五子系统架构** | Instructions、State、Verification、Scope、Lifecycle |
| **记忆持久化** | 让代理在会话之间记住修正和项目规则 |
| **会话连续性** | 支持多会话工作流，保持上下文一致 |
| **验证工作流** | 内置测试、类型检查、质量评估机制 |
| **范围控制** | 单特性开发策略，防止代理越权或范围蔓延 |
| **规则文件生成** | 自动生成 CLAUDE.md、AGENTS.md 等 AI 编程规则 |
| **代码扫描** | 可选的项目分析功能，提取架构和业务知识 |

---

## 🏗️ 五子系统 Harness 框架

每个 Harness 由五个核心子系统组成：

| 子系统 | 作用 | 核心文件 |
|--------|------|----------|
| **Instructions** | 定义代理行为准则和工作流程 | AGENTS.md, CLAUDE.md, docs/ |
| **State** | 跟踪特性状态和会话进度 | feature_list.json, progress.md |
| **Verification** | 确保代码质量和可验证性 | init.sh, 测试套件, 类型检查 |
| **Scope** | 定义任务边界和完成标准 | 单特性策略, 完成定义清单 |
| **Lifecycle** | 管理会话启动、执行和交接 | init.sh, 清理状态清单 |

---

## 🚀 快速开始

### 方式一：构建完整 Harness

```bash
# 创建最小化 Harness 配置
cd skills/harness-creator

# 使用模板生成基础文件
cp templates/agents.md ../..
cp templates/feature-list.json ../..
cp templates/init.sh ../..
cp templates/progress.md ../..
```

### 方式二：扫描项目生成知识（可选场景）

```bash
# 进入技能目录
cd skills/repo-to-wiki

# 扫描本地项目（作为 Harness 的一个场景）
python3 scripts/main.py /path/to/your/project

# 指定输出目录
python3 scripts/main.py /path/to/project --output ./output

# 只生成规则文件
python3 scripts/main.py /path/to/project --rules-only
```

---

## 📁 输出结构

### Harness 核心文件

```
your-project/
├── AGENTS.md              # AI 协作操作手册（入口）
├── CLAUDE.md              # Claude Code 主规则文件
├── feature_list.json      # 特性状态追踪器
├── progress.md            # 会话连续性日志
├── init.sh                # 初始化和验证脚本
├── docs/                  # 详细文档目录
│   ├── ARCHITECTURE.md    # 技术架构文档
│   ├── PRODUCT.md         # 产品说明
│   └── ...
└── .claude/
    └── rules/             # 模块化规则目录
```

### 项目扫描输出（可选）

```
{output_dir}/
├── wiki/
│   ├── human/             # 给人读的文档
│   │   ├── PROJECT_WIKI.md
│   │   ├── BUSINESS_QA.md
│   │   └── ARCHITECTURE.md
│   └── ai/                # 给 AI 读的结构化知识
│       ├── _index.json
│       ├── L0_profile.md
│       ├── L1_architecture.md
│       ├── L2_modules.md
│       └── L3_business.md
└── .cursorrules           # Cursor 规则（可选）
```

---

## 📋 核心文件说明

### 1. AGENTS.md — AI 协作操作手册

**定位**：代理进入项目后的"入职材料"，定义工作规则和流程

**核心内容**：
- ✅ 启动工作流（代理启动时应执行的步骤）
- ✅ 工作规则（单特性开发、验证要求、进度更新）
- ✅ 必需产出物（feature_list.json、progress.md、init.sh）
- ✅ 完成定义（Implementation + Verification + Evidence + Restartable）
- ✅ 会话结束流程

### 2. feature_list.json — 特性状态追踪

**定位**：跟踪项目特性的开发状态和依赖关系

```json
{
  "features": [
    {
      "id": "feat-001",
      "name": "Document Import",
      "description": "Allow users to import PDF and TXT documents",
      "dependencies": [],
      "status": "done",
      "evidence": "tests pass, manual verification on 2024-01-15"
    }
  ]
}
```

### 3. init.sh — 初始化与验证脚本

**定位**：确保项目可启动、可验证、可构建

```bash
#!/bin/bash
set -e
echo "=== Installing dependencies ==="
npm install
echo "=== Running type check ==="
npm run check
echo "=== Running tests ==="
npm test
echo "=== Building application ==="
npm run build
echo "=== Verification complete ==="
```

---

## 🎯 典型使用场景

### 场景一：为新项目构建 Harness

**问题**：团队开始使用 AI 编程代理，需要建立规范的工作流程

**解决方案**：
```bash
# 创建基础 Harness 文件
cp skills/harness-creator/templates/agents.md .
cp skills/harness-creator/templates/feature-list.json .
cp skills/harness-creator/templates/init.sh .

# 编辑 AGENTS.md，添加项目特定规则
# 编辑 init.sh，适配项目技术栈
```

### 场景二：分析现有项目（作为 Harness 的一部分）

**问题**：接手老旧项目，需要快速理解代码结构

**解决方案**：
```bash
# 扫描项目生成 Wiki 和规则
python3 skills/repo-to-wiki/scripts/main.py .

# 输出后，按以下顺序阅读：
# 1. wiki/human/PROJECT_WIKI.md — 了解项目全貌
# 2. wiki/human/BUSINESS_QA.md — 理解核心业务
# 3. wiki/human/ARCHITECTURE.md — 掌握技术架构
```

### 场景三：提升代理可靠性

**问题**：代理经常忘记规则，导致重复犯错

**解决方案**：
```bash
# 评估现有 Harness 的五个子系统
# 找出最弱的子系统并改进

# 创建记忆持久化机制
# 更新 AGENTS.md，添加规则迭代机制
```

---

## 🛠️ 项目结构

```
make-your-harness/
├── skills/
│   ├── harness-creator/          # Harness 构建核心技能
│   │   ├── templates/            # Harness 文件模板
│   │   │   ├── agents.md
│   │   │   ├── feature-list.json
│   │   │   ├── init.sh
│   │   │   └── progress.md
│   │   ├── references/           # 深度模式文档
│   │   │   ├── memory-persistence-pattern.md
│   │   │   ├── context-engineering-pattern.md
│   │   │   ├── tool-registry-pattern.md
│   │   │   ├── multi-agent-pattern.md
│   │   │   ├── lifecycle-bootstrap-pattern.md
│   │   │   └── gotchas.md
│   │   └── evals/                # 评估用例
│   └── repo-to-wiki/            # 项目扫描子技能（可选）
│       ├── scripts/              # Python 脚本
│       │   ├── main.py           # 统一入口
│       │   ├── scan_engine.py    # 项目扫描
│       │   ├── knowledge_extractor.py
│       │   ├── report_generator.py
│       │   └── rule_generator.py
│       ├── assets/               # 模板文件
│       └── skills/               # 子技能
│           ├── nexus-mapper/     # AST 解析与知识库生成
│           └── gitnexus-explorer/
├── docs/                         # 项目文档
├── samples/                      # 输出示例
└── README.md                     # 本文件
```

---

## 📚 参考资源

### Harness 工程模式

| 文档 | 涵盖内容 |
|------|----------|
| [记忆持久化](skills/harness-creator/references/memory-persistence-pattern.md) | 四级指令层级、自动记忆分类、后台提取 |
| [上下文工程](skills/harness-creator/references/context-engineering-pattern.md) | 选择/压缩/隔离/写入操作、预算管理 |
| [工具注册](skills/harness-creator/references/tool-registry-pattern.md) | 故障关闭注册、每调用并发、权限管道 |
| [多代理协调](skills/harness-creator/references/multi-agent-pattern.md) | Coordinator/Fork/Swarm 模式、上下文共享 |
| [生命周期与引导](skills/harness-creator/references/lifecycle-bootstrap-pattern.md) | Hook 系统、后台任务、依赖顺序初始化 |
| [陷阱](skills/harness-creator/references/gotchas.md) | 15 种非明显失败模式及修复方法 |

### 示例文件

查看 [samples/](samples/) 目录获取完整示例：
- [samples/CLAUDE.md](samples/CLAUDE.md) — AI 编程行为准则模板
- [samples/AGENTS.md](samples/AGENTS.md) — AI 协作操作手册模板
- [samples/Karpathy-CLAUDE.md](samples/Karpathy-CLAUDE.md) — Karpathy 风格示例

---

## 📊 Harness 效果评估

### 运行基准测试

1. **定义代表性任务**：选择 2-3 个真实工作任务
2. **运行对比会话**：在有无 Harness 的情况下分别执行
3. **记录指标**：成功率、时间、Token 使用、返工量
4. **聚合结果**：计算改进率和效率变化

---

## ❓ 常见问题

### Q: Harness 和 AI 规则文件有什么区别？

A: Harness 是完整的代理运行时系统，包含五个子系统；AI 规则文件（CLAUDE.md/AGENTS.md）只是其中的 Instructions 子系统。

### Q: 什么时候需要扫描代码？

A: 代码扫描是可选的场景，适用于：
- 接手陌生项目需要快速理解
- 从现有代码提取架构模式和业务规则
- 为老项目生成 AI 友好的规则文件

### Q: 如何验证 Harness 是否有效？

A: 使用真实任务测试：
1. 在无 Harness 情况下运行任务
2. 在有 Harness 情况下运行相同任务
3. 比较成功率、时间、返工量等指标

---

## 📄 License

MIT

---

**最后更新**：2026-05-21