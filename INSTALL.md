CentOS 7 安装文档
--------------------------

生产环境使用

说明 安装过程中遇到问题可咨询
~~~~~~~
-  # 开头的行表示注释
-  > 开头的行表示需要在 mysql 中执行
-  $ 开头的行表示需要执行的命令
~~~~~~~
环境
-  系统: CentOS 7
-  IP: 10.211.55.4
-  目录: /opt
-  数据库: mariadb
-  代理: nginx

开始安装
~~~~~~~~~~~~

.. code-block:: shell

	# 推荐用yum upgrade取代yum update，yum update只更新系统中已有的软件包，不会更新内核软件包(kernel-这个包)，yum upgrade是更彻底的update，会分析包的废弃关系，可以跨小版本升级（比如从centos 7.1升级到centos 7.4），除了做了yum update完全相同的事之外，还会更新kernel-的包，也会卸载掉已经废弃的包。
    $ yum update -y

    # 防火墙 与 selinux 设置说明, 如果已经关闭了 防火墙 和 Selinux 的用户请跳过设置
    $ systemctl start firewalld
    $ firewall-cmd --zone=public --add-port=80/tcp --permanent  # nginx 端口

    $ firewall-cmd --reload  # 重新载入规则

    $ setenforce 0
    $ sed -i "s/SELINUX=enforcing/SELINUX=disabled/g" /etc/selinux/config

    # 安装依赖包
    $ yum -y install wget gcc epel-release git

    # 安装 Redis, Dolphindoctor 使用 Redis 做 cache 和 celery broke
    $ yum -y install redis
    $ systemctl enable redis
    $ systemctl start redis

    # 安装 MySQL, 1 如果已经安装MySQL可以跳过；2 如果不使用 Mysql 可以跳过相关 Mysql 安装和配置, 支持sqlite3, mysql, postgres等
    $ yum -y install mariadb mariadb-devel mariadb-server MariaDB-shared # centos7下叫mariadb, 用法与mysql一致
    $ systemctl enable mariadb
    $ systemctl start mariadb

    # 创建数据库 Dolphindoctor 并授权
    $ DB_PASSWORD=`cat /dev/urandom | tr -dc A-Za-z0-9 | head -c 24`  # 生成随机数据库密码
    $ echo -e "\033[31m 你的数据库密码是 $DB_PASSWORD \033[0m"
    $ mysql -uroot -e "create database dolphindoctor default charset 'utf8'; grant all on dolphindoctor.* to 'dolphindoctor'@'127.0.0.1' identified by '$DB_PASSWORD'; flush privileges;"
    # 比如：mysql -uroot -pAbc@1234 -e "create database dolphindoctor default charset 'utf8'; grant all on dolphindoctor.* to 'dolphindoctor'@'127.0.0.1' identified by 'Abc@1234'; flush privileges;"

    # 安装 Nginx, 用作代理服务器整合 Dolphindoctor 与各个组件
    $ vi /etc/yum.repos.d/nginx.repo
	'''
    [nginx]
    name=nginx repo
    baseurl=http://nginx.org/packages/centos/7/$basearch/
    gpgcheck=0
    enabled=1
	'''

    $ yum -y install nginx
    $ systemctl enable nginx

    # 安装 Python3.6
    $ yum -y install python36 python36-devel

    # 配置并载入 Python3 虚拟环境
    $ cd /opt
    $ python3.6 -m venv py3  # py3 为虚拟环境名称, 可自定义
    $ source /opt/py3/bin/activate  # 退出虚拟环境可以使用 deactivate 命令

    # 看到下面的提示符代表成功, 以后运行 Dolphindoctor 都要先运行以上 source 命令, 载入环境后默认以下所有命令均在该虚拟环境中运行
    (py3) [root@localhost py3]

    # 下载 Dolphindoctor
    $ cd /opt/
    $ git clone --depth=1 https://github.com/samucc/dolphindoctor.git

    # 安装依赖 RPM 包
    $ yum -y install $(cat /opt/dolphindoctor/requirements/rpm_requirements.txt)

    # 安装 Python 库依赖
    $ pip install --upgrade pip setuptools
    $ pip install -r /opt/dolphindoctor/requirements/requirements.txt

