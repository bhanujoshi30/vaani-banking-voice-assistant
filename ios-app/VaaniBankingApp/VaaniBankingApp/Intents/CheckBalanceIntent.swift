//
//  CheckBalanceIntent.swift
//  VaaniBankingApp
//
//  App Intent for checking balance via Siri and Shortcuts
//

import AppIntents
import SwiftUI
import UIKit

@available(iOS 16.0, *)
struct CheckBalanceIntent: AppIntent {
    static var title: LocalizedStringResource = "Check Balance"

    static var description = IntentDescription("Check your account balance with Vaani")

    // Siri will suggest this phrase to users
    static var suggestedInvocationPhrase: LocalizedStringResource = "Check my balance"

    // Optional: Allow custom message parameter
    @Parameter(title: "Message", default: "Check balance")
    var message: String?

    // Enable background execution
    static var openAppWhenRun: Bool = true

    @MainActor
    func perform() async throws -> some IntentResult & ProvidesDialog & ShowsSnippetView {
        let queryMessage = message ?? "Check balance"

        print("🎤 Siri Intent: CheckBalance - Message: \(queryMessage)")

        // Persist pending message as a fallback for Siri handoff
        UserDefaults.standard.set(queryMessage, forKey: "VaaniPendingMessage")

        // Create deep link URL
        let encodedMessage = queryMessage.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? queryMessage
        guard let url = URL(string: "vaani://chat?message=\(encodedMessage)") else {
            throw IntentError.invalidURL
        }

        // Open the app with deep link
        await UIApplication.shared.open(url)

        // Return result with dialog and snippet view
        return .result(
            dialog: "Opening Vaani to check your balance...",
            view: BalanceSnippetView(message: queryMessage)
        )
    }
}

// MARK: - Additional Banking Intents

@available(iOS 16.0, *)
struct TransferMoneyIntent: AppIntent {
    static var title: LocalizedStringResource = "Transfer Money"
    static var description = IntentDescription("Transfer money to another account")
    static var suggestedInvocationPhrase: LocalizedStringResource = "Transfer money"
    static var openAppWhenRun: Bool = true

    @MainActor
    func perform() async throws -> some IntentResult & ProvidesDialog {
        let raw = "I want to transfer money"
        UserDefaults.standard.set(raw, forKey: "VaaniPendingMessage")
        let url = URL(string: "vaani://chat?message=I%20want%20to%20transfer%20money")!
        await UIApplication.shared.open(url)

        return .result(dialog: "Opening Vaani for money transfer...")
    }
}

@available(iOS 16.0, *)
struct ViewTransactionsIntent: AppIntent {
    static var title: LocalizedStringResource = "View Transactions"
    static var description = IntentDescription("View your recent transactions")
    static var suggestedInvocationPhrase: LocalizedStringResource = "Show my transactions"
    static var openAppWhenRun: Bool = true

    @MainActor
    func perform() async throws -> some IntentResult & ProvidesDialog {
        let raw = "Show my recent transactions"
        UserDefaults.standard.set(raw, forKey: "VaaniPendingMessage")
        let url = URL(string: "vaani://chat?message=Show%20my%20recent%20transactions")!
        await UIApplication.shared.open(url)

        return .result(dialog: "Opening your transaction history...")
    }
}

@available(iOS 16.0, *)
struct SetReminderIntent: AppIntent {
    static var title: LocalizedStringResource = "Set Payment Reminder"
    static var description = IntentDescription("Set a payment reminder with Vaani")
    static var suggestedInvocationPhrase: LocalizedStringResource = "Set a payment reminder"
    static var openAppWhenRun: Bool = true

    @MainActor
    func perform() async throws -> some IntentResult & ProvidesDialog {
        let url = URL(string: "vaani://chat?message=I%20want%20to%20set%20a%20payment%20reminder")!
        await UIApplication.shared.open(url)

        return .result(dialog: "Opening Vaani to set a reminder...")
    }
}

// MARK: - Snippet Views

@available(iOS 16.0, *)
struct BalanceSnippetView: View {
    let message: String

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(spacing: 12) {
                Image(systemName: "indianrupeesign.circle.fill")
                    .font(.system(size: 40))
                    .foregroundColor(.green)

                VStack(alignment: .leading, spacing: 4) {
                    Text("Vaani Banking")
                        .font(.headline)
                        .foregroundColor(.primary)

                    Text("Voice Assistant")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }

                Spacer()
            }

            Divider()

            HStack {
                Image(systemName: "message.fill")
                    .foregroundColor(.blue)
                Text(message)
                    .font(.body)
                    .foregroundColor(.primary)
            }

            Text("Opening chat to check your balance...")
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .padding()
        .background(Color(UIColor.secondarySystemBackground))
        .cornerRadius(12)
    }
}

// MARK: - Error Handling

enum IntentError: Error, LocalizedError {
    case invalidURL
    case notLoggedIn
    case networkError

    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Invalid URL"
        case .notLoggedIn:
            return "Please log in to Vaani Banking first"
        case .networkError:
            return "Network connection error"
        }
    }
}

// MARK: - App Shortcuts Provider

@available(iOS 16.0, *)
struct VaaniAppShortcuts: AppShortcutsProvider {
    static var appShortcuts: [AppShortcut] {
        return [
            AppShortcut(
                intent: CheckBalanceIntent(),
                phrases: [
                    "Check my ${applicationName} balance",
                    "What's my balance in ${applicationName}",
                    "Show my ${applicationName} account balance"
                ],
                shortTitle: "Check Balance",
                systemImageName: "indianrupeesign.circle.fill"
            ),
            AppShortcut(
                intent: TransferMoneyIntent(),
                phrases: [
                    "Transfer money with ${applicationName}",
                    "Send money using ${applicationName}"
                ],
                shortTitle: "Transfer Money",
                systemImageName: "arrow.left.arrow.right"
            ),
            AppShortcut(
                intent: ViewTransactionsIntent(),
                phrases: [
                    "Show transactions in ${applicationName}",
                    "View my ${applicationName} transactions"
                ],
                shortTitle: "Transactions",
                systemImageName: "list.bullet.rectangle"
            )
        ]
    }
}
