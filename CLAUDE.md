# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在本仓库中工作时提供指导。

## 项目概述

`baihe-autogui` 是一个基于 `pyautogui` 的 Python GUI 自动化框架，采用 **Target + Element + Auto** 的多态链式架构。

## 常用命令

```bash
# 安装依赖
uv sync

# 运行包
uv run baihe-autogui

# 添加依赖
uv add <package>

# 移除依赖
uv remove <package>

# 构建可分发包
uv build

# 代码质量检查
ruff check src/

# 自动修复
ruff check --fix src/

# 运行测试
pytest tests/

# 运行单个测试文件
pytest tests/test_auto.py

# 运行单个测试函数
pytest tests/test_auto.py::TestAuto::test_locate_point
```

## 技术要求

- **Python 版本**：`==3.8.*`（锁定版本，兼容 Windows 7）
- **代码质量工具**：ruff（配置在 `pyproject.toml`）

## 核心架构

### Target（目标）
定位抽象基类，子类实现：
- `PointTarget` - 点坐标定位
- `RegionTarget` - 区域定位（返回中心点）
- `ImageTarget` - 图像匹配定位

所有 Target 支持 `search_region` 参数，子集语义判断存在性。

### Element（元素）
Target + Action 的链式封装。`Element` 由 `Auto.locate()` 创建，支持：
- `click()` / `wait()` / `write()` - 链式操作
- `if_exists()` / `wait_until_exists()` / `assert_exists()` - 条件方法

### Auto（入口）
自动化入口，`locate()` 返回一个 Element；`locate_all()` 返回 Element 列表，图像未找到时返回空列表 `[]`。`locate_all()` 的图像匹配结果会被快照缓存，后续复用该缓存坐标。

`Auto` 默认配置：
- `_pause = 0.1` - pyautogui 操作间隔
- `_failsafe = True` - 启用故障安全（鼠标移到角落终止）

### API 示例
```python
from baihe_autogui import Auto

auto = Auto()

# 定位方式
auto.locate((100, 200))              # 点坐标
auto.locate((100, 200, 80, 30))      # 区域
auto.locate('btn.png')                # 图像
auto.locate('btn.png', region=(0,0,800,600))  # 指定搜索区域
auto.locate('btn.png', confidence=0.9, retry=3, timeout=0.5)  # 图像参数

# 链式操作
auto.locate('btn.png').click().wait(0.5).write('hello')

# 条件执行
auto.locate('btn.png').if_exists().click()
auto.locate('btn.png').wait_until_exists(timeout=5).click()
auto.locate('btn.png').assert_exists().click()

# 获取所有匹配
for e in auto.locate_all('btn.png'):
    e.click()
```

### 坐标语义
`region=` 参数限制搜索区域，但**不切换为局部坐标系**。图像匹配结果始终是屏幕绝对坐标，嵌套 `locate()` 复用外层绝对区域。所有鼠标操作（`click()`、`move_to()` 等）均使用绝对屏幕坐标。

## 项目结构

```
src/baihe_autogui/
├── __init__.py           # 主包导出
└── core/
    ├── auto.py           # Auto 入口
    ├── element.py        # Element 类
    ├── target.py         # Target 基类与实现
    └── types.py          # 类型别名
tests/
    ├── test_auto.py      # Auto 测试
    ├── test_element.py   # Element 测试
    ├── test_target.py    # Target 测试
    └── test_types.py     # 类型测试
```

## 设计决策

- **即时查找**：`locate()` 时立即查找并缓存位置
- **子集语义**：Target 必须完全在搜索区域内才算存在
- **无状态 Element**：每次操作复用缓存位置，不自动重新查找
- **绝对坐标**：`region=` 仅限制搜索区域，匹配结果始终是屏幕绝对坐标，不切换局部坐标系

## 异常类型

| 异常 | 触发场景 |
|------|---------|
| `ValidationError` | 输入验证失败（如格式错误的元组、无效的 confidence） |
| `ElementNotFoundError` | 必需元素不存在（立即操作时） |
| `ElementTimeoutError` | 等待元素超时（`wait_until_exists`） |
| `ImageNotFoundError` | 图像匹配失败（`ImageTarget` 查找失败） |
