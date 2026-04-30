# 测试规范 — Python

## 测试框架
- 使用 pytest + pytest-mock
- 测试文件位置：`tests/` 目录

## 命名规范
- 测试文件：`test_xxx.py`
- 测试函数：`test_期望结果_条件`

## 编写要求
- MUST 为所有 Service 层公共方法编写测试
- MUST 使用 fixture 管理测试数据
- NEVER 在测试中连接真实数据库（使用 mock）

## 示例

```python
def test_get_user_by_id(user_service, mock_repo):
    mock_repo.get_by_id.return_value = mock_user
    result = user_service.get_by_id(1)
    assert result is not None
```
