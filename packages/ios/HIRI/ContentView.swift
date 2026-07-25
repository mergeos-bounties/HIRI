import SwiftUI

// MARK: - ContentView (Device List)

struct ContentView: View {
    @State private var viewModel = HIRIViewModel()
    @State private var apiBaseURL: String = "http://127.0.0.1:8780"
    @State private var showSettings = false
    @State private var searchText = ""

    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                // Connection status bar
                HStack {
                    Circle()
                        .fill(viewModel.isConnected ? Color.green : Color.red)
                        .frame(width: 8, height: 8)
                    Text(viewModel.isConnected
                         ? "Bridge v\(viewModel.bridgeVersion) · \(viewModel.devices.count) devices"
                         : "Disconnected")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Spacer()
                    if viewModel.isLoading {
                        ProgressView()
                            .scaleEffect(0.7)
                    }
                }
                .padding(.horizontal)
                .padding(.vertical, 6)

                // Area filter
                if !viewModel.areas.isEmpty {
                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: 8) {
                            FilterChip(title: "All Rooms", isSelected: viewModel.selectedArea == "") {
                                viewModel.selectedArea = ""
                                Task { await viewModel.loadDevices() }
                            }
                            ForEach(viewModel.areas, id: \.self) { area in
                                FilterChip(title: area.replacingOccurrences(of: "_", with: " ").capitalized,
                                           isSelected: viewModel.selectedArea == area) {
                                    viewModel.selectedArea = area
                                    Task { await viewModel.loadDevices() }
                                }
                            }
                        }
                        .padding(.horizontal)
                        .padding(.vertical, 8)
                    }
                    Divider()
                }

                // Device list
                if viewModel.errorMessage != nil && !viewModel.isConnected {
                    ContentUnavailableView(
                        "Cannot Connect",
                        systemImage: "wifi.slash",
                        description: Text(viewModel.errorMessage ?? "Check bridge URL")
                    )
                } else if viewModel.devices.isEmpty && !viewModel.isLoading {
                    ContentUnavailableView(
                        "No Devices",
                        systemImage: "square.stack.3d.up.slash",
                        description: Text("No devices found\(viewModel.selectedArea.isEmpty ? "" : " in this area")")
                    )
                } else {
                    List {
                        ForEach(filteredDevices) { device in
                            NavigationLink(destination: DeviceDetailView(device: device, viewModel: $viewModel)) {
                                DeviceRowView(device: device)
                            }
                            .listRowInsets(EdgeInsets(top: 4, leading: 16, bottom: 4, trailing: 16))
                        }
                    }
                    .listStyle(.plain)
                    .refreshable {
                        await viewModel.loadDevices()
                    }
                    .searchable(text: $searchText, prompt: "Search devices by name / id")
                }
            }
            .navigationTitle("HIRI")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: { showSettings = true }) {
                        Image(systemName: "gearshape.fill")
                    }
                }
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(action: { Task { await viewModel.loadDevices() } }) {
                        Image(systemName: "arrow.clockwise")
                    }
                }
            }
            .sheet(isPresented: $showSettings) {
                SettingsView(apiBaseURL: $apiBaseURL, onSave: { newURL in
                    Task {
                        await APIService.shared.updateBaseURL(newURL)
                        await viewModel.loadDevices()
                    }
                })
            }
            .task {
                await viewModel.loadDevices()
            }
        }
    }

    private var filteredDevices: [Device] {
        if searchText.isEmpty { return viewModel.devices }
        return viewModel.devices.filter {
            $0.name.localizedCaseInsensitiveContains(searchText) ||
            $0.id.localizedCaseInsensitiveContains(searchText)
        }
    }
}

// MARK: - Device Row

struct DeviceRowView: View {
    let device: Device

    var body: some View {
        HStack(spacing: 12) {
            // Domain icon
            ZStack {
                RoundedRectangle(cornerRadius: 8)
                    .fill(Color(hex: device.domainColor).opacity(0.2))
                    .frame(width: 40, height: 40)
                Image(systemName: device.domainIcon)
                    .foregroundColor(Color(hex: device.domainColor))
                    .font(.system(size: 18))
            }

            VStack(alignment: .leading, spacing: 2) {
                Text(device.name)
                    .font(.headline)
                    .lineLimit(1)
                HStack(spacing: 4) {
                    Text(device.areaName)
                        .font(.caption)
                        .foregroundColor(.secondary)
                    if !device.online {
                        Text("Offline")
                            .font(.caption)
                            .foregroundColor(.red)
                    }
                }
            }

            Spacer()

            // State indicator
            VStack(alignment: .trailing, spacing: 2) {
                Text(device.friendlyState)
                    .font(.caption)
                    .foregroundColor(device.isOn ? .green : .secondary)
                if device.domain == "light" && device.isOn {
                    Text("\(Int(device.brightness))%")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
            }
        }
        .padding(.vertical, 2)
    }
}

// MARK: - Filter Chip

struct FilterChip: View {
    let title: String
    let isSelected: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.caption)
                .fontWeight(isSelected ? .semibold : .regular)
                .padding(.horizontal, 12)
                .padding(.vertical, 6)
                .background(isSelected ? Color.accentColor : Color(.systemGray6))
                .foregroundColor(isSelected ? .white : .primary)
                .clipShape(Capsule())
        }
    }
}

// MARK: - Settings View

struct SettingsView: View {
    @Binding var apiBaseURL: String
    let onSave: (String) -> Void
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationStack {
            Form {
                Section("Bridge Connection") {
                    TextField("API Base URL", text: $apiBaseURL)
                        .keyboardType(.URL)
                        .autocapitalization(.none)
                        .disableAutocorrection(true)
                    Text("Default: http://127.0.0.1:8780")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                Section("About") {
                    HStack {
                        Text("HIRI iOS")
                        Spacer()
                        Text("1.0.0")
                            .foregroundColor(.secondary)
                    }
                    Text("SwiftUI client for HIRI-bridge. Connects to a local or remote bridge instance to browse and control smart home devices.")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            .navigationTitle("Settings")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("Save") {
                        onSave(apiBaseURL)
                        dismiss()
                    }
                }
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { dismiss() }
                }
            }
        }
    }
}

// MARK: - Color Hex Extension

extension Color {
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let r, g, b, a: UInt64
        switch hex.count {
        case 6:
            (r, g, b, a) = ((int >> 16) & 0xFF, (int >> 8) & 0xFF, int & 0xFF, 255)
        case 8:
            (r, g, b, a) = ((int >> 24) & 0xFF, (int >> 16) & 0xFF, (int >> 8) & 0xFF, int & 0xFF)
        default:
            (r, g, b, a) = (128, 128, 128, 255)
        }
        self.init(
            .sRGB,
            red: Double(r) / 255,
            green: Double(g) / 255,
            blue: Double(b) / 255,
            opacity: Double(a) / 255
        )
    }
}

// MARK: - Preview

#Preview {
    ContentView()
}