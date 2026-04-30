# 规则文件编写规范

## 目录

1. [AGENTS.md 编写原则](#agentsmd-编写原则)
2. [CLAUDE.md 编写原则](#claudemd-编写原则)
3. [规则文件结构](#规则文件结构)
4. [输出文件清单](#输出文件清单)

---

## AGENTS.md 编写原则

### 应该写的内容
- 构建、测试、运行命令
- 非默认的技术选型
- 分层架构约束
- 私域组件/内部库的使用方式
- 安全红线
- 代码审查重点

### 不应该写的内容
- 语言本身的通用规范
- Linter/Formatter 已经自动检查的规则
- README 中的人类介绍性文字
- 频繁变动的内容
- 详细的 API 文档（给链接即可）

### 渐进式披露原则
- 主文档控制在 **100-150 行**
- 具体细节推送到独立文档并通过链接引用
- 这可以带来 10-15% 的全方位提升

### 禁令必须搭配替代方案
```markdown
# ❌ 错误
NEVER use raw SQL queries.

# ✅ 正确
NEVER use raw SQL queries. Use the QueryBuilder from `src/db/query-builder.ts` instead.
```

## CLAUDE.md 编写原则

### 五级层次结构
```
~/.claude/CLAUDE.md              # 全局用户配置
项目根目录/
├── CLAUDE.md                    # 项目级配置
├── CLAUDE.local.md              # 个人本地配置
├── src/
│   └── CLAUDE.md                # 子目录配置
└── .claude/
    └── rules/                   # 模块化规则
```

### 优先级（从高到低）
1. CLAUDE.local.md
2. 当前目录的 CLAUDE.md
3. 父目录的 CLAUDE.md
4. ~/.claude/CLAUDE.md

### 独有能力
| 功能 | 说明 |
|------|------|
| 模块化导入 | `@path/to/rules.md` |
| 路径限定规则 | YAML frontmatter 中定义 |
| Hooks 联动 | 自动触发检查命令 |
| 自动记忆 | `/remember` 指令 |

### "是什么 → 为什么 → 怎么做"结构
```markdown
## 技术栈（是什么）
- 后端：Node.js 22 + Express + TypeScript

## 关键架构决策（为什么）
- 使用 Prisma 而非原生 SQL：团队不熟悉 SQL 优化

## 常用命令（怎么做）
npm run dev
npm run test
```

## 规则文件结构
```markdown
# {Project Name} — AI Coding Rules

## Project Overview
## Architecture
## Naming Conventions
## Coding Patterns
## API Design
## Data Access
## Security
## Dependencies
## Known Pitfalls
## Custom Rules          ← 用户维护，不被覆盖
```

## 输出文件清单
| 文件 | 说明 | 必须生成 |
|------|------|---------|
| AGENTS.md | 通用 AI 协作规范 | ✅ |
| CLAUDE.md | Claude Code 主规则 | ✅ |
| .claude/rules/*.md | 模块化规则 | 可选 |
| .cursorrules | Cursor 规则 | 可选 |
| .copilot-instructions.md | Copilot 规则 | 可选 |

## 规则质量要求
- 规则必须可测试（给规则 → 验证 AI 是否遵循）
- 每条规则必须包含真实代码示例
- 禁令必须搭配替代方案
- 未知内容必须标注 `LOW_CONFIDENCE`