# Firmware Flash Safety Checklist

## Before Flashing

1. **Backup current firmware** — Use `esptool.py read_flash`
2. **Verify firmware hash** — Check SHA256 matches expected
3. **Check USB connection** — Stable cable, no hubs
4. **Close serial monitors** — Release COM port

## During Flash

1. **Hold BOOT button** when prompted
2. **Do not disconnect** during transfer
3. **Watch for errors** in terminal output
4. **Verify progress** reaches 100%

## After Flash

1. **Reset device** — Press RST button
2. **Check serial output** — Verify boot messages
3. **Test WiFi** — Never use default credentials
4. **Change default passwords** — Immediate priority

## Common Mistakes

| Mistake | Risk | Solution |
|---------|------|----------|
| Wrong baud rate | Corrupted flash | Use 115200 or 921600 |
| Bad USB cable | Transfer failure | Use data cable, not charge-only |
| Missing drivers | Device not found | Install CP2102/CH340 drivers |
| Power during flash | Bricked device | Ensure stable power supply |

## WiFi Security

- **Never** hardcode WiFi passwords in firmware
- Use environment variables or config files
- Implement OTA updates with signing
- Rotate credentials regularly
