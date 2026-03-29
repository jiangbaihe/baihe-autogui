# baihe-autogui

基于 `pyautogui` 的轻量 GUI 自动化封装，提供清晰的 `Auto -> Element -> Target` 调用链。

## 安装

```bash
uv add baihe-autogui
```

或

```bash
pip install baihe-autogui
```

如果希望连同 inspect 辅助工具一起安装：

```bash
uv add "baihe-autogui[inspect]"
```

或

```bash
pip install "baihe-autogui[inspect]"
```

`baihe-autogui[extra]` 也会作为同一组扩展依赖的兼容别名保留。

inspect 扩展会在 Python 3.8 上固定使用 `PySide6==6.1.3` 以兼容 Win7，而在 Python 3.9 及以上环境中会自动解析到更新的兼容 `PySide6` 版本。
`inspect` / `extra` 扩展依赖会跟随一个兼容的 inspect 版本线，而不会为了每一个 inspect patch 都重发主包。

`opencv-python` 会作为包依赖一起安装，因此使用 `confidence=...` 的图像匹配不需要再额外手动补装 OpenCV。
仅支持 Windows。
支持 `Python >=3.8`。

## 示例

- [quick_start.py](examples/quick_start.py) 展示常见的鼠标和键盘操作流程。
- [conditional_flow.py](examples/conditional_flow.py) 展示可选动作和异常处理方式。

## 快速开始

```python
from baihe_autogui import Auto

auto = Auto()

# 全局鼠标移动
auto.move_to(100, 200)
auto.move_by(20, -10)

# 点坐标定位
auto.locate((100, 200)).click()

# 区域定位，点击区域中心点
auto.locate((100, 200, 80, 30)).click()
auto.locate((100, 200, 80, 30)).hover(anchor="top_right")
auto.locate((100, 200, 80, 30)).click(anchor="bottom", dy=-2)

# 图像定位
auto.locate("button.png").hover().click().wait(0.5).write("hello")
auto.locate("button.png").right_click()
auto.locate("button.png").double_click().press("enter")
auto.locate("button.png").hotkey("ctrl", "a").write("replacement")
auto.locate("button.png").highlight(timeout=1.5).click()

# 条件执行
auto.locate("button.png").if_exists().click()
auto.locate("button.png").wait_until_exists(timeout=5).click()
auto.locate("button.png").assert_exists().click()
if auto.locate("button.png").exists():
    auto.locate("button.png").click()

# 在外层匹配区域内继续查找
auto.locate("dialog.png").locate("confirm.png").click()

# 按顺序尝试多个定位器
auto.locate([
    "primary_button.png",
    "fallback_button.png",
    (100, 200),
]).click()

# 获取单个定位器的所有匹配
for element in auto.locate_all("button.png"):
    element.click()

# 汇总多个定位器的全部结果
for element in auto.locate_all(["button.png", "secondary_button.png", (100, 200)]):
    element.click()

# 高亮并清理调试边框
submit = auto.locate("submit.png")
submit.highlight(timeout=5)
submit.clear_highlight()
auto.clear_highlights()
```

## 核心概念

### Target

负责描述“如何找到目标”：

- `PointTarget`：点坐标定位
- `RegionTarget`：区域定位，返回区域中心点
- `ImageTarget`：图像匹配定位

所有 `Target` 都支持 `search_region`。只有当目标完整落在该区域内时，才会被视为存在。

### Element

由 `Auto.locate()` 返回的链式动作包装：

- `hover()` / `click()` / `right_click()` / `double_click()`：支持 `anchor`、`dx`、`dy` 的元素鼠标动作
- `wait()` / `write()`：通用动作
- `press()` / `hotkey()`：键盘动作
- `highlight()` / `clear_highlight()`：调试高亮动作
- `locate()` / `locate_all()`：在当前图像或区域范围内继续查找
- `exists()`：布尔存在性检查
- `if_exists()` / `wait_until_exists()` / `assert_exists()`：条件控制

### Auto

主入口。`move_to(x, y)` 用于移动到屏幕绝对坐标，`move_by(dx, dy)` 用于相对当前鼠标位置移动；`locate()` 返回单个 `Element`，`locate_all()` 返回列表，当图像未匹配到时返回 `[]`。`clear_highlights()` 可清除当前所有调试高亮。

## API 说明

### locate()

```python
auto.locate(target, *, region=None, confidence=0.8, timeout=0, retry=0)
```

