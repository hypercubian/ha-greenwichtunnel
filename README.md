# Greenwich Foot Tunnel Lifts — Home Assistant Integration

![Release](https://img.shields.io/github/v/release/hypercubian/ha-greenwichtunnel?include_prereleases)
![License](https://img.shields.io/github/license/hypercubian/ha-greenwichtunnel)
![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5)
![Python](https://img.shields.io/badge/python-3.12+-blue)

Home Assistant custom integration that exposes live community-sourced lift status for the **Greenwich Foot Tunnel** — the pedestrian crossing under the Thames between Island Gardens (north) and Cutty Sark (south).

Data comes from [greenwichlifts.co.uk](https://www.greenwichlifts.co.uk/), a crowdsourced tracker built by Andreas Nikolaou after the council's hardware-based LiftCheck system went offline. Commuters report whether each lift is working as they pass through; this integration polls the same public Supabase backend the website uses and surfaces the latest state to Home Assistant.

## Entities

| Entity | Device class | On = | Attributes |
| --- | --- | --- | --- |
| `binary_sensor.greenwich_foot_tunnel_north_lift` | `running` | Latest report says the lift is functioning | `last_report_at`, `last_report_created`, `report_count_24h`, `availability_pct_24h`, `is_stale` |
| `binary_sensor.greenwich_foot_tunnel_south_lift` | `running` | Latest report says the lift is functioning | (as above) |

- `is_stale` flips to `true` when the most recent report is more than 6 hours old. The binary sensor keeps showing the last known state so your automations have something to react to, but you can branch on the attribute if you want to treat stale data as unknown.
- If no reports have been submitted for a location in the last 24 hours, the entity becomes `unavailable`.

## Installation

### HACS (recommended)

1. In HACS, open **Integrations** → **⋮** → **Custom repositories**.
2. Add `https://github.com/hypercubian/ha-greenwichtunnel` with category **Integration**.
3. Install **Greenwich Foot Tunnel Lifts** and restart Home Assistant.
4. **Settings → Devices & services → Add integration → Greenwich Foot Tunnel Lifts** and press **Submit**. There is no configuration to fill in.

### Manual

Copy `custom_components/greenwich_tunnel` into your Home Assistant `config/custom_components/` directory, restart, and add the integration from the UI.

## How it works

- Polls `https://uhgfgayyfbtjlttescvv.supabase.co/rest/v1/reports` every 5 minutes.
- Requests the last 24 hours of reports in a single call, then aggregates per location.
- The Supabase anon key embedded in the source is the same one the greenwichlifts.co.uk frontend ships to every visitor; it grants only the row-level-security-filtered read access the website already exposes publicly.
- Latest-status decisions use `created_at` (the report submission time), not the user-entered `timestamp`, to protect against clock drift on contributor devices.

## Data quality caveats

- The feed is crowdsourced, not authoritative. A broken lift may go unreported for hours overnight; the first commuter through in the morning will correct it.
- The Royal Borough of Greenwich publishes 30-day availability figures on [its official status page](https://www.royalgreenwich.gov.uk/parking-transport-and-streets/travel-foot-bike-or-public-transport/check-status-foot-tunnels), but it is updated manually and is not live.
- If you need authoritative real-time telemetry, file an FOI with the council (see `foi-request-rbg-lifts.md` in this repo for a template).

## Development

```bash
poetry install
poetry run pre-commit install
poetry run pytest
```

The integration targets Python 3.12+ and matches the pre-commit / mypy-strict / three-tier test layout used across personal projects.

## License

MIT. See [LICENSE](LICENSE).
