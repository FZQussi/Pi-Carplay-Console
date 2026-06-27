# AveoOS — Workflow de Desenvolvimento

> Setup local, padrões de código, workflow Git e debugging. Para setup no Pi real, ver [`INSTALL.md`](INSTALL.md).

---

## 1. Setup local

```bash
git clone <repo>
cd Pi-Carplay-Console

python3 -m venv .venv
source .venv/bin/activate        # Linux/Mac
# .venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

### Correr o backend

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

- `--reload` — auto-restart ao editar
- `--host 0.0.0.0` — expor na rede (útil para aceder do telemóvel durante testes)
- Sem debug: `uvicorn backend.main:app`

### Abrir a dashboard

<http://localhost:8000/>

### Limitações em Windows / macOS

- `bluetoothctl` **não existe** no Windows → o `BluetoothService.get_status()` vai devolver `error` (esperado)
- `playerctl` **não está** no PATH por defeito no macOS → instalar via brew OU seguir a secção §6 "toggle play" para teste manual
- A capa do Spotify funciona em qualquer plataforma (usa API HTTP)

---

## 2. Estrutura de pastas (resumo)

```
Pi-Carplay-Console/
├── backend/
│   ├── main.py
│   ├── api/
│   │   ├── music.py
│   │   ├── bluetooth.py
│   │   └── system.py
│   ├── services/
│   │   ├── bluetooth.py
│   │   ├── music.py
│   │   ├── power.py        # V2
│   │   └── system.py
│   └── core/
│       ├── config.py
│       ├── events.py
│       └── ws.py
├── frontend/
│   ├── pages/
│   │   └── index.html
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
├── docs/
├── scripts/
│   ├── systemd/
│   ├── kiosk/
│   └── power/
├── tests/
├── requirements.txt
├── LICENSE
└── README.md
```

---

## 3. Padrões de código

### Python (backend)

- **Versão**: Python 3.12+
- **Type hints**: usar em todas as funções públicas
- **Docstrings**: estilo Google ou NumPy (escolher um e manter)
- **Naming**:
  - Classes: `PascalCase` (`BluetoothService`)
  - Funções/métodos: `snake_case` (`get_status`)
  - Módulos: `snake_case`
  - Constantes em `core/config.py`: `UPPER_SNAKE_CASE`
- **Async**: `async def` para funções que fazem I/O (httpx, DBus, GPIO polling). `def` para controlos rápidos
- **Subprocessos**: usar `subprocess.run` síncrono para chamadas de <1s, `asyncio.create_subprocess_exec` para >1s
- **Erros**: nunca engolir exceções sem deixar vestígio. Padrão de retorno:

  ```python
  try:
      ...
      return {"status": "discoverable"}
  except Exception as e:
      return {"error": str(e)}
  ```

### JavaScript (frontend)

- **ES2020** features (sem build step)
- **Naming**: `camelCase` para funções/vars, `kebab-case` para IDs de DOM
- **Sem frameworks**: vanilla, sem jQuery, sem React na V1
- **Fetch sempre com erro**:

  ```js
  try {
      const res = await fetch("/status");
      const data = await res.json();
      // ...
  } catch (e) {
      console.error("Erro:", e);
  }
  ```

### CSS

- **Classes kebab-case** (`.app-grid`, `.progress-bar`)
- **Mobile-first**: mas a única "resolução" é o touchscreen do carro, 800×480 típicamente
- **Variáveis CSS** em `:root` para tema (cores, espaçamentos)

### Comentários

- **Idioma**: PT para comentários de cabeçalho e descritivos (mantém consistência com `docs/`).
- Mantém comentários curtos e direcionados a "porquê", não "o quê".

---

## 4. Workflow Git

### Branches

| Prefixo | Uso |
|---------|-----|
| `feat/` | Nova funcionalidade (`feat/bluetooth-auto-reconnect`) |
| `fix/`  | Correção de bug (`fix/cover-fallback-empty-artist`) |
| `refactor/` | Refactor sem mudança de comportamento |
| `docs/` | Apenas documentação (`docs/architecture-mongoose-error`) |
| `test/` | Adicionar/ajustar testes |

### Mensagens de commit

Formato convencional (PT):

```
feat(bluetooth): adicionar auto-reconnect no power on

