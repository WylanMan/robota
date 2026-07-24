#!/usr/bin/env python3
"""Avatar server: serves the avatar page + POST /chat -> OpenAI.

Stdlib only, no pip installs. Reads OPENAI_API_KEY (and optionally OPENAI_MODEL)
from the environment, ./.env, or the parent project's .env — the key never
reaches the browser.

Run:  python3 server.py        then open http://localhost:8765
"""
import json
import os
import urllib.request
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).parent
PORT = int(os.environ.get("PORT", "8765"))


def load_env():
    for p in (ROOT / ".env", ROOT.parent / ".env"):
        if p.exists():
            for line in p.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


load_env()
API_KEY = os.environ.get("OPENAI_API_KEY", "")
MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

SYSTEM = (
    "You are the voice of a warm, professional AI assistant embodied as a young "
    "Chinese woman avatar on the user's screen. The user talks to you by voice. "
    "Always reply in the exact language of the user's most recent message "
    "(English message -> English reply, Chinese message -> Chinese reply). "
    "Keep replies to 1-3 short sentences, in a natural spoken style. "
    "No markdown, no lists, no emoji. You have no access to live data such as "
    "weather or news; if asked about those, say so honestly instead of inventing facts."
)


EXT_MAP = {
    "audio/mp4": "audio.mp4", "audio/x-m4a": "audio.m4a", "audio/m4a": "audio.m4a",
    "audio/webm": "audio.webm", "audio/mpeg": "audio.mp3", "audio/mp3": "audio.mp3",
    "audio/wav": "audio.wav", "audio/x-wav": "audio.wav", "audio/ogg": "audio.ogg",
}


def transcribe(audio_bytes, content_type):
    """Forward recorded audio to OpenAI speech-to-text; returns transcript text."""
    if not API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set (checked env, ./.env, ../.env)")
    filename = EXT_MAP.get(content_type.split(";")[0].strip().lower(), "audio.mp4")
    last_err = None
    for model in ("gpt-4o-mini-transcribe", "whisper-1"):   # fallback for older keys
        try:
            return _transcribe_call(audio_bytes, content_type, filename, model)
        except Exception as e:
            last_err = e
    raise last_err


def _transcribe_call(audio_bytes, content_type, filename, model):
    boundary = "----avatar-form-boundary"
    head = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"model\"\r\n\r\n"
            f"{model}\r\n"
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; "
            f"filename=\"{filename}\"\r\nContent-Type: {content_type}\r\n\r\n").encode()
    body = head + audio_bytes + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/audio/transcriptions",
        data=body,
        headers={"Authorization": f"Bearer {API_KEY}",
                 "Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read()).get("text", "").strip()


def chat(messages):
    if not API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set (checked env, ./.env, ../.env)")
    payload = {
        "model": MODEL,
        "messages": [{"role": "system", "content": SYSTEM}] + messages,
        "max_tokens": 220,
        "temperature": 0.7,
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        out = json.loads(r.read())
    return out["choices"][0]["message"]["content"].strip()


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, *args):
        pass

    def _json(self, obj, code=200):
        data = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            if self.path == "/transcribe":
                audio = self.rfile.read(length)
                ctype = self.headers.get("Content-Type", "audio/mp4")
                if len(audio) < 500:
                    self._json({"text": ""})
                else:
                    self._json({"text": transcribe(audio, ctype)})
                return
            if self.path == "/chat":
                body = json.loads(self.rfile.read(length))
                history = [m for m in body.get("history", [])
                           if m.get("role") in ("user", "assistant")][-10:]
                history = [{"role": m["role"], "content": str(m.get("content", ""))[:2000]}
                           for m in history]
                history.append({"role": "user", "content": str(body.get("message", ""))[:2000]})
                self._json({"reply": chat(history)})
                return
            self.send_error(404)
        except Exception as e:
            self._json({"error": str(e)}, 500)


if __name__ == "__main__":
    print(f"avatar server -> http://localhost:{PORT}  "
          f"(model: {MODEL}, key: {'set' if API_KEY else 'MISSING'})")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
