# Firmware Flash Safety Checklist

## Pre-Flash Safety Checks

### Hardware Preparation
- [ ] Verify power supply voltage matches ESP board requirements (3.3V or 5V)
- [ ] Ensure stable power source with adequate current capacity (500mA minimum)
- [ ] Check USB cable quality - use data cables, not charge-only cables
- [ ] Confirm proper board selection in IDE/tooling matches physical hardware
- [ ] Inspect GPIO pins for shorts or physical damage
- [ ] Remove all external peripherals and sensors during initial flash

### Software Verification
- [ ] Backup existing firmware before flashing (if applicable)
- [ ] Verify firmware binary integrity (checksum/hash validation)
- [ ] Confirm firmware version compatibility with hardware revision
- [ ] Review partition table matches flash size
- [ ] Test build/compile completes without errors
- [ ] Verify bootloader compatibility

### Connection Safety
- [ ] Use proper serial adapter with correct voltage levels
- [ ] Connect GPIO0 to GND for boot/flash mode (ESP8266/ESP32)
- [ ] Ensure stable physical connection - secure USB port
- [ ] Check device enumeration in system (COM port on Windows, /dev/ttyUSB* on Linux)
- [ ] Verify no other applications accessing serial port

## Flash Process Safety

### During Flash
- [ ] Monitor flash progress - do not interrupt
- [ ] Do not disconnect power or USB during flash operation
- [ ] Watch for error messages or verification failures
- [ ] Ensure adequate ventilation - boards may heat up
- [ ] Keep metal objects and liquids away from board

### Flash Parameters
- [ ] Set correct flash size (4MB, 8MB, 16MB, etc.)
- [ ] Configure proper flash mode (QIO, DIO, DOUT, QOUT)
- [ ] Set appropriate flash frequency (40MHz, 80MHz)
- [ ] Verify baud rate is stable (115200 standard, 921600 for faster flash)

## Security Configuration

### WiFi Security - CRITICAL
- [ ] **NEVER use default WiFi passwords in production firmware**
- [ ] **NEVER hardcode WiFi credentials in source code**
- [ ] Implement WiFi configuration portal for first-time setup
- [ ] Use WPA2/WPA3 encryption - disable WEP/WPA
- [ ] Generate unique device credentials per unit
- [ ] Store WiFi credentials in encrypted flash partition
- [ ] Implement credential rotation capability
- [ ] Add WiFi reset mechanism (button press or factory reset)

### Access Control
- [ ] Change default admin passwords
- [ ] Disable unnecessary services (Telnet, FTP)
- [ ] Enable secure protocols (HTTPS, MQTT with TLS)
- [ ] Implement firmware signature verification
- [ ] Configure OTA update authentication
- [ ] Set secure boot flags if available
- [ ] Disable debug interfaces in production builds

### Network Security
- [ ] Configure firewall rules if applicable
- [ ] Disable WPS (WiFi Protected Setup)
- [ ] Hide SSID broadcast if appropriate
- [ ] Implement MAC address filtering for sensitive deployments
- [ ] Use certificate pinning for critical connections
- [ ] Enable encrypted flash if supported

## Post-Flash Verification

### Functional Testing
- [ ] Verify device boots successfully
- [ ] Check serial output for boot messages and errors
- [ ] Test WiFi connection functionality
- [ ] Verify all GPIO pins function as expected
- [ ] Test OTA update capability
- [ ] Confirm sensor readings (if applicable)
- [ ] Validate network connectivity and services

### Security Validation
- [ ] Confirm no default credentials active
- [ ] Test WiFi configuration portal access
- [ ] Verify encrypted connections (SSL/TLS)
- [ ] Check for open ports (nmap scan)
- [ ] Validate authentication mechanisms
- [ ] Test factory reset functionality

### Documentation
- [ ] Record firmware version flashed
- [ ] Document device MAC address
- [ ] Note any configuration changes
- [ ] Log flash date and time
- [ ] Record any issues encountered
- [ ] Update device inventory/registry

## Recovery Procedures

### If Flash Fails
- [ ] Do not panic - most ESP devices are hard to brick
- [ ] Try re-entering flash mode (GPIO0 to GND, then reset)
- [ ] Reduce baud rate to 115200 or lower
- [ ] Try different USB port or cable
- [ ] Use espressif official flash tools (esptool.py, Flash Download Tool)
- [ ] Attempt flash with minimal partitions first (bootloader only)
- [ ] Check for adequate power supply under load

### Emergency Recovery
- [ ] Use JTAG debugger if available
- [ ] Flash via SD card if board supports it
- [ ] Try factory bootloader restore
- [ ] Consult hardware-specific recovery procedures
- [ ] Contact manufacturer support if hardware failure suspected

## Best Practices

### Development Environment
- Use version control for all firmware code
- Maintain separate development, staging, and production builds
- Implement automated testing before flash
- Keep toolchain and libraries updated
- Document all custom configurations

### Production Deployment
- Flash in controlled environment (ESD protection)
- Batch test firmware on sample devices first
- Maintain firmware version registry
- Implement rollback capability
- Monitor devices post-deployment

### Security Reminders
- ⚠️ **Default WiFi credentials are the #1 IoT security risk**
- ⚠️ **Always change defaults before deployment**
- ⚠️ **Never commit credentials to version control**
- ⚠️ **Use environment variables or secure vaults for secrets**
- ⚠️ **Regularly audit and update security configurations**

## Common Mistakes to Avoid

- ❌ Interrupting flash process
- ❌ Using wrong board configuration
- ❌ Insufficient power supply
- ❌ Flashing without backup
- ❌ Hardcoded WiFi passwords
- ❌ Default admin credentials in production
- ❌ Unencrypted OTA updates
- ❌ No factory reset mechanism
- ❌ Skipping post-flash verification
- ❌ Deploying without security audit

## Resources

### Official Tools
- esptool.py - Official ESP flashing tool
- ESP Flash Download Tool - Windows GUI tool
- PlatformIO - Cross-platform development environment
- Arduino IDE - Beginner-friendly option

### Documentation
- ESP8266 Technical Reference: https://www.espressif.com/en/support/documents/technical-documents
- ESP32 Technical Reference: https://www.espressif.com/en/support/documents/technical-documents
- ESP-IDF Programming Guide: https://docs.espressif.com/projects/esp-idf/

### Security Guidelines
- OWASP IoT Security Guidance
- NIST Cybersecurity Framework
- IoT Security Foundation Best Practices

---

**Remember: Safety first, security always. Taking time to follow this checklist prevents costly mistakes and security vulnerabilities.**