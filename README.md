# 连锁药店管理系统

基于 `Vue 3`、`Django REST Framework` 和 `openGauss` 的前后端分离项目，用于连锁药店的账号管理、药品管理、库存管理、销售管理、公告管理和数据看板展示。

这份 README 面向团队协作，重点说明两件事：

1. 队友如何从零开始在本地把项目跑起来
2. 队友如何按照统一方式复现数据库、后端和前端环境

## 1. 项目简介

系统包含 3 类角色：

- `系统管理员`：管理药店管理员、销售员、门店、公告和看板
- `药店管理员`：管理药品、厂商、库存、采购单和排班
- `销售员`：查询药品、创建销售单、更新物流和提交订单审核

## 2. 技术栈

### 前端

- `Vue 3`
- `Vite`
- `Vue Router`
- `Pinia`
- `Axios`
- `Element Plus`

### 后端

- `Python 3.9`
- `Django 4.2`
- `Django REST Framework`
- `Simple JWT`
- `gunicorn`

### 数据库

- `openGauss 5.0.1`
- `Docker`

## 3. 目录结构

```text
backend/
  apps/
  config/
  opengauss_backend/
  scripts/
  .env.example
  manage.py
  requirements.txt
frontend/
  src/
  .env.example
  package.json
  vite.config.js
sql/
  schema.sql
  init_data.sql
docker-compose.yml
start_project.bat
stop_project.bat
README.md
```

## 4. 本地复现方案总览

团队本地开发建议使用下面两种方式之一：

### 方案 A：Docker Compose 一键运行

适合以下场景：

- 队友第一次拉代码，想最快把项目完整跑起来
- 只需要体验功能，不急着改代码
- 希望数据库初始化过程尽量自动化

这套方式会同时启动：

- `db`：openGauss
- `backend`：Django API
- `frontend`：nginx 托管的前端页面

### 方案 B：前后端分离开发

适合以下场景：

- 需要频繁修改前端或后端代码
- 需要使用 Vite 热更新
- 需要单独调试 Django 接口

这套方式通常只用 Docker 启动数据库，然后本地分别运行：

- `python manage.py runserver`
- `npm run dev`

如果你是第一次接手这个项目，建议先走方案 A；确认项目能运行后，再切到方案 B 做开发。

## 5. 方案 A：Docker Compose 一键运行

### 5.1 环境要求

请先确认本机已安装：

- `Git`
- `Docker Desktop` 或其他可用 Docker 环境
- 可用的网络环境，用于拉取 Docker 镜像

建议确认以下端口没有被占用：

- `5432`：openGauss
- `8000`：后端
- `8080`：前端

### 5.2 拉取代码

```powershell
git clone <你的仓库地址>
cd database
```

如果你是直接收到压缩包，解压后进入项目根目录即可。

### 5.3 配置根目录环境变量

在项目根目录执行：

```powershell
Copy-Item .env.example .env
```

然后编辑根目录的 `.env`，至少确认这些值：

```env
SECRET_KEY=replace-with-a-secure-secret-key
DEBUG=False
ALLOWED_HOSTS=127.0.0.1,localhost,backend
CORS_ALLOWED_ORIGINS=http://127.0.0.1:8080,http://localhost:8080
DB_NAME=pharmacy_system
DB_USER=gaussdb
DB_PASSWORD=你自己设置的数据库密码
DB_PORT=5432
INIT_DB_DEMO_DATA=True
```

注意：

- `DB_PASSWORD` 可以自定义，但后续相关配置必须保持一致
- `INIT_DB_DEMO_DATA=True` 表示首次初始化时自动导入演示数据
- `.env` 不要提交到 Git

### 5.4 启动全部服务

```powershell
docker compose up --build
```

首次启动会做这些事情：

1. 拉取 openGauss、Python、Node、nginx 相关镜像
2. 构建前后端镜像
3. 启动数据库容器
4. 后端自动等待数据库可用
5. 后端自动创建 `pharmacy_system` 数据库
6. 如果数据库为空，自动执行：
   - `sql/schema.sql`
   - `sql/init_data.sql`
