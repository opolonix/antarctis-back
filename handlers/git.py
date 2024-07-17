from fastapi import APIRouter, Request, HTTPException
import subprocess, hashlib, hmac, os
from config import SECRET

router = APIRouter()

@router.post("/git", include_in_schema=False)
async def github_webhook(request: Request):
    """Хук для гита, реализвация ci/cd"""
    signature = request.headers.get("X-Hub-Signature")
    
    if signature is None:
        raise HTTPException(status_code=403, detail="Signature header required")

    body = await request.body()
    hash_algorithm, signature_hash = signature.split("=", 1)

    if hash_algorithm != "sha1":
        raise HTTPException(status_code=501, detail="Unsupported hash algorithm")

    hmac_hash = hmac.new(SECRET.encode(), body, hashlib.sha1).hexdigest()
    if not hmac.compare_digest(signature_hash, hmac_hash):
        raise HTTPException(status_code=403, detail="Invalid signature")

    last_dir = os.getcwd()
    subprocess.run("git pull", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    os.system(f"cd html")
    subprocess.run("git pull", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    os.system(f"cd {last_dir}")

    return True