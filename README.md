# 连锁药店管理系统

基于 `Vue 3`、`Django REST Framework` 和 `openGauss` 的前后端分离项目，用于连锁药店的账号管理、药品管理、库存管理、销售管理、公告管理和数据看板展示。

这份 README 以“队友如何稳定复现项目”为目标编写，覆盖：

- 本地 Docker Compose 一键运行
- 本地前后端分离开发
- 云服务器部署
- Docker Hub 拉镜像失败时的处理办法
- 容器状态、日志和常见故障排查

## 1. 项目简介

系统包含 3 类角色：

- `系统管理员`：管理药店管理员、销售员、门店、公告和看板
- `药店管理员`：管理药品、厂商、库存、采购单和排班
- `销售员`：查询药品、创建销售单和查看授权订单记录

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

## 4. 推荐复现方式

项目推荐两种使用方式：

### 方式 A：Docker Compose 一键运行

适合：

- 第一次拉代码，想最快跑起来
- 只需要体验功能，不急着改代码
- 希望数据库初始化自动完成

这套方式会同时启动：

- `db`：openGauss
- `backend`：Django API
- `frontend`：nginx 托管的前端页面

### 方式 B：前后端分离开发

适合：

- 需要频繁修改前端或后端代码
- 需要 Vite 热更新
- 需要单独调试 Django 接口

这套方式通常只用 Docker 跑数据库，然后本地分别运行：

- `python manage.py runserver`
- `npm run dev`

如果你是第一次接手项目，建议先走方式 A；确认项目能完整运行后，再切换到方式 B 做开发。

## 5. 方式 A：Docker Compose 一键运行

### 5.1 环境要求

请先确认本机已安装：

- `Git`
- `Docker Desktop` 或其他可用 Docker 环境
- 可用网络环境，用于拉取或导入 Docker 镜像

建议确认以下端口未被占用：

- `5432`：openGauss
- `8000`：后端
- `8080`：前端

### 5.2 拉取代码

```powershell
git clone <你的仓库地址>
cd database
```

如果你收到的是压缩包，解压后进入项目根目录即可。

### 5.3 配置根目录环境变量

在项目根目录执行：

```powershell
Copy-Item .env.example .env
```

然后编辑根目录 `.env`，至少确认这些值：

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
OPENGAUSS_IMAGE=enmotech/opengauss:5.0.1
PYTHON_BASE_IMAGE=python:3.9-slim
NODE_BASE_IMAGE=node:20-alpine
NGINX_BASE_IMAGE=nginx:1.27-alpine
```

说明：

- `DB_PASSWORD` 可自定义，但后续相关配置必须一致
- `INIT_DB_DEMO_DATA=True` 表示首次初始化时自动导入演示数据
- 四个 `*_IMAGE` 变量用于在 Docker Hub 不可达时切换镜像来源
- `.env` 不要提交到 Git

### 5.4 启动全部服务

```powershell
docker compose up -d --build
```

首次启动会做这些事情：

1. 拉取 openGauss、Python、Node、nginx 相关镜像
2. 构建前后端镜像
3. 启动数据库容器
4. 后端自动等待数据库可连接
5. 后端自动创建 `pharmacy_system` 数据库
6. 若数据库为空，自动执行：
   - `sql/schema.sql`
   - `sql/init_data.sql`
7. 启动前端容器

### 5.5 查看运行状态

```powershell
docker compose ps
```

如果三项服务都为 `Up`，说明容器已经正常运行。

查看日志：

```powershell
docker logs pharmacy-opengauss --tail 100
docker logs pharmacy-backend --tail 100
docker logs pharmacy-frontend --tail 100
```

### 5.6 访问项目

启动完成后访问：

- 前端：`http://127.0.0.1:8080`
- 后端：`http://127.0.0.1:8000`
- API 前缀：`http://127.0.0.1:8000/api`

### 5.7 停止服务

```powershell
docker compose down
```

如果你想连数据库卷一起删除，重新做一次全新初始化：

```powershell
docker compose down -v
```

## 6. Docker Hub 拉镜像失败时怎么办

这是这次复现里最常见的障碍。

典型现象：

```text
Get "https://registry-1.docker.io/v2/": timeout
```

### 6.1 先测试镜像源连通性

在终端执行：

```powershell
curl.exe -I --max-time 15 https://docker.m.daocloud.io/v2/
curl.exe -I --max-time 15 https://docker.1ms.run/v2/
```

如果返回 `401`、`302`、`404` 之类 HTTP 响应，说明镜像源可达。

### 6.2 临时手动拉取并改回原标签

