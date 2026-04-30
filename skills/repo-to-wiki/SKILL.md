---
name: repo-to-wiki
description: "分析代码仓库或 GitHub 链接，提取系统架构、业务流程、核心类清单，生成双轨知识库（Wiki）和 AI 编程规则文件（CLAUDE.md + AGENTS.md）。使用场景：1) 接手新项目时快速理解代码结构 2) 为项目生成 AI 友好的规则文件 3) 从已有项目抽取可复用的规则规范。触发词：分析仓库、生成wiki、生成规则、项目文档、AI规则文件、知识图谱、架构文档。不适用：代码修改、重构、生成。"
---
# repo-to-wiki — AI 驱动的项目知识抽取与规则生成

> 分析代码仓库或 GitHub 链接，生成双轨知识库（human + ai Wiki）和 AI 编程规则文件（CLAUDE.md + AGENTS.md）。

## Input Types

- **本地路径**：`/path/to/project`
- **GitHub URL**：`https://github.com/username/repo`（支持 tree/branch/path、PR 链接）

## Output Structure

```
{output_dir}/
├── wiki/                        # 双轨知识库
│   ├── human/                   # 给人读的文档
│   │   ├── PROJECT_WIKI.md      # 项目综合手册
│   │   ├── BUSINESS_QA.md       # 业务问卷
│   │   └── ARCHITECTURE.md      # 架构文档
│   └── ai/                      # 给 AI 读的结构化知识
│       ├── _index.json          # AI 路由总控
│       ├── L0_profile.md        # 技术约束
│       ├── L1_architecture.md   # 系统架构
│       ├── L2_modules.md        # 模块分析
│       └── L3_business.md       # 业务逻辑
├── CLAUDE.md                    # Claude Code 主规则
├── AGENTS.md                    # 通用 AI 协作规范
├── CLAUDE.local.md              # 本地配置模板
├── .claude/rules/               # 模块化规则
├── .cursorrules                 # Cursor 规则（可选）
└── .copilot-instructions.md     # Copilot 规则（可选）
```

## Execution Flow

### Phase 0: 输入处理
**输入**：本地路径（`/path/to/project`）或 GitHub URL（`https://github.com/username/repo`）
**输出**：验证后的项目根目录路径、技术栈类型标识
1. 识别输入类型（本地路径 vs GitHub URL）
2. GitHub URL → `scripts/github_fetcher.py` 克隆到临时目录
3. 验证项目存在且可访问
4. 识别技术栈（pom.xml/package.json/pyproject.toml/go.mod 等）
5. 加载对应的语言参考文件

### Phase 1: 项目扫描
**输入**：项目根目录路径、技术栈类型
**输出**：扫描结果（文件统计、模块结构、核心类列表、技术栈详情）
1. 遍历项目文件，统计文件类型和数量
2. 识别模块结构（目录层次）
3. 分析构建配置文件，提取技术栈和依赖
4. 生成 AST 节点数据（使用 nexus-mapper）
5. 识别核心类（Controller/Service/Repository 等）

### Phase 2: 知识提取
**输入**：扫描结果、技术栈类型
**输出**：知识图谱（业务流程、架构模式、安全约束、性能要求）
1. 分析核心模块（hub analysis）
2. 从代码中提取业务逻辑和功能清单
3. 识别业务规则（通过注解、常量、验证逻辑）
4. 从 Controller/Service 方法名推断核心业务流程
5. 识别架构模式（MVC/DDD/分层等）
6. 提取安全约束和性能要求

### Phase 3: Wiki 生成
**输入**：知识图谱、技术栈类型
**输出**：`wiki/human/` 和 `wiki/ai/` 目录下的文档
1. 生成 human/ 文档（PROJECT_WIKI.md、BUSINESS_QA.md、ARCHITECTURE.md）
2. 生成 ai/ 文档（L0-L3 + _index.json）

