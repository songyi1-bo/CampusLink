# CampusLink

校园生活 Web 应用，提供注册登录、个人资料、图片上传和统一页面布局。校园拼车支持发布、筛选、报名、退出和行程管理，并已接入可选的高德地图代码；校园二手书支持发布、筛选、收藏、联系卖家和状态管理；校园悬赏支持发布、筛选、单人接单、撤回、提交完成和发布者确认。

技术栈：Vue 3 + TypeScript + Naive UI + Tailwind CSS / FastAPI + SQLAlchemy / MySQL。

## Quick Start

环境：Node.js 22.12+、Python 3.12、MySQL 8。以下命令使用 Windows PowerShell，从项目根目录开始。

### 1. 安装依赖

```powershell
python -m venv backend/.venv
backend/.venv/Scripts/python.exe -m pip install -r backend/requirements.txt
npm --prefix frontend ci
```

### 2. 配置数据库

本机 MySQL 服务启动后，执行：

```powershell
backend/.venv/Scripts/python.exe database/setup.py
```

在终端输入 MySQL 管理账号密码，脚本自动执行建库建表 SQL、创建项目专用账号，并生成 `backend/.env` 和随机 JWT 密钥，无需复制或编辑文件。默认使用本机 3306 端口和 root 管理账号；其他配置可用 `--host`、`--port`、`--user` 指定。

已有 `.env` 时只检查连接和用户表，不覆盖配置或数据。升级已有公共框架数据库时，运行 `backend/.venv/Scripts/python.exe database/migrate_ride.py` 新增拼车表、运行 `backend/.venv/Scripts/python.exe database/migrate_book.py` 新增二手书表，不会删除旧数据。升级悬赏表时运行 `backend/.venv/Scripts/python.exe database/migrate_quest.py`。全新初始化已包含三个业务模块的表。

高德地图为可选配置：在 `frontend/.env` 填写 `VITE_AMAP_KEY`（Web 端 JS API Key），在 `backend/.env` 填写 `AMAP_SECURITY_CODE`（对应安全密钥），重启前后端。安全密钥不可放入 `VITE_` 变量。配置步骤及限制见 [部署说明](docs/deployment.md)。未配置地图仍可手动填写地点并使用全部拼车业务。

> 如果这台电脑使用项目附带的本地 MySQL，先运行 `backend/.venv/Scripts/python.exe database/local_mysql.py start`。其他电脑使用自己已安装的 MySQL 服务即可。

### 3. 启动

终端一，启动后端：

```powershell
cd backend
.venv/Scripts/python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

终端二，从项目根目录启动前端：

```powershell
cd frontend
npm run dev
```

- 网页：http://127.0.0.1:5173
- API 文档：http://127.0.0.1:8000/docs
- 健康检查：http://127.0.0.1:8000/api/health

前端开发服务器已将 `/api`、`/uploads` 代理到后端；需要改后端地址时参照 `frontend/.env.example`。

### 4. 开发账号（可选）

在 `backend` 目录执行：

```powershell
.venv/Scripts/python.exe -m app.seed
```

创建 `user01`、`user02`、`user03`，密码均为 `CampusLink123!`，已有账号不覆盖。

## 开发与交接

### 已配置电脑上的快速启动（Windows）

完成依赖安装和数据库初始化后，可双击项目根目录的 `start.cmd`，或在 PowerShell 执行 `./start.ps1`。
脚本在需要时启动项目目录内的 MySQL、后端及前端，并检查数据库与 API 连通性。
看到 `CampusLink is ready` 后，在浏览器打开 http://127.0.0.1:5173。
服务在后台运行，关闭启动窗口不会停止服务；重启电脑后再次执行即可。
运行日志位于 `.local/backend.stderr.log`、`.local/frontend.stdout.log` 等文件。
此入口用于已按上述步骤配置好、使用项目本地 MySQL 的电脑；首次安装仍需完成 Quick Start。

- [项目文档](docs/README.md)：需求、数据库与程序设计、测试报告、部署维护、用户手册和工作分配。
- 前端构建检查：在 `frontend` 目录运行 `npm run build`。
- 不提交真实 `.env`、`.local/`、虚拟环境、`node_modules/`、上传文件或构建产物。