这是最稳妥的无配置文件方案。以服务器 Linux 为例：

```bash
docker pull docker.1ms.run/enmotech/opengauss:5.0.1
docker tag docker.1ms.run/enmotech/opengauss:5.0.1 enmotech/opengauss:5.0.1

docker pull docker.1ms.run/library/python:3.9-slim
docker tag docker.1ms.run/library/python:3.9-slim python:3.9-slim

docker pull docker.1ms.run/library/node:20-alpine
docker tag docker.1ms.run/library/node:20-alpine node:20-alpine

docker pull docker.1ms.run/library/nginx:1.27-alpine
docker tag docker.1ms.run/library/nginx:1.27-alpine nginx:1.27-alpine
```

拉取完成后再执行：

```bash
docker compose up -d --build --pull never
```

### 6.3 使用 `.env` 覆盖基础镜像

如果你已经有稳定可用的镜像前缀，也可以在 `.env` 中直接改成替代镜像，例如：

```env
OPENGAUSS_IMAGE=docker.1ms.run/enmotech/opengauss:5.0.1
PYTHON_BASE_IMAGE=docker.1ms.run/library/python:3.9-slim
NODE_BASE_IMAGE=docker.1ms.run/library/node:20-alpine
NGINX_BASE_IMAGE=docker.1ms.run/library/nginx:1.27-alpine
```

这样重新执行 `docker compose up -d --build` 时，会直接从替代镜像源构建。

## 7. 方式 B：前后端分离开发

这套方式更适合日常开发。

### 7.1 环境要求

请先安装：

- `Python 3.9`
- `Node.js 20+`
- `npm`
- `Docker`

### 7.2 第一步：先启动数据库

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
- Database：`pharmacy_system`
- User：`gaussdb`
- Password：根目录 `.env` 中的 `DB_PASSWORD`

### 7.3 第二步：配置后端环境变量

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

### 7.4 第三步：安装后端依赖

```powershell
cd backend
python -m pip install -r requirements.txt
```

### 7.5 第四步：初始化数据库

```powershell
python scripts\init_compose_db.py
```

说明：

- 项目以 `sql/schema.sql` 和 `sql/init_data.sql` 为准
- 不要把 `python manage.py migrate` 当作主初始化方式

### 7.6 第五步：启动后端

```powershell
python manage.py check
python manage.py runserver
```

后端默认地址：

- `http://127.0.0.1:8000`
- API 前缀：`http://127.0.0.1:8000/api`

### 7.7 第六步：配置前端环境变量

```powershell
Copy-Item frontend\.env.example frontend\.env
```

默认情况下 `frontend/.env` 内容如下，通常不需要修改：

```env
VITE_API_BASE_URL=/api
```

### 7.8 第七步：安装并启动前端

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

前端默认地址：

- `http://127.0.0.1:5173`

本地开发时，Vite 会自动把 `/api` 代理到 `http://127.0.0.1:8000`。

## 8. Windows 一键启动方式

项目根目录提供了两个脚本：

- `start_project.bat`
- `stop_project.bat`

适用前提：

- 已安装 Python 和 Node.js
- 已准备好 `backend/.env`
- 本地 openGauss 已在 `127.0.0.1:5432` 运行
- 后端和前端依赖已安装完成

启动：

```powershell
.\start_project.bat
```

停止：

```powershell
.\stop_project.bat
```

## 9. 云服务器部署记录版步骤

这是这次实际验证成功的方案，适合阿里云 Ubuntu + 宝塔 + Docker。

### 9.1 服务器准备

建议至少具备：

- Ubuntu 22.04 或兼容 Linux
- 已安装 Docker 和 Docker Compose
- 已放行安全组端口：`22`、`8888`、`8080`、`8000`

说明：

- `8888` 用于宝塔面板
- `8080` 用于当前前端临时访问
- `8000` 用于后端接口临时访问
- `5432` 不建议长期对公网开放

### 9.2 拉取项目

```bash
mkdir -p /www/wwwroot
cd /www/wwwroot
git clone <你的仓库地址> pharmacy-system
cd pharmacy-system
```

### 9.3 配置环境变量

```bash
cp .env.example .env
```

示例：

```env
SECRET_KEY=你自己的随机字符串
DEBUG=False
ALLOWED_HOSTS=你的公网IP,127.0.0.1,localhost,backend
CORS_ALLOWED_ORIGINS=http://你的公网IP:8080,http://127.0.0.1:8080,http://localhost:8080
DB_NAME=pharmacy_system
DB_USER=gaussdb
DB_PASSWORD=你自己的数据库密码
DB_PORT=5432
INIT_DB_DEMO_DATA=True
```

