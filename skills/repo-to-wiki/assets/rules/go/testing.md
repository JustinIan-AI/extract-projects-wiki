# 测试规范 — Go

## 测试框架
- 使用 Go 标准 testing 包 + testify
- 测试文件位置：与源文件同目录

## 命名规范
- 测试文件：`xxx_test.go`
- 测试函数：`TestXxx(t *testing.T)`

## 编写要求
- MUST 为所有导出函数编写测试
- MUST 使用 table-driven tests
- NEVER 在测试中连接真实数据库

## 示例

```go
func TestGetUserByID(t *testing.T) {
    tests := []struct {
        name    string
        id      int64
        want    *User
        wantErr bool
    }{
        {"valid id", 1, &User{ID: 1}, false},
        {"invalid id", -1, nil, true},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got, err := service.GetByID(tt.id)
            if (err != nil) != tt.wantErr {
                t.Errorf("GetByID() error = %v, wantErr %v", err, tt.wantErr)
            }
        })
    }
}
```
