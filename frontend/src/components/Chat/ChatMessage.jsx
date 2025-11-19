import { useState } from "react";
import PropTypes from "prop-types";
import TransactionTable from "./TransactionTable.jsx";
import AccountBalanceCards from "./AccountBalanceCards.jsx";
import LoanInfoCard from "./LoanInfoCard.jsx";
import ReminderCard from "./ReminderCard.jsx";
import TransferFlow from "./TransferFlow.jsx";
import TransferReceipt from "./TransferReceipt.jsx";
import StatementRequestCard from "./StatementRequestCard.jsx";
import ReminderManagerCard from "./ReminderManagerCard.jsx";
import "./ChatMessage.css";

/**
 * ChatMessage component - Displays a single chat message
 */
const ChatMessage = ({ message, userName, language = 'en-IN', session, onFeedback, onAddAssistantMessage }) => {
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
  
  // Debug: Log message data to console
  if (message.role === 'assistant') {
    console.log('📩 Assistant Message:', {
      content: message.content.substring(0, 50) + '...',
      hasStatementData: !!message.statementData,
      hasStructuredData: !!message.structuredData,
      statementData: message.statementData,
      structuredData: message.structuredData,
    });
  }

  const handleFeedback = (isPositive) => {
    if (feedbackSubmitted) return;
    
    setFeedbackSubmitted(true);
    
    // Store feedback data
    const feedbackData = {
      messageId: message.id,
      role: message.role,
      content: message.content,
      feedback: isPositive ? 'positive' : 'negative',
      timestamp: new Date().toISOString(),
      structuredData: message.structuredData,
      statementData: message.statementData,
    };
    
    // Log to console (in production, send to backend)
    console.log('📊 User Feedback:', feedbackData);
    
    // Call callback if provided
    if (onFeedback) {
      onFeedback(feedbackData);
    }
    
    // Store in localStorage for later collection
    try {
      const existingFeedback = JSON.parse(localStorage.getItem('ai_feedback') || '[]');
      existingFeedback.push(feedbackData);
      localStorage.setItem('ai_feedback', JSON.stringify(existingFeedback));
    } catch (error) {
      console.error('Error storing feedback:', error);
    }
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString("en-IN", {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const formatDateForStatement = (value) => {
    if (!value) return "—";
    try {
      const date = typeof value === "string" ? new Date(value) : value;
      if (isNaN(date.getTime())) return "—";
      return date.toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric",
      });
    } catch (e) {
      console.error('Date formatting error:', e, 'value:', value);
      return "—";
    }
  };

  const formatAmountForCsv = (amount) => {
    const num = Number(amount ?? 0);
    return num.toFixed(2);
  };

  const isDebitTransaction = (type = "") => {
    const lowered = type.toLowerCase();
    return ["withdraw", "debit", "payment", "transfer_out", "upi", "bill"].some((token) =>
      lowered.includes(token),
    );
  };

  const buildStatementCsv = ({
    bankName,
    account,
    accountHolder,
    fromDate,
    toDate,
    currency,
    closingBalance,
    transactions,
  }) => {
    try {
      const generatedAt = formatDateForStatement(Date.now());

      // Sort transactions by date
      const sortedTransactions = [...transactions].sort((a, b) => {
        try {
          const aDateStr = a.date || a.occurred_at || a.occurredAt || "";
          const bDateStr = b.date || b.occurred_at || b.occurredAt || "";
          
          if (!aDateStr || !bDateStr) return 0;
          
          const aTime = new Date(aDateStr).getTime();
          const bTime = new Date(bDateStr).getTime();
          
          if (isNaN(aTime) || isNaN(bTime)) return 0;
          
          return aTime - bTime;
        } catch (e) {
          console.error('Sort error:', e, 'a:', a, 'b:', b);
          return 0;
        }
      });

    const totalDelta = sortedTransactions.reduce((acc, txn) => {
      const amount = Number(txn.amount ?? 0);
      return acc + (isDebitTransaction(txn.type || txn.transaction_type) ? -amount : amount);
    }, 0);

    const closing = Number(closingBalance ?? 0);
    const openingBalance = closing - totalDelta;
    let runningBalance = openingBalance;

    const openingDisplay = formatAmountForCsv(openingBalance);
    const closingDisplay = (() => {
      const finalBalance = sortedTransactions.reduce((acc, txn) => {
        const amount = Number(txn.amount ?? 0);
        return acc + (isDebitTransaction(txn.type || txn.transaction_type) ? -amount : amount);
      }, openingBalance);
      return formatAmountForCsv(finalBalance);
    })();

    const headerLines = [
      `"${bankName}","Account Statement"`,
      `"Account Holder","${accountHolder}"`,
      `"Account Number","${account.accountNumber}"`,
      `"Account Type","${(account.accountType || '').replace(/_/g, " ").toUpperCase()}"`,
      `"Statement Period","${fromDate} to ${toDate}"`,
      `"Opening Balance (${currency})","${openingDisplay}"`,
      `"Closing Balance (${currency})","${closingDisplay}"`,
      `"Generated On","${generatedAt}"`,
      "",
      "Transaction Date,Value Date,Description,Reference No.,Debit (INR),Credit (INR),Balance (INR),Status",
    ];

    const txnLines = sortedTransactions.map((txn) => {
      const amount = Number(txn.amount ?? 0);
      const txnType = txn.type || txn.transaction_type;
      const debit = isDebitTransaction(txnType) ? formatAmountForCsv(amount) : "";
      const credit = isDebitTransaction(txnType) ? "" : formatAmountForCsv(amount);
      const occurred = formatDateForStatement(txn.date || txn.occurred_at || txn.occurredAt || Date.now());
      const reference = txn.reference_id || txn.referenceId || "—";
      const description = (txn.description ?? "").replace(/\s+/g, " ").trim() || "—";
      runningBalance += isDebitTransaction(txnType) ? -amount : amount;
      const balanceFormatted = formatAmountForCsv(runningBalance);

      return [
        occurred,
        occurred,
        description,
        reference,
        debit,
        credit,
        balanceFormatted,
        txn.status ?? "—",
      ]
        .map((value) => `"${String(value ?? "").replace(/"/g, '""')}"`)
        .join(",");
    });

    return [...headerLines, ...txnLines].join("\n");
    } catch (error) {
      console.error('CSV build error:', error);
      throw new Error(`CSV generation failed: ${error.message}`);
    }
  };

  const handleDownloadStatement = (statementData) => {
    console.log('🔍 Download button clicked, statementData:', statementData);
    
    if (!statementData || !statementData.transactions) {
      console.error('❌ No statement data available:', statementData);
      alert('No statement data available');
      return;
    }

    try {
      console.log('📊 Building CSV with data:', {
        accountNumber: statementData.accountNumber || statementData.account_number,
        accountType: statementData.accountType || statementData.account_type,
        transactionCount: statementData.transactions.length,
        fromDate: statementData.fromDate || statementData.from_date,
        toDate: statementData.toDate || statementData.to_date,
      });

      const accountNumber =
        statementData.accountNumber || statementData.account_number || 'unknown';
      const accountType =
        statementData.accountType || statementData.account_type || 'savings';
      const fromDate = statementData.fromDate || statementData.from_date || '—';
      const toDate = statementData.toDate || statementData.to_date || '—';
      const currency = statementData.currency || 'INR';
      const closingBalance =
        statementData.currentBalance ?? statementData.current_balance ?? 0;

      const csv = buildStatementCsv({
        bankName: "Sun National Bank",
        account: {
          accountNumber,
          accountType,
        },
        accountHolder: userName || "Account Holder",
        fromDate,
        toDate,
        currency,
        closingBalance,
        transactions: statementData.transactions,
      });

      console.log('✅ CSV generated successfully, length:', csv.length);

      const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      const suffix = accountNumber ? accountNumber.slice(-5) : "acct";
      const sanitizedFrom = (fromDate || "").replace(/[^0-9]/g, "") || "from";
      const sanitizedTo = (toDate || "").replace(/[^0-9]/g, "") || "to";
      const filename = `snb_statement_${suffix}_${sanitizedFrom}_to_${sanitizedTo}.csv`;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      console.log('✅ Download triggered:', filename);
    } catch (error) {
      console.error('❌ Error generating statement:', error);
      console.error('Error stack:', error.stack);
      alert(`Failed to download statement: ${error.message}`);
    }
  };

  return (
    <div className={`chat-message chat-message--${message.role}`}>
      <div className="chat-message__avatar">
        {message.role === "assistant" ? (
          <svg
            width="32"
            height="32"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <circle cx="12" cy="12" r="10" fill="#FF8F42" />
            <path
              d="M8 14C8 14 9.5 16 12 16C14.5 16 16 14 16 14"
              stroke="white"
              strokeWidth="2"
              strokeLinecap="round"
            />
            <circle cx="9" cy="9" r="1.5" fill="white" />
            <circle cx="15" cy="9" r="1.5" fill="white" />
          </svg>
        ) : (
          <svg
            width="32"
            height="32"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <circle cx="12" cy="12" r="10" fill="#7CB5FF" />
            <circle cx="12" cy="10" r="3" fill="white" />
            <path
              d="M6 19C6 16 8.5 14 12 14C15.5 14 18 16 18 19"
              stroke="white"
              strokeWidth="2"
              strokeLinecap="round"
            />
          </svg>
        )}
      </div>
      <div className="chat-message__content">
        <div className="chat-message__header">
          <span className="chat-message__role">
            {message.role === "assistant" ? "Vaani" : userName}
          </span>
          <span className="chat-message__time">{formatTime(message.timestamp)}</span>
        </div>
        {/* Only show text if content exists and is not just whitespace */}
        {message.content && message.content.trim() && (
          <div className="chat-message__text">{message.content}</div>
        )}
        
        {/* Render structured data components */}
        {message.structuredData && (
          <div className="chat-message__structured">
            {message.structuredData.type === 'transactions' && message.structuredData.transactions && (
              <TransactionTable 
                transactions={message.structuredData.transactions} 
                language={language}
                accounts={message.structuredData.accounts}
                accountTransactions={message.structuredData.accountTransactions}
                totalCount={message.structuredData.total_count}
              />
            )}
            
            {message.structuredData.type === 'balance' && message.structuredData.accounts && (
              <AccountBalanceCards 
                accounts={message.structuredData.accounts} 
                language={language}
              />
            )}
            
            {message.structuredData.type === 'loan' && message.structuredData.loanInfo && (
              <LoanInfoCard 
                loanInfo={message.structuredData.loanInfo} 
                language={language}
              />
            )}
            
            {message.structuredData.type === 'reminder' && message.structuredData.reminder && (
              <ReminderCard 
                reminder={message.structuredData.reminder} 
                language={language}
              />
            )}
            
            {message.structuredData.type === 'transfer' && session && (
              <TransferFlow 
                session={session}
                language={language}
                transferData={message.structuredData}
                onTransferInitiated={(data, receiptData) => {
                  console.log('Transfer initiated:', data, receiptData);
                  // Add success message first
                  if (onAddAssistantMessage) {
                    // Use receiptData if available, otherwise use data
                    const amount = receiptData?.amount || data?.amount || 0;
                    const beneficiaryName = receiptData?.beneficiaryName || data?.beneficiaryName || 'beneficiary';
                    
                    const successMessage = language === 'hi-IN' 
                      ? `₹${parseFloat(amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })} ${beneficiaryName} को सफलतापूर्वक स्थानांतरित कर दिया गया है।`
                      : `Successfully transferred ₹${parseFloat(amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })} to ${beneficiaryName}.`;
                    
                    onAddAssistantMessage(successMessage, null, null);
                    
                    // Then add receipt as assistant message
                    if (receiptData) {
                      onAddAssistantMessage(
                        '', // Empty text - receipt component will display
                        null, // No statement data
                        { type: 'transfer_receipt', receipt: receiptData } // Structured data for receipt
                      );
                    }
                  }
                }}
              />
            )}
            
            {message.structuredData.type === 'statement_request' && session && (
              <StatementRequestCard
                accounts={message.structuredData.accounts || []}
                language={language}
                session={session}
                detectedAccount={message.structuredData.detectedAccount}
                detectedPeriod={message.structuredData.detectedPeriod}
                requiresAccount={message.structuredData.requiresAccount}
                requiresPeriod={message.structuredData.requiresPeriod}
                onDownload={handleDownloadStatement}
                onSuccess={(message) => {
                  if (onAddAssistantMessage) {
                    onAddAssistantMessage(message, null, null);
                  }
                }}
              />
            )}

            {message.structuredData.type === 'reminder_manager' && session && (
              <ReminderManagerCard
                session={session}
                language={language}
                intent={message.structuredData.intent}
                accounts={message.structuredData.accounts}
                prefilled={message.structuredData.prefilled || {}}
                onSuccess={(message) => {
                  if (onAddAssistantMessage) {
                    onAddAssistantMessage(message, null, null);
                  }
                }}
              />
            )}
            
            {message.structuredData?.type === 'transfer_receipt' && message.structuredData?.receipt && (
              <TransferReceipt 
                receipt={message.structuredData.receipt}
                language={language}
              />
            )}
          </div>
        )}
        
        {message.statementData && (
          <div className="chat-message__statement">
            <button
              className="chat-message__download-btn"
              onClick={() => handleDownloadStatement(message.statementData)}
              title="Download account statement as CSV"
            >
              📄 Download Statement
            </button>
          </div>
        )}

        {/* Feedback buttons for assistant messages */}
        {message.role === 'assistant' && (
          <div className="chat-message__feedback">
            <span className="chat-message__feedback-label">
              {language === 'hi-IN' ? 'यह उत्तर कैसा था?' : 'Was this helpful?'}
            </span>
            <div className="chat-message__feedback-buttons">
              <button
                type="button"
                className={`chat-message__feedback-btn chat-message__feedback-btn--positive ${feedbackSubmitted ? 'chat-message__feedback-btn--submitted' : ''}`}
                onClick={() => handleFeedback(true)}
                disabled={feedbackSubmitted}
                title={language === 'hi-IN' ? 'अच्छा' : 'Good response'}
              >
                👍
              </button>
              <button
                type="button"
                className={`chat-message__feedback-btn chat-message__feedback-btn--negative ${feedbackSubmitted ? 'chat-message__feedback-btn--submitted' : ''}`}
                onClick={() => handleFeedback(false)}
                disabled={feedbackSubmitted}
                title={language === 'hi-IN' ? 'बुरा' : 'Bad response'}
              >
                👎
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

ChatMessage.propTypes = {
  message: PropTypes.shape({
    id: PropTypes.number.isRequired,
    role: PropTypes.oneOf(["user", "assistant"]).isRequired,
    content: PropTypes.string.isRequired,
    timestamp: PropTypes.instanceOf(Date).isRequired,
    statementData: PropTypes.shape({
      account_number: PropTypes.string,
      account_type: PropTypes.string,
      from_date: PropTypes.string,
      to_date: PropTypes.string,
      period_type: PropTypes.string,
      current_balance: PropTypes.number,
      currency: PropTypes.string,
      transaction_count: PropTypes.number,
      transactions: PropTypes.arrayOf(PropTypes.object),
    }),
    structuredData: PropTypes.shape({
      type: PropTypes.oneOf([
        'transactions',
        'balance',
        'loan',
        'reminder',
        'transfer',
        'transfer_receipt',
        'statement_request',
        'reminder_manager',
      ]),
      transactions: PropTypes.arrayOf(PropTypes.object),
      accounts: PropTypes.arrayOf(PropTypes.object),
      loanInfo: PropTypes.object,
      reminder: PropTypes.object,
      intent: PropTypes.string,
    }),
  }).isRequired,
  userName: PropTypes.string.isRequired,
  language: PropTypes.string,
  session: PropTypes.object,
  onFeedback: PropTypes.func,
};

export default ChatMessage;
