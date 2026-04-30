# AGENTS.md — [项目名称] AI 协作操作手册

> **职责**：定义项目专属的开发规范，是 AI 进入项目后的"入职材料"
> **适用**：所有支持 AGENTS.md 的 AI 编程工具（Claude Code、Cursor、Copilot 等）
> **维护**：版本号 | 最后更新：YYYY-MM-DD | 维护人：[负责人]

---

## 1. 技术栈全景

### 后端
- **语言 runtime**：[如 Node.js 22 / Python 3.12 / Go 1.22]
- **框架**：[如 Express / FastAPI / Gin]
- **ORM/数据访问**：[如 Prisma / SQLAlchemy / GORM]
- **数据库**：[如 PostgreSQL 16 / MySQL 8]
- **缓存**：[如 Redis 7 / Memcached]

### 前端（如有）
- **框架**：[如 React 19 / Vue 3 / Next.js 15]
- **状态管理**：[如 Zustand / Pinia / Redux Toolkit]
- **UI 组件库**：[如 TailwindCSS + shadcn/ui / Element Plus]
- **构建工具**：[如 Vite / Turbopack / Webpack 5]

### 基础设施
- **容器化**：[如 Docker + Kubernetes / Serverless]
- **CI/CD**：[如 GitHub Actions / GitLab CI / Harness]
- **代码仓库结构**：[monorepo / multi-repo]

---

## 2. 常用命令速查

```bash
# ============ 开发环境 ============
[启动命令，如：npm run dev / make run-dev / python manage.py runserver]

# ============ 测试 ============
[测试命令，如：npm run test / pytest / go test ./...]

# ============ 构建 ============
[构建命令，如：npm run build / make build / go build]

# ============ 代码检查 ============
[lint 命令，如：npm run lint / ruff check . / golangci-lint run]

# ============ 代码格式化 ============
[格式化命令，如：npm run format / prettier --write . / gofmt -w]

# ============ 数据库 ============
[迁移命令，如：npm run db:migrate / alembic upgrade head / go run cmd/migrate/main.go]

# ============ 依赖管理 ============
[依赖安装，如：npm install / pip install -r requirements.txt / go mod download]
```

---

## 3. 目录结构与模块边界

```
[项目名]/
├── src/                          # 源代码
│   ├── routes/                   # [路由层：参数校验、路由转发]
│   ├── services/                 # [业务逻辑层：核心业务处理]
│   ├── repositories/             # [数据访问层：数据库操作封装]
│   ├── models/                   # [数据模型：实体定义]
│   ├── middleware/               # [中间件：认证、日志、限流]
│   └── utils/                    # [工具函数]
├── tests/                        # [测试文件，与 src 结构对应]
├── docs/                         # [文档目录]
├── scripts/                      # [运维脚本、数据库迁移等]
├── configs/                      # [配置文件]
└── [其他目录...]
```

### 禁止改动区域
> 以下目录/模块存在历史遗留问题，非必要不修改：
- `[列出禁止改动目录，如：src/legacy/、configs/old-config/]`

---

## 4. 架构约束（CRITICAL）

### 4.1 分层规则（MUST 遵守）

| 层 | 职责 | 禁止行为 |
|----|------|----------|
| Routes/Controller | 参数校验、路由转发 | ❌ 禁止写业务逻辑 |
| Services | 业务逻辑处理 | ❌ 禁止直接操作 DB |
| Repositories | 数据访问封装 | ❌ 禁止包含业务判断 |

### 4.2 技术选型约束

| 场景 | 推荐方案 | 禁止方案 |
|------|----------|----------|
| [如：状态管理] | [Zustand] | [Redux、MobX] |
| [如：HTTP 请求] | [axios] | [原生 fetch] |
| [如：日期处理] | [dayjs] | [moment.js（已废弃）] |
| [如：数据校验] | [zod / joi] | [裸用 JSON] |

---

## 5. 安全红线（CRITICAL）

> 🚨 以下规则必须严格遵守，违反将导致安全风险

