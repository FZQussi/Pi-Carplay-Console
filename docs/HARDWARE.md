# AveoOS — Hardware & Wiring

> Componentes, pinout e considerações de integração no carro. Para o software, ver [`ARCHITECTURE.md`](ARCHITECTURE.md). Para o procedimento de instalação no Pi, ver [`INSTALL.md`](INSTALL.md).

> **Aviso:** trabalhar com a elétrica de um carro implica risco de curto-circuito e danos na bateria. Desligar o terminal negativo da bateria antes de mexer em cablagens não relacionadas com o circuito ACC. Em caso de dúvida, consultar um instalador profissional.

---

## 1. Lista de componentes (BOM)

| Componente | Especificação | Notas |
|------------|--------------|-------|
| **Raspberry Pi 4** | 2 GB RAM (mínimo), 4 GB recomendado | O Pi 3 também funciona mas é mais lento. Pi 5 não testado ainda |
| **Alimentação do Pi** | Conversor DC-DC 12V → 5V/3A+, low-noise | Algo como o Mean Well RSDW20UW-5 ou conversor automotivo dedicado para Pi. NÃO usar carregadores de telemóvel genéricos — falham no arranque do carro |
| **Ecrã tátil 7"** | HDMI + USB touch (genérico) **ou** DSI oficial | A oficial dá-se melhor com o Pi, mas a genérica HDMI dá mais flexibilidade |
| **DAC** | HiFiBerry DAC+ standard **ou** USB DAC | DAC+ funciona via GPIO (HAT); escolher um **não-plus** se também usar sensor ACC nesses pinos |
| **Módulo Bluetooth** | Built-in no Pi 4 | Suficiente para A2DP/AVRCP |
| **Sensor ACC** | Cabo + divisor resistivo 12V→3.3V → GPIO | Ver secção 3 |
| **Botões físicos (opcional, V2)** | 4-6 botões momentâneos → GPIO | Vol+, Vol-, Source, Power |
| **Cabos de áudio** | 3.5 mm → AUX do carro **ou** RCA → amp do carro | Ligar à entrada AUX existente |
| **Fusíveis inline** | 5A + 3A | Um na linha 12V principal, outro na linha do Pi |
| **Filtro de ruído** | Capacitor de filtro EMI na linha 12V | Crítico para isolar picos do alternador |
| **Housing/case** | Custom impresso em 3D **ou** caixa genérica | Montar por trás do ecrã, ventilado |

---

## 2. Diagrama de wiring (texto)

```
[Bateria 12V]
     │
     ├──[Fusível 5A]──[Filtro EMI]──┬── ACC (sino da ignição)
     │                              │
     │                          [Conversor DC-DC 12V→5V/3A]
     │                              │
     │                              └─[RPi 4 5V input]
     │
     └──[GND chassis] ────────────────────────[RPi GND]────[DAC GND]────[Sensor ACC GND]

[ACC 12V] ── [Divisor resistivo R1=20kΩ, R2=10kΩ] ── [GPIO17 (RPi)]
                                                         │
                                                    [GND RPi]

[Botão Power (opcional)] ── [GPIO27 (RPi)] ── [GND RPi]
   (pull-up interno habilitado)

[Saída DAC L/R] ── [AUX 3.5mm/RCA] ── [Entrada AUX do carro ou amp externo]
```

---

## 3. Sensor ACC em detalhe

### O que queremos detetar

O pino **ACC** (accessory) do carro está a 12V quando a chave de ignição está em *ACC/IGN* e a 0V quando está em *OFF*. Isto permite ao AveoOS:

- Arrancar o Pi quando se liga a ignição
- Saber quando se desliga para fazer shutdown limpo

### Circuito recomendado

```
+12V ACC ──┬── R1 20kΩ ──┬── GPIO17 ──┬── R2 10kΩ ── GND
           │             │            │
           │       (Pi input)          │
           │                           
        (filtro)
```

