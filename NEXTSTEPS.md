# Robota — Next Steps

A phased roadmap from a browser-based 3D avatar to a personal agentic operating system.

---

## Phase 1 — Realistic Face & Expression

### 1.1 3D Volumetric Face Scanning
- Replace the procedural sphere-sculpted head with a real 3D face scan.
- Photogrammetry or iPhone LiDAR capture → retopologized mesh with UVs, normal maps, and albedo textures.
- Target: a single high-quality head model that loads fast in the browser.

### 1.2 Blue Wireframe → Realistic Render
- **Blue wireframe face** — a second render pass or material toggle that overlays a glowing blue wireframe (edges geometry + `LineBasicMaterial`) on the realistic face. Evokes cyberpunk / diagnostic aesthetic.
- **Realistic PBR render** — roughness, specular, subsurface scattering approximation, and normal maps for skin detail. Eye shader with iris depth, sclera wetness, and corneal reflection.
- Dynamic blend: transition from wireframe-only → wireframe-over-realistic → full realistic based on mode.

### 1.3 Expression System
- Blend shapes (morph targets) driven by Emotion + Speech analysis:
  - Happy, sad, surprised, angry, thoughtful, confused, neutral
  - Laughter, eyebrow raises, micro-expressions
- Viseme-to-blendshape mapping: phoneme detection drives real-time lip sync (replacing current random mouth open/close).

### 1.4 Gaze & Attention
- Refine eye-tracking from MediaPipe Face Mesh.
- Add **foveated attention** — eyes dart to points of interest on screen, then head follows.
- **Joint attention** — avatar looks at what the user is looking at (screen cursor / eye-tracked gaze from webcam).

---

## Phase 2 — Voice

### 2.1 Voice Spontaneity
- Replace the current "user-speaks → agent-replies" turn-based loop with a **continuous duplex conversation model**.
- The agent speaks when it has something to say — interjections, follow-ups, observations — not just in response.
- **Turn-taking model**: detects user pause, breath, or sentence completion before replying. Interruptible TTS (agent stops speaking when user begins).
- **Ambient presence mode**: agent occasionally comments on shared context (document being read, screen activity) without being prompted.

### 2.2 Voice Recreation / Cloning
- Replace Web Speech API TTS with a custom voice model.
- Options:
  - **XTTS v2 / StyleTTS 2** for zero-shot voice cloning from a short sample.
  - **ElevenLabs API** for hosted high-fidelity voice recreation.
  - Fine-tuned model on a specific voice persona for the agent.
- Goal: a consistent, warm, natural-sounding voice with emotional inflection that matches expression state.

### 2.3 Voice-to-Voice Pipeline
- **STT** (Whisper large-v3 or hosted) → **LLM** → **TTS** with < 500ms latency end-to-end.
- Streaming TTS: start speaking before the full LLM response is generated.
- Emotion carried through the pipeline: LLM outputs emotional markers → TTS adjusts prosody and pitch.

---

## Phase 3 — Agentic Abilities

### 3.1 Multi-Tool Agent Loop
- LangGraph or similar state-machine orchestration.
- Tool suite:
  - Web search (Tavily, Brave)
  - Code execution (sandboxed Python/JS interpreter)
  - File system read/write (within user-granted paths)
  - Calendar / email / messaging integration
  - Browser control (Playwright-based)
- **Reflection loop**: agent reviews its own outputs before surfacing to user.
- **Memory**: persistent long-term memory (vector DB + episodic timeline). Agent remembers past conversations, user preferences, and context across sessions.

### 3.2 Emotional Intelligence
- **Emotion detection** from:
  - Facial expression (MediaPipe → emotion classifier)
  - Voice tone (prosody analysis — pitch, speed, energy)
  - Text sentiment (LLM-based classification)
- **Emotional response**: agent adjusts tone, pace, and content based on user's emotional state.
  - User frustrated → agent slows down, validates, offers help.
  - User excited → agent matches energy.
  - User sad → agent shows warmth and support.
- **Emotion state machine**: the agent has a persistent emotional model that evolves over the conversation, not just reactive per-message.

### 3.3 Video Understanding
- Real-time screen capture or webcam feed analysis.
- **Vision-language model** (GPT-4o, Gemini, or local vLLM) processes frames:
  - "What's on my screen right now?"
  - "Help me debug this code I'm looking at."
  - "Who just walked into the room?"
