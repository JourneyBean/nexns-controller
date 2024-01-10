# NexNS Controller

NexNS Controller 是 NexNS 服务器的控制中心。装有 NexNS CoreDNS Plugin 的服务器在初始化时会先从 NexNS Controller 读取数据。NexNS Controller 是所有域名数据的保存者。

## docker部署

*待补充*

## 部署步骤

1. **下载仓库**

    ```bash
    git clone https://github.com/JourneyBean/nexns-controller.git
    ```

2. **创建并启用虚拟环境**

    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3. **安装依赖**

    ```bash
    pip install -r requirements.txt
    ```

4. **迁移数据库**

    ```bash
    python ./manage.py migrate
    ```

5. **创建第一位用户**

    ```bash
    python ./manage.py add_user
    ```

6. **创建客户端**

    ```bash
    python ./manage.py add_client
    ```

7. **运行**

    ```bash
    python ./manage.py runserver
    ```

## API

*待补充*

## 后续开发计划

- ~~**发布功能：** 支持先编辑数据，再发布~~finished
- ~~**消息支持：** 支持通知 NexNS CoreDNS Plugin 热重载~~finished
- **DNSSEC支持：** 发布时对域名进行签名
