
# 安装ollama

## 安装步骤[url](https://ollama.com/download/linux)
```bash 
sudo apt-get update
curl -fsSL https://ollama.com/install.sh | sh
```

## 启动ollama服务

```bash
sudo systemctl start ollama
```

## 查看日记

```bash
journalctl -e -u ollama
```

## 验证

```bash
ollama --version
```


# ollama无法通过ip访问的修复：


在linux配置perplexica时候，必须验证在本地浏览器，通过服务器ip可以访问，如：http://127.0.0.1:11434 ，显示：Ollama is running 才表示成功

## 部署ollama后，修改

```bash
sudo vim  /etc/systemd/system/ollama.service.d/override.conf
```

- 增加：

```bash
[Service]
Environment="OLLAMA_HOST=0.0.0.0"
```

## 重启服务：

```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama
```


参考：https://github.com/ollama/ollama/blob/main/docs/faq.md
