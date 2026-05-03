---
alwaysApply: true
---
# 智能数据分析系统 - 开发流程管理规则

## ⚙️ 项目配置

project:
  name: "智能数据分析系统"
  team: "ROC"
  repo: "https://github.com/RockNinjaCoder/-.git"
  linear_project_id: "ff4a08ba-8c10-4c5e-a10c-719c8125f691"

linear_issues:
  phase1: "ROC-5"   # 前后端基础框架搭建
  phase2: "ROC-6"   # 前端 UI 研发
  phase3: "ROC-7"   # 后端接口研发
  phase4: "ROC-8"   # 前后端联调

---

## 🎯 日常口语命令映射

当用户用日常口语描述开发操作时，自动执行以下映射：

### 1. 开始任务
| 用户说 | 自动执行 |
|--------|---------|
| "开始做XXX" | 更新 Linear Issue 状态为 In Progress |
| "开始 Phase 1" | 更新 ROC-5 状态为 In Progress |
| "我来做登录功能" | 查找相关 Issue，更新状态为 In Progress |

### 2. 完成任务
| 用户说 | 自动执行 |
|--------|---------|
| "完成了" | 更新当前 Issue 状态为 Done |
| "做完了XXX" | 标记对应 Issue 为 Done |
| "Phase 2 搞定了" | 更新 ROC-6 状态为 Done |

### 3. 创建分支
| 用户说 | 自动执行 |
|--------|---------|
| "给我开个分支" | 创建 `feature/当前任务名` 分支 |
| "开始做新功能" | 创建 `feature/功能名` 分支并切换 |
| "修复 bug" | 创建 `fix/bug描述` 分支 |

### 4. 提交代码
| 用户说 | 自动执行 |
|--------|---------|
| "提交" | Git add + commit（根据当前分支命名） |
| "推送到远程" | Git push origin 当前分支 |
| "提交并推送" | commit + push |

---

## 🔧 命令执行流程

### 当用户说 "开始做登录功能"

1. **解析意图**：识别为「开始任务」意图
2. **查找 Issue**：在 Linear 中搜索 "登录" 相关 Issue
3. **推荐分支**：
   - 主分支：`main`
   - 新分支：`feature/login` 或 `feat/login-system`
4. **询问确认**：---
alwaysApply: true
---
