# 系统部署维护说明

## 适用范围

本说明用于整组应用的部署与维护。当前已填写公共框架在 Windows 本机课程开发环境中的运行方式；三个模块新增配置及最终交付环境预留在后文，尚未完成生产部署方案。环境为 Node.js 22.12+、Python 3.12、MySQL 8；安装和启动命令见 [Quick Start](../README.md)。默认服务仅监听本机，前端 5173、后端 8000、MySQL 3306。

## 已有公共配置与本地启动

后端使用 `backend/.env`。首次运行 `database/setup.py`，在终端输入 MySQL 管理账号密码，脚本执行初始化 SQL，创建仅有项目库读写权限的本地应用账号，并自动写入以下配置：

| 变量 | 含义 |
| --- | --- |
| DATABASE_HOST / DATABASE_PORT | MySQL 地址与端口 |
| DATABASE_NAME | 默认 campuslink |
| DATABASE_USER / DATABASE_PASSWORD | 对项目库有读写权限的数据库账号 |
| JWT_SECRET | 随机生成且至少 32 字符，拒绝示例占位值 |

已有 `.env` 时脚本只检查连接和用户表，不覆盖配置。真实密码、密钥不提交仓库。前端默认无需配置，若修改后端端口，参照 `frontend/.env.example` 设置 `BACKEND_PROXY_TARGET` 并重启前端；VITE_ 变量会暴露给浏览器，不存凭据。

启动顺序：MySQL → 首次执行 `database/setup.py` → FastAPI → Vite。健康检查 `/api/health` 返回 200 表示数据库可连，API 文档位于 `/docs`。终端中按 Ctrl+C 停止前后端。

使用项目本地 MySQL 脚本的电脑可在根目录执行 `backend/.venv/Scripts/python.exe database/local_mysql.py start` 或 `stop`。脚本依赖 `.local/mysql-8.4.11-winx64/`，不会随 Git 克隆；普通 MySQL 安装不需要此脚本。不要对已有环境重复执行 setup。

## 数据维护与恢复

`backend/uploads/` 自动创建，保存头像等图片。未引用文件不自动清理，删除前先查询所有引用它的用户和业务数据。

备份前暂停应用写入，使用 MySQL 工具备份数据库，同时复制 `backend/uploads/`；将 `.env` 单独保管在受限位置。备份文件含用户数据，不放入仓库。已安装 MySQL 客户端时，可执行以下示例，按实际账号和库名替换，文件保存至项目外的备份目录：

```powershell
mysqldump -u <数据库账号> -p --single-transaction --no-tablespaces --set-gtid-purged=OFF --result-file=<备份文件绝对路径> campuslink
```

恢复时停止应用，先备份现有状态，在确认目标库后通过 MySQL 客户端导入 SQL，再恢复对应 uploads 目录并启动应用检查资料与头像。恢复会改变目标库数据，不可直接对唯一开发库试验。备份恢复流程尚未做实际演练。

结构更新通过明确 SQL 执行，`CREATE TABLE IF NOT EXISTS` 不会修改已有表。更换 JWT_SECRET 会使旧 Token 失效，用户需重新登录。

## 排障与交付

| 现象 | 检查方式 |
| --- | --- |
| 后端无法启动 | 检查虚拟环境依赖、.env、JWT_SECRET 是否为真实随机值 |
| 健康检查 503 | 检查 MySQL 是否启动、账号权限、数据库名和端口 |
| 前端请求失败 | 检查 8000 端口及代理配置，修改配置后重启 |
| 头像不显示 | 检查 uploads 文件是否存在、后端静态服务及开发代理 |
| 端口被占用 | 停止对应旧服务，或协调修改端口与代理 |

前端在 `frontend` 目录执行 `npm run build`，产物为 `dist/`。`npm run preview` 不提供当前开发代理，不能当作完整前后端部署。最终部署目标确定后，需补充静态文件托管、API 与 uploads 转发方案。

交付包应包含源代码、锁文件、配置示例、完整数据库 SQL 和文档；不附带真实凭据、node_modules、虚拟环境或 MySQL 数据目录。全组业务完成后按课程要求以组长学号命名归档文件。

## 业务模块运行配置

### 拼车升级与高德地图

