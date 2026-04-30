# API 设计规范 — JavaScript/TypeScript

## URL 规范
- RESTful 风格：`/api/v1/{resource}`

## 路由定义
- Express：`router.get('/users/:id', ...)`
- NestJS：`@Get(':id')`

## 响应格式
```json
{
  "code": 0,
  "data": {},
  "message": "success"
}
```

## 示例

```typescript
router.get('/api/v1/users/:id', async (req, res) => {
  const user = await userService.getById(req.params.id);
  res.json({ code: 0, data: user, message: 'success' });
});
```
