# 下载 searxng-docker
```bash
git clone https://github.com/searxng/searxng-docker.git
mv searxng-docker searxng
```

# 修改Docker-Compose配置文件
```bash
cd searxng
vim docker-compose.yaml
```

注释掉与Caddy相关的部分，因为不需要使用Caddy作为反向代理。
将IP地址从127.0.0.1改为0.0.0.0以便局域网访问。
修改端口号为未被占用的端口。

# 编辑环境配置文件

编辑.env文件，设置你的域名：    
```bash
vim .env
```
如果没有域名，直接设置：SEARXNG_HOSTNAME=127.0.0.1

# 启动 searxng
```bash
docker-compose up -d
``` 

# 生成密钥并修改设置

生成一个随机密钥并更新settings.yml文件：

```bash
cd searxng
sed -i "s|ultrasecretkey|$(openssl rand -hex 32)|g" settings.yml
```

# 删除 searxng
```bash
docker-compose down
```

# 访问 searxng
```bash
http://localhost:4008/
```

#命令测试
```bash
curl -kLX GET --data-urlencode q='langchain' -d format=json http://localhost:4008
```

# 特别注意

如果上面的json方式无法访问，做下面的改动

由于docker-compose.yaml中挂载了searxng_run

```bash 
- ./searxng_run:/etc/searxng:rw
```

所以在searxng_run中，设置settings.yml

```bash
vim searxng_run/settings.yml
```

加入json格式
```bash
search:
    formats:
        - html
        - json
```

# 重启 searxng
```bash
docker-compose down
docker-compose up -d
```

