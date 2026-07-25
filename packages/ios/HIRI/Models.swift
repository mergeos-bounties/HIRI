import Foundation

// MARK: - Device Model (matches HIRI-bridge REST API)

struct Device: Codable, Identifiable, Equatable {
    let id: String
    var name: String
    var domain: String
    var manufacturer: String
    var model: String
    var area: String
    var online: Bool
    var state: [String: JSONValue]
    var attributes: [String: JSONValue]
    var adapter: String

    var domainIcon: String {
        switch domain {
        case "light": return "lightbulb.fill"
        case "switch": return "switch.2"
        case "binary_sensor": return "sensor.fill"
        case "sensor": return "gauge"
        case "climate": return "thermometer"
        case "cover": return "blinds.horizontal.open"
        case "lock": return "lock.fill"
        case "fan": return "fan.fill"
        case "media_player": return "tv.fill"
        case "vacuum": return "vacuum.fill"
        case "camera": return "video.fill"
        case "button": return "circle.circle.fill"
        case "number": return "number"
        case "select": return "list.bullet"
        case "siren": return "bell.fill"
        case "humidifier": return "humidity.fill"
        case "water_heater": return "drop.fill"
        case "alarm_control_panel": return "shield.fill"
        default: return "questionmark.circle.fill"
        }
    }

    var domainColor: String {
        switch domain {
        case "light": return "FFD60A"
        case "switch": return "30D158"
        case "binary_sensor": return "64D2FF"
        case "sensor": return "BF5AF2"
        case "climate": return "FF9F0A"
        case "cover": return "8E8E93"
        case "lock": return "FF453A"
        default: return "AEAEB2"
        }
    }

    var isOn: Bool {
        state["state"]?.stringValue == "on"
    }

    var brightness: Double {
        if let b = state["brightness"]?.doubleValue {
            return b / 255.0 * 100.0
        }
        return 0
    }

    var friendlyState: String {
        if let stateStr = state["state"]?.stringValue {
            return stateStr.replacingOccurrences(of: "_", with: " ").capitalized
        }
        return "Unknown"
    }

    var areaName: String {
        area.replacingOccurrences(of: "_", with: " ").capitalized
    }
}

// MARK: - JSON Value (handles mixed types from bridge API)

enum JSONValue: Codable, Equatable {
    case string(String)
    case number(Double)
    case bool(Bool)
    case null

    var stringValue: String? {
        if case .string(let s) = self { return s }
        return nil
    }

    var doubleValue: Double? {
        if case .number(let d) = self { return d }
        return nil
    }

    var boolValue: Bool? {
        if case .bool(let b) = self { return b }
        return nil
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        if let str = try? container.decode(String.self) {
            self = .string(str)
        } else if let num = try? container.decode(Double.self) {
            self = .number(num)
        } else if let bool = try? container.decode(Bool.self) {
            self = .bool(bool)
        } else {
            self = .null
        }
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        switch self {
        case .string(let s): try container.encode(s)
        case .number(let n): try container.encode(n)
        case .bool(let b): try container.encode(b)
        case .null: try container.encodeNil()
        }
    }
}

// MARK: - Command Request

struct CommandRequest: Codable {
    let action: String
    let data: [String: JSONValue]?

    init(action: String, data: [String: JSONValue]? = nil) {
        self.action = action
        self.data = data
    }
}

// MARK: - Health Response

struct HealthResponse: Codable {
    let ok: Bool
    let service: String
    let version: String
    let domains: [String]
    let authRequired: Bool
    let adapters: [String]

    enum CodingKeys: String, CodingKey {
        case ok, service, version, domains
        case authRequired = "auth_required"
        case adapters
    }
}