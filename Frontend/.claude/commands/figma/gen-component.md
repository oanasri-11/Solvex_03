<!-- figma-code-context v1.8.0 -->
---
description: 从 Figma 设计稿生成前端组件
---

# 从 Figma 生成组件

你将根据 Figma 设计稿 URL 生成完整的前端组件代码。

## 核心原则

目标是组件在浏览器中的视觉效果与设计稿一致。Figma 内部结构不需要在代码中复刻。

## 第一步：检测项目技术栈

读取项目配置：

1. `package.json` → 框架、样式方案
2. `tsconfig.json` → 语言、路径别名
3. 扫描已有组件 → 命名规范、导出风格、Props 模式、样式写法

## 第二步：获取 Figma 设计数据

1. 调用 `get_node({ url, depth: 8, precision: "implementation" })` 获取节点视觉结构
2. 如果是 COMPONENT_SET，调用 `get_component_variants({ url })` 获取变体属性和状态 CSS
3. 调用 `get_node_css({ url, recursive: true, mode: "css" })` 获取样式参考；Tailwind 项目可再补充 `mode: "tailwind"`
4. 如有图标/矢量/图片节点且代码需要真实资源，调用 `export_image({ url, format: "auto" })` 或传入明确 `nodeIds`；明确必须 SVG 时调用 `export_svg`
5. 如果 URL 缺少 `node-id`，先调用 `get_file_structure({ url })`，再用 scoped `search_nodes` 定位组件节点

## 第三步：检查已有组件

1. 扫描项目组件目录，查找同名或功能相似的组件
2. 已有 → 告知用户，不重复生成
3. 部分匹配 → 扩展已有组件
4. 不存在 → 新建

## 第四步：确定文件位置

根据项目结构决定组件放在哪里。如果无法确定，询问用户。

## 第五步：生成组件代码

### Props 设计

- 从 Figma 变体属性推断 props 类型
- 从节点内容推断数据 props
- 添加事件 handler props（可选，类型完整但不实现逻辑）
- 数据、状态和事件通过 props 暴露，避免硬编码页面上下文

### 样式生成

- 使用项目已有的样式方案
- 优先使用项目已有的 design token / CSS 变量
- 不引入项目中没有的新依赖

### 代码规范

- 遵循项目已有的代码规范
- 导出方式与项目已有组件一致
- 生成结果必须是可复用组件，不能包含只服务单个页面的路由、全局布局或业务副作用
