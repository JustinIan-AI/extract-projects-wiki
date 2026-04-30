# 测试规范 — JavaScript/TypeScript

## 测试框架
- 使用 Jest / Vitest
- 测试文件位置：与源文件同目录或 `__tests__/` 目录

## 命名规范
- 测试文件：`[module].test.ts`
- 测试函数：`describe('模块名', () => { it('should xxx', ...) })`

## 编写要求
- MUST 为所有 Service 层公共方法编写测试
- MUST 为所有 API 端点编写集成测试
- NEVER 在测试中连接真实数据库（使用 mock）

## 示例

```typescript
describe('UserService', () => {
  it('should return user by id', async () => {
    const mockRepo = jest.mocked(userRepository);
    mockRepo.findById.mockResolvedValue(mockUser);
    const result = await userService.getById(1);
    expect(result).toEqual(mockUser);
  });
});
```
