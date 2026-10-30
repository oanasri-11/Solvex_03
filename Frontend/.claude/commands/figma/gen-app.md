<!-- figma-code-context v1.8.0 -->
---
description: 从 Figma 文件生成完整应用
---

# 从 Figma 生成完整应用

你将根据 Figma 文件 URL，生成包含所有页面和组件的完整前端应用。

## 核心原则

- 目标是每个页面的**视觉效果**与设计稿一致
- Figma 内部结构不需要在代码中复刻
- 全程自主决策，不中断用户（除非遇到无法推断的关键选择）
- 严格依赖顺序：共享组件 → 页面
- 先框架后细节：骨架 → 结构 → 样式 → 精修
- 应用生成必须默认组件化：共享组件和页面区块先实现，页面只负责组合和数据传入

## 阶段 1：分析与规划

1. **检测技术栈**：读取 package.json、tsconfig.json、项目结构
2. **获取文件结构**：调用 `get_file_structure({ url })` 获取所有页面和顶层 Frame
3. **盘点已有组件**：扫描组件目录，识别可直接复用、可扩展和必须新建的组件
4. **识别共享组件**：调用 `search_nodes({ url, type: "COMPONENT_SET", depth: 4, maxResults: 50 })`；如结果不足，再对具体页面传 `parentId/pageId` 缩小范围
5. **输出执行计划**：页面清单、组件依赖、路由结构、组件拆分图、生成顺序

## 阶段 2：基础设施

1. 项目脚手架（如需要）
2. 创建所有页面空壳（正确路由位置 + 布局容器）
3. 创建共享组件占位（Props 接口 + 最小实现）
4. 质量关卡：构建通过

## 阶段 3：结构填充

对每个组件和页面：

1. 调用 `get_node({ url 或 fileKey/nodeId, depth: 8, precision: "implementation" })` 获取视觉结构
2. 先实现共享组件和页面区块组件，再在页面中引用已有/新建组件
3. 如有图标/矢量/图片且代码需要真实资源 → `export_image({ url 或 fileKey/nodeIds, format: "auto" })`；明确必须 SVG 时调用 `export_svg`
4. 质量关卡：构建通过

## 阶段 4：样式填充

对每个组件/页面：

1. 调用 `get_node_css({ url 或 fileKey/nodeId, recursive: true, mode: "css" })` 获取样式参考
2. 应用精确样式值
3. 质量关卡：构建通过

## 阶段 5：精修

1. 对每个页面/组件调用 `get_node_css`，对比视觉效果，修正差异（最多 3 轮）
2. 执行组件化自检：确认重复 UI、独立交互区块、独立数据区块已提取或复用组件
3. 确认页面文件主要负责路由、布局编排和数据传入，不承载大量重复 DOM
4. 确认所有资源已正确引用
5. 最终全量验证：构建通过 + 类型检查 + lint

## 组件化工程规范

- 优先复用项目已有组件、design token、样式工具和图标体系；只有不存在合适抽象时才新建
- Figma 中的 COMPONENT / COMPONENT_SET、明显复用单元、重复 2 次以上的卡片/列表项/按钮组/导航项/表单项必须提取或复用组件
- 有独立交互、局部状态或事件接口的区域必须提取组件，例如 tab、dropdown、modal、form、carousel
- 有独立数据输入边界的区块必须提取组件，例如 user card、product card、sidebar item、metric tile
- 页面文件应主要负责路由、布局编排和数据传入；组件文件负责自身结构、Props、样式和局部状态接口
- 可以内联一次性、无交互、无复用价值的纯布局 wrapper 或细小装饰元素
- 不要为了组件化复刻 Figma 的无意义嵌套 frame；按工程语义拆分

## 错误处理

- API 429 → 等待 30s 重试（最多 3 次）
- 构建失败 → 分析错误 → 修复 → 重试（最多 3 次）
- 3 次仍失败 → 记录，继续下一个
- 不要默认全文件深搜；先 `get_file_structure`，再 scoped `search_nodes`