7. 启动前端容器

### 5.5 访问项目

启动完成后访问：

- 前端：`http://127.0.0.1:8080`
- 后端 API 根路径：`http://127.0.0.1:8000`
- 主要接口前缀：`http://127.0.0.1:8000/api`

### 5.6 停止服务

```powershell
docker compose down
```

如果你想连数据库数据一起清空，重新做一次全新初始化：

```powershell
docker compose down -v
```

## 6. 方案 B：前后端分离开发

这套方式更适合日常开发。

### 6.1 环境要求

请先安装：

- `Python 3.9`
- `Node.js 20+`
- `npm`
- `Docker`

### 6.2 第一步：先启动数据库

建议直接复用仓库里的 Compose，只启动数据库服务：

```powershell
Copy-Item .env.example .env
```

编辑根目录 `.env`，保证里面的 `DB_PASSWORD` 是你打算使用的密码。

然后执行：

```powershell
docker compose up -d db
```

启动成功后，本机数据库连接信息如下：

- Host：`127.0.0.1`
- Port：`5432`
- Database：`pharmacy_system`（后续可自动创建）
- User：`gaussdb`
- Password：你在根目录 `.env` 中设置的 `DB_PASSWORD`

### 6.3 第二步：配置后端环境变量

进入后端目录，复制示例配置：

```powershell
Copy-Item backend\.env.example backend\.env
```

编辑 `backend/.env`，重点确认这些值：

```env
SECRET_KEY=replace-with-a-secure-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
CORS_ALLOWED_ORIGINS=http://127.0.0.1:5173,http://localhost:5173
DB_NAME=pharmacy_system
DB_USER=gaussdb
DB_PASSWORD=和根目录 .env 中保持一致
DB_HOST=127.0.0.1
DB_PORT=5432
DB_ADMIN_DB=postgres
INIT_DB_DEMO_DATA=True
```

最关键的一点：

- `backend/.env` 里的 `DB_PASSWORD` 必须和根目录 `.env` 一致，否则后端连不上数据库

### 6.4 第三步：安装后端依赖

```powershell
cd backend
python -m pip install -r requirements.txt
```

### 6.5 第四步：初始化数据库

执行：

```powershell
python scripts\init_compose_db.py
```

这个脚本会自动完成以下工作：

- 等待 openGauss 可连接
- 如果 `pharmacy_system` 不存在，则自动创建
- 如果数据库为空，则执行 `sql/schema.sql`
- 如果 `INIT_DB_DEMO_DATA=True`，再执行 `sql/init_data.sql`

注意：

- 这个项目以 `sql/schema.sql` 和 `sql/init_data.sql` 为准
- 不要把 `python manage.py migrate` 当作主初始化方式

### 6.6 第五步：启动后端

```powershell
python manage.py check
python manage.py runserver
```

后端默认地址：

- `http://127.0.0.1:8000`
- API 前缀：`http://127.0.0.1:8000/api`

### 6.7 第六步：配置前端环境变量

另开一个终端，回到项目根目录后执行：

```powershell
Copy-Item frontend\.env.example frontend\.env
```

`frontend/.env` 默认内容如下，通常不需要修改：

```env
VITE_API_BASE_URL=/api
```

### 6.8 第七步：安装并启动前端

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

前端默认地址：

- `http://127.0.0.1:5173`

本地开发时，Vite 会自动把 `/api` 代理到 `http://127.0.0.1:8000`。

## 7. Windows 一键启动方式

项目根目录提供了两个脚本：

- `start_project.bat`
- `stop_project.bat`

适用前提：

- 你已经安装好 Python 和 Node.js
- 你已经准备好 `backend/.env`
- 本地 openGauss 已经在 `127.0.0.1:5432` 运行
- 后端依赖和前端依赖已经安装完成

启动：

```powershell
.\start_project.bat
```

停止：

```powershell
.\stop_project.bat
```