### 9.4 若 Docker Hub 不可达，先手动导入镜像

```bash
docker pull docker.1ms.run/enmotech/opengauss:5.0.1
docker tag docker.1ms.run/enmotech/opengauss:5.0.1 enmotech/opengauss:5.0.1

docker pull docker.1ms.run/library/python:3.9-slim
docker tag docker.1ms.run/library/python:3.9-slim python:3.9-slim

docker pull docker.1ms.run/library/node:20-alpine
docker tag docker.1ms.run/library/node:20-alpine node:20-alpine

docker pull docker.1ms.run/library/nginx:1.27-alpine
docker tag docker.1ms.run/library/nginx:1.27-alpine nginx:1.27-alpine
```

### 9.5 启动服务

```bash
docker compose up -d --build --pull never
```

### 9.6 查看状态

```bash
docker compose ps
docker logs pharmacy-opengauss --tail 100
docker logs pharmacy-backend --tail 100
docker logs pharmacy-frontend --tail 100
```

### 9.7 访问地址

- 前端：`http://你的公网IP:8080`
- 后端：`http://你的公网IP:8000`

当前这套方式是“先跑起来”的直连方式；后续更规范的做法是：

- 使用宝塔反向代理
- 只开放 `80/443`
- 关闭公网 `8000`
- 关闭公网 `5432`
- 绑定域名并配置 HTTPS

## 10. 演示账号

可直接使用以下账号登录：

- `sysadmin / Admin@123`
- `storeadmin / Admin@123`
- `sales01 / Admin@123`

前提是数据库已成功导入演示数据。

## 11. 本地验证步骤

建议至少完成以下检查：

- 能打开前端登录页
- 能正常登录系统管理员账号
- 登录后能进入首页看板
- 药品、库存、销售等页面能正常加载数据

后端自检：

```powershell
cd backend
python manage.py check
```

烟雾测试：

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

## 12. 团队协作约定

为了保证每个人复现结果一致，建议统一遵守这些规则：

1. `sql/schema.sql` 是数据库结构的权威来源
2. `sql/init_data.sql` 是演示数据的权威来源
3. 不要把 Django migration 当作主建库方式
4. 如果改了表结构，必须同步更新 `sql/schema.sql`
5. 如果改了演示数据，提交前同步更新 `sql/init_data.sql`
6. `.env`、`backend/.env`、`frontend/.env` 不要提交到仓库
7. 前端统一通过 `/api` 访问后端，避免每个人本地都写死不同地址

## 13. 常见问题

### 13.1 `docker compose up` 失败

常见原因：

- Docker 没启动
- Docker Hub 拉镜像失败
- 5432、8000、8080 端口已被占用

先检查：

```powershell
docker compose ps
```

### 13.2 数据库容器启动失败

这次复现里最常见的点有：

- openGauss 镜像需要 `privileged: true`
- 旧版 `healthcheck` 会把数据库误判为 unhealthy
- 如果卷里已有半初始化数据，需先：

```powershell
docker compose down -v
```

再重新启动。

### 13.3 Docker Hub 不可达

可采用两种方式：

- 先从可达镜像源 `pull + tag` 回原始镜像名
- 在 `.env` 中直接覆盖 `OPENGAUSS_IMAGE`、`PYTHON_BASE_IMAGE`、`NODE_BASE_IMAGE`、`NGINX_BASE_IMAGE`

### 13.4 登录成功但页面没有数据

优先检查：

- 是否执行了 `sql/init_data.sql`
- `INIT_DB_DEMO_DATA` 是否为 `True`
- 前端请求是否正确代理到后端 `/api`

## 14. 提交前检查清单

每位队友在提交代码前，建议至少确认：

- 前端能正常启动
- 后端能正常启动
- 数据库能正常连接
- 三个角色都能登录
- 自己修改涉及的数据结构已同步到 SQL 文件
- 没有把 `.env` 或数据库密码提交到仓库

## 15. 推荐给新队友的最短复现路径

如果只是想最快复现项目，请直接按下面做：

1. 拉取仓库
2. 在根目录执行 `Copy-Item .env.example .env`
3. 把 `.env` 里的 `DB_PASSWORD` 改成你自己设置的值
4. 如果 Docker Hub 不通，先手动 `pull + tag` 必要镜像
5. 执行 `docker compose up -d --build`
6. 打开 `http://127.0.0.1:8080`
7. 使用 `sysadmin / Admin@123` 登录

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
