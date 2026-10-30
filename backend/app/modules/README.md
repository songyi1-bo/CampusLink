# 业务模块开发空间

ride、quest、book 分别使用 /api/rides、/api/quests、/api/books 前缀。
ride 已实现行程与成员接口，数据表为 ride_trip 和 ride_member；book 已实现书籍与收藏接口，数据表为 book_listing 和 book_favorite；quest 已实现悬赏流程，数据表为 quest_task。各模块的 schemas、service、router 分别负责校验、业务事务和接口；map_proxy 提供高德固定上游代理，安全密钥仅留在后端。

开发时使用 app.auth.dependencies.CurrentUser 获取已认证用户，使用 DatabaseSession 获取请求会话，使用 ApiResponse 返回统一响应。
直接在各自 Router 中添加接口；不要自行修改 User、认证或公共响应约定。
