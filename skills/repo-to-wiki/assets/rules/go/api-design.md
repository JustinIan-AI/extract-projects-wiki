# API 设计规范 — Go

## URL 规范
- RESTful 风格：`/api/v1/{resource}`

## 路由定义
- Gin：`r.GET("/users/:id", handler)`
- Echo：`e.GET("/users/:id", handler)`

## 响应格式
```json
{
  "code": 0,
  "data": {},
  "message": "success"
}
```

## 示例

```go
r.GET("/api/v1/users/:id", func(c *gin.Context) {
    id := c.Param("id")
    user, err := userService.GetByID(id)
    if err != nil {
        c.JSON(500, gin.H{"code": 1, "message": err.Error()})
        return
    }
    c.JSON(200, gin.H{"code": 0, "data": user, "message": "success"})
})
```
