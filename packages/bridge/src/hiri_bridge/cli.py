from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from hiri_bridge import __version__
from hiri_bridge.adapters import import_from_adapter, list_adapters
from hiri_bridge.adapters.mqtt_pub import MqttDiscoveryPublisher
from hiri_bridge.config import OUT_DIR
from hiri_bridge.devices.registry import DeviceRegistry
from hiri_bridge.devices.types import DOMAINS
from hiri_bridge.ha.discovery import export_discovery

app = typer.Typer(help="HIRI-bridge — Home Assistant smart-home bridge.", no_args_is_help=True)
devices_app = typer.Typer(help="Device registry")
ha_app = typer.Typer(help="Home Assistant helpers")
adapters_app = typer.Typer(help="Bridge adapters")
mqtt_app = typer.Typer(help="MQTT discovery publish")
app.add_typer(devices_app, name="devices")
app.add_typer(ha_app, name="ha")
app.add_typer(adapters_app, name="adapters")
app.add_typer(mqtt_app, name="mqtt")
console = Console()


def _registry() -> DeviceRegistry:
    reg = DeviceRegistry()
    reg.load_or_seed()
    return reg


@app.command("version")
def version_cmd() -> None:
    console.print(f"HIRI-bridge {__version__}")
    console.print(f"Domains: {', '.join(DOMAINS)}")


@app.command("demo")
def demo_cmd() -> None:
    """Seed registry, adapters, MQTT dry-run, export HA discovery pack."""
    reg = _registry()
    stats = reg.stats()
    console.print_json(data=stats)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    disc = export_discovery(reg.list())
    path = OUT_DIR / "discovery.json"
    path.write_text(json.dumps(disc, indent=2) + "\n", encoding="utf-8")
    console.print(f"[green]discovery[/green] {path} ({len(disc)} entities)")
    # sample command
    dev = reg.apply_command(
        "light.living_main",
        "turn_on",
        {"brightness": 180, "effect": "pulse", "color_temp": 350},
    )
    console.print(f"[cyan]command demo[/cyan] {dev.id} → {dev.state}")
    # adapters
    console.print_json(data={"adapters": list_adapters()})
    z2m = import_from_adapter("z2m")
    tuya = import_from_adapter("tuya")
    for d in z2m + tuya:
        reg.upsert(d)
    console.print(f"[cyan]imported[/cyan] z2m={len(z2m)} tuya={len(tuya)} total={reg.stats()['total']}")
    mqtt = MqttDiscoveryPublisher()
    dry = mqtt.publish(reg.list()[:5], dry_run=True)
    console.print(
        f"[cyan]mqtt dry-run[/cyan] {dry.get('count')} msgs · {dry.get('broker')} · {mqtt.status()}"
    )
    console.print("[bold]HIRI bridge demo complete (offline).[/bold]")


@devices_app.command("list")
def devices_list(
    domain: str | None = typer.Option(None, "--domain", "-d"),
    area: str | None = typer.Option(None, "--area", "-a", help="Filter by room/area"),
    online_only: bool = typer.Option(False, "--online", help="Only online devices"),
) -> None:
    reg = _registry()
    table = Table(title="HIRI devices")
    table.add_column("ID")
    table.add_column("Domain")
    table.add_column("Area")
    table.add_column("Name")
    table.add_column("State")
    table.add_column("Adapter")
    n = 0
    for d in reg.list():
        if domain and d.domain != domain:
            continue
        dev_area = getattr(d, "area", None) or (d.attributes or {}).get("area") or ""
        if area and str(dev_area).lower() != area.strip().lower():
            continue
        if online_only and not getattr(d, "online", True):
            continue
        n += 1
        table.add_row(
            d.id,
            d.domain,
            str(dev_area),
            d.name,
            json.dumps(d.state, ensure_ascii=False)[:40],
            d.adapter,
        )
    console.print(table)
    console.print(f"[dim]shown={n}[/dim]")


