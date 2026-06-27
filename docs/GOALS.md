# AveoOS — Objetivos

> Este documento define **o quê** e **o porquê**. O **quando** vive em [`ROADMAP.md`](ROADMAP.md), e o **como** em [`ARCHITECTURE.md`](ARCHITECTURE.md).

---

## Visão

AveoOS é um sistema de infotainment automóvel construído para Raspberry Pi 4 destinado ao Chevrolet Aveo 1.2 2009.

O objetivo não é criar um clone de Android Auto, mas sim uma plataforma modular, rápida e fiável para:

- Reprodução de música por Bluetooth
- Controlo multimédia touchscreen
- Integração com smartphone
- Navegação futura
- Gestão inteligente de energia
- Interface otimizada para condução

O sistema deve arrancar automaticamente com o veículo, desligar de forma segura e apresentar uma experiência semelhante a uma head unit OEM.

---

## Objetivos da V1

### Funcionais

- Interface touchscreen fullscreen
- Ligação Bluetooth automática
- Reprodução de áudio Bluetooth A2DP
- Controlo multimédia AVRCP
- Mostrar:
  - Música atual
  - Artista
  - Estado Bluetooth
  - Hora
- Gestão de energia básica
- Shutdown seguro

### Não Funcionais

- Arranque inferior a 15 segundos
- Interface fluida
- Sem dependência de internet (capa do álbum Spotify é a única exceção intencional na V1)
- Totalmente operável offline em tudo o resto
- Recuperação automática após falha elétrica

---

## Arquitetura (alto nível)

### Sistema Operativo

Raspberry Pi OS Lite.

Motivos:

- Menor consumo de recursos
- Maior velocidade de boot
- Maior estabilidade (sem camada gráfica nativa)

---

### Backend

**Linguagem:** Python 3.12+
**Framework:** FastAPI

Responsabilidades:

- Bluetooth Manager
- Media Manager
- GPS Manager (futuro)
- Power Manager
- System Monitor
- API REST
- WebSocket (eventos em tempo real)

Módulos detalhados: [`ARCHITECTURE.md`](ARCHITECTURE.md).

---

### Frontend

Tecnologias:

- HTML5
- CSS3
- JavaScript

**Sem React na V1.** Cada ecrã é uma página HTML leve, estilizada por CSS partilhado, e ligada ao backend via fetch + WebSocket.

A motivação para manter vanilla:

- Simplicidade
- Menor consumo de recursos
- Menor tempo de desenvolvimento
- Sem build step — mais fácil de iterar e debugar diretamente no Pi

---

### Comunicação

REST + WebSocket.

Fluxo:

```
Bluetooth/Sistema Event → Backend → WebSocket → Interface atualizada
                                  ↘ REST (fallback, comandos)
```

---

## Filosofia de Desenvolvimento

Cada módulo deve funcionar isoladamente.

Nenhum módulo pode depender diretamente de outro.

**Toda a comunicação deve passar pelo backend central.**

Objetivo:

- Facilidade de manutenção
- Testes unitários possíveis sem mock infrastructure
- Substituir ou remover um módulo não exige mexer nos outros
- Futuras expansões (GPS, OBD2, clima) encaixam sem refactor do core

---

## Critérios de Sucesso

A experiência alvo:

1. O utilizador entra no carro
2. Liga a ignição
3. O sistema arranca em menos de 15 segundos
4. O telemóvel conecta automaticamente via Bluetooth
5. A música continua a tocar de onde parou
6. A interface apresenta:
   - Hora
   - Estado Bluetooth
   - Música atual (título, artista, capa)
7. Sem necessidade de qualquer interação manual

---