## 运行教程

### 在 `config/env.py` 中配置数据库信息

```bash
# 默认是Postgres SQL
# 数据库类型 MYSQL/SQLSERVER/SQLITE3/POSTGRESQL
DATABASE_TYPE = "POSTGRESQL"
# 数据库地址
DATABASE_HOST = "127.0.0.1"
# 数据库端口
DATABASE_PORT = 3306
# 数据库用户名
DATABASE_USER = ""
# 数据库密码
DATABASE_PASSWORD = ""
# 数据库名
DATABASE_NAME = ""
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


## 数据导出
 python manage.py dumpdata > db_init.json