.. code-block:: shell


    # 修改 Dolphindoctor 配置文件  如果config.yml已经存在可以不操作
    $ cd /opt/dolphindoctor
    $ cp config_example.yml config.yml

    $ SECRET_KEY=`cat /dev/urandom | tr -dc A-Za-z0-9 | head -c 50`  # 生成随机SECRET_KEY
    $ echo "SECRET_KEY=$SECRET_KEY" >> ~/.bashrc
    $ BOOTSTRAP_TOKEN=`cat /dev/urandom | tr -dc A-Za-z0-9 | head -c 16`  # 生成随机BOOTSTRAP_TOKEN
    $ echo "BOOTSTRAP_TOKEN=$BOOTSTRAP_TOKEN" >> ~/.bashrc

    $ sed -i "s/SECRET_KEY:/SECRET_KEY: $SECRET_KEY/g" /opt/dolphindoctor/config.yml
    $ sed -i "s/BOOTSTRAP_TOKEN:/BOOTSTRAP_TOKEN: $BOOTSTRAP_TOKEN/g" /opt/dolphindoctor/config.yml
	# 开发环境 此处可以不操作
    $ sed -i "s/# DEBUG: true/DEBUG: false/g" /opt/dolphindoctor/config.yml
    $ sed -i "s/# LOG_LEVEL: DEBUG/LOG_LEVEL: ERROR/g" /opt/dolphindoctor/config.yml
    $ sed -i "s/# SESSION_EXPIRE_AT_BROWSER_CLOSE: false/SESSION_EXPIRE_AT_BROWSER_CLOSE: true/g" /opt/dolphindoctor/config.yml
	# DB_PASSWORD如果不是随机生成的，可以手动修改为已知密码
    $ sed -i "s/DB_PASSWORD: /DB_PASSWORD: $DB_PASSWORD/g" /opt/dolphindoctor/config.yml

    $ echo -e "\033[31m 你的SECRET_KEY是 $SECRET_KEY \033[0m"
    $ echo -e "\033[31m 你的BOOTSTRAP_TOKEN是 $BOOTSTRAP_TOKEN \033[0m"

    $ vi config.yml  # 确认内容有没有错误，上述操作的步骤内容全部生效

.. code-block:: yaml

    '''
	# SECURITY WARNING: keep the secret key used in production secret!
    # 加密秘钥 生产环境中请修改为随机字符串, 请勿外泄, PS: 纯数字不可以
    SECRET_KEY:'aE9qkcLEVyyKEbEMHsBOUuej4jJeaaMIbNZl3xSmSZwbpWmSza'

    # SECURITY WARNING: keep the bootstrap token used in production secret!
    # 预共享Token koko和guacamole用来注册服务账号, 不在使用原来的注册接受机制
    BOOTSTRAP_TOKEN:'i0jesjQOpFKFhG6j'

    # Development env open this, when error occur display the full process track, Production disable it
    # DEBUG 模式 开启DEBUG后遇到错误时可以看到更多日志
    DEBUG: false

    # DEBUG, INFO, WARNING, ERROR, CRITICAL can set. See https://docs.djangoproject.com/en/1.10/topics/logging/
    # 日志级别
    LOG_LEVEL: ERROR
    # LOG_DIR:

    # Session expiration setting, Default 24 hour, Also set expired on on browser close
    # 浏览器Session过期时间, 默认24小时, 也可以设置浏览器关闭则过期
    # SESSION_COOKIE_AGE: 86400
    SESSION_EXPIRE_AT_BROWSER_CLOSE: true

    # Database setting, Support sqlite3, mysql, postgres ....
    # 数据库设置
    # See https://docs.djangoproject.com/en/1.10/ref/settings/#databases

    # SQLite setting:
    # 使用单文件sqlite数据库
    # DB_ENGINE: sqlite3
    # DB_NAME:

    # MySQL or postgres setting like:
    # 使用Mysql作为数据库
    DB_ENGINE: mysql
    DB_HOST: 127.0.0.1
    DB_PORT: 3306
    DB_USER: dolphindoctor
    DB_PASSWORD: Abc@1234
    DB_NAME: dolphindoctor

    # When Django start it will bind this host and port
    # ./manage.py runserver 127.0.0.1:8080
    # 运行时绑定端口
    HTTP_BIND_HOST: 0.0.0.0
    HTTP_LISTEN_PORT: 8080

    # Use Redis as broker for celery and web socket
    # Redis配置
    REDIS_HOST: 127.0.0.1
    REDIS_PORT: 6379
    # REDIS_PASSWORD:
    # REDIS_DB_CELERY: 3
    # REDIS_DB_CACHE: 4

    # Use OpenID authorization
    # 使用OpenID 来进行认证设置
    # BASE_SITE_URL: http://localhost:8080
    # AUTH_OPENID: false  # True or False
    # AUTH_OPENID_SERVER_URL: https://openid-auth-server.com/
    # AUTH_OPENID_REALM_NAME: realm-name
    # AUTH_OPENID_CLIENT_ID: client-id
    # AUTH_OPENID_CLIENT_SECRET: client-secret

    # OTP settings
    # OTP/MFA 配置
    # OTP_VALID_WINDOW: 0
    # OTP_ISSUER_NAME: Dolphindoctor
	'''