如果双击脚本后启动失败，优先检查：

- 数据库是否已启动
- `python` 或 Miniconda 路径是否可用
- `npm.cmd` 是否已加入环境变量

## 8. 演示账号

可直接使用以下账号登录：

- `sysadmin / Admin@123`
- `storeadmin / Admin@123`
- `sales01 / Admin@123`

前提是数据库已经成功导入演示数据。

## 9. 本地验证步骤

队友在本地复现后，建议至少完成以下检查：

### 9.1 页面访问检查

- 能打开前端登录页
- 能正常登录系统管理员账号
- 登录后能进入首页看板
- 药品、库存、销售等页面能正常加载数据

### 9.2 后端自检

```powershell
cd backend
python manage.py check
```

### 9.3 烟雾测试

```powershell
cd backend
python scripts\smoke_check.py
```

这个脚本会检查：

- 登录接口是否可用
- 当前用户接口是否正常
- 用户列表查询是否正常
- 药品模糊搜索是否正常
- 库存查询是否正常
- 销售创建后库存是否正确扣减
- 测试结束后是否成功清理测试订单

## 10. 团队协作约定

为了保证每个人复现结果一致，建议统一遵守这些规则：

1. `sql/schema.sql` 是数据库结构的权威来源
2. `sql/init_data.sql` 是演示数据的权威来源
3. 不要把 Django migration 当作主建库方式
4. 如果改了表结构，必须同步更新 `sql/schema.sql`
5. 如果改了演示数据，提交前同步更新 `sql/init_data.sql`
6. `.env`、`backend/.env`、`frontend/.env` 不要提交到仓库
7. 前端统一通过 `/api` 访问后端，避免每个人本地都写死不同地址

## 11. 常见问题

### 11.1 `docker compose up` 失败

常见原因：

- Docker 没启动
- 网络无法拉取镜像
- 5432、8000、8080 端口已被占用

可以先检查：

```powershell
docker compose ps
```

### 11.2 后端提示数据库连不上

优先检查：

- openGauss 是否已经启动
- `backend/.env` 的 `DB_HOST` 是否为 `127.0.0.1`
- `backend/.env` 的 `DB_PASSWORD` 是否和根目录 `.env` 一致
- 本机 5432 端口是否被其他数据库程序占用

### 11.3 提示数据库是“半初始化状态”

说明数据库里已经有部分表，但不是完整初始化状态。

处理方式：

- 开发环境直接清空数据库后重新初始化
- 如果是 Docker 卷中的旧数据，可执行：

```powershell
docker compose down -v
```

然后重新启动。

### 11.4 登录成功但页面没有数据

优先检查：

- 是否执行了 `sql/init_data.sql`
- `INIT_DB_DEMO_DATA` 是否为 `True`
- 前端请求是否正确代理到后端 `/api`

## 12. 提交前检查清单

每位队友在提交代码前，建议至少确认：

- 前端能正常启动
- 后端能正常启动
- 数据库能正常连接
- 三个角色都能登录
- 自己修改涉及的数据结构已经同步到 SQL 文件
- 没有把 `.env` 或数据库密码提交到仓库

## 13. 推荐给新队友的最短复现路径

如果只是想最快复现项目，请直接按下面做：

1. 拉取仓库
2. 在根目录执行 `Copy-Item .env.example .env`
3. 把 `.env` 里的 `DB_PASSWORD` 改成你自己设置的值
4. 执行 `docker compose up --build`
5. 打开 `http://127.0.0.1:8080`
6. 使用 `sysadmin / Admin@123` 登录

如果只是想本地开发，请按下面做：

1. `docker compose up -d db`
2. 配好 `backend/.env`
3. 在 `backend` 中执行：
   - `python -m pip install -r requirements.txt`
   - `python scripts\init_compose_db.py`
   - `python manage.py runserver`
4. 在 `frontend` 中执行：
   - `npm.cmd install`
   - `npm.cmd run dev`
5. 打开 `http://127.0.0.1:5173`
