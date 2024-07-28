## 98自动签到
1.定时任务触发
2.需要代理
3.支持随机回复

### docker-compose.yaml
```
version: "3"
services:
  qd_98:
    image: spacey0409/qd_98:1.0.0
    command: python3 /app/main.py
    volumes:
      # 配置文件
      - path/to/conf.yaml:/app/conf.yaml
    restart: always
    network_mode: host
    hostname: qd_98
    container_name: qd_98
```

### conf.yaml
https://github.com/spacey0409/qd_98/blob/main/conf.yaml
