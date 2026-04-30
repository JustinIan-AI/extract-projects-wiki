# 测试规范 — Java/Spring Boot

## 测试框架
- 使用 JUnit 5 + Mockito
- 测试文件位置：`src/test/java/` 与源文件同包

## 命名规范
- 测试类：`XxxTest.java`
- 测试方法：`should_期望结果_when_条件`

## 编写要求
- MUST 为所有 Service 层公共方法编写测试
- MUST 为所有 API 端点编写集成测试（MockMvc）
- NEVER 在测试中连接真实数据库（使用 @MockBean 或 H2）

## 示例

```java
@ExtendWith(MockitoExtension.class)
class UserServiceTest {
    @Mock
    private UserMapper userMapper;

    @InjectMocks
    private UserServiceImpl userService;

    @Test
    void should_returnUser_when_getById() {
        when(userMapper.selectById(1L)).thenReturn(mockUser);
        User result = userService.getById(1L);
        assertThat(result).isNotNull();
    }
}
```
