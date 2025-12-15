## 运行教程
### 克隆项目
```bash
git clone https://github.com/jiangzhikj/zq-platform
# 进入项目目录
cd zq-platform/backend-django
```

### 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

### 在 `env/dev_env.py` 中配置数据库信息
```bash
# 默认是Postgres SQL
# 数据库类型 MYSQL/SQLSERVER/SQLITE3/POSTGRESQL
DATABASE_TYPE = "MYSQL"
# 数据库地址
DATABASE_HOST = "127.0.0.1"
# 数据库端口
DATABASE_PORT = 3306
# 数据库用户名
DATABASE_USER = "fuadmin"
# 数据库密码
DATABASE_PASSWORD = "fuadmin"
# 数据库名
DATABASE_NAME = "fu_admin_pro"
```

### 安装依赖环境
```bash
pip install -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple -r requirements.txt
```

### 执行迁移命令
```bash
python manage.py makemigrations core scheduler
```
```bash
python manage.py migrate
```
### 初始化数据
```bash
python manage.py loaddata db_init.json
```
### 启动项目
```bash
python manage.py runserver 0.0.0.0:8000
```

### 启动任务调度器（可选）
```bash
# 生产环境
python start_scheduler.py
```

### 备份数据（可选）
```bash
python manage.py dumpdata core scheduler --indent 4 > db_init.json
```
