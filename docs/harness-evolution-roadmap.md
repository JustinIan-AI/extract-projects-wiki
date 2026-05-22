# Harness Engineering 演进路线图

> 从最小 Harness 到企业级 AI Agent 运行时体系的完整演进路径

**最后更新**: 2026-05-21

---

## 目录

1. [为什么 5 个文件是最小 Harness](#1-为什么-5-个文件是最小-harness)
2. [从 Prompt 驱动到 State 驱动](#2-从-prompt-驱动到-state-驱动)
3. [扩展五大子系统](#3-扩展五大子系统)
4. [演进为企业级体系](#4-演进为企业级体系)
5. [演进路线图总结](#5-演进路线图总结)

---

## 1. 为什么 5 个文件是最小 Harness

### 5 个文件对应 AI Agent 运行时的 5 个核心维度

| 文件 | 维度 | 解决的问题 |
|------|------|-----------|
| **AGENTS.md** | **Instructions（指令）** | "AI 应该做什么" — 定义行为准则、启动流程、工作规则 |
| **feature_list.json** | **State（状态）** | "当前做到哪了" — 特性追踪、依赖关系、进度透明 |
| **progress.md** | **State（状态）** | "会话之间如何衔接" — 跨会话上下文、日志 |
| **init.sh** | **Verification（验证）** | "如何确认做对了" — 标准化验证命令 |
| **CLAUDE.md** | **Scope（范围）** | "边界在哪" — 权限边界、禁止行为 |

### 最小化原则

- **最少的必要文件**：5 个文件覆盖了 Agent 循环的最小闭环（感知→决策→执行→验证→记忆）
- **人类可读 + AI 可解析**：JSON 和 Markdown 的组合让人类编辑和 AI 解析都很方便
- **零外部依赖**：不需要数据库、API 或服务，纯文件驱动

---

## 2. 从 Prompt 驱动到 State 驱动

### Prompt 驱动的局限

```
Prompt 驱动的问题：
├── 每次会话从零开始
├── 上下文窗口有限
├── AI 依赖"记住"规则
└── 状态变化靠猜测
```

### State 驱动的优势

```
State 驱动的优势：
├── 外部化记忆（文件持久化）
├── 状态转移显式化
├── 验证自动化
└── 会话连续性保证
```

### 演进路径

#### 阶段 1: Prompt 驱动
```
└── 大量 System Prompt 规则
```

#### 阶段 2: 显式状态
```
├── feature_list.json（什么在做）
└── progress.md（做到哪了）
```

#### 阶段 3: 状态转移规则
```
├── State Machine 定义（Todo → In Progress → Done → Verified）
└── Transition conditions（什么触发状态变化）
```

#### 阶段 4: 状态驱动执行
```
├── Agent 读取 State → 决策 → 执行 → 更新 State
└── State 成为唯一事实来源
```

---

## 3. 扩展五大子系统

### 3.1 Skills（技能库）

#### 扩展路径

```
初始：硬编码工具调用
    └── "Use git diff to see changes"

演进：Skill Registry
    ├── skills/
    │   ├── python-testing/
    │   │   ├── SKILL.md
    │   │   ├── prompts/
    │   │   └── patterns/
    │   ├── api-design/
    │   └── security-scan/
    └── Skill 定义：
        ├── 触发条件（什么场景用）
        ├── 输入/输出规范
        └── 验证方法
```

#### 扩展要点

- Skill 是**可插拔的能力单元**
- 每个 Skill 有自己的 `SKILL.md` 定义触发条件
- 支持 Skill 组合和依赖管理

---

### 3.2 Workflow（工作流）

#### 扩展路径

```
初始：单步执行
    └── "Do X"

演进：多步骤流程
    └── Step1 → Step2 → Step3

演进：条件分支
    └── If A → Step1
        Else → Step2

演进：Workflow 引擎
    ├── 状态机驱动
    ├── 可视化流程图
    ├── 异常处理和重试
    └── 并行/串行执行
```

#### 扩展要点

- Workflow = 多个 Feature 的有序组合
- 支持 DAG（非循环有向图）表达依赖
- 每个步骤有明确的输入/输出/验证

---

### 3.3 Memory（记忆系统）

#### 扩展路径

```
初始：无记忆
    └── 每次会话从零开始

演进：文件持久化
    └── progress.md, feature_list.json

演进：分层记忆
    ├── Instruction Memory（AGENTS.md, CLAUDE.md）
    ├── Auto-Memory（自动写入的日志、发现）
    └── Session Extraction（会话结束后后台提取）

演进：结构化记忆库
    ├── .claude/memory/
    │   ├── index.json（总索引，~200 行上限）
    │   ├── user-preferences.md
    │   ├── project-patterns.md
    │   └── session-history/
    └── 检索机制（关键词匹配/语义搜索）
```

#### 关键模式（来自 memory-persistence-pattern.md）

| 模式 | 说明 |
|------|------|
| **两层写入** | 先写 topic 文件 → 再更新 index（防崩溃） |
| **本地优先** | local > project > user > org |
| **边界索引** | index 硬上限 ~25KB，详细内容按需加载 |

#### 两层写入协议

```
Every memory write is a two-step operation:
1. Write the full content to a dedicated topic file
2. Append a one-line pointer to the index

If the process crashes between steps, the worst outcome is an orphaned topic file — the index remains consistent.
```

---

### 3.4 Policy（策略/策略引擎）

#### 扩展路径

```
初始：规则文本
    └── "Use bun, not npm"

演进：显式 Policy 文件
    └── policies/
        ├── security.md
        ├── code-style.md
        └── error-handling.md

演进：Policy 引擎
    ├── Policy = Condition + Action
    ├── 条件：什么情况下触发
    ├── 动作：执行什么操作
    └── 效果：验证是否符合

演进：可审计 Policy
    ├── Policy 版本控制
    ├── Policy 变更日志
    └── Policy 影响分析
```

#### Policy 示例

```yaml
# security-policy.yaml
policies:
  - id: no-eval
    condition: "code contains 'eval('"
    action: "reject"
    message: "eval() is forbidden for security reasons"
    
  - id: require-tests
    condition: "new feature without test"
    action: "warn"
    message: "New features require tests"
```

---

### 3.5 Evaluation（评估系统）

#### 扩展路径

```
初始：手动验证
    └── ./init.sh（人工运行）

演进：自动化测试
    └── pytest, jest, etc.

演进：Harness 基准测试
    ├── 定义代表性任务
    ├── 有/无 Harness 对比
    └── 指标：成功率、时间、Token 消耗

演进：持续评估平台
    ├── 每次 Commit 触发评估
    ├── 指标趋势图
    ├── 回归检测
    └── A/B Testing 不同 Harness
```

#### 评估指标框架

| 维度 | 指标 | 测量方法 |
|------|------|----------|
| **可靠性** | 成功率 | 完成任务数 / 总任务数 |
| **效率** | 时间、Token | 对比基线 |
| **质量** | 返工率 | 提交后被回退的比例 |
| **一致性** | 规则遵守率 | Policy 违规次数 |

---

## 4. 演进为企业级体系

### 4.1 Multi-Agent Runtime（多代理运行时）

#### 架构演进

```
                    ┌─────────────┐
                    │  Coordinator│  ← 编排层
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐       ┌─────▼─────┐      ┌────▼────┐
   │Researcher│       │Implementer│      │ Reviewer│
   └─────────┘       └───────────┘      └─────────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                    ┌──────▼──────┐
                    │ Shared State│  ← 共享状态（任务队列）
                    └─────────────┘
```

#### 关键设计

| 设计 | 说明 |
|------|------|
| **零上下文继承** | Coordinator 不传递上下文，只传递合成后的 Spec |
| **单层 Fork** | 防止递归 Fork 导致上下文爆炸 |
| **异步结果** | Fire-and-forget 注册，立即返回 Task ID |

#### 三种委托模式

| 模式 | 上下文共享 | 适用场景 | 约束 |
|------|-----------|---------|------|
| **Coordinator** | 无 — workers 从头开始 | 复杂多阶段任务（研究→合成→实现→验证） | 最慢但最安全 |
| **Fork** | 完整 — 子进程继承父进程历史 | 快速并行拆分，共享加载的上下文 | **仅单层** — 递归 Fork 会指数级增加上下文成本 |
| **Swarm** | 点对点通过共享任务列表 | 长期独立工作流 | **扁平名单** — 团队成员不能 spawn 其他成员 |

---

### 4.2 Skill Registry（技能注册中心）

```
企业级 Skill Registry：
├── 内部 Skill 市场
│   ├── 官方认证 Skills（安全审查）
│   ├── 团队私有 Skills
│   └── 实验性 Skills
├── Skill 元数据
│   ├── 版本、作者、依赖
│   ├── 安全评级
│   ├── 使用统计
│   └── 效果评分
└── Skill 生命周期
    ├── 开发 → 评审 → 发布
    ├── 版本管理
    └── 废弃/替换
```

---

### 4.3 Sandbox（沙箱隔离）

```
多层安全架构：

┌─────────────────────────────────────┐
│          Enterprise Network         │
│  ┌───────────────────────────────┐  │
│  │       Organization           │  │
│  │  ┌─────────────────────────┐ │  │
│  │  │    Project Sandbox       │ │  │
│  │  │  ├── 隔离的文件系统       │ │  │
│  │  │  ├── 网络限制             │ │  │
│  │  │  ├── 资源配额（CPU/内存） │ │  │
│  │  │  └── 操作审计日志         │ │  │
│  │  └─────────────────────────┘ │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

#### 安全控制

- **最小权限**：Agent 只有完成当前任务所需的权限
- **操作审计**：所有文件修改、网络请求都被记录
- **资源隔离**：防止恶意代码或无限循环影响其他任务

---

### 4.4 Trace / Eval 平台（追踪与评估平台）

#### 评估平台架构

```
         ┌──────────────┐
         │  Commit Hook │
         └──────┬───────┘
                │
    ┌───────────▼───────────┐
    │   Evaluation Runner   │
    │  ┌─────────────────┐  │
    │  │ Task Executor   │  │
    │  │ - Run harness   │  │
    │  │ - Capture trace  │  │
    │  └─────────────────┘  │
    │  ┌─────────────────┐  │
    │  │ Metrics Collector│ │
    │  │ - Success rate   │  │
    │  │ - Token usage    │  │
    │  │ - Time taken     │  │
    │  └─────────────────┘  │
    └───────────┬───────────┘
                │
    ┌───────────▼───────────┐
    │   Analytics Dashboard │
    │  - Trend charts       │
    │  - Regression alerts   │
    │  - A/B test results    │
    └───────────────────────┘
```

#### 核心能力

- **全链路追踪**：每个 Task 的完整执行路径
- **自动化基准**：每次 PR 触发评估
- **回归检测**：指标下降自动告警
- **A/B Testing**：对比不同 Harness 版本

---

### 4.5 企业级治理体系

```
治理层次：

┌─────────────────────────────────────────────────┐
│              Governance Framework                 │
├─────────────────────────────────────────────────┤
│  1. Security & Compliance                        │
│     ├── 权限模型（RBAC）                         │
│     ├── 数据分类（公开/内部/机密）                │
│     └── 合规审计（SOC2, ISO27001）               │
├─────────────────────────────────────────────────┤
│  2. Quality Assurance                           │
│     ├── Code Review Gates                        │
│     ├── Policy Enforcement                        │
│     └── Quality Metrics (coverage, complexity)   │
├─────────────────────────────────────────────────┤
│  3. Cost Management                              │
│     ├── Token 预算控制                            │
│     ├── 模型选择策略                              │
│     └── 成本归因（按项目/团队）                   │
├─────────────────────────────────────────────────┤
│  4. Observability                                │
│     ├── Centralized logging                       │
│     ├── Distributed tracing                       │
│     └── Alerting & on-call                        │
├─────────────────────────────────────────────────┤
│  5. Lifecycle Management                         │
│     ├── Agent 版本管理                            │
│     ├── Rollback procedures                       │
│     └── Change management                          │
└─────────────────────────────────────────────────┘
```

---

## 5. 演进路线图总结

```
┌─────────────────────────────────────────────────────────────────┐
│                        演进路线图                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Phase 1: 最小 Harness（5 文件）                                  │
│     AGENTS.md + feature_list.json + progress.md + init.sh + CLAUDE.md
│                                                                  │
│  Phase 2: State 驱动                                            │
│     └── 状态转移规则 + 验证自动化                                  │
│                                                                  │
│  Phase 3: 扩展子系统                                             │
│     ├── Skills Registry                                         │
│     ├── Workflow Engine                                         │
│     ├── Memory System（分层持久化）                               │
│     ├── Policy Engine                                           │
│     └── Evaluation Framework                                    │
│                                                                  │
│  Phase 4: Multi-Agent Runtime                                   │
│     └── Coordinator / Fork / Swarm 模式                         │
│                                                                  │
│  Phase 5: 企业级平台                                            │
│     ├── Skill Registry Market                                    │
│     ├── Sandbox Isolation                                        │
│     ├── Trace / Eval Platform                                    │
│     └── Governance Framework                                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 核心原则

> **每个阶段都是前一个阶段的增量扩展，而不是重写。** 最小 Harness 是起点，通过**添加子系统和增强机制**逐步演进到企业级体系。

---

## 参考资源

- [memory-persistence-pattern.md](../skills/harness-creator/references/memory-persistence-pattern.md) — 记忆持久化模式
- [context-engineering-pattern.md](../skills/harness-creator/references/context-engineering-pattern.md) — 上下文工程模式
- [tool-registry-pattern.md](../skills/harness-creator/references/tool-registry-pattern.md) — 工具注册与安全模式
- [multi-agent-pattern.md](../skills/harness-creator/references/multi-agent-pattern.md) — 多代理协调模式
- [lifecycle-bootstrap-pattern.md](../skills/harness-creator/references/lifecycle-bootstrap-pattern.md) — 生命周期与引导模式
- [gotchas.md](../skills/harness-creator/references/gotchas.md) — 15 种非明显失败模式及修复

---

## 开发路线图

- [x] 理论框架设计
- [ ] 实现 Phase 2: State 驱动
- [ ] 实现 Phase 3: 扩展子系统
- [ ] 实现 Phase 4: Multi-Agent Runtime
- [ ] 实现 Phase 5: 企业级平台

---

## 相关文档

- [README.md](../README.md) — 项目总览
- [progress.md](../progress.md) — 会话进度日志
- [feature_list.json](../feature_list.json) — 特性状态追踪
