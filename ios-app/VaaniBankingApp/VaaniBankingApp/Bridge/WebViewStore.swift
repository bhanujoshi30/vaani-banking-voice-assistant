//
//  WebViewStore.swift
//  VaaniBankingApp
//
//  WKWebView store and JavaScript bridge for React integration
//

import Foundation
import WebKit
import Combine

@MainActor
final class WebViewStore: NSObject, ObservableObject {
    @Published var webView: WKWebView?
    @Published var lastResponse: String?
    @Published var isReady = false
    
    // Send a message to React via JS function window.sendAutoMessage
    func sendMessage(_ message: String) {
        guard let webView = webView else { return }
        let escaped = message
            .replacingOccurrences(of: "\\", with: "\\\\")
            .replacingOccurrences(of: "\"", with: "\\\"")
            .replacingOccurrences(of: "\n", with: "\\n")
            .replacingOccurrences(of: "\r", with: "\\r")
        let js = """
        (function(){
          if (typeof window.sendAutoMessage === 'function') {
            window.sendAutoMessage(\"\(escaped)\");
            return 'SUCCESS';
          } else {
            return 'NOT_READY';
          }
        })();
        """
        webView.evaluateJavaScript(js) { result, error in
            if let str = result as? String, str == "NOT_READY" {
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
                    self.sendMessage(message)
                }
            }
        }
    }
    
    func reload() { webView?.reload() }
}

// Receive messages from React -> Native
extension WebViewStore: WKScriptMessageHandler {
    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        guard message.name == "nativeHandler" else { return }
        if let dict = message.body as? [String: Any],
           let type = dict["type"] as? String {
            switch type {
            case "chatResponse":
                if let response = dict["response"] as? String {
                    DispatchQueue.main.async { self.lastResponse = response }
                }
            case "ready":
                DispatchQueue.main.async { self.isReady = true }
            default:
                break
            }
        }
    }
}
