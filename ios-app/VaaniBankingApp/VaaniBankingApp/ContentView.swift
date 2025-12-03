//
//  ContentView.swift
//  VaaniBankingApp
//
//  Created by Ashok Vardhan Jangeti on 02/12/25.
//

import SwiftUI
import WebKit

// Select how to load the React frontend
// .production: load deployed URL
// .localhost: load local Vite dev server
// .bundled: load bundled dist/ assets (add to project if used)
enum FrontendMode: String, CaseIterable { case production = "Prod", localhost = "Local", bundled = "Bundled" }
#if DEBUG
private let defaultMode: FrontendMode = .localhost
#else
private let defaultMode: FrontendMode = .production
#endif

@MainActor
struct ContentView: View {
    @EnvironmentObject var appState: AppState
    @StateObject private var webViewStore = WebViewStore()
    @State private var isLoading = true
    @State private var showError = false
    @State private var errorMessage = ""
    @State private var currentMode: FrontendMode = defaultMode
    #if DEBUG
    @State private var showDebugOverlay = true
    #else
    @State private var showDebugOverlay = false
    #endif

    // Deliver a pending message into the WebView with a short retry until the bridge is ready
    @MainActor
    private func deliverPendingMessage(_ msg: String, attempt: Int = 0) {
        // De-dup guard: suppress duplicates within 3 seconds
        if let lastMsg = appState.lastDeliveredMessage,
           let lastAt = appState.lastDeliveredAt,
           lastMsg == msg,
           Date().timeIntervalSince(lastAt) < 3.0 {
            appState.pendingMessage = nil
            return
        }
        if webViewStore.isReady {
            webViewStore.sendMessage(msg)
            appState.lastDeliveredMessage = msg
            appState.lastDeliveredAt = Date()
            appState.pendingMessage = nil
            return
        }
        if attempt < 25 { // ~5s
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.2) {
                self.deliverPendingMessage(msg, attempt: attempt + 1)
            }
        } else {
            webViewStore.sendMessage(msg)
            appState.lastDeliveredMessage = msg
            appState.lastDeliveredAt = Date()
            appState.pendingMessage = nil
        }
    }

    var body: some View {
        ZStack {
            WebViewContainer(store: webViewStore, isLoading: $isLoading, mode: $currentMode)
                .ignoresSafeArea()

            if isLoading {
                VStack(spacing: 16) {
                    ProgressView()
                        .scaleEffect(1.4)
                    Text("Loading Vaani Banking…")
                        .foregroundColor(.secondary)
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .background(Color(.systemBackground))
            }

            if showError {
                VStack(spacing: 16) {
                    Image(systemName: "wifi.slash")
                        .font(.system(size: 56))
                        .foregroundColor(.red)
                    Text("Connection Error")
                        .font(.title3)
                        .bold()
                    Text(errorMessage)
                        .multilineTextAlignment(.center)
                        .foregroundColor(.secondary)
                        .padding(.horizontal)
                    Button {
                        showError = false
                        webViewStore.reload()
                    } label: {
                        Label("Retry", systemImage: "arrow.clockwise")
                            .padding(.horizontal, 16)
                            .padding(.vertical, 10)
                            .background(Color.accentColor)
                            .foregroundColor(.white)
                            .cornerRadius(10)
                    }
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .background(Color(.systemBackground))
            }
            // Debug overlay (build switch + bridge status)
            if showDebugOverlay {
                VStack {
                    HStack(spacing: 8) {
                        Text("Mode:")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        Picker("Mode", selection: $currentMode) {
                            Text("Prod").tag(FrontendMode.production)
                            Text("Local").tag(FrontendMode.localhost)
                            Text("Bundled").tag(FrontendMode.bundled)
                        }
                        .pickerStyle(.segmented)
                        .frame(maxWidth: 260)

                        Circle()
                            .fill(webViewStore.isReady ? Color.green : Color.orange)
                            .frame(width: 10, height: 10)
                        Text(webViewStore.isReady ? "Bridge: Ready" : "Bridge: Waiting")
                            .font(.caption)
                            .foregroundColor(.secondary)

                        Spacer()

                        Button {
                            withAnimation { showDebugOverlay.toggle() }
                        } label: {
                            Image(systemName: "xmark.circle.fill")
                                .foregroundColor(.secondary)
                        }
                    }
                    .padding(8)
                    .background(.ultraThinMaterial)
                    .cornerRadius(12)
                    .padding([.top, .horizontal])

                    Spacer()
                }
                .transition(.move(edge: .top))
            } else {
                // Reveal overlay with long-press top-right corner in DEBUG
                #if DEBUG
                VStack {
                    HStack {
                        Spacer()
                        Color.clear
                            .frame(width: 44, height: 44)
                            .contentShape(Rectangle())
                            .onLongPressGesture {
                                withAnimation { showDebugOverlay = true }
                            }
                    }
                    Spacer()
                }
                #endif
            }
        }
        .onChange(of: appState.pendingMessage) { oldValue, newValue in
            guard oldValue != newValue, let msg = newValue, !msg.isEmpty else { return }
            let sender = self
            DispatchQueue.main.async {
                sender.deliverPendingMessage(msg)
            }
        }
    }
}

struct WebViewContainer: UIViewRepresentable {
    @ObservedObject var store: WebViewStore
    @Binding var isLoading: Bool
    @Binding var mode: FrontendMode

    func makeCoordinator() -> Coordinator { Coordinator(self) }

    func makeUIView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()
        config.defaultWebpagePreferences.allowsContentJavaScript = true
        config.allowsInlineMediaPlayback = true
        config.userContentController.add(store, name: "nativeHandler")

        let webView = WKWebView(frame: .zero, configuration: config)
        webView.navigationDelegate = context.coordinator
        store.webView = webView
        loadURL(for: mode, in: webView)
        return webView
    }

    func updateUIView(_ uiView: WKWebView, context: Context) {}
    
    private func loadURL(for mode: FrontendMode, in webView: WKWebView) {
        switch mode {
        case .production:
            if let url = URL(string: "https://vaani-banking-voice-assistant.vercel.app") {
                webView.load(URLRequest(url: url))
            }
        case .localhost:
            if let url = URL(string: "http://localhost:5173") {
                webView.load(URLRequest(url: url))
            }
        case .bundled:
            if let url = Bundle.main.url(forResource: "index", withExtension: "html", subdirectory: "dist") {
                webView.loadFileURL(url, allowingReadAccessTo: url.deletingLastPathComponent())
            }
        }
    }

    class Coordinator: NSObject, WKNavigationDelegate {
        var parent: WebViewContainer
        init(_ parent: WebViewContainer) { self.parent = parent }

        func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
            parent.isLoading = false
        }

        func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
            parent.isLoading = false
        }

        func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {
            parent.isLoading = false
        }
    }
}

#Preview { ContentView() }
