# 校园悬赏模块设计说明

## 目标与范围

CampusQuest 面向校园内的跑腿代办、学习互助、维修帮忙和其他互助需求。它复用 CampusLink 账号、JWT、统一请求响应、页面布局及绿色主题，采用 Vue 3 与 FastAPI、SQLAlchemy、MySQL。一个任务由一名发布者发起，最多由一名其他同学接取，完成后由发布者确认。赏金在线下结算，系统不处理支付、聊天、评价或争议仲裁。

## 功能与验收条件

| 编号 | 功能 | 验收条件 |
| --- | --- | --- |
| Q01 | 浏览筛选 | 匿名可浏览；标题和描述包含关键词；分类和状态取交集；每页默认 12 条，支持最新、赏金降序、截止升序 |
| Q02 | 发布 | 登录后填写标题、描述、分类、地点、金额、截止时间和联系方式；成功跳转详情 |
| Q03 | 编辑 | 仅发布者可编辑未过期且无人接单任务，回显联系方式；越权 403，状态不允许 409 |
| Q04 | 接单 | 发布者不能接自己的任务；未过期 open 任务仅能被一人接取；并发接单仅一个成功 |
| Q05 | 撤回 | 当前接单者可在提交前撤回，清除接单人及联系方式，任务恢复 open |
| Q06 | 完成确认 | 接单者提交 2–500 字完成说明，发布者确认后完成；其他用户无权操作 |
| Q07 | 取消 | 仅发布者可取消 open 任务，过期未接单任务也可取消；已接单任务不得单方取消 |
| Q08 | 联系权限 | 匿名 401，旁观者 403；发布者可核对本人联系信息，当前接单者在 accepted/submitted/completed 可查看双方信息 |
| Q09 | 我的悬赏 | 登录后按我发布的/我接取的和状态查询；已完成、取消记录保留；撤回后不属于我接取的 |
| Q10 | 过期 | open 且 deadline 不晚于服务器当前时间时展示 expired，不可接取或编辑；已接单任务仍可交付与确认 |

标题 2–80 字，描述 5–1500 字，地点 2–160 字，去除首尾空格。赏金 0–9999.99 元且最多两位小数。截止时间必须包含时区并处于未来 30 天内。联系类型为 wechat/qq/phone，联系值 3–64 字，禁止换行或控制字符。请求中未知字段返回 422。金额使用 Decimal / NUMERIC，输出两位小数字符串；时间以 UTC 入库，接口返回带时区时间，页面按浏览器本地时间显示。

## 状态与角色

| 当前状态 | 动作 | 操作者 | 后续状态 | 条件与数据变化 |
| --- | --- | --- | --- | --- |
| open | 编辑 | 发布者 | open | 未过期；更新业务字段 |
| open | accept | 其他登录用户 | accepted | 未过期；写入接单者及其联系方式 |
| accepted | withdraw | 当前接单者 | open | 清空接单者和联系方式；若已截止则显示已过期 |
| accepted | submit | 当前接单者 | submitted | 保存完成说明；截止后也可提交 |
| submitted | confirm | 发布者 | completed | 确认交付，保留记录和双方联系权限 |
| open | cancel | 发布者 | cancelled | 不再可接单，历史仍可查询 |

expired 是派生展示状态，不是数据库状态；不需要定时任务。接单后不自动过期、不自动取消，防止完成过程中的任务被静默关闭。完成与取消为终态。重复动作返回 409，不重复更改状态。提交完成后不能撤回；不提供驳回、重新开启或撤回历史，双方通过已授权联系信息沟通。

## 页面与代码结构

| 路由 | 文件 | 登录要求 | 作用 |
| --- | --- | --- | --- |
| /quest | index.vue、QuestList.vue | 无 | 大厅筛选、排序、分页和空态 |
| /quest/mine | Mine.vue、QuestList.vue | 需要 | 本人发布与当前接取记录 |
| /quest/new | Edit.vue | 需要 | 发布悬赏 |
| /quest/:id | Detail.vue | 无 | 公开详情；登录后按 relation 显示操作 |
| /quest/:id/edit | Edit.vue | 需要 | 获取详情、权限及本人联系方式后编辑 |