### Phase 4: 规则文件生成
**输入**：扫描结果、知识图谱、技术栈类型
**输出**：AI 编程规则文件集
1. **[检查点]** 检测输出目录是否存在已有规则文件，展示将覆盖/新增的文件列表，等待用户确认
2. 生成 AGENTS.md（通用规则）
3. 生成 CLAUDE.md（主规则文件，@导入 AGENTS.md）
4. 生成 .claude/rules/*.md（按技术栈选择模板）
5. 生成其他工具规则（.cursorrules、.copilot-instructions.md）

### Phase 5: 交互确认
**输入**：生成的所有文件列表
**输出**：用户确认结果、额外规则收集
1. 展示生成的文件列表和目录结构
2. 询问用户是否需要调整输出内容或格式
3. 收集用户反馈的额外规则或定制需求

## 详细规范

- Wiki 内容规范：详见 [references/wiki-spec.md](references/wiki-spec.md)
- 规则文件编写规范：详见 [references/rules-spec.md](references/rules-spec.md)
- Legacy Rule Miner 方法论：详见 [references/rule-miner-methodology.md](references/rule-miner-methodology.md)

## 核心原则

1. **Copy-Paste First** — 新代码必须模仿最近的同类代码
2. **No Surprise** — 禁止引入项目从未使用过的模式
3. **Version Lock** — 禁止升级依赖版本，除非明确要求
4. **Gradual Improvement Only** — 只能做方法内的安全改进
5. **Pitfall Awareness** — 已知陷阱必须显式标注

## 质量红线

- 禁止编造内容，所有输出必须基于实际代码分析
- 禁止输出空洞模板，未知内容标注 `LOW_CONFIDENCE`
- 技术栈检测必须准确，规则模板必须与技术栈匹配
- 禁令必须搭配替代方案

## 异常与边界条件

| 场景 | 触发条件 | 处理动作 |
|------|----------|----------|
| 项目不存在 | 本地路径无效或 GitHub 克隆失败 | 提示用户检查路径是否正确，退出流程 |
| 技术栈识别失败 | 无构建配置文件（pom.xml/package.json 等） | 标记为未知技术栈，使用通用模板，提示用户手动指定 |
| 输出目录已有文件 | 目标文件已存在 | **[检查点]** 询问用户「覆盖 / 跳过 / 追加」三选一 |
| GitHub 权限不足 | 克隆失败（404/403/认证失败） | 提示用户检查权限，提供本地路径作为替代方案 |
| 空项目 | 目录为空或仅含配置文件 | 提示用户项目内容过少，建议提供完整项目 |
| 超大项目 | 文件数量超过 10000 | 提示用户项目过大，建议缩小范围或增加超时时间 |
| 网络超时 | GitHub 克隆超时 | 重试一次；仍失败则提示用户检查网络或使用本地路径 |
| 循环依赖检测 | 模块间存在循环依赖 | 记录警告信息，继续执行但在输出中标记风险 |

## 命令行接口

```bash
# 扫描本地项目
python3 scripts/main.py /path/to/project

# 扫描 GitHub 仓库
python3 scripts/main.py https://github.com/username/repo

# 指定输出目录
python3 scripts/main.py /path/to/project --output ./output

# 只生成 Wiki
python3 scripts/main.py /path/to/project --wiki-only

# 只生成规则文件
python3 scripts/main.py /path/to/project --rules-only

# 指定工具
python3 scripts/main.py /path/to/project --tools claude,cursor
```

## 脚本文件

| 脚本 | 职责 |
|------|------|
| `scripts/main.py` | 统一入口，编排全流程 |
| `scripts/scan_engine.py` | 项目扫描、技术栈检测、AST 提取 |
| `scripts/knowledge_extractor.py` | 知识提取、业务流程推断 |
| `scripts/report_generator.py` | Wiki 文档生成 |
| `scripts/rule_generator.py` | 规则文件生成（按技术栈选择模板） |
| `scripts/github_fetcher.py` | GitHub 链接处理 |
| `scripts/code_explorer.py` | 多文件/跨目录代码探查 |