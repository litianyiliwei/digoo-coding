# 前端工程规范

- Change ID：N/A（项目级架构基线）
- 状态：FROZEN（用户于 2026-11-17 批准）
- 来源基线：用户确认的流程工具包范围、`docs/product/BASELINE-BRIEF.md`、`AGENTS.md`
- 关联需求/AC：RA-001、FLOW-001、BR-001–007
- 生成日期/版本：2026-11-17 / v0.2.0-draft

## 1. 技术栈与版本

当前工具包没有 Web/H5、移动端或桌面 UI，故框架、运行时渲染库和 UI 组件库均 N/A（用户确认不定义前后端）。若未来 Change 加入产品 UI，须在进入 Figma/UI 阶段前通过基线修订明确 Vue/React 或相应平台技术栈，不允许 Agent 自选。

## 2. 仓库与目录结构

当前仓库只采用 `docs/`、`prompts/`、`.claude/skills/`、`scripts/` 等既有流程目录；无前端源码目录。

## 3. 路由与页面边界

N/A：当前没有页面或客户端路由。

## 4. 组件边界

N/A：没有 UI 组件库。

## 5. 状态管理

无前端状态。全局阶段状态唯一保存在 `workflow-state.json`，由 `workflow.py` 控制。

## 6. API 客户端与类型

N/A：没有前端 API 客户端；CLI/数据结构约定见 `api-conventions.md`。

## 7. 表单与状态展示

N/A：没有产品交互表单。Agent 对用户的澄清和审批在宿主界面进行，不把模型提示词当作应用表单契约。

## 8. 权限与数据范围

无 UI 权限层；用户、构建 Agent、独立验证 Agent、工作流脚本权限见 `docs/product/role-permission-matrix.csv` 和 BR-005/007。

## 9. 视觉与可访问性

当前无 UI 页面、设计 token 或可访问性实现，N/A（流程工具包范围无前端）。未来 UI Change 必须先确定目标框架/组件库，再按 `AGENTS.md` Stage 06 Figma 工作流产出真实设计与审计；文档/脚本工具不创建虚构设计 token。

## 10. 日志、隐私与错误上报

N/A：无客户端遥测/错误上报；CLI 错误以退出码和本地证据日志记录，禁止写入凭据或个人隐私。

## 11. GIS 地图与图层

N/A：当前没有农业业务客户端或地图功能。

## 12. 电商远期页面（DEFERRED）

N/A：当前范围无产品页面、电商或交易能力。

## 13. 测试与质量门禁

无前端单元/视觉回归测试。流程脚本按 `test-strategy.md` 验证；未来 UI Change 在技术栈明确后再定义组件、可访问性和运行时布局检查。