### 5.1 数据安全
- [示例：所有数据库查询 MUST 按 tenantId 过滤，防止数据越权]
- [示例：用户敏感字段（密码、token、手机号）MUST 脱敏后返回]

### 5.2 输入校验
- [示例：所有外部输入 MUST 经过 schema 校验（使用 zod / joi）]
- [示例：NEVER 直接拼接用户输入到 SQL/命令中]

### 5.3 密钥管理
- [示例：NEVER 硬编码密钥、密码、Access Token]
- [示例：所有密钥必须从环境变量或配置中心读取]

---

## 6. API 设计规范

### 6.1 响应格式（MUST 统一）

```[语言]
// ✅ 正确格式
res.json({ code: 0, data: result, message: 'success' });

// ❌ 禁止格式
res.json(result);
res.send('ok');
```

### 6.2 路径命名
- [示例：统一使用 `/api/v2/` 前缀，旧版 `/api/v1/` 已废弃]

### 6.3 错误处理
```[语言]
// [定义统一的错误码和错误格式]
// [示例：业务异常使用 BusinessException，抛出标准错误结构]
```

---

## 7. Git 工作流

### 分支命名
```
feature/[JIRA-ID]-brief-description    # 功能分支
bugfix/[JIRA-ID]-brief-description      # Bug 修复
hotfix/[JIRA-ID]-brief-description      # 紧急修复
```

### Commit 格式（遵循 Conventional Commits）
```
feat:     新功能
fix:      Bug 修复
docs:     文档变更
style:    代码格式（不影响功能）
refactor: 重构（非新功能、非修复）
test:     测试相关
chore:    构建/工具变更
```

### PR 要求
- [MUST 包含测试用例]
- [MUST 通过 CI 检查（lint + test + build）]
- [MUST 至少 1 人 Review]
- [NEVER 直接向 main/master 分支推送]

---

## 8. 测试规范

### 测试框架
- [如：Jest / Vitest / pytest / Go testing]

### 覆盖率要求
- [如：核心业务逻辑 80%，工具函数 90%]

### 测试文件位置
- [与源文件同目录，如 `user.service.ts` → `user.service.test.ts`]
- [或统一在 `tests/` 目录]

### 必须覆盖的场景
- ✅ 正常业务流程
- ✅ 边界条件（空值、最大值、特殊字符）
- ✅ 异常场景（网络失败、权限不足、数据不存在）
- ❌ NEVER 在测试中连接真实数据库（使用 mock）

---

## 9. 经验教训（AI 犯过的错误记录）

> 以下是 AI 在本项目中曾经犯过的错误，防止重蹈覆辙

```markdown
## 历史教训
- ❌ [示例：本项目使用 ESM，NEVER 用 `require()`，统一使用 `import`]
- ❌ [示例：数据库迁移文件 NEVER 直接修改，只能新增 migration]
- ❌ [示例：前端路由统一通过 `useNavigate`，NEVER 使用 `window.location`]
- ❌ [示例：环境变量必须通过 `config/index.ts` 导出，NEVER 直接用 `process.env.xxx`]
```

---

## 10. 内部私有依赖

> 以下组件库不在 AI 训练数据中，使用前必须参考源码

```markdown
## 私有依赖
- `@company/ui-kit`：位于 `packages/internal-ui/`
- `@company/request`：位于 `packages/internal-request/`

使用这些组件前，MUST 先阅读对应的 README 和 examples 目录。
```

---

## 11. 参考文档链接

- 架构设计文档：[链接]
- API 接口文档：[链接]
- 数据库 ER 图：[链接]
- 部署流程文档：[链接]

---

## 📌 渐进式披露原则

> 以下是详细规范文档，通过链接引用，避免主文件过于臃肿

- 详细架构规范 → [./docs/architecture.md]
- 详细测试规范 → [./docs/testing-guide.md]
- 安全合规说明 → [./docs/security.md]
- 数据库设计规范 → [./docs/database.md]

---

*AGENTS.md 主文件应控制在 100-150 行以内，详细信息通过链接引用。*
