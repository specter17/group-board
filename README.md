# Group Board

A tiny FastAPI app where group members post shared notes. Posts are saved to `posts.json`.

## Run locally

```bash
docker build -t group-board .
docker run -p 8000:8000 group-board
# open http://localhost:8000
```

Or without Docker: `pip install -r requirements.txt && uvicorn main:app --reload`

## Deploy on AWS EC2 (simplest, ~5 min)

1. EC2 console -> Launch instance: Amazon Linux 2023, t2.micro / t3.micro (free tier).
2. Security group: allow inbound TCP 22 (SSH) and TCP 80 (HTTP) from anywhere.
3. SSH in, then install Docker and Git:
   ```bash
   sudo dnf install -y docker git
   sudo systemctl enable --now docker
   sudo usermod -aG docker ec2-user && newgrp docker
   ```
4. Get the code onto the instance (git clone your repo, or `scp -r group-board ec2-user@<public-ip>:~`).
5. Build and run, mapping port 80 to the app:
   ```bash
   cd group-board
   docker build -t group-board .
   docker run -d --restart unless-stopped -p 80:8000 -v $(pwd)/data:/data -e DATA_FILE=/data/posts.json group-board
   ```
6. Open `http://<EC2-public-IP>` and share the link with your group.

## Alternative: AWS App Runner (no server to manage)

1. Push this folder to a GitHub repo.
2. App Runner -> Create service -> Source: repository -> runtime Python 3.11.
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port 8000`
   - Port: 8000, health check path: `/health`
3. Deploy. You get a public HTTPS URL.
   (Note: App Runner storage is not persistent, so posts reset on redeploy. Fine for a demo.)

## Clean up

Terminate the EC2 instance (or delete the App Runner service) when done to avoid charges.
