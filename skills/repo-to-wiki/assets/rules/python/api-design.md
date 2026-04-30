# API 设计规范 — Python

## URL 规范
- RESTful 风格：`/api/v1/{resource}`

## 视图函数
- 使用 Django REST Framework 的 `@api_view` 或 FastAPI 的路由装饰器

## 响应格式
```json
{
  "code": 0,
  "data": {},
  "message": "success"
}
```

## 示例

```python
@router.get("/api/v1/users/{user_id}")
async def get_user(user_id: int):
    user = await user_service.get_by_id(user_id)
    return {"code": 0, "data": user, "message": "success"}
```