@devices_app.command("stats")
def devices_stats(
    domain: str | None = typer.Option(None, "--domain", "-d", help="Filter by device domain"),
    area: str | None = typer.Option(None, "--area", "-a", help="Filter by room/area"),
    adapter: str | None = typer.Option(None, "--adapter", help="Filter by adapter"),
) -> None:
    """Domain / area / adapter counts from the registry (offline, no tokens)."""
    reg = _registry()
    by_domain: dict[str, int] = {}
    by_area: dict[str, int] = {}
    by_adapter: dict[str, int] = {}
    online = 0
    total = 0
    for d in reg.list():
        if domain and d.domain != domain:
            continue
        if area:
            dev_area = getattr(d, "area", None) or (d.attributes or {}).get("area") or ""
            if str(dev_area).lower() != area.strip().lower():
                continue
        if adapter and d.adapter != adapter:
            continue
        total += 1
        by_domain[d.domain] = by_domain.get(d.domain, 0) + 1
        dev_area = getattr(d, "area", None) or "unknown"
        by_area[str(dev_area)] = by_area.get(str(dev_area), 0) + 1
        by_adapter[d.adapter] = by_adapter.get(d.adapter, 0) + 1
        if getattr(d, "online", True):
            online += 1
    console.print_json(
        data={
            "total": total,
            "online": online,
            "by_domain": by_domain,
            "by_area": by_area,
            "by_adapter": by_adapter,
        }
    )


@devices_app.command("search")
def devices_search(
    query: str = typer.Argument(..., help="Substring over id/name/area/domain/manufacturer/model"),
    limit: int = typer.Option(30, "--limit", "-n", min=1, max=200),
    manufacturer: str | None = typer.Option(None, "--manufacturer", "-m", help="Filter by manufacturer"),
) -> None:
    """Search devices by id, name, area, domain, manufacturer, or model."""
    q = query.strip().lower()
    reg = _registry()
    table = Table(title=f"Device search: {query}" + (f" mfg={manufacturer}" if manufacturer else ""))
    table.add_column("ID")
    table.add_column("Domain")
    table.add_column("Area")
    table.add_column("Name")
    table.add_column("Manufacturer")
    n = 0
    for d in reg.list():
        if manufacturer and d.manufacturer.lower() != manufacturer.strip().lower():
            continue
        blob = f"{d.id} {d.domain} {d.name} {getattr(d, 'area', '')} {d.manufacturer} {d.model}".lower()
        if q not in blob:
            continue
        table.add_row(d.id, d.domain, str(getattr(d, "area", "")), d.name, d.manufacturer)
        n += 1
        if n >= limit:
            break
    console.print(table)
    console.print(f"[dim]hits={n}[/dim]")


@devices_app.command("cmd")
def devices_cmd(
    device_id: str = typer.Option(..., "--id"),
    action: str = typer.Option(..., "--action", "-a"),
    data: str = typer.Option("{}", "--data"),
) -> None:
    reg = _registry()
    payload = json.loads(data)
    try:
        dev = reg.apply_command(device_id, action, payload)
    except KeyError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc
    console.print_json(data=dev.model_dump())


@devices_app.command("seed")
def devices_seed() -> None:
    reg = DeviceRegistry()
    reg.seed()
    console.print(f"[green]Seeded[/green] {reg.stats()['total']} devices")


@devices_app.command("sim-tick")
def devices_sim_tick() -> None:
    """Advance DHT22/soil sensor simulators and update registry state (offline)."""
    from hiri_bridge.sensors.sim import tick_farm_sensors

    reg = _registry()
    updated = tick_farm_sensors(reg.list())
    reg.save()
    console.print_json(data={"updated": len(updated), "readings": updated[:12]})


@devices_app.command("sim-history")
def devices_sim_history(
    device_id: str = typer.Option(..., "--id"),
    limit: int = typer.Option(10, "--limit", "-n", min=1, max=50),
) -> None:
    """Show recent in-process sensor sim history for a device."""
    from hiri_bridge.sensors.sim import sensor_history, tick_farm_sensors

    reg = _registry()
    # ensure at least one sample exists
    tick_farm_sensors(reg.list())
    rows = sensor_history(device_id, limit=limit)
    console.print_json(data={"id": device_id, "n": len(rows), "history": rows})