- **R1 + R2** fazem um divisor: 12V × 10/(20+10) = 4V. Segura usando um *clamp diode* ou um *zener 3.3V* entre GPIO17 e GND para evitar sobretensão.
- **Filtro**: capacitor cerâmico 100 nF em paralelo com R2 para absorver picos do alternador.
- **GPIO17** é escolhido por estar perto dos pinos de 3.3V e GND no header (BCM pin 11).

> ⚠️ Sem divisor, queimas a GPIO em poucos segundos. Sem zener, picos do alternador (>30V nos arranques a frio) também podem queimar.

### Cabo prático

- Fio AWG 22 sinal (vermelho, identificado como "ACC")
- Blindagem recomendada se o cabo for longo (>1 m)
- Conector rápido tipo posi-tap ou splice soldado para ligação ao chicote do carro

---

## 4. Pinout do Raspberry Pi (BCM)

Pinos relevantes usados pelo AveoOS V1:

| Função | BCM GPIO | Pin físico | Notas |
|--------|---------:|----------:|-------|
| ACC input | GPIO17 | Pin 11 | Com divisor 12V→3.3V; pull-down interno |
| DAC HAT I²S (V1) | — | Pinos 12, 35, 40, 38 | Se usar HiFiBerry DAC+ standard |
| Botão power (V2) | GPIO27 | Pin 13 | Pull-up interno; GND no outro terminal |
| Vol+ / Vol− (V2) | GPIO23 / GPIO24 | Pin 16 / Pin 18 | |
| Source (V2) | GPIO22 | Pin 15 | |

Para referência completa, consultar <https://pinout.xyz>.

---

## 5. Considerações de instalação no carro

### Ruído elétrico

O alternador e os relés do carro geram picos que quebram eletrónica:

- **Filtro EMI** na entrada 12V — não dispensável
- **Toroid** em volta dos cabos de áudio se a fonte de ruído for muito forte (raro)
- **Chassis como GND** — não usar massa de outro componente, ligar diretamente à bateria ou bom chassi

### Vibração e temperatura

- **Cartão SD**: SSDs/módulos eMMC são preferíveis em ambientes com muita vibração. Alternativa ao SD: boot por USB SSD.
- **Temperatura**: o Pi 4 throttle acima de 80 °C. Dispor o dissipador e fluxo de ar. Evitar exposição solar direta no ecrã.

### Fonte de alimentação

Um conversor DC-DC 12V → 5V dedicado é **muito** preferível a um carregador 12V USB genérico. Procurar:

- Tensão de saída regulada ±5%
- Corrente contínua ≥ 3 A (sem queda em cold start)
- Proteções: curto-circuito, inversão de polaridade, sobreaquecimento
- **Soft-start** — alguns conversores arrancam em rampa, o que protege o Pi

### Fusíveis

- **Sempre** um fusível inline na linha 12V (5 A ou menos consoante o conversor)
- Fusível de backup na linha ACC
- **Nunca** confiar em fusíveis OEM do carro sem verificar a posição e amperagem

### Onde montar

Sugestões:

- Por trás do ecrã (se o ecrã suportar)
- No lugar do rádio original, ocupando o slot
- No porta-luvas com extensão de cabos (mais simples para desenvolvimento)

---

## 6. Cabos e conetores úteis

- **Posi-tap** — ligação rápida no chicote sem cortar fio
- **Wago 221** — para ligações pontuais até 5A
- **Terminais tipo "AMP/Tyco"** — se ligar a chicote OEM do carro (rádio original)

---

## 7. Próximas revisões

- Esquemático em KiCad (V2)
- Diagrama Fritzing do wiring (V2)
- Plano de pinout oficial para V2.3 (OBD2, climatização, etc.)

---

## Ver também

- [`INSTALL.md`](INSTALL.md) — passo-a-passo da configuração do software no Pi
- [`ROADMAP.md`](ROADMAP.md) — quando cada componente de hardware será integrado
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — como o software usa este hardware
