 # Installing Ollama

## Installation Steps [url](https://ollama.com/download/linux)
```bash 
sudo apt-get update
curl -fsSL https://ollama.com/install.sh | sh
```

## Start Ollama Service

```bash
sudo systemctl start ollama
```

## View Logs

```bash
journalctl -e -u ollama
```

## Verify Installation

```bash
ollama --version
```

# Fix for Ollama IP Access Issues:

When configuring perplexica on Linux, you must verify that the service is accessible through the server IP in your local browser. For example, accessing http://127.0.0.1:11434 should display "Ollama is running" to indicate success.

## Modify After Deploying Ollama

```bash
sudo vim  /etc/systemd/system/ollama.service.d/override.conf
```

- Add the following:

```bash
[Service]
Environment="OLLAMA_HOST=0.0.0.0"
```

## Restart Service:

```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

Reference: https://github.com/ollama/ollama/blob/main/docs/faq.md