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
  phase1_overview: "ROC-5"    # Phase 1 概览
  phase1_tasks: "ROC-10"      # Phase 1 子任务（关联为ROC-5子任务）
  phase2_overview: "ROC-6"    # 前端 UI 研发
  phase2_tasks: "ROC-11"      # Phase 2 子任务（关联为ROC-6子任务）
  phase3_overview: "ROC-7"    # 后端接口研发
  phase3_tasks: "ROC-12"      # Phase 3 子任务（关联为ROC-7子任务）
  phase4_overview: "ROC-8"    # 前后端联调
  phase4_tasks: "ROC-13"      # Phase 4 子任务（关联为ROC-8子任务）

state_ids:
  todo: "064f3b6e-9547-401f-94ea-9a7c44568a6b"       # Todo
  in_progress: "1d562cbd-851c-4d93-829f-b96290b93bff"  # In Progress
  done: "8a11de85-ca47-43e7-bf01-6a1e991952be"      # Done
  canceled: "a6008536-d39c-495d-a5b1-99257340482e" # Canceled

---

## ⚡ 强制同步规则

**每次完成任何开发任务后（包括但不限于）：**

1. **Phase 完成后**：必须同步更新 Linear Issue 状态
   - 找到对应的 `phaseX_overview` Issue（如 ROC-5）
   - 找到对应的 `phaseX_tasks` Issue（如 ROC-10）
   - 将两个 Issue 的 stateId 更新为 "done"

2. **子任务完成时**：同步更新子任务 Issue 状态

3. **代码提交/推送时**：同步更新对应 Issue 状态（如适用）

4. **开始新 Phase 时**：将前一 Phase 标记为 Done，开始 Phase 标记为 In Progress

---

## 🎯 日常口语命令映射

当用户用日常口语描述开发操作时，自动执行以下映射：

### 1. 开始任务
| 用户说 | 自动执行 |
|--------|---------|
| "开始 Phase 1" | 更新 ROC-5, ROC-10 状态为 In Progress |
| "开始 Phase 2" | 更新 ROC-6, ROC-11 状态为 In Progress |
| "开始做XXX" | 更新对应 Issue 状态为 In Progress |
| "我来做了" | 更新当前相关 Issue 状态为 In Progress |

### 2. 完成任务
| 用户说 | 自动执行 |
|--------|---------|
| "完成了" | 更新当前 Issue 状态为 Done |
| "Phase 1 完成了" | 更新 ROC-5, ROC-10 状态为 Done |
| "Phase 2 搞定了" | 更新 ROC-6, ROC-11 状态为 Done |
| "做完了" | 更新对应 Issue 状态为 Done |
| "任务完成" | 更新对应 Issue 状态为 Done |

### 3. 创建分支
| 用户说 | 自动执行 |
|--------|---------|
| "开个分支" | 创建 `feature/当前任务名` 分支 |
| "创建分支" | 创建 `feature/功能名` 分支并切换 |
| "修复 bug" | 创建 `fix/bug描述` 分支 |

### 4. 提交代码
| 用户说 | 自动执行 |
|--------|---------|
| "提交" | Git add + commit（根据当前分支命名） |
| "推送" | Git push origin 当前分支 |
| "提交并推送" | commit + push |

### 5. Linear 同步
| 用户说 | 自动执行 |
|--------|---------|
| "同步 Linear" | 同步当前 Phase 状态到 Linear |
| "更新状态" | 同步当前 Issue 状态到 Linear |

---

## 🔧 命令执行流程

### Phase 完成流程

当用户完成 Phase 1 时：

1. **识别 Phase**：识别为 "Phase 1 完成"
2. **更新状态**：
   - 调用 `updateIssue(id="ROC-5", stateId="done")`
   - 调用 `updateIssue(id="ROC-10", stateId="done")`
3. **检查下一 Phase**：
   - 如果开始 Phase 2，更新 ROC-6, ROC-11 为 In Progress
4. **确认完成**：返回更新结果给用户

---

## 📋 Issue 状态映射表

| 状态名称 | stateId | 说明 |
|---------|---------|------|
| Todo | 064f3b6e-... | 未开始 |
| In Progress | 1d562cbd-... | 进行中 |
| Done | 8a11de85-... | 已完成 |
| Canceled | a6008536-... | 已取消 |

---

## 📊 当前进度

| Phase | 概览 Issue | 子任务 Issue | 状态 |
|-------|-----------|-------------|------|
| Phase 1 | ROC-5 | ROC-10 | Done |
| Phase 2 | ROC-6 | ROC-11 | Todo |
| Phase 3 | ROC-7 | ROC-12 | Todo |
| Phase 4 | ROC-8 | ROC-13 | Todo |

**更新规则版本：v2.0**