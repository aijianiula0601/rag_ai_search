# Download searxng-docker
```bash
git clone https://github.com/searxng/searxng-docker.git
mv searxng-docker searxng
```

# Modify Docker-Compose Configuration
```bash
cd searxng
vim docker-compose.yaml
```

Comment out Caddy-related sections as we don't need Caddy as a reverse proxy.
Change IP address from 127.0.0.1 to 0.0.0.0 for LAN access.
Modify port number to an unused port.

# Edit Environment Configuration

Edit the .env file to set your domain name:    
```bash
vim .env
```
If you don't have a domain name, simply set: SEARXNG_HOSTNAME=127.0.0.1

# Start searxng
```bash
docker-compose up -d
``` 

# Generate Key and Modify Settings

Generate a random key and update settings.yml:

```bash
cd searxng
sed -i "s|ultrasecretkey|$(openssl rand -hex 32)|g" settings.yml
```

# Remove searxng
```bash
docker-compose down
```

# Access searxng
```bash
http://localhost:4008/
```

# Test Command
```bash
curl -kLX GET --data-urlencode q='langchain' -d format=json http://localhost:4008
```

# Special Note

If the JSON format is not accessible, make the following changes:

Since docker-compose.yaml mounts searxng_run:

```bash 
- ./searxng_run:/etc/searxng:rw
```

Configure settings.yml in searxng_run:

```bash
vim searxng_run/settings.yml
```

Add JSON format:
```bash
search:
    formats:
        - html
        - json
```

# Restart searxng
```bash
docker-compose down
docker-compose up -d
``` 