@devices_app.command("export")
def devices_export(
    out: Path = typer.Option(..., "--out", "-o", help="Output JSON file path"),
) -> None:
    """Export device registry as a JSON snapshot (no tokens/secrets)."""
    reg = _registry()
    snapshot = [d.model_dump() for d in reg.list()]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
    console.print(f"[green]Wrote[/green] {out} devices={len(snapshot)}")


@ha_app.command("discovery")
def ha_discovery(out: Path | None = typer.Option(None, "--out", "-o")) -> None:
    reg = _registry()
    disc = export_discovery(reg.list())
    path = out or (OUT_DIR / "discovery.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(disc, indent=2) + "\n", encoding="utf-8")
    console.print(f"[green]Wrote[/green] {path} entities={len(disc)}")


@ha_app.command("entity-mapping")
def ha_entity_mapping(
    out: Path | None = typer.Option(None, "--out", "-o"),
) -> None:
    """Export device-to-entity mapping for HA configuration."""
    reg = _registry()
    mapping = {}
    for d in reg.list():
        entity_id = d.id
        mapping[entity_id] = {
            "entity_id": entity_id,
            "name": d.name,
            "domain": d.domain,
            "manufacturer": d.manufacturer,
            "model": d.model,
            "area": d.area,
            "adapter": d.adapter,
            "online": d.online,
        }
    path = out or (OUT_DIR / "entity_mapping.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(mapping, indent=2) + "\n", encoding="utf-8")
    console.print(f"[green]Wrote[/green] {path} devices={len(mapping)}")
    # Show summary
    by_manufacturer: dict[str, int] = {}
    for d in reg.list():
        by_manufacturer[d.manufacturer] = by_manufacturer.get(d.manufacturer, 0) + 1
    console.print(f"[dim]Manufacturers: {json.dumps(by_manufacturer)}[/dim]")


@adapters_app.command("list")
def adapters_list() -> None:
    table = Table(title="HIRI adapters")
    table.add_column("Name")
    table.add_column("Kind")
    table.add_column("Live")
    table.add_column("Status")
    table.add_column("Description")
    for row in list_adapters():
        table.add_row(
            row["name"],
            row["kind"],
            "yes" if row["live"] else "no",
            str(row["status"]),
            row["description"][:48],
        )
    console.print(table)


@adapters_app.command("import")
def adapters_import(
    name: str = typer.Argument(..., help="z2m | tuya | ha_rest"),
) -> None:
    reg = _registry()
    try:
        devices = import_from_adapter(name)
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc
    for d in devices:
        reg.upsert(d)
    console.print(f"[green]Imported[/green] {len(devices)} from {name} · total={reg.stats()['total']}")


@mqtt_app.command("publish")
def mqtt_publish(
    dry_run: bool = typer.Option(True, "--dry-run/--live"),
    host: str | None = typer.Option(None, "--host"),
    port: int | None = typer.Option(None, "--port"),
) -> None:
    """Publish HA MQTT discovery (default dry-run, no broker required)."""
    reg = _registry()
    pub = MqttDiscoveryPublisher(host=host, port=port)
    result = pub.publish(reg.list(), dry_run=dry_run)
    console.print_json(data={k: v for k, v in result.items() if k != "messages"})
    if dry_run and result.get("messages"):
        console.print(f"[dim]sample topics:[/dim] {', '.join(m['topic'] for m in result['messages'][:5])}")


@app.command("serve")
def serve_cmd(
    host: str = typer.Option("127.0.0.1", "--host"),
    port: int = typer.Option(8780, "--port", min=1, max=65535),
) -> None:
    try:
        import uvicorn
    except ImportError as exc:
        console.print('[red]Install API:[/red] pip install -e ".[api]"')
        raise typer.Exit(1) from exc
    console.print(f"HIRI bridge http://{host}:{port}/health")
    console.print("[dim]Optional auth: set HIRI_API_TOKEN for POST protection[/dim]")
    uvicorn.run("hiri_bridge.api:app", host=host, port=port, log_level="info")


if __name__ == "__main__":
    app()
