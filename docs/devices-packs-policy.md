# Device Packs Policy

## Append-Only for Device Packs

**Device packs** (in `packages/bridge/data/packs/`) must **append** to the device registry and **never replace** the entire `devices.json`.

## Why Append-Only?

- **Seed devices** live in `data/devices.json` as the canonical baseline
- **Packs** add domain-specific device packs on top of the seed
- Replacing the entire registry would **overwrite** seed devices and user-discovered devices
- Appending preserves the merge chain: `seed → pack1 → pack2 → ...`

## How It Works

The `DeviceRegistry` class merges pack data into the existing registry:

```python
# In src/hiri_bridge/config.py
registry = DeviceRegistry.load(registry_path)
registry.merge_pack(pack_data)  # Appends, not replaces
```

## Creating a Device Pack

1. Create your pack JSON in `packages/bridge/data/packs/<pack-name>.json`
2. Devices in the pack are **merged** into the registry (keyed by `id`)
3. The pack's devices are **appended** to the registry, never overwriting seed devices
4. Run `hiri-bridge devices list` to verify pack devices are visible

## Anti-Truncation Rule

**Never** write a pack file that replaces `devices.json` entirely. The registry expects to be built incrementally:

```
seed devices.json → merged with pack1 → merged with pack2 → ...
```

If a pack replaces the file instead, seed devices and previously merged devices will be **lost**.

## Verification

After creating a pack, verify it doesn't truncate existing devices:

```bash
hiri-bridge devices list | wc -l   # Should show seed + pack devices
```