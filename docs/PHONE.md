# Telefone mãos-livres (HFP) + Contactos (PBAP)

Estado: **funcional e verificado em hardware** (telemóvel Android via Bluetooth).

Permite, a partir do ecrã do carro:

- Receber chamadas com **modal sobre qualquer ecrã** + **identificação do chamador**
  (número e, se estiver nos contactos, o **nome**).
- **Atender / Recusar / Desligar**.
- **Silenciar (mute)** durante a chamada.
- **Marcar** um número no teclado (dialpad).
- Ver a **lista de contactos** do telemóvel (PBAP), na lateral, com **scroll** e
  **barra de pesquisa** (filtra por nome ou número).

---

## Como funciona

O ponto-chave: o **PipeWire** (não o oFono daemon) trata do HFP. Em vez do
backend "native" normal, ligámos a *telephony nativa* do PipeWire, que expõe a
API **compatível `org.ofono`** (`org.ofono.VoiceCallManager` / `VoiceCall`) no
**system bus**. Assim:

```
Telemóvel (HFP-AG)  ──Bluetooth──▶  PipeWire/WirePlumber (HFP-HF, backend native)
                                          │ expõe org.ofono.* (provide-ofono)
                                          ▼
   PhoneService (backend/services/phone.py, python3-dbus, system bus)
                                          │  /phone/status, /answer, /hangup, /dial, /mute
                                          ▼
   Frontend: modal de chamada + dialpad + lista de contactos
```

- **Estado de chamada** entra no `build_status()` → vai no push WebSocket de 1s,
  por isso a chamada aparece sem polling extra (`main.py`).
- **Contactos**: PBAP via **obexd** (`org.bluez.obex`) no **session bus**. O
  backend corre como serviço de sistema, por isso descobre o endereço do session
  bus em runtime (igual ao `playerctl`/Bluetooth — `core/runtime.py`).
- **Nome do chamador**: resolvido por correspondência do número recebido contra a
  cache de contactos (últimos 9 dígitos). O frontend pré-carrega `/phone/contacts`
  no arranque para a cache estar quente.

> Importante: `GetModems`/`GetCalls` do PipeWire devolvem um **dicionário**
> (`a{oa{sv}}`), ao contrário do oFono real (`a(oa{sv})`). O `PhoneService._items`
> aceita os dois.

### Endpoints
`GET /phone/status` · `GET /phone/contacts` · `POST /phone/answer` ·
`POST /phone/hangup` · `POST /phone/dial?number=` · `POST /phone/mute`

---

## Instalação

1. Dependências: `obexd-client`, `python3-dbus` (PipeWire/WirePlumber já presentes).
   **Não** é preciso o daemon oFono.
2. Correr o setup (como utilizador do kiosk, não root):
   ```bash
   bash scripts/phone/setup-hfp.sh
   ```
   Aplica `scripts/phone/51-bluez-ofono.conf` ao WirePlumber, instala a política
   D-Bus que deixa o utilizador possuir `org.ofono`, desliga o oFono daemon se
   existir, e reinicia o WirePlumber.
3. **Religar o Bluetooth no telemóvel** para registar o HFP.
4. Confirmar o modem:
   ```bash
   dbus-send --system --print-reply --dest=org.ofono / org.ofono.Manager.GetModems
   ```
5. **Contactos:** no telemóvel, autorizar "partilhar contactos / acesso à lista
   telefónica" para o dispositivo emparelhado (senão o PBAP falha com OBEX 0x53).

Off-Pi (sem telemóvel/telephony) os endpoints `/phone/*` devolvem
`available: false` sem rebentar.

---

## Limitações conhecidas & próximos TODOs

- [ ] **Mute — confirmar direção.** Hoje silencia `@DEFAULT_AUDIO_SOURCE@` (o
      microfone por defeito). Verificar numa chamada que silencia **o que o outro
      lado ouve**; se silenciar o lado errado, apontar para o nó de captura
      específico ligado ao sink HFP em vez do default.
- [ ] **Áudio SCO** — confirmar que o áudio da chamada sai pelos altifalantes do
      carro e o micro do carro chega ao chamador (volume/eco). O PipeWire native
      encaminha, mas o nível/rota podem precisar de afinação no hardware.
- [ ] **Cache de contactos no `connect`.** Hoje a cache aquece quando o frontend
      pede `/phone/contacts` (arranque + abrir o ecrã). Se uma chamada chegar
      antes disso, o nome não resolve. Puxar a lista quando o telemóvel liga
      (deteção do modem) e/ou guardar em disco.
- [ ] **Reconexão BT frágil.** Religar do lado do Pi falha às vezes com
      `le-connection-abort-by-local` após muitos ciclos; é preciso religar do
      telemóvel. Investigar auto-reconnect fiável.
- [ ] **Polish UI:** duração da chamada em curso, histórico de chamadas,
      estado "a marcar" mais visível na marcação de saída.
- [ ] **PBAP:** refrescar contactos periodicamente; lidar com listas muito
      grandes (hoje renderiza tudo — 500+ contactos é aceitável, mas há margem).

---

## Troubleshooting

| Sintoma | Causa | Resolução |
|---|---|---|
| `/phone/status` → `available:false` com telemóvel ligado | `org.ofono` não registado | confirmar que o WirePlumber possui `org.ofono` (`busctl --system list \| grep ofono`); correr `setup-hfp.sh`; religar telemóvel |
| Sem modem em `GetModems` | HFP não ligou | religar o Bluetooth **no telemóvel** |
| `RegisterProfile ... UUID already registered` (oFono) | oFono daemon a competir | `setup-hfp.sh` desliga-o; confirmar `systemctl is-enabled ofono` = disabled |
| Contactos vazios / OBEX `0x53` | PBAP não autorizado | autorizar partilha de contactos no telemóvel |
| Chamada sem áudio | rota SCO | afinação PipeWire (ver TODOs) |
