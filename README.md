#### Setup to cloud

##### Create env
<code>.env</code>
```
PROXY_API_KEY=
```


<code>/etc/systemd/system/broker.service</code>
```
[Unit]
Description=Broker Proxy

After=network.target

[Service]
User=ubuntu

WorkingDirectory=/home/ubuntu/broker-proxy

ExecStart=/usr/bin/python3 -m uvicorn app:app --host 127.0.0.1 --port 9000

Restart=always

EnvironmentFile=/home/ubuntu/broker-proxy/.env

[Install]
WantedBy=multi-user.target
```

##### Reload
```
sudo systemctl daemon-reload

sudo systemctl enable broker

sudo systemctl start broker

sudo systemctl status broker
```

