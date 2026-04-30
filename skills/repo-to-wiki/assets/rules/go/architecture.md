# 架构规范 — Go

## 分层架构

### Handler 层
- 职责：参数校验、路由转发、返回格式化
- NEVER：禁止在此层编写业务逻辑

### Service 层
- 职责：业务逻辑处理
- NEVER：禁止直接操作数据库

### Repository 层
- 职责：数据访问逻辑
- NEVER：禁止包含业务判断

## 依赖方向
```
Handler → Service → Repository
```

## 项目结构
```
cmd/           # 入口
internal/
  handler/     # HTTP handler
  service/     # 业务逻辑
  repository/  # 数据访问
  model/       # 数据模型
pkg/           # 公共库
```
