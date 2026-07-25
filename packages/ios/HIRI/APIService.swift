import Foundation

// MARK: - API Service

actor APIService {
    static let shared = APIService()

    private var baseURL: String = "http://127.0.0.1:8780"
    private var session: URLSession

    private init() {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 10
        config.timeoutIntervalForResource = 30
        self.session = URLSession(configuration: config)
    }

    func updateBaseURL(_ url: String) {
        baseURL = url.hasSuffix("/") ? String(url.dropLast()) : url
    }

    // MARK: - Health

    func health() async throws -> HealthResponse {
        let url = URL(string: "\(baseURL)/health")!
        let (data, _) = try await session.data(from: url)
        return try JSONDecoder().decode(HealthResponse.self, from: data)
    }

    // MARK: - Devices

    func listDevices(domain: String? = nil, area: String? = nil) async throws -> [Device] {
        var components = URLComponents(string: "\(baseURL)/devices")!
        var queryItems: [URLQueryItem] = []
        if let domain = domain, !domain.isEmpty {
            queryItems.append(URLQueryItem(name: "domain", value: domain))
        }
        if let area = area, !area.isEmpty {
            queryItems.append(URLQueryItem(name: "area", value: area))
        }
        if !queryItems.isEmpty {
            components.queryItems = queryItems
        }
        let (data, _) = try await session.data(from: components.url!)
        return try JSONDecoder().decode([Device].self, from: data)
    }

    func getDevice(_ id: String) async throws -> Device {
        let url = URL(string: "\(baseURL)/devices/\(id)")!
        let (data, _) = try await session.data(from: url)
        return try JSONDecoder().decode(Device.self, from: data)
    }

    func sendCommand(deviceId: String, action: String, data: [String: JSONValue]? = nil) async throws -> [String: JSONValue] {
        let url = URL(string: "\(baseURL)/devices/\(deviceId)/command")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        let command = CommandRequest(action: action, data: data)
        request.httpBody = try JSONEncoder().encode(command)
        let (responseData, _) = try await session.data(for: request)
        return try JSONDecoder().decode([String: JSONValue].self, from: responseData)
    }

    // MARK: - Stats

    func stats() async throws -> [String: JSONValue] {
        let url = URL(string: "\(baseURL)/stats")!
        let (data, _) = try await session.data(from: url)
        return try JSONDecoder().decode([String: JSONValue].self, from: data)
    }

    // MARK: - Areas

    func fetchAreas() async throws -> [String] {
        let devices = try await listDevices()
        let areas = Set(devices.map { $0.area })
        return areas.sorted()
    }
}

// MARK: - Observable ViewModel

@MainActor
@Observable
final class HIRIViewModel {
    var devices: [Device] = []
    var areas: [String] = []
    var selectedArea: String = ""
    var isLoading = false
    var errorMessage: String?
    var bridgeVersion: String = ""
    var isConnected = false

    private let api = APIService.shared

    func loadDevices() async {
        isLoading = true
        errorMessage = nil
        do {
            let health = try await api.health()
            bridgeVersion = health.version
            isConnected = health.ok

            devices = try await api.listDevices(area: selectedArea.isEmpty ? nil : selectedArea)
            areas = try await api.fetchAreas()
        } catch {
            errorMessage = "Connection failed: \(error.localizedDescription)"
            isConnected = false
            devices = []
        }
        isLoading = false
    }

    func toggleDevice(_ device: Device) async {
        let action = device.isOn ? "turn_off" : "turn_on"
        do {
            _ = try await api.sendCommand(deviceId: device.id, action: action)
            // Refresh device list
            await loadDevices()
        } catch {
            errorMessage = "Command failed: \(error.localizedDescription)"
        }
    }

    func setBrightness(deviceId: String, brightness: Int) async {
        let brightnessVal = min(255, max(0, brightness))
        do {
            _ = try await api.sendCommand(
                deviceId: deviceId,
                action: "turn_on",
                data: ["brightness": .number(Double(brightnessVal))]
            )
            await loadDevices()
        } catch {
            errorMessage = "Brightness command failed: \(error.localizedDescription)"
        }
    }
}