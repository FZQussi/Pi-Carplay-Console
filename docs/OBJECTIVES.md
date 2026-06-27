# Projeto: AveoOS

## Visão

AveoOS é um sistema de infotainment automóvel construído para Raspberry Pi 4 destinado ao Chevrolet Aveo 1.2 2009.

O objetivo não é criar um clone de Android Auto, mas sim uma plataforma modular, rápida e fiável para:

* Reprodução de música por Bluetooth
* Controlo multimédia touchscreen
* Integração com smartphone
* Navegação futura
* Gestão inteligente de energia
* Interface otimizada para condução

O sistema deve arrancar automaticamente com o veículo, desligar de forma segura e apresentar uma experiência semelhante a uma head unit OEM.

---

# Objetivos da V1

## Funcionais

* Interface touchscreen fullscreen
* Ligação Bluetooth automática
* Reprodução de áudio Bluetooth A2DP
* Controlo multimédia AVRCP
* Mostrar:

  * música atual
  * artista
  * estado Bluetooth
  * hora
* Gestão de energia básica
* Shutdown seguro

## Não Funcionais

* Arranque inferior a 15 segundos
* Interface fluida
* Sem dependência de internet
* Totalmente operável offline
* Recuperação automática após falha elétrica

---

# Arquitetura

## Sistema Operativo

Raspberry Pi OS Lite

Motivos:

* menor consumo
* maior velocidade
* maior estabilidade

---

## Backend

Python 3.12+

Framework:

FastAPI

Responsabilidades:

* Bluetooth Manager
* Media Manager
* GPS Manager (futuro)
* Power Manager
* System Monitor
* API REST
* WebSocket

---

## Frontend

Tecnologias:

* HTML5
* CSS3
* JavaScript

Sem React na V1.

Motivos:

* simplicidade
* menor consumo de recursos
* menor tempo de desenvolvimento

---

## Comunicação

WebSocket

Fluxo:

Bluetooth Event
→ Backend
→ WebSocket
→ Interface Atualizada

---

# Estrutura do Projeto

```
aveo-os/

backend/
├── main.py
├── bluetooth/
├── power/
├── system/
├── services/

frontend/
├── index.html
├── music.html
├── settings.html
├── assets/
├── css/
├── js/

docs/

scripts/

tests/

requirements.txt

README.md
```

---

# Roadmap

## Sprint 1

Infraestrutura

Objetivos:

* Configurar Raspberry
* Configurar Git
* Configurar FastAPI
* Configurar Chromium Kiosk

Entregável:

Dashboard visível no touchscreen.

---

## Sprint 2

Bluetooth

Objetivos:

* Pairing
* Auto reconnect
* Estado da ligação

Entregável:

Telemóvel liga automaticamente.

---

## Sprint 3

Metadata

Objetivos:

* Música atual
* Artista
* Álbum
* Capa

Entregável:

Player funcional.

---

## Sprint 4

Controlo multimédia

Objetivos:

* Play
* Pause
* Next
* Previous

Entregável:

Controlo completo do Spotify.

---

## Sprint 5

Power Manager

Objetivos:

* Deteção ACC
* Shutdown seguro

Entregável:

Integração automóvel básica.

---

# Filosofia de Desenvolvimento

Cada módulo deve funcionar isoladamente.

Nenhum módulo pode depender diretamente de outro.

Toda a comunicação deve passar pelo backend central.

Objetivo:

Facilidade de manutenção e futuras expansões.

---

# Critérios de Sucesso

O utilizador entra no carro.

Liga a ignição.

O sistema arranca.

O telemóvel conecta automaticamente.

A música continua a tocar.

A interface apresenta:

* Hora
* Estado Bluetooth
* Música atual

Sem necessidade de qualquer interação manual.
