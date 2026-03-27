# baihe-autogui

基于 `pyautogui` 的轻量 GUI 自动化封装，保留 `Auto -> Element -> Target` 这条清晰调用链，不过度抽象。

## 安装

```bash
uv sync
```

## 示例

- [quick_start.py](examples/quick_start.py) 展示常见的鼠标和键盘操作流程。
- [conditional_flow.py](examples/conditional_flow.py) 展示可选动作和异常处理方式。

## 快速开始

```python
from baihe_autogui import Auto

auto = Auto()

# 点坐标定位
auto.locate((100, 200)).click()

# 区域定位，点击区域中心点
auto.locate((100, 200, 80, 30)).click()

# 图像定位
auto.locate("button.png").move_to().click().wait(0.5).write("hello")
auto.locate("button.png").right_click()
auto.locate("button.png").double_click().press("enter")
auto.locate("button.png").hotkey("ctrl", "a").write("replacement")

# 条件执行
auto.locate("button.png").if_exists().click()
auto.locate("button.png").wait_until_exists(timeout=5).click()
auto.locate("button.png").assert_exists().click()

# 获取所有匹配项
for element in auto.locate_all("button.png"):
    element.click()
```

## 核心概念

### Target

负责描述“如何找到目标”：

- `PointTarget`：点坐标定位
- `RegionTarget`：区域定位，返回区域中心点
- `ImageTarget`：图像匹配定位

所有 Target 都支持 `search_region`，并且只有当目标完整落在该区域内时，才会被视为存在。

### Element

由 `Auto.locate()` 返回的链式动作包装：

- `move_to()` / `click()` / `right_click()` / `double_click()`：鼠标动作
- `wait()` / `write()`：通用动作
- `press()` / `hotkey()`：键盘动作
- `if_exists()` / `wait_until_exists()` / `assert_exists()`：条件控制

### Auto

主入口。`locate()` 返回单个 `Element`；`locate_all()` 返回列表，当图像未匹配到时返回 `[]`。

## API 说明

### locate()

```python
auto.locate(target, *, region=None, confidence=0.8, timeout=0, retry=0)
```

- `target`：点 `(x, y)`、区域 `(x, y, w, h)` 或图像路径
- `region`：搜索区域 `(x, y, w, h)`，默认全屏
- `confidence`：图像匹配置信度，范围 `0.0-1.0`
- `timeout`：每次重试之间的等待秒数
- `retry`：重试次数，`0` 表示不重试
- 点和区域元组必须全部是整数
- 区域宽高必须大于 `0`

### Element 动作

```python
element.move_to()            # 将鼠标移动到目标位置
element.click()              # 在目标位置点击
element.right_click()        # 在目标位置右键点击
element.double_click()       # 在目标位置双击
element.wait(seconds)        # 等待
element.write(text)          # 输入文本
element.press("enter")       # 按下单个按键
element.hotkey("ctrl", "c")  # 按下组合键
element.if_exists()          # 目标不存在时跳过后续动作
element.wait_until_exists(timeout=10)  # 等待目标出现
element.assert_exists()      # 断言目标必须存在
```

### 异常

- `ValidationError`：输入无效，例如元组格式错误或重试参数不合法
- `ElementNotFoundError`：立即执行动作时，必需元素不存在
- `ElementTimeoutError`：等待必需元素时超时
- `ImageNotFoundError`：图像目标未匹配到

## 开发

```bash
uv sync --dev
uv run pytest -q
uv run ruff check .
uv build
```

GitHub Actions 会在 `push` 和 `pull_request` 时使用 Python 3.8 运行同样的检查。协作说明见 [CONTRIBUTING.md](CONTRIBUTING.md)。
发布说明见 [RELEASING.md](RELEASING.md)。

## 设计原则

- `locate()` 延迟解析，只有动作真正执行时才取位置
- `locate_all()` 会快照图像匹配结果，并复用缓存点位
- 目标必须完整落在搜索区域内，才会被视为存在