- `target`：点 `(x, y)`、区域 `(x, y, w, h)`、图像路径，或由这些定位器混合组成的列表
- `region`：搜索区域 `(x, y, w, h)`，默认全屏
- `confidence`：图像匹配置信度，范围 `0.0-1.0`
- `timeout`：每次重试之间的等待秒数
- `retry`：重试次数，`0` 表示不重试
- 点和区域元组必须全部是整数
- 区域宽高必须大于 `0`
- `locate([...])` 会按输入顺序尝试各个定位器，返回第一个命中的结果
- `locate_all([...])` 会按输入顺序展开每个定位器的全部结果
- `locate_all()` 会先对高度重叠的图像匹配结果去重，再返回 `Element` 列表

### Element 动作

```python
auto.move_to(100, 200)       # 移动到屏幕绝对坐标
auto.move_by(20, -10)        # 基于当前鼠标位置相对移动
element.hover(anchor="center", dx=0, dy=0)  # 移动到目标锚点
element.click(anchor="center", dx=0, dy=0)    # 在目标锚点点击
element.right_click(anchor="center", dx=0, dy=0)  # 在目标锚点右键点击
element.double_click(anchor="center", dx=0, dy=0)  # 在目标锚点双击
element.wait(seconds)        # 等待
element.write(text)          # 输入文本
element.press("enter")       # 按下单个按键
element.hotkey("ctrl", "c")  # 按下组合键
element.highlight(timeout=1.5, color="red", thickness=2)  # 绘制临时高亮
element.clear_highlight()    # 清除当前元素的高亮
element.locate("inner.png")  # 在当前图像或区域内继续查找
element.locate_all("item.png")  # 在当前图像或区域内查找全部匹配项
element.exists()             # 返回 True/False，但不改变链式状态
element.if_exists()          # 目标不存在时跳过后续动作
element.wait_until_exists(timeout=10)  # 等待目标出现
element.assert_exists()      # 断言目标必须存在
auto.clear_highlights()      # 清除全部高亮
```

嵌套 `locate()` 会把当前图像匹配框或区域元组作为下一次搜索的 `region=...`。  
点目标本身不定义面积，因此不能作为外层搜索范围。  
`exists()` 只做当前目标是否存在的布尔判断。  
`if_exists()` 一旦发现目标不存在，当前链上后续动作都会被跳过，包括 `wait()`、键盘动作，以及嵌套 `locate()`。在这种跳过状态下，`locate()` 会继续返回同一个已跳过的 `Element`，而 `locate_all()` 会返回 `[]`。  
`anchor` 支持 `top_left`、`top`、`top_right`、`left`、`center`、`right`、`bottom_left`、`bottom`、`bottom_right`。  
`dx` / `dy` 会在锚点解析完成后，再作为屏幕绝对坐标偏移应用。  
点目标只支持 `anchor="center"`，因为单个点天然不存在九宫格区域。  
如果当前 `Element` 已经缓存了点位或区域，`highlight()` 会优先复用缓存，避免高亮位置与后续动作漂移。  
点目标的高亮会绘制成柔和红色十字，区域和图像目标则绘制为柔和红色边框。
像 `red`、`green`、`blue`、`yellow` 这样的命名颜色现在会映射到更柔和的默认色板，而不是纯高饱和原色。
当前 overlay 后端基于 `pywin32` 和原生 Win32 窗口实现。
如果当前环境无法提供 overlay 后端，`highlight()` 会抛出 `OverlayUnavailableError`。

### 坐标语义

- `region=(x, y, w, h)` 只负责限制搜索范围，不会切换到局部坐标系。
- 图像匹配得到的仍然是基于屏幕的绝对坐标。
- 嵌套 `locate()` 只是复用外层的绝对区域继续搜索。
- `auto.move_to()`、`element.hover()`、`click()` 等鼠标动作最终使用的也都是屏幕绝对坐标。

### 异常

- `ValidationError`：输入无效，例如元组格式错误或重试参数不合法
- `ElementNotFoundError`：立即执行动作时，必需元素不存在
- `ElementTimeoutError`：等待必需元素时超时
- `ImageNotFoundError`：图像目标未匹配到
- `OverlayUnavailableError`：当前环境无法创建调试高亮 overlay
- `__version__`：包根导出的已安装版本字符串

## 说明

- `locate()` 是延迟解析的，只有动作真正执行时才取位置。
- `locate_all()` 会快照图像匹配结果，并复用缓存点位。
- 目标必须完整落在搜索区域内，才会被视为存在。

开发与发版流程见 [CONTRIBUTING.md](CONTRIBUTING.md)。