已有公共框架数据库在项目根目录执行：

```powershell
backend/.venv/Scripts/python.exe database/migrate_ride.py
```

脚本仅创建缺失的 `ride_trip`、`ride_member`，不会清空用户或业务数据；重复执行不会重复建表。它不会自动修复已有但结构不同的表。新数据库的 `init.sql` 已包含这两张表。

本机已配置环境可双击根目录 `start.cmd`，服务地址为 http://127.0.0.1:5173，日志在 `.local/`。启动器检查端口和健康状态，不自动更新旧数据库。

地图可选，未配置时手动填写三个地点仍可发布和报名。启用步骤：

1. 在高德控制台申请 Web 端（JS API）Key 及其对应安全密钥，按控制台要求配置实际访问域名。
2. 在 `frontend/.env` 设置 `VITE_AMAP_KEY=你的Key`、`VITE_AMAP_SERVICE_HOST=/_AMapService`。
3. 在 `backend/.env` 设置 `AMAP_SECURITY_CODE=对应安全密钥`。不要放到前端变量、代码或仓库中。
4. 重启前后端。进入发布页点击“地图选点”，验证搜索、点击选点、定位和保存回显。定位由用户主动点击并授权；远程浏览器部署应使用 HTTPS，本机可使用 localhost 安全上下文。

`/_AMapService/status` 只返回是否配置，不能证明 Key、域名和配额有效。代理只允许固定高德 REST 路径，不接受任意上游地址。地图 JS Key 会被浏览器读取，这是客户端 SDK 的配置；安全密钥由后端代理追加。生产静态托管需将 `/api`、`/uploads` 和 `/_AMapService` 转发到后端，不能只部署 dist。本机有效 Key 下地图、搜索、选点、地址解析及回填已通过联调；当前位置定位待用户授权验证。

### 二手书升级

已有公共框架数据库在项目根目录执行：

```powershell
backend/.venv/Scripts/python.exe database/migrate_book.py
```

脚本仅创建缺失的 `book_listing`、`book_favorite`，不会清空用户或业务数据；重复执行不会重复建表。新数据库的 `init.sql` 已包含这两张表。二手书不依赖地图或其他外部服务，无新增环境变量；书籍图片复用公共 `backend/uploads/` 上传目录，无需单独的文件目录。

| 模块 | 新增依赖与环境变量 | 初始化 SQL / 数据 | 文件目录及维护事项 |
| --- | --- | --- | --- |
| 校园拼车 | @amap/amap-jsapi-loader；可选地图变量见上文 | migrations/001_add_ride.sql | 地点、行程、成员和联系方式保存在 MySQL，无新增上传目录 |
| 校园悬赏 | 无 | quest_task；migrate_quest.py 或 003_add_quest.sql | /quest；无新增外部服务 |
| 二手书 | 无 | migrations/002_add_book.sql | 书籍、收藏和联系方式保存在 MySQL；书籍图片复用公共 uploads 目录，无新增上传目录 |

## 最终部署环境

待确定最终运行环境、实际端口与访问地址、完整初始化顺序、前端静态资源及接口转发、启动停止方法、日志位置，以及更新和回退步骤。按实际部署环境填写，不默认必须上云。

业务完成后汇总全部数据库表与文件目录的备份恢复方法，在目标环境实际验证后记录日期和结果；当前本地启动说明不能替代最终部署验收。


## 校园悬赏安装与升级

全新安装执行 database/setup.py 时，init.sql 会同时创建 quest_task。已有数据库在备份后，从根目录运行 `backend/.venv/Scripts/python.exe database/migrate_quest.py`，该脚本仅创建缺失表，可重复执行，不删除数据。若应用账号无 CREATE 权限，使用具备建表权限的数据库账号执行 migrations/003_add_quest.sql，勿给日常运行账号额外开放权限。

重启后端并重新构建或启动前端，访问 /quest。没有新增环境变量和依赖。金额仅记录线下约定，时间按 UTC 保存并在页面显示为浏览器本地时间。列表报 500 时检查迁移是否执行、数据库连接和日志；409 表示状态或截止时间变化，刷新详情再操作；403 表示当前用户无权操作。备份时将 quest_task 与 user 等业务表共同备份，避免丢失外键对应关系。
