# dolphindoctor
 dolphindoctor project

安装文档
++++++++++++++++++++++++

**Dolphindoctor 环境要求：**

- 硬件配置: 2个CPU核心, 4G 内存, 50G 硬盘（最低）
- 操作系统: Linux 发行版 x86_64 eg:centos7

- Python = 3.6.x
- Mysql Server ≥ 5.6
- Mariadb Server ≥ 5.5.56
- Redis

生产环境部署部署

- Dolphindoctor 为管理后台, 管理员可以通过 Web 页面进行资产管理、用户管理等操作, 用户可以通过 JSON 接口进行数据访问；

端口说明
~~~~~~~~~~~~~~
- Dolphindoctor 默认端口为 8080/tcp 配置文件 dolphindoctor/config.yml
- Nginx 默认端口为 80/tcp
- Redis 默认端口为 6379/tcp
- Mysql 默认端口为 3306/tcp

+------------+-----------------+------------+
|  Protocol  |   Server name   |    Port    |
+============+=================+============+
|     TCP    |    Dolphindoctor   |    8080    |
+------------+-----------------+------------+
|     TCP    |        Db       |    3306    |
+------------+-----------------+------------+
|     TCP    |       Redis     |    6379    |
+------------+-----------------+------------+
|     TCP    |       Nginx     |     80     |
+------------+-----------------+------------+


**安装步骤**


1. 安装 python3.6 mysql Redis

.. code-block:: vim

    # 编译或者直接从仓库获取都可以, 版本要求参考最上方环境要求

2. 创建 py3 虚拟环境

.. code-block:: shell

    $ python3.6 -m venv /opt/py3

3. 载入 py3 虚拟环境

.. code-block:: shell

    # 每次手动操作 Dolphindoctor 都需要使用下面的命令载入 py3 虚拟环境
    $ source /opt/py3/bin/activate
    # 部分系统可能会提示 source: not found , 可以使用 "." 代替 "source"
    $ . /opt/py3/bin/activate

4. 获取 Dolphindoctor 代码

.. code-block:: shell

    $ cd /opt
    $ git clone --depth=1 https://github.com/samucc/dolphindoctor.git
    # 如果没有安装 git 请先安装

5. 安装依赖

.. code-block:: shell

    $ cd /opt/dolphindoctor/requirements
    # 根据当前系统, 选择对应的文件执行即可
    # 如 Centos: yum install -y $(cat rpm_requirements.txt)
    # 如 Ubuntu: apt-get install -y $(cat deb_requirements.txt)

    $ pip install -r requirements.txt
    # 确保已经载入 py3 虚拟环境, 中间如果遇到报错一般是依赖包没装全, 可以通过 搜索引擎 解决

6. 修改配置文件

.. code-block:: shell

    # 如果已经存在config.yml且配置完成可忽略
	$ cd /opt/dolphindoctor
    $ cp config_example.yml config.yml
    $ vim config.yml
    # 注意 SECRET_KEY 和 BOOTSTRAP_TOKEN 不能使用纯数字字符串

7. 启动 Dolphindoctor

.. code-block:: shell

    $ cd /opt/dolphindoctor
    $ ./dpd start  # 可以 -d 参数在后台运行 ./dpd start -d
    # 确保已经载入 py3 虚拟环境, 中间如果遇到报错请参考 FAQ 文档或者 搜索引擎 解决


8. 配置 nginx 代理

.. code-block:: shell

    # 参考 http://nginx.org/en/linux_packages.html 文档安装最新的稳定版 nginx

    $ rm -rf /etc/nginx/conf.d/default.conf
    $ vim /etc/nginx/conf.d/dolphindoctor.conf

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
            proxy_pass http://localhost:8080;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header Host $host;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }

.. code-block:: shell

    $ nginx -t
    $ nginx -s reload

9. 开始使用 Dolphindoctor

.. code-block:: vim

    # 检查应用是否已经正常运行
    # 服务全部启动后, 访问 Dolphindoctor 服务器 nginx 代理的 80 端口, 不要通过8080端口访问
    # 默认账号: admin 密码: admin

如遇到问题可咨询
