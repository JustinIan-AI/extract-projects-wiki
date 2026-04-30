# API 设计规范 — Java/Spring Boot

## URL 规范
- RESTful 风格：`/api/v1/{resource}`
- 使用名词而非动词：`/users` 而非 `/getUsers`

## Spring Boot 注解
- GET：`@GetMapping`
- POST：`@PostMapping`
- PUT：`@PutMapping`
- DELETE：`@DeleteMapping`

## 响应格式
```json
{
  "code": 200,
  "msg": "success",
  "data": {}
}
```

## 示例

```java
@RestController
@RequestMapping("/api/v1/users")
public class UserController {
    @GetMapping("/{id}")
    public AjaxResult getById(@PathVariable Long id) {
        return AjaxResult.success(userService.getById(id));
    }
}
```
