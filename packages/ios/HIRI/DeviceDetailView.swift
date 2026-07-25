import SwiftUI

// MARK: - Device Detail View

struct DeviceDetailView: View {
    let device: Device
    @Binding var viewModel: HIRIViewModel
    @State private var localBrightness: Double = 0
    @State private var isRefreshing = false

    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                // Header card
                VStack(spacing: 12) {
                    ZStack {
                        RoundedRectangle(cornerRadius: 16)
                            .fill(Color(hex: device.domainColor).opacity(0.15))
                            .frame(width: 72, height: 72)
                        Image(systemName: device.domainIcon)
                            .font(.system(size: 36))
                            .foregroundColor(Color(hex: device.domainColor))
                    }

                    Text(device.name)
                        .font(.title2)
                        .fontWeight(.bold)

                    HStack(spacing: 8) {
                        Label(device.areaName, systemImage: "location.fill")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        Text("·")
                            .foregroundColor(.secondary)
                        Label(device.domain.capitalized, systemImage: "tag.fill")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
                .padding(.top)

                // Power toggle
                if device.domain == "light" || device.domain == "switch" || device.domain == "fan" {
                    VStack(spacing: 8) {
                        Text("Power")
                            .font(.headline)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding(.horizontal)

                        Button(action: {
                            Task { await viewModel.toggleDevice(device) }
                        }) {
                            HStack {
                                Image(systemName: device.isOn ? "power.circle.fill" : "power.circle")
                                    .font(.title2)
                                Text(device.isOn ? "Turn Off" : "Turn On")
                                    .fontWeight(.semibold)
                            }
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 12)
                            .background(device.isOn ? Color.red.opacity(0.1) : Color.green.opacity(0.1))
                            .foregroundColor(device.isOn ? .red : .green)
                            .clipShape(RoundedRectangle(cornerRadius: 10))
                            .overlay(
                                RoundedRectangle(cornerRadius: 10)
                                    .stroke(device.isOn ? Color.red.opacity(0.3) : Color.green.opacity(0.3), lineWidth: 1)
                            )
                        }
                        .padding(.horizontal)
                    }
                }

                // Brightness slider (for lights)
                if device.domain == "light" && device.isOn {
                    VStack(spacing: 8) {
                        HStack {
                            Text("Brightness")
                                .font(.headline)
                            Spacer()
                            Text("\(Int(localBrightness))%")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                        .padding(.horizontal)

                        HStack {
                            Image(systemName: "sun.min.fill")
                                .foregroundColor(.secondary)
                            Slider(value: $localBrightness, in: 0...100, step: 5) { editing in
                                if !editing {
                                    let mappedBrightness = Int(localBrightness / 100.0 * 255)
                                    Task {
                                        await viewModel.setBrightness(deviceId: device.id, brightness: mappedBrightness)
                                    }
                                }
                            }
                            .tint(Color(hex: device.domainColor))
                            Image(systemName: "sun.max.fill")
                                .foregroundColor(.secondary)
                        }
                        .padding(.horizontal)
                    }
                    .onAppear {
                        localBrightness = device.brightness
                    }
                }

                // State details
                VStack(spacing: 8) {
                    Text("State")
                        .font(.headline)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(.horizontal)

                    VStack(spacing: 0) {
                        DetailRow(label: "Status", value: device.friendlyState, icon: "circle.fill",
                                  color: device.isOn ? .green : .secondary)
                        Divider().padding(.leading, 48)
                        DetailRow(label: "Online", value: device.online ? "Yes" : "No", icon: "antenna.radiowaves.left.and.right",
                                  color: device.online ? .green : .red)
                        Divider().padding(.leading, 48)
                        DetailRow(label: "Domain", value: device.domain.capitalized, icon: "tag")
                        if device.domain == "light" && device.isOn {
                            Divider().padding(.leading, 48)
                            DetailRow(label: "Brightness", value: "\(Int(device.brightness))%", icon: "sun.max.fill")
                        }
                    }
                    .background(Color(.systemGray6))
                    .clipShape(RoundedRectangle(cornerRadius: 10))
                    .padding(.horizontal)
                }

                // Device info
                VStack(spacing: 8) {
                    Text("Device Info")
                        .font(.headline)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(.horizontal)

                    VStack(spacing: 0) {
                        DetailRow(label: "ID", value: device.id, icon: "number")
                        Divider().padding(.leading, 48)
                        DetailRow(label: "Model", value: device.model, icon: "chip.fill")
                        Divider().padding(.leading, 48)
                        DetailRow(label: "Manufacturer", value: device.manufacturer, icon: "building.2.fill")
                        Divider().padding(.leading, 48)
                        DetailRow(label: "Adapter", value: device.adapter.uppercased(), icon: "cable.connector")
                    }
                    .background(Color(.systemGray6))
                    .clipShape(RoundedRectangle(cornerRadius: 10))
                    .padding(.horizontal)
                }
            }
            .padding(.bottom, 30)
        }
        .navigationTitle(device.name)
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button(action: { Task { await viewModel.loadDevices() } }) {
                    Image(systemName: "arrow.clockwise")
                }
            }
        }
    }
}

// MARK: - Detail Row

struct DetailRow: View {
    let label: String
    let value: String
    var icon: String = "circle.fill"
    var color: Color = .secondary

    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: icon)
                .foregroundColor(color)
                .frame(width: 20)
            Text(label)
                .foregroundColor(.secondary)
                .font(.subheadline)
            Spacer()
            Text(value)
                .font(.subheadline)
                .fontWeight(.medium)
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 10)
    }
}

// MARK: - Preview

#Preview {
    NavigationStack {
        DeviceDetailView(
            device: Device(
                id: "light.living_main",
                name: "Living Room Light",
                domain: "light",
                manufacturer: "HIRI",
                model: "HIRI-RGBW",
                area: "living",
                online: true,
                state: ["state": .string("on"), "brightness": .number(128)],
                attributes: ["rgb": .bool(true)],
                adapter: "local"
            ),
            viewModel: .constant(HIRIViewModel())
        )
    }
}