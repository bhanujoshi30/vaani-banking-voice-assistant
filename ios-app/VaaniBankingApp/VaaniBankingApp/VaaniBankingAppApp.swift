//
//  VaaniBankingAppApp.swift
//  VaaniBankingApp
//
//  Created by Ashok Vardhan Jangeti on 02/12/25.
//

import SwiftUI
import AppIntents
import Combine

@main
struct VaaniBankingAppApp: App {
    @StateObject private var appState = AppState()
    
    init() {
        if #available(iOS 16.0, *) {
            // App Intents auto-register; keeping hook for clarity
            print("✅ App launched with App Intents support")
        }
    }
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appState)
                .onOpenURL { url in
                    handleDeepLink(url)
                    // Mark that URL-based payload was handled for this activation
                    UserDefaults.standard.set(true, forKey: "VaaniHandledURLForActivation")
                }
                .onReceive(NotificationCenter.default.publisher(for: UIApplication.didBecomeActiveNotification)) { _ in
                    // Only deliver persisted message if we didn't get a URL this activation
                    let handledURLThisActivation = UserDefaults.standard.bool(forKey: "VaaniHandledURLForActivation")
                    if !handledURLThisActivation,
                       let pending = UserDefaults.standard.string(forKey: "VaaniPendingMessage"), !pending.isEmpty {
                        appState.pendingMessage = pending
                        UserDefaults.standard.removeObject(forKey: "VaaniPendingMessage")
                    }
                    // Reset activation flag
                    UserDefaults.standard.removeObject(forKey: "VaaniHandledURLForActivation")
                }
        }
    }
    
    private func handleDeepLink(_ url: URL) {
        // Example deep link handling logic
        // Extracting a "message" query parameter as an example payload
        if let comps = URLComponents(url: url, resolvingAgainstBaseURL: false),
           let msg = comps.queryItems?.first(where: { $0.name == "message" })?.value {
            appState.pendingMessage = msg
        }
    }
}

// Simple shared app state to pass deep-link message into WebView
final class AppState: ObservableObject {
    @Published var pendingMessage: String?
    // Track last delivered message to avoid duplicate sends within a short window
    @Published var lastDeliveredMessage: String?
    @Published var lastDeliveredAt: Date?
}
