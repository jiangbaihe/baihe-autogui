# CLAUDE.md

本文件用于帮助新的代码助手或新设备上的会话快速接手本仓库，尽量减少上下文缺失。

## 1. 项目定位

`baihe-autogui` 是一个基于 `pyautogui` 的轻量 GUI 自动化库，核心目标是：

- 用尽可能简单的 API 提供常见 GUI 自动化能力
- 保持清晰的 `Auto -> Element -> Target` 调用链
- 避免过度抽象，优先让使用方式直观

这是一个库项目，不是完整应用。重点在 API 设计、定位语义、链式交互体验和发布稳定性。

## 2. 当前状态快照

### 已发布状态

- PyPI 项目：`baihe-autogui`
- 当前已发布版本：`0.1.3`
- 发布方式：GitHub Actions + PyPI Trusted Publishing

### 当前工作区状态

如果当前工作区不是干净的，请优先运行：

```bash
git status --short --branch
```

建议同时核对：

- `pyproject.toml` 中的当前版本号
- `git log --oneline --decorate -5`
- `git tag --list`

最近一个重要功能增量是：

- `locate()` / `locate_all()` 在保留“单个多类型定位器”能力的基础上，新增支持“混合定位器列表”
- 对应的英文 / 中文 README 与测试已经同步覆盖

不要假设当前工作区永远带着这组未提交改动；应以实时 `git status` 为准。

## 3. 技术约束

- Python 版本锁定为 `==3.8.*`
- 构建工具：`uv`
- 构建后端：`uv_build`
- 代码质量工具：`ruff`
- 测试工具：`pytest`

这些约束在 [pyproject.toml](pyproject.toml) 中定义，不要轻易放宽版本范围，除非明确要做兼容性策略调整。

## 4. 常用命令

### 基础开发

```bash
uv sync --dev
uv run pytest -q
uv run ruff check .
uv build
```

### 烟雾测试

```bash
uv run --python 3.8 --no-project --with ./dist/*.whl python scripts/smoke_import.py
```

在 PowerShell 下，`./dist/*.whl` 可能不会自动展开；必要时先解析出具体 wheel 路径再传给 `uv run --with`。

### 其他常用命令

```bash
uv add <package>
uv remove <package>
uv run pytest tests/test_auto.py
uv run pytest tests/test_auto.py::TestAuto::test_locate_point
```

## 5. 仓库重点文件

### 代码

- `src/baihe_autogui/core/auto.py`
  负责 `locate()` / `locate_all()` 的输入解析与目标创建
- `src/baihe_autogui/core/element.py`
  负责链式动作、条件控制、嵌套定位
- `src/baihe_autogui/core/target.py`
  负责点、区域、图像等 Target 的解析语义
- `src/baihe_autogui/core/types.py`
  负责公开输入类型别名

### 测试

- `tests/test_auto.py`
- `tests/test_element.py`
- `tests/test_target.py`
- `tests/test_types.py`

### 文档 / 发布

- `README.md`
- `README_zh.md`
- `CHANGELOG.md`
- `RELEASING.md`
- `.github/workflows/release.yml`

## 6. 核心架构

### Target

Target 描述“如何找到目标”。

当前主要类型：

- `PointTarget`
- `RegionTarget`
- `ImageTarget`
- `MultiTarget`

其中 `MultiTarget` 是“按顺序回退尝试多个定位器”的组合目标，用来支持：

```python
auto.locate(["primary.png", "fallback.png", (100, 200)])
```

### Element

`Element` 是链式动作包装器，用来承接：

- 鼠标动作：`move_to()` / `click()` / `right_click()` / `double_click()`
- 键盘动作：`write()` / `press()` / `hotkey()`
- 条件动作：`if_exists()` / `wait_until_exists()` / `assert_exists()`
- 嵌套定位：`locate()` / `locate_all()`

### Auto

`Auto` 是用户入口。

当前语义：

- `locate(single_locator)`：返回一个 `Element`
- `locate_all(single_locator)`：返回一个 `Element` 列表
- `locate(locator_list)`：按输入顺序尝试多个定位器，返回第一个命中的 `Element`
- `locate_all(locator_list)`：按输入顺序展开每个定位器的结果并合并返回