Atualmente ao ligar o telemóvel após desligar o Pi, é necessário
emparelhar de novo. Festival a partir do perfil 'trusted' do
bluetoothctl resolve o problema.

Refs: #12
```

Tipos canónicos: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `style`.

### Antes de abrir PR

1. `pip install -r requirements.txt` se adicionou deps
2. Testar manualmente (`uvicorn ... --reload`, browser)
3. Atualizar `docs/...` relevante (architecture, roadmap, etc.)
4. Se sprint mudou → atualizar `docs/ROADMAP.md`

---

## 5. Como adicionar um novo serviço

Template mínimo (ex: `services/power.py`):

```python
# backend/services/power.py
from typing import Any


class PowerService:
    """Lê estado do GPIO ACC e gere shutdown seguro."""

    def get_status(self) -> dict[str, Any]:
        """Retorna estado atual da ignição."""
        # TODO: substituir por leitura real de GPIO
        return {"acc": False, "ignition": False}

    def graceful_shutdown(self) -> dict[str, str]:
        """Coordena um shutdown limpo."""
        return {"status": "shutting-down"}
```

Adicionar router:

```python
# backend/api/system.py
from fastapi import APIRouter
from backend.services.power import PowerService

router = APIRouter(prefix="/power", tags=["power"])
power = PowerService()


@router.get("/status")
def status():
    return power.get_status()


@router.post("/shutdown")
def shutdown():
    return power.graceful_shutdown()
```

Montar em `main.py`:

```diff
  app.include_router(music.router)
  app.include_router(bluetooth.router)
+ app.include_router(system.router)
```

Adicionar a `requirements.txt` se introduzir nova dep.

---

## 6. Debugging

### Backend

```bash
# Auto-reload + log detalhado
uvicorn backend.main:app --reload --log-level debug

# Logs em produção
journalctl -u aveoos-backend -f

# Chamar endpoints à mão
curl -s http://localhost:8000/status | python3 -m json.tool
curl -X POST http://localhost:8000/music/play
```

### Bluetooth (na máquina alvo)

```bash
bluetoothctl
# Dentro do prompt do bluetoothctl:
scan on
pair <MAC>
trust <MAC>
connect <MAC>
info <MAC>          # confirma Connected: yes
```

### Áudio / metadata

```bash
playerctl -l                       # lista players disponíveis
playerctl --all-players status
playerctl metadata --format "{{ status }} {{ artist }} - {{ title }}"
```

### Frontend (kiosk)

- Atalho para DevTools: `Ctrl+Shift+I` (configurável em kiosk mode)
- Em alternativa, `chromium --remote-debugging-port=9222 --kiosk ...` e abrir `chrome://inspect` de outro PC
- `console.log` aparece em DevTools → Console

### Hardware I/O

```bash
gpiodetect                                         # chips GPIO disponíveis
gpioinfo gpiochip0                                 # ver pinos
gpioget --chip 0 --bias=pull-down 17               # ler GPIO17 (ACC)
```

---

## 7. Testes

Estrutura `tests/` é criada na Fase 0 do projeto. Planos:

- **Framework**: pytest
- **Padrão**: cada módulo `services/` tem um teste correspondente em `tests/`
- **Cobertura inicial**: lógica de negócio sem I/O (parsing, validação)
- **Para subprocess**: usar `unittest.mock` para evitar chamadas reais em CI

Exemplo de teste unitário:

```python
# tests/services/test_music.py
from backend.services.music import MusicService


def test_toggle_play_changes_playing_state():
    svc = MusicService()
    assert svc.get_current_track()["playing"] is False
    svc.play()
    assert svc.get_current_track()["playing"] is True
    svc.pause()
    assert svc.get_current_track()["playing"] is False
```

Correr:

```bash
pytest tests/ -v
```

---

## 8. Checklist antes de deploy

- [ ] Toda a nova lógica tem teste unitário (pelo menos smoke test)
- [ ] Sem credenciais hardcoded em código (movidas para `core/config.py` ou env vars)
- [ ] `requirements.txt` atualizado se adicionou deps
- [ ] `docs/` atualizado (ARCHITECTURE.md se mudou módulos, ROADMAP.md se sprint avançou)
- [ ] Branches `feat/...` ou `fix/...` (não commit direto a `main`)
- [ ] Mensagens de commit seguem convenção
