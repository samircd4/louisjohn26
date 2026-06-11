
# Stop Service
sudo fuser -k 8080/tcp
sudo lsof -i :8080

# Run manually
uv run uvicorn api:app --host 0.0.0.0 --port 8080 --reload


# 1. Start your system service up again
sudo systemctl start product-extractor

# 2. Enable it so it boots automatically if your VPS restarts
sudo systemctl enable product-extractor