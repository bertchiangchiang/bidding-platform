# 招标询比价平台（Frappe bidding App）

内部询比价平台原型：采购方发布招标 → 供应商在线提交报价 → 采购方多维评分评比 → **供应商可见排名但看不到他人价格** → 定标。

技术栈：Frappe Framework（MIT）+ 自研 App `bidding`（Python + MariaDB + Redis）。原型已内部部署运行。

## 协作说明（给协作者 AI / 开发者）

你无法访问我们的内网环境。本仓库即完整源码，请在本仓库基础上开发，产出格式：

- 每个文件给**完整内容**，第一行注释标目标路径
- 不要长篇说明文档，改动意图一两句即可
- 拿不准的业务规则列「待确认问题」，不要脑补

部署、建表（DocType JSON 自动建表，无需写 SQL）、验收由项目所有方负责。代码只用 Frappe 标准 API（`frappe.get_doc` / `frappe.get_all` / whitelist / File / portal）。

## 已有功能（已实测验收）

| 能力 | 说明 |
|------|------|
| 招标单管理 | Tender + Tender Item（全中文 DocType），状态：草稿/进行中/已截止/已定标 |
| 供应商门户 | www/quotes：招标大厅（角色三分支：访客/供应商/管理员） |
| 在线报价 | 多明细行报价表单，提交即入库 |
| 排名 API | `api.py get_ranking`：供应商只见排名+自己价格，管理员见全部价格（核心资产，改动必须回归此隔离） |
| **评标评分** | Score Template（维度+权重，合计100校验）+ Evaluation（评审人打分、加权总分、多评审人取平均）✅ 新增 |
| **定标** | `api.py award`：管理员定标→招标单转已定标→报价标记中标，重复定标/供应商调用均拒绝 ✅ 新增 |
| 双口径排名 | 按评分（加权总分）或按总价，管理员可切换；总分全员可见、价格隔离 ✅ 新增 |
| 我的报价 | 供应商门户首页可见自己全部报价单（单号/项目/总价/状态） |
| 数据隔离 | 供应商只能查 owner=自己的报价单；门户只显示「草稿/进行中」招标 |
| 全中文 | 访客/登录用户/新用户钩子三层语言覆盖 |

## 代码结构

```
frappe-bidding/
├── docker-compose.yml          # frappe 镜像 + mariadb + redis（密码为占位符，部署方自填）
└── apps/bidding/bidding/
    ├── hooks.py                # User.before_insert 强制中文；登录页标题纠偏
    ├── overrides.py
    ├── api.py                  # get_ranking（双口径排名）+ award（定标）+ submit_quote
    ├── seed.py                 # 演示数据（密码为占位符）
    └── bidding/doctype/
        ├── tender/             # 招标单（含 evaluation_mode / score_template 字段）
        ├── tender item/        # 招标品目
        ├── supplier quote/     # 供应商报价单（含 awarded 中标标记）
        ├── quote item/         # 报价明细
        ├── score template/     # 评分模板（维度+权重）
        ├── score dimension/    # 评分维度子表
        ├── evaluation/         # 评标评分单（加权总分）
        └── evaluation score/   # 评分明细子表
    └── www/quotes.py|html|js   # 门户首页（排名含评分列/中标徽章/管理员定标按钮）
```

注意：仓库内 www 页面存在两份（app 包根 `bidding/www/` 与模块目录 `bidding/bidding/www/`），部署环境两份都要同步。

## 待开发需求（按优先级）

### P0 · 评标核心 ✅ 已完成（2026-11-18 验收通过）
- [x] Score Template 评分模板：维度+权重（价格40%/资质25%/交期15%/案例20%，可自定义），绑定 Tender
- [x] Evaluation 评分单：评审人逐维度打分，自动加权总分，多评审人取平均；评审角色与供应商严格隔离
- [x] 排名升级：按加权总分排序（管理员可切换总价口径）
- [x] 定标 Award：生成中标记录、其余标记未中标，供应商侧只看到状态「已定标」
- [x] 三视角回归已通过：管理员全价 / 供应商甲 / 供应商乙互相看不到对方价格，加权总分全员可见

### P1 · 供应商门户补全（下一批）
- [ ] 招标详情页（品目明细 + 截止倒计时）
- [ ] 截止前撤回重报（留版本痕迹）
- [ ] 提交前预览总价 → 成功页
- [ ] 供应商注册自助化（注册后自动挂「供应商」角色）

### P2 · 管理端
- [ ] 按招标单聚合的报价汇总视图 + 导出 Excel
- [ ] 评标工作台（Evaluation 列表快捷入口）

### P3 · 附件
- [ ] 报价单附件（资质/标书），白名单 pdf/office/图片，≤20MB
- [ ] Tender 需求文件，门户可下载

### P4 · 自动化与通知
- [ ] deadline 到点自动「进行中→已截止」→ 自动开标
- [ ] 邮件通知：新招标邀标 / 新报价提醒管理员 / 定标通知

## 已否决方案（不要建议）

- Odoo 社区版：供应商在线报价需自写 portal、评标需二开、全家桶运维重（模块 purchase/purchase_requisition 已验证存在，结论仍是弃用）
- ERPNext 全家桶：过重
- wzhnbb/bidding：空壳仓库，无源码

## License

- 底座 Frappe Framework：MIT
- 本仓库自研部分：随项目所有方内部使用
