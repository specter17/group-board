import json
import os
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="Group Board")
DATA_FILE = Path(os.getenv("DATA_FILE", "posts.json"))


class Post(BaseModel):
    author: str
    text: str


def load():
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text())
    return []


def save(posts):
    DATA_FILE.write_text(json.dumps(posts))


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/posts")
def get_posts():
    return load()


@app.post("/api/posts")
def add_post(post: Post):
    posts = load()
    posts.insert(0, {
        "author": post.author.strip()[:40] or "anon",
        "text": post.text.strip()[:500],
        "time": datetime.utcnow().strftime("%d %b %H:%M UTC"),
    })
    save(posts[:200])
    return {"ok": True}


@app.get("/", response_class=HTMLResponse)
def home():
    return """<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Group Board</title>
<style>
body{font-family:system-ui,sans-serif;max-width:640px;margin:2rem auto;padding:0 1rem;background:#f6f7f9;color:#222}
h1{margin-bottom:.2rem}
form{display:flex;gap:.5rem;flex-wrap:wrap;margin:1rem 0}
input{padding:.6rem;border:1px solid #ccc;border-radius:6px;font-size:1rem}
#author{width:130px}#text{flex:1;min-width:180px}
button{padding:.6rem 1.2rem;border:0;border-radius:6px;background:#2563eb;color:#fff;font-size:1rem;cursor:pointer}
.post{background:#fff;padding:.8rem 1rem;border-radius:8px;margin-bottom:.6rem;box-shadow:0 1px 2px #0001}
.meta{font-size:.8rem;color:#777}
</style></head><body>
<h1>Group Board</h1><div class="meta">Shared notes for the team</div>
<form id="f"><input id="author" placeholder="Your name" required>
<input id="text" placeholder="Write something..." required><button>Post</button></form>
<div id="posts"></div>
<script>
const esc=s=>s.replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
async function load(){
  const r=await fetch('/api/posts');const p=await r.json();
  document.getElementById('posts').innerHTML=p.map(x=>
   `<div class="post"><div>${esc(x.text)}</div><div class="meta">${esc(x.author)} · ${x.time}</div></div>`).join('');
}
document.getElementById('f').onsubmit=async e=>{
  e.preventDefault();
  await fetch('/api/posts',{method:'POST',headers:{'Content-Type':'application/json'},
   body:JSON.stringify({author:author.value,text:text.value})});
  text.value='';load();
};
load();setInterval(load,5000);
</script></body></html>"""
