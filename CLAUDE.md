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
自动化入口，`locate()` / `locate_all()` 返回 Element。

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