前端统一通过 api.ts 调用公共 request；表单禁止重复提交，错误保留并允许重试。列表用请求序号避免较慢的旧响应覆盖新筛选结果，加载失败清空旧列表；详情刷新先清空旧权限与联系数据。撤回、取消、确认完成使用确认弹窗。后端 router.py 声明路径与响应，schemas.py 校验，service.py 处理状态与事务，models.py 映射表。

## 数据库设计

使用公共 user 与新建 quest_task，不新增账号表。用户与发布任务为一对多，用户与当前接取任务为一对多；任务上分别保存发布者和可空接单者外键。由于每条任务仅需一个当前接单者，不另建接单关系表。

| 字段 | 类型 | 可空与默认 | 说明 |
| --- | --- | --- | --- |
| id | BIGINT | 非空 自增 | 主键 |
| owner_id | BIGINT | 非空 | 发布者，外键 user.id |
| assignee_id | BIGINT | 可空 NULL | 当前接单者，外键 user.id |
| title | VARCHAR(80) | 非空 | 标题 |
| description | VARCHAR(1500) | 非空 | 公开需求描述 |
| category | VARCHAR(16) | 非空 | delivery/study/repair/other |
| location | VARCHAR(160) | 非空 | 交付地点 |
| reward | NUMERIC(8,2) | 非空 | 赏金，0–9999.99 |
| deadline | DATETIME(6) | 非空 | UTC 截止时间 |
| contact_type | VARCHAR(16) | 非空 | 发布者联系类型 |
| contact_value | VARCHAR(64) | 非空 | 发布者联系值 |
| assignee_contact_type | VARCHAR(16) | 可空 NULL | 接单者联系类型 |
| assignee_contact_value | VARCHAR(64) | 可空 NULL | 接单者联系值 |
| completion_note | VARCHAR(500) | 非空 空字符串 | 私有完成说明 |
| status | VARCHAR(16) | 非空 open | 业务状态 |
| created_at | DATETIME(6) | 非空 当前时间 | 创建时间 |
| updated_at | DATETIME(6) | 非空 自动更新时间 | 更新时间 |

外键使用 ON DELETE RESTRICT，CHECK 限制分类、状态、赏金和发布者不能作为接单者。索引 ix_quest_browse(status,category,deadline,id)、ix_quest_owner(owner_id,created_at,id)、ix_quest_assignee(assignee_id,created_at,id) 支持大厅及个人查询。两种排序和关键词包含搜索在大数据量时仍可能扫描、排序；当前未做性能压测，不承诺大规模性能。

## 接口契约

统一前缀 /api/quests，成功为 HTTP 200 与 `{code:200,message:"success",data:...}`，失败沿用公共异常响应。需登录时发送 Bearer Token，不允许客户端指定 owner_id 或 assignee_id。静态 /mine 在 /{task_id} 前注册。

| 方法 路径 | 登录与角色 | 请求 | data 与错误 |
| --- | --- | --- | --- |
| GET / | 公开 | page、page_size、keyword、category、status、sort | items/total/page/page_size；422 参数不合法 |
| POST / | 登录 | QuestWrite | 详情；401/422 |
| GET /mine | 登录 | scope=published/accepted；page、page_size、status | 分页详情；401/422 |
| GET /{id} | 公开 | 正整数 id | 公开详情；404/422 |
| PUT /{id} | 发布者 | QuestWrite | 更新详情；401/403/404/409/422 |
| GET /{id}/relation | 登录 | 无 | role、can_*、completion_note；401/404 |
| GET /{id}/contacts | 发布者或当前接单者 | 无 | owner 与可空 assignee 联系对象；401/403/404 |
| POST /{id}/accept | 非发布者 | contact_type、contact_value | 更新详情；401/403/404/409/422 |
| POST /{id}/withdraw | 当前接单者 | 空对象 | 更新详情；401/403/404/409 |
| POST /{id}/submit | 当前接单者 | completion_note | 更新详情；401/403/404/409/422 |
| POST /{id}/confirm | 发布者 | 空对象 | 更新详情；401/403/404/409 |
| POST /{id}/cancel | 发布者 | 空对象 | 更新详情；401/403/404/409 |

