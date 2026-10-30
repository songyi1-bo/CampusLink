# Quest 开发空间

CampusQuest 校园悬赏模块。/quest 大厅，/quest/mine 我的悬赏，/quest/new 发布，/quest/:id 详情，/quest/:id/edit 编辑。
QuestList 复用列表与分页，Edit 处理发布编辑，Detail 管理接单与完成流程。设计及状态规则见 docs/quest-plan.md。
接口前缀 /api/quests，统一使用 src/api/request.ts，不直接使用 Axios。
