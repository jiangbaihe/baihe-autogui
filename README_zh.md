# baihe-autogui

基于 `pyautogui` 的轻量封装，保留 `Auto -> Element -> Target` 这一条清晰调用链，不过度抽象。

## 安装

```bash
uv sync
```

## 快速开始

```python
from baihe_autogui import Auto

auto = Auto()

# 点坐标定位
auto.locate((100, 200)).click()

# 区域定位（点击中心点）
auto.locate((100, 200, 80, 30)).click()

# 图像定位
auto.locate('button.png').click().wait(0.5).write('hello')

# 条件执行
auto.locate('button.png').if_exists().click()
auto.locate('button.png').wait_until_exists(timeout=5).click()
auto.locate('button.png').assert_exists().click()

# 获取所有匹配
for e in auto.locate_all('button.png'):
    e.click()
```

## 核心概念

### Target（目标）

屏幕定位抽象：
- `PointTarget` - 点坐标定位
- `RegionTarget` - 区域定位（返回中心点）
- `ImageTarget` - 图像匹配定位

所有 Target 都支持 `search_region`，并且只有目标完整落在搜索区域内时才算存在。

### Element（元素）

由 `Auto.locate()` 创建的链式动作封装：
- `click()` / `wait()` / `write()` - 链式动作
- `if_exists()` / `wait_until_exists()` / `assert_exists()` - 条件方法

### Auto（入口）

主入口。`locate()` 返回单个 `Element`，`locate_all()` 返回列表；图像未命中时返回空列表。

## API 参考

### locate()

```python
auto.locate(target, *, region=None, confidence=0.8, timeout=0, retry=0)
```

- `target`: 点 `(x, y)`、区域 `(x, y, w, h)` 或图像路径
- `region`: 搜索区域 `(x, y, w, h)`，默认为全屏
- `confidence`: 图像匹配置信度 (0.0-1.0)
- `timeout`: 每次重试间隔时间（秒）
- `retry`: 重试次数（0 = 不重试）
- 点和区域元组必须全部为整数
- 区域宽高必须大于 0

### Element 动作

```python
element.click()           # 在目标位置点击
element.wait(seconds)     # 等待
element.write(text)       # 输入文本
element.if_exists()      # 元素不存在时跳过后续操作
element.wait_until_exists(timeout=10)  # 等待元素出现
element.assert_exists()  # 断言元素必须存在
```

## 架构设计

- `locate()` 按需解析，只有执行动作时才真正取位置
- `locate_all()` 会快照图像匹配结果，并复用缓存点位
- 目标必须完整落在搜索区域内才算存在