page 为 1–100000，page_size 为 1–50。category 可省略；status 默认 open，大厅筛选支持 open/accepted/submitted/completed/cancelled/expired，省略我的列表状态则返回全部；sort 为 latest/reward/deadline。公开详情仅含 id、owner、assignee、title、description、category、location、reward、deadline、status、display_status、created_at、updated_at；人物只含 id、nickname、avatar。

relation 返回 role(owner/assignee/visitor)、can_edit、can_accept、can_withdraw、can_submit、can_confirm、can_cancel、can_contact 和 completion_note。旁观者的 completion_note 为 null。relation、contacts 和 mine 均返回 Cache-Control: no-store。

发布请求示例（deadline 按运行当天填写未来 30 天内的时间）：

```json
{"title":"帮取校园资料","description":"请到快递站领取学习资料并送至图书馆门口","category":"delivery","location":"图书馆门口","reward":"5.00","deadline":"2026-10-27T10:00:00+08:00","contact_type":"wechat","contact_value":"campus_demo"}
```

接单：`POST /api/quests/3/accept`，请求 `{"contact_type":"wechat","contact_value":"helper_demo"}`。提交：`POST /api/quests/3/submit`，请求 `{"completion_note":"资料已送到约定地点"}`。确认：发布者向 `/api/quests/3/confirm` 发送空对象。

状态冲突示例：HTTP 409，`{"code":409,"message":"悬赏状态已变化，请刷新后重试","data":null}`。未登录 401、角色无权 403、任务不存在 404、状态不允许 409、参数不合法 422、服务异常 500。调用者根据状态码处理，不依赖逐字文案。

## 事务与隐私

所有编辑和状态变更先 `SELECT FOR UPDATE` 锁定 quest_task 行，使用 populate_existing 刷新 ORM，避免认证 SELECT 建立的 MySQL 快照造成旧状态判断。两个用户同时接单会串行检查：先获得锁者把 open 改为 accepted 并提交，后者读取 accepted 后返回 409。业务异常回滚，会话结束释放锁。联系接口同样用当前读检查，撤回后原接单者失去权限。

公开详情与列表使用独立响应模型，不序列化联系方式和完成说明。前端根据 relation 决定按钮，后端再次校验角色、截止时间和状态，按钮隐藏不构成访问控制。登录身份来自公共 JWT，不信任请求中的用户编号。

## 安装与维护

新环境按 README 安装依赖并执行 database/setup.py；init.sql 已含 quest_task。已有环境备份后执行 `backend/.venv/Scripts/python.exe database/migrate_quest.py`，无 CREATE 权限时用具备权限的管理账号执行 migrations/003_add_quest.sql。迁移可重复执行且不清空旧数据，不负责修改已存在的不兼容表结构。

无需新增依赖或环境变量。启动后端和前端，访问 /quest。备份时同时备份 user、quest_task 和其他业务表。出现 500 先检查连接与迁移；409 刷新后查看当前状态；403 检查角色。不要在日志和公开描述中写入真实联系方式或 Token。

## 实际验证

2026-10-26 在 Windows、Python 3.12、Node.js、MySQL 8.4.11、Vite 与浏览器环境验证。完整实测项目见 testing.md 的校园悬赏记录。已通过前端类型和构建、真实 MySQL 接口、双账号浏览器主流程和 375px 布局；未完成公网部署、安全评估、大规模并发压测及全系统最终验收。
