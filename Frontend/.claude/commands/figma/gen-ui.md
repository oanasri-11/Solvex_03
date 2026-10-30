<!-- figma-code-context v1.8.0 -->
---
description: 从 Figma 设计稿还原 UI，通用入口
---

# 从 Figma 还原 UI

你将根据 Figma 设计稿 URL 生成视觉效果一致的前端代码。

## 核心原则

目标是浏览器中的**视觉效果**与设计稿一致，而不是每个 Figma 节点属性都一一对应到代码。

- Figma 的内部结构（嵌套 frame、auto-layout、constraints）是设计工具的实现方式，不需要在代码中复刻
- 用最简洁的 HTML/CSS 实现相同的视觉效果
- 关键是最终渲染结果看起来一样：颜色、尺寸、间距、字体、圆角、阴影、层叠关系
- 默认采用工程化组件结构：页面/应用文件负责编排，组件文件负责稳定 UI 单元、Props、样式和局部交互接口
- 组件化是完成标准的一部分，不能把完整页面或重复 UI 堆在单个文件中

## 工作流程

### MCP 使用约定

- 优先把 Figma URL 直接传给 MCP 工具，不要为 Claude Code 和 Codex 维护两套解析流程
- `get_node` 默认是轻量读取；只有需要变量或 SVG 绑定时才显式传 `includeVariables` / `includeSvg`
- `get_node_css` 的 Tailwind 输出只作为参考；复杂渐变、阴影、字体以 CSS 输出为准
- 如果 URL 缺少 `node-id`，先调用 `get_file_structure({ url })`，再用 scoped `search_nodes` 定位目标 frame

### 第一步：检测项目技术栈

读取项目配置，确定框架和样式方案：

1. `package.json` → 框架、样式库
2. `tsconfig.json` → 语言、路径别名
3. 扫描已有组件 → 命名规范、导出方式、Props 模式、样式写法、文件组织

### 第二步：理解设计结构

调用 `get_node({ url, depth: 8, precision: "explore" })` 获取视觉层级，理解组件的视觉组成：

- 整体布局方向和对齐
- 主要区块划分
- 文本内容和层级
- 颜色和间距模式

### 第三步：制定组件拆分计划

先判断目标是组件、页面还是应用，再列出：

- 可直接复用的已有组件
- 需要扩展复用的已有组件
- 必须新建的共享组件、页面区块组件和复用 UI 单元
- 页面壳与组件之间的 Props 和事件边界

### 第四步：获取实现样式

调用 `get_node_css({ url, recursive: true, mode: "css" })` 获取样式参考。仅当项目明确使用 Tailwind 时，再补充 `mode: "tailwind"`。

### 第五步：导出资源

- 如有图标/矢量/图片且代码实现需要真实资源 → 调用 `export_image({ url, format: "auto" })` 或传入明确 `nodeIds`；明确必须 SVG 时调用 `export_svg`
- 如有 COMPONENT_SET → 调用 `get_component_variants({ url })` 获取变体和状态 CSS

### 第六步：生成代码

- 使用项目技术栈实现
- 优先复用项目已有组件和 design token
- 不引入项目中没有的新依赖
- 事件接口预留但不实现逻辑
- 先实现或复用组件，再用页面或应用入口编排这些组件

### 第七步：组件化自检

完成前检查拆分是否符合下方工程规范；若页面文件仍包含大量重复 DOM 或可提取交互区块，先重构再结束。

### 第八步：验证

启动 dev server，确认视觉效果与设计稿一致。

## 组件化工程规范

- 优先复用项目已有组件、design token、样式工具和图标体系；只有不存在合适抽象时才新建
- Figma 中的 COMPONENT / COMPONENT_SET、明显复用单元、重复 2 次以上的卡片/列表项/按钮组/导航项/表单项必须提取或复用组件
- 有独立交互、局部状态或事件接口的区域必须提取组件，例如 tab、dropdown、modal、form、carousel
- 有独立数据输入边界的区块必须提取组件，例如 user card、product card、sidebar item、metric tile
- 页面文件应主要负责路由、布局编排和数据传入；组件文件负责自身结构、Props、样式和局部状态接口
- 可以内联一次性、无交互、无复用价值的纯布局 wrapper 或细小装饰元素
- 不要为了组件化复刻 Figma 的无意义嵌套 frame；按工程语义拆分