.. code-block:: shell

    # 运行 Dolphindoctor
    $ cd /opt/dolphindoctor
    $ ./dpd start -d  # 后台运行使用 -d 参数./dpd start -d
	$ ./dpd start all -d
    # 新版本更新了运行脚本, 使用方式./dpd start|stop|status all  后台运行请添加 -d 参数

    $ vim dpd.service
	'''
	[Unit]
	Description=dpd
	After=network.target mysqld.service redis.service
	Wants=mysqld.service redis.service

	[Service]
	Type=forking
	Environment="PATH=/opt/py3/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/root/bin"
	ExecStart=/opt/dolphindoctor/dpd start all -d
	ExecReload=
	ExecStop=/opt/dolphindoctor/dpd stop all

	[Install]
	WantedBy=multi-user.target
	'''
    $ chmod 755 /usr/lib/systemd/system/dpd.service
    $ systemctl enable dpd  # 配置自启


.. code-block:: shell

    # 配置 Nginx 整合各组件
    $ rm -rf /etc/nginx/conf.d/default.conf

.. code-block:: shell

    $ vi /etc/nginx/conf.d/dolphindoctor.conf
	'''
	upstream dolphindoctor {
		server localhost:8080;
		# 这里是 dolphindoctor 的后端ip
	}

    server {
        listen 80;

        client_max_body_size 100m;  # 录像及文件上传大小限制

        location /media/ {
            add_header Content-Encoding gzip;
            root /opt/dolphindoctor/data/;  # 录像位置, 如果修改安装目录, 此处需要修改
        }

        location /static/ {
            root /opt/dolphindoctor/data/;  # 静态资源, 如果修改安装目录, 此处需要修改
        }

        location / {
			proxy_pass http://dolphindoctor;  # 如果dolphindoctor安装在别的服务器，请填写它的ip
			proxy_set_header X-Real-IP $remote_addr;
			proxy_set_header Host $host;
			proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
		}
    }
	'''


.. code-block:: shell

    # 运行 Nginx
    $ nginx -t   # 确保配置没有问题, 有问题请先解决
    $ systemctl start nginx

    # 访问 http://10.211.55.4 (注意 没有 :8080 通过 nginx 代理端口进行访问)
    # 默认账号: admin 密码: admin


多组件负载说明

.. code-block:: shell

    ...

    # nginx 代理设置
    $ vi /etc/nginx/nginx.conf
	'''
    user  nginx;
    worker_processes  auto;

    error_log  /var/log/nginx/error.log warn;
    pid        /var/run/nginx.pid;

	# Load dynamic modules. See /usr/share/nginx/README.dynamic.
	include /usr/share/nginx/modules/*.conf;

    events {
        worker_connections  1024;
    }

    # 加入 tcp 代理
    stream {
        log_format  proxy  '$remote_addr [$time_local] '
                           '$protocol $status $bytes_sent $bytes_received '
                           '$session_time "$upstream_addr" '
                           '"$upstream_bytes_sent" "$upstream_bytes_received" "$upstream_connect_time"';

        access_log /var/log/nginx/tcp-access.log  proxy;
        open_log_file_cache off;

    }
    # 到此结束

    http {
        include       /etc/nginx/mime.types;
        default_type  application/octet-stream;

        log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                          '$status $body_bytes_sent "$http_referer" '
                          '"$http_user_agent" "$http_x_forwarded_for"';

        access_log  /var/log/nginx/access.log  main;

        sendfile        on;
        # tcp_nopush     on;

        keepalive_timeout  65;

        # 关闭版本显示
        server_tokens off;

        include /etc/nginx/conf.d/*.conf;
    }
	'''

    $ vi /etc/nginx/conf.d/dolphindoctor.conf
	'''
    upstream dolphindoctor {
        server localhost:8080;
        # 这里是 dolphindoctor 的后端ip
    }

    server {
        listen 80;
        server_name demo.dolphindoctor.org;  # 自行修改成你的域名

        client_max_body_size 100m;  # 录像上传大小限制

        location / {
            proxy_pass http://dolphindoctor;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header Host $host;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            access_log off;
        }

        location /media/ {
            add_header Content-Encoding gzip;
            root /opt/dolphindoctor/data/;  # 录像位置, 如果修改安装目录, 此处需要修改
        }

        location /static/ {
            root /opt/dolphindoctor/data/;  # 静态资源, 如果修改安装目录, 此处需要修改
        }

    }
	'''

    $ nginx -t
    $ nginx -s reload

如遇到问题可咨询