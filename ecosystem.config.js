module.exports = {
  apps: [
    {
      name: "proxy-app",
      script: "python3",
      args: "-m uvicorn app:app --host 127.0.0.1 --port 9000",
      cwd: "/home/ec2-user/proxy",
      interpreter: "none",
      autorestart: true,
      watch: false,
      env: {
        PORT: 9000,
      },
    },
  ],
};
