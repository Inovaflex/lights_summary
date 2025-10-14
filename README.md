# My Home Assistant Integration
Custom integration for Home Assistant

# Installation

Copy the 'lights_summary' folder to your custom_components directory in Home Assistant.
Restart Home Assistant

Credits
Author: Tomas Haglund

# 💡 Lights Summary Integration for Home Assistant

### Overview
The **Lights Summary** custom integration creates smart summary sensors that monitor all devices in a specific **area** with a given **label** (for example, `Lights`).  
Each summary sensor shows how many lights or switches in that area are currently **on**, and updates in real time whenever a device changes state.

---

## 🧭 Features

### 🏠 Area-Based Scanning
- Monitors only the selected **area** (e.g. *Bedroom*, *Living Room*, *Kitchen*).
- Ignores devices from all other areas automatically.

### 🏷️ Label Filtering
- Only includes devices that have a specific **label** (e.g. *Lights*, *Fans*, *Outlets*).
- Labels are read directly from the **device registry** — entities don’t need labels.
- Label matching is **case-insensitive** (`Lights`, `lights`, or `LIGHTS` all match).

### 💡 Domain Filtering
- Supports the following domains:
  - `light`
  - `switch`
- Entities from other domains (sensors, media players, covers, etc.) are ignored.

### ⚙️ Entity State Tracking
- For all labeled devices in the area:
  - Counts **how many supported entities exist**.
  - Counts **how many are ON**.
- Displays a clean summary like:
 Lights on: 2 of 5
  or
  All Lights Off


### ⚡ Real-Time Updates
- Updates **instantly** when any included light or switch changes state.
- Uses the Home Assistant event bus (`state_changed`) — no polling required.

### 🪪 Sensor Attributes
Each summary sensor provides detailed attributes:

| Attribute | Description |
|------------|--------------|
| `label` | The label name being tracked |
| `status` | `on`, `off`, or `unknown` |
| `entities_on` | Number of entities currently ON |
| `entities_total` | Total number of entities included |
| `entity_list` | List of all included entity IDs |

### 🧩 Multiple Sensors
- Create one summary per **area + label** combination.
- Example:
- `Living Room Lights Summary`
- `Bedroom Lights Summary`

---

## 🧠 Technical Details
- Reads **device labels** and **area assignments** from Home Assistant’s registries:
- `device_registry.async_get`
- `area_registry.async_get`
- `entity_registry.async_get`
- Matching is case-insensitive for simplicity.
- No scheduled polling — completely **event-driven**.
- Logging:
- **Debug**: discovery and internal scanning details.
- **Info**: logs when devices change state (e.g., light turned ON).

---

## 🪞 Example Dashboard Display

| Area | Label | Example State | Example Attributes |
|------|--------|----------------|--------------------|
| Bedroom | Lights | `Lights on: 1 of 3` | `status: on`, `entities_on: 1`, `entities_total: 3` |
| Living Room | Lights | `All Lights Off` | `status: off`, `entities_on: 0`, `entities_total: 4` |

---

## 💬 Example Use Cases
- **Dashboard summary:** show how many lights are on in each room.
- **Automation trigger:**  
- “If all Bedroom lights are off → turn off the power outlet.”
- “If any ‘Lights’ are on after midnight → send a notification.”

---

## ⚙️ Configuration
1. Copy the integration into `config/custom_components/lights_summary/`.
2. Restart Home Assistant.
3. Add the integration via **Settings → Devices & Services → Add Integration → Lights Summary**.
4. Choose:
 - **Area** (e.g. *Bedroom*)
 - **Label** (e.g. *Lights*)

A new sensor will be created with the name:  
Bedroom Lights Summary


---

## 🧩 Files

| File | Purpose |
|------|----------|
| `__init__.py` | Integration setup |
| `manifest.json` | Metadata for Home Assistant |
| `config_flow.py` | User setup form for area and label |
| `sensor.py` | Core logic for summary sensor |
| `const.py` | Constants (e.g. supported domains) |

---

## 🧱 Constants
```python
SUPPORTED_DOMAINS = ["light", "switch"]
To add support for more entity types (e.g. fan, cover), just modify this list.

Example Automation:
alias: Notify if lights left on
trigger:
  - platform: state
    entity_id: sensor.bedroom_lights_summary
    to: "on"
condition: []
action:
  - service: notify.mobile_app_phone
    data:
      message: "Bedroom lights are still on!"
mode: single

🧩 Credits

Created for Home Assistant 2025.10+
Author: Tomas Haglund