## 7. 已经拍板的语义

这些属于项目内已经明确的设计决定，后续改动时应默认延续：

### 1. 坐标语义是绝对坐标

- `region=(x, y, w, h)` 只限制搜索区域
- 不会切换到局部坐标系
- 图像匹配结果始终是屏幕绝对坐标
- 鼠标动作也始终使用绝对屏幕坐标

### 2. `locate_all()` 的图像结果会缓存

- 图像匹配结果会快照为缓存点位 / 区域
- 后续 `Element` 动作复用缓存
- 避免重复查找导致行为漂移

### 3. Target 的存在性采用“完整落入搜索区域”语义

- 点必须在区域内
- 区域必须完整落在区域内
- 不是“只要有交集就算存在”

### 4. 发布工作流保持无头

发布工作流不依赖有头桌面环境。

原因：

- 发布链路要尽量简单稳定
- 单元测试应通过 mock 规避真实 GUI 依赖
- 真正的 GUI 集成测试如果以后要做，应该独立成单独 workflow，而不是污染发布流程

### 5. 新增的“定位器列表”能力不替换旧能力

必须保留现有单个定位器输入：

- `(x, y)`
- `(x, y, w, h)`
- `"image.png"` / `Path(...)` / `bytes`

新能力只是额外支持：

```python
[
    (100, 200),
    (100, 200, 300, 400),
    "button.png",
]
```

### 6. 列表语义已经确定

- `locate([...])`：按输入顺序回退尝试
- `locate_all([...])`：按输入顺序展开全部结果
- 空列表不是合法输入，应抛出 `ValidationError`

## 8. 发布与版本管理

### 发布流程

发布依赖 `.github/workflows/release.yml`：

- `push` 以 `v*` 命名的 tag 会触发发布
- `build` job 会执行：
  - `uv sync --locked --dev`
  - `uv run pytest -q`
  - `uv run ruff check .`
  - `uv build`
  - wheel smoke test
- `publish-pypi` job 通过 OIDC Trusted Publishing 发布到 PyPI

### 环境

- GitHub environment：`pypi`
- PyPI 发布方式：Trusted Publishing
- 发布目标：https://pypi.org/project/baihe-autogui/

### 发版前本地建议检查

```bash
uv sync --dev
uv run pytest -q
uv run ruff check .
uv build
```

必要时再跑 wheel smoke test。

## 9. 测试与 CI 注意事项

### 1. Headless CI

CI 在 Ubuntu 无头环境里跑。不要让测试在 import 或运行时偷偷依赖真实桌面环境。

如果测试涉及：

- `pyautogui`
- `screen size`
- 鼠标点击
- 图像查找

优先 mock `gui` 适配层，而不是触发真实 GUI 调用。

### 2. `pyautogui` 导入

项目里已经把 `pyautogui` 改成延迟导入，以避免无头环境 import 直接失败。不要轻易改回模块级硬导入。

### 3. README_zh 编码

`README_zh.md` 实际是 UTF-8 文件，但某些终端或 PowerShell 输出会显示乱码。  
如果需要可靠读取，请显式用：

```powershell
Get-Content -Raw -Encoding utf8 README_zh.md
```

不要因为终端显示乱码就误判文件内容损坏。

## 10. 如果未来继续开发，优先关注什么

### API 层

- 保持输入模型简单直观
- 避免引入不必要的配置对象
- 优先让用户一眼看懂 `locate()` / `locate_all()` 的行为

### 文档层

每次新增 API 语义，至少同步：

- `README.md`
- `README_zh.md`
- `CHANGELOG.md`

### 测试层

新增 API 语义时，至少补这些维度：

- 成功路径
- 回退路径
- 边界输入
- 向后兼容

## 11. 建议新会话的接手顺序

如果是新设备或新会话，请按下面顺序建立上下文：

1. 读本文件 `CLAUDE.md`
2. 看 `git status --short --branch`
3. 看 `README.md`
4. 看 `README_zh.md`
5. 看 `pyproject.toml`
6. 如果涉及发布，再看 `RELEASING.md` 和 `.github/workflows/release.yml`

如果工作区有未提交改动，优先确认这些改动是否就是当前任务的一部分，不要贸然覆盖。
