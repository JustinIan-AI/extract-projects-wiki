# 架构规范 — Java/Spring Boot

## 分层架构

### Controller 层
- 位置：`src/main/java/.../controller/`
- 职责：参数校验、路由转发、返回格式化
- NEVER：禁止在此层编写业务逻辑

### Service 层
- 位置：`src/main/java/.../service/`
- 职责：业务逻辑处理
- NEVER：禁止直接操作数据库

### Mapper/Repository 层
- 位置：`src/main/java/.../mapper/` 或 `src/main/java/.../repository/`
- 职责：数据访问逻辑
- NEVER：禁止包含业务判断

## 依赖方向
```
Controller → Service → Mapper/Repository
```

## 新增代码位置
- 新增 API：在 Controller 层添加
- 新增业务逻辑：在 Service 层添加
- 新增数据访问：在 Mapper/Repository 层添加
