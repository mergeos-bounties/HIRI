import { execSync } from 'node:child_process';
import { mkdtempSync, writeFileSync, rmSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';

const REPO = 'mergeos-bounties/HIRI';

function sh(cmd) {
  return execSync(cmd, { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] }).trim();
}

function ensureLabel(name, color, description) {
  try {
    sh(`gh label create ${JSON.stringify(name)} --repo ${REPO} --color ${color} --description ${JSON.stringify(description)}`);
  } catch {
    try {
      sh(`gh label edit ${JSON.stringify(name)} --repo ${REPO} --color ${color} --description ${JSON.stringify(description)}`);
    } catch { /* ignore */ }
  }
}

function createIssue(title, body, labels) {
  const dir = mkdtempSync(join(tmpdir(), 'hiri-issue-'));
  const file = join(dir, 'body.md');
  try {
    writeFileSync(file, body, 'utf8');
    const labelFlags = labels.map((l) => `--label ${JSON.stringify(l)}`).join(' ');
    console.log(sh(`gh issue create --repo ${REPO} --title ${JSON.stringify(title)} --body-file ${JSON.stringify(file)} ${labelFlags}`));
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
}

for (const row of [
  ['bounty', '5319E7', 'Eligible for MergeOS MRG bounty'],
  ['bounty: feature', 'A2EEEF', 'Feature bounty'],
  ['bridge', '1D76DB', 'HIRI-bridge work'],
  ['firmware', 'D93F0B', 'ESP32/ESP8266 firmware'],
  ['web', '0E8A16', 'HIRI-web'],
  ['admin', 'FBCA04', 'HIRI-admin'],
  ['android', 'A2EEEF', 'HIRI-android'],
  ['ios', 'BFD4F2', 'HIRI-ios'],
  ['ha', '5319E7', 'Home Assistant integration'],
  ['mqtt', 'C5DEF5', 'MQTT'],
  ['reward:25-mrg', 'FEF2C0', '25 MRG'],
  ['reward:50-mrg', 'FEF2C0', '50 MRG'],
  ['reward:100-mrg', 'FEF2C0', '100 MRG'],
  ['reward:200-mrg', 'FEF2C0', '200 MRG'],
  ['good first issue', '7057FF', 'Good first issue'],
  ['documentation', '0075CA', 'Docs'],
  ['device-pack', 'BFDADC', 'Per-device-type pack'],
]) ensureLabel(...row);

const footer = `

## Claim

1. Follow https://github.com/mergeos-bounties  
2. Star https://github.com/mergeos-bounties/mergeos  
3. Star https://github.com/mergeos-bounties/mergeos-contracts
4. Comment: \`I claim this bounty\`  
5. MergeOS [Claim #1](https://github.com/mergeos-bounties/mergeos/issues/1) with issue link  
6. PR to **HIRI** with \`Fixes #<n>\`

Policy: [docs/BOUNTY.md](../blob/master/docs/BOUNTY.md)
`;

const issues = [
  { title: '[25 MRG] Docs: HA MQTT discovery setup guide', labels: ['bounty', 'bounty: feature', 'documentation', 'ha', 'reward:25-mrg', 'good first issue'],
    body: `## 25 MRG\n\nWrite docs/HA_SETUP.md: Mosquitto + discovery prefix + import flow.\n\n## Acceptance\n- [ ] Doc + README link\n${footer}` },
  { title: '[25 MRG] Bridge: hiri-bridge adapters list CLI', labels: ['bounty', 'bounty: feature', 'bridge', 'reward:25-mrg', 'good first issue'],
    body: `## 25 MRG\n\nCLI \`hiri-bridge adapters list\` showing local/mqtt/ha_rest/z2m stubs.\n\n## Acceptance\n- [ ] Command + test\n${footer}` },
  { title: '[50 MRG] Bridge: live MQTT publish discovery (paho optional extra)', labels: ['bounty', 'bounty: feature', 'bridge', 'mqtt', 'ha', 'reward:50-mrg'],
    body: `## 50 MRG\n\nOptional mqtt extra: connect broker and publish discovery + state.\n\n## Acceptance\n- [ ] Works with docker mosquitto in docs\n- [ ] Offline tests mock client\n${footer}` },
  { title: '[50 MRG] Bridge: Zigbee2MQTT adapter (read devices from z2m API)', labels: ['bounty', 'bounty: feature', 'bridge', 'reward:50-mrg'],
    body: `## 50 MRG\n\nAdapter under adapters/z2m.py importing devices into registry.\n\n## Acceptance\n- [ ] Fixture-based tests\n${footer}` },
  { title: '[50 MRG] Bridge: Tuya cloud/local adapter stub + mapping table', labels: ['bounty', 'bounty: feature', 'bridge', 'reward:50-mrg'],
    body: `## 50 MRG\n\nDocumented adapter interface + offline stub.\n\n## Acceptance\n- [ ] Module + tests\n${footer}` },
  { title: '[100 MRG] Bridge: Home Assistant WebSocket event stream', labels: ['bounty', 'bounty: feature', 'bridge', 'ha', 'reward:100-mrg'],
    body: `## 100 MRG\n\nSubscribe HA WS events, sync state into registry.\n\n## Acceptance\n- [ ] Optional live mode + mocked tests\n${footer}` },
  { title: '[100 MRG] Bridge: Matter adapter research + scaffold', labels: ['bounty', 'bounty: feature', 'bridge', 'reward:100-mrg'],
    body: `## 100 MRG\n\nMatter bridge direction doc + code scaffold.\n\n## Acceptance\n- [ ] docs/MATTER.md + package stub\n${footer}` },
  { title: '[50 MRG] Firmware: real DHT22 / soil ADC drivers', labels: ['bounty', 'bounty: feature', 'firmware', 'reward:50-mrg'],
    body: `## 50 MRG\n\nReplace simulated sensors with drivers; keep sim fallback.\n\n## Acceptance\n- [ ] Build on esp32dev\n- [ ] Compile notes in PR\n${footer}` },
  { title: '[50 MRG] Firmware: deep sleep + battery reporting', labels: ['bounty', 'bounty: feature', 'firmware', 'reward:50-mrg'],
    body: `## 50 MRG\n\nLow-power farm node mode.\n\n## Acceptance\n- [ ] Config flags + docs\n${footer}` },
  { title: '[100 MRG] Firmware: OTA updates via MQTT/HTTP', labels: ['bounty', 'bounty: feature', 'firmware', 'reward:100-mrg'],
    body: `## 100 MRG\n\nSafe OTA path for ESP32.\n\n## Acceptance\n- [ ] Documented flash/OTA flow\n${footer}` },
  { title: '[50 MRG] Firmware: TLS MQTT (optional)', labels: ['bounty', 'bounty: feature', 'firmware', 'mqtt', 'reward:50-mrg'],
    body: `## 50 MRG\n\nSecure MQTT for production HA.\n\n## Acceptance\n- [ ] Build flag + README\n${footer}` },
  { title: '[50 MRG] Web: room/area grouping + search', labels: ['bounty', 'bounty: feature', 'web', 'reward:50-mrg'],
    body: `## 50 MRG\n\nImprove packages/web dashboard UX.\n\n## Acceptance\n- [ ] Screenshots desktop+mobile\n${footer}` },
  { title: '[50 MRG] Admin: adapter status page + config form', labels: ['bounty', 'bounty: feature', 'admin', 'reward:50-mrg'],
    body: `## 50 MRG\n\nAdmin UI for HA URL/token (store locally only).\n\n## Acceptance\n- [ ] Screenshots + no secrets committed\n${footer}` },
  { title: '[100 MRG] Android: Compose device list + light control', labels: ['bounty', 'bounty: feature', 'android', 'reward:100-mrg'],
    body: `## 100 MRG\n\nImplement packages/android against bridge API.\n\n## Acceptance\n- [ ] Screenshots emulator\n- [ ] README build steps\n${footer}` },
  { title: '[100 MRG] iOS: SwiftUI device list + switch control', labels: ['bounty', 'bounty: feature', 'ios', 'reward:100-mrg'],
    body: `## 100 MRG\n\nImplement packages/ios against bridge API.\n\n## Acceptance\n- [ ] Screenshots simulator\n${footer}` },
  { title: '[200 MRG] End-to-end: ESP firmware + bridge + HA discovery video', labels: ['bounty', 'bounty: feature', 'firmware', 'bridge', 'ha', 'reward:200-mrg'],
    body: `## 200 MRG\n\nDocumented E2E path with evidence video/screenshots.\n\n## Acceptance\n- [ ] Evidence + reproducible steps\n${footer}` },
  { title: '[25 MRG] CONTRIBUTING.md monorepo layout', labels: ['bounty', 'bounty: feature', 'documentation', 'reward:25-mrg', 'good first issue'],
    body: `## 25 MRG\n\nHow to work on bridge/firmware/web packages.\n\n## Acceptance\n- [ ] File + README link\n${footer}` },
  { title: '[25 MRG] CI: cache pip + optional firmware compile job', labels: ['bounty', 'bounty: feature', 'firmware', 'reward:25-mrg', 'good first issue'],
    body: `## 25 MRG\n\nImprove .github/workflows/ci.yml.\n\n## Acceptance\n- [ ] CI green\n${footer}` },
  { title: '[50 MRG] Bridge: auth token for admin API', labels: ['bounty', 'bounty: feature', 'bridge', 'admin', 'reward:50-mrg'],
    body: `## 50 MRG\n\nOptional API key middleware.\n\n## Acceptance\n- [ ] Tests with/without key\n${footer}` },
  { title: '[50 MRG] Web + Admin: Vietnamese UI strings', labels: ['bounty', 'bounty: feature', 'web', 'admin', 'reward:50-mrg'],
    body: `## 50 MRG\n\ni18n VI for dashboards.\n\n## Acceptance\n- [ ] Screenshots\n${footer}` },
];

// Per-domain device packs (bridge coverage)
const domains = [
  ['light', 'RGB / CT / effects'],
  ['switch', 'multi-gang relay'],
  ['binary_sensor', 'door/window/motion/leak'],
  ['sensor', 'PM2.5 / CO2 / energy'],
  ['climate', 'thermostat presets'],
  ['cover', 'tilt blinds'],
  ['lock', 'PIN / door codes stub'],
  ['fan', 'preset modes'],
  ['media_player', 'source list'],
  ['vacuum', 'room cleaning map stub'],
  ['camera', 'snapshot URL'],
  ['button', 'double/long press'],
  ['number', 'calibration min/max'],
  ['select', 'scene modes'],
  ['siren', 'tones'],
  ['humidifier', 'modes'],
  ['water_heater', 'away mode'],
  ['alarm_control_panel', 'code required'],
];

for (const [domain, note] of domains) {
  issues.push({
    title: `[25 MRG] Device pack: \`${domain}\` — ${note}`,
    labels: ['bounty', 'bounty: feature', 'bridge', 'device-pack', 'ha', 'reward:25-mrg', 'good first issue'],
    body: `## 25 MRG — device domain pack

Expand **${domain}** support in HIRI-bridge.

### Deliver
1. Seed devices or richer state machine in \`packages/bridge\`
2. HA discovery fields for ${domain} (${note})
3. Command coverage + unit tests
4. Note in README domains table

### Acceptance
- [ ] Tests pass
- [ ] \`hiri-bridge ha discovery\` includes ${domain}
- [ ] Web can show the device when bridge is running
${footer}`,
  });
}

for (const issue of issues) {
  createIssue(issue.title, issue.body, issue.labels);
}
console.log(`Created ${issues.length} issues on ${REPO}`);