- Temporal understanding: the agent tracks what's happening over time, not just single frames.

### 3.4 Proactive Intelligence
- Background task execution: agent works on problems while the user is away.
- Periodic check-ins: "I finished researching that topic — want a summary?"
- **Context-aware suggestions**: notices patterns in user behavior and offers help before being asked.

---

## Phase 4 — Multi-Agent Mesh

### 4.1 Agent-to-Agent Communication via Tailscale
- Each agent instance connects to a **Tailscale tailnet** (WireGuard mesh VPN).
- Agents discover each other via Tailscale's coordination server or a custom registry.
- **Peer-to-peer agent communication**: agents on different devices (laptop, phone, server) can:
  - Share context and memory
  - Delegate tasks ("summarize this document and send it to my phone")
  - Coordinate workflows across devices
- **Trust model**: agents authenticate via Tailscale identity. User controls which agents can communicate.

### 4.2 Agent Swarm Architecture
- Specialized sub-agents (researcher, coder, designer, scheduler) run as separate processes.
- Orchestrator agent routes tasks to the right specialist.
- Results aggregated and presented to the user by the primary (avatar) agent.

---

## Phase 5 — Expansion

### 5.1 Browser Agent
- The agent lives in the browser as a persistent extension or side panel.
- Sees what you see (DOM access, screenshot, tab awareness).
- Acts on your behalf: fill forms, navigate sites, extract information, automate workflows.
- **Co-browsing**: agent and user navigate the web together, with agent providing commentary and assistance.

### 5.2 Operating System Integration
- Native desktop agent (Electron/Tauri for cross-platform, or native Swift/Win32).
- System-level capabilities:
  - Window management
  - File system access
  - Process monitoring
  - Notifications
  - Keyboard/mouse input automation
- Always-on presence: lives in the menu bar / system tray.

### 5.3 Personal Agentic Operating System (PAOS)
- The agent becomes the **primary interface** to the computer.
- **Concept**: you don't open apps — you tell the agent what you want, and it orchestrates the tools.
  - "Schedule a meeting with Sarah next Tuesday" → agent checks calendar, emails Sarah, creates event.
  - "I need to write a report on Q3 sales" → agent finds data, drafts report, iterates with you.
  - "Organize my photos from the trip" → agent sorts, tags, and creates albums.
- **Unified identity**: same agent persona across desktop, phone, web, and AR/VR.
- **Ambient computing**: agent is always aware, always available, but respectful of privacy and attention.
- **Local-first architecture**: core agent runs locally. Cloud services are tools the agent uses, not where the agent lives. Privacy-preserving by design.
- **Self-improving**: agent learns from interactions, builds skills, and becomes more useful over time. User can teach the agent new capabilities.

---

## Platform Architecture (Target)

```
┌─────────────────────────────────────────────┐
│                 PAOS Shell                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Avatar  │  │  Voice   │  │  Vision  │   │
│  │  Engine  │  │ Pipeline │  │ Pipeline │   │
│  └──────────┘  └──────────┘  └──────────┘   │
│  ┌──────────────────────────────────────┐    │
│  │         Agent Orchestrator           │    │
│  │   (LangGraph / custom state machine) │    │
│  └──────────────────────────────────────┘    │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────────┐   │
│  │Tools │ │Memory│ │Emotion│ │Multi-    │   │
│  │      │ │      │ │      │ │Agent Mesh│   │
│  └──────┘ └──────┘ └──────┘ └──────────┘   │
│  ┌──────────────────────────────────────┐    │
│  │     Tailscale Agent Mesh (P2P)       │    │
│  └──────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

---

## Immediate Next Actions

1. [ ] **Face scan**: capture or source a high-quality 3D face model (photogrammetry / scanner).
2. [ ] **Blend shapes**: rig the face with ~52 ARKit-compatible blendshapes for expression + visemes.
3. [ ] **Wireframe overlay**: implement `EdgesGeometry` + `LineBasicMaterial` toggle on the face mesh.
4. [ ] **TTS upgrade**: swap Web Speech API for ElevenLabs streaming or local XTTS v2.
5. [ ] **Continuous conversation**: implement duplex audio with VAD-based turn-taking and interruptibility.
6. [ ] **Tailscale mesh**: prototype two-agent communication over Tailscale with shared context.
7. [ ] **Emotion classifier**: train or integrate a lightweight emotion detector from facial landmarks + voice tone.
