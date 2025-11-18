import PropTypes from "prop-types";

/**
 * ChatMessage component - Displays a single chat message
 */
const ChatMessage = ({ message, userName }) => {
  // Debug: Log message data to console
  if (message.role === 'assistant') {
    console.log('📩 Assistant Message:', {
      content: message.content.substring(0, 50) + '...',
      hasStatementData: !!message.statementData,
      statementData: message.statementData,
    });
  }

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
        accountNumber: statementData.account_number,
        accountType: statementData.account_type,
        transactionCount: statementData.transactions.length,
        fromDate: statementData.from_date,
        toDate: statementData.to_date,
      });

      const csv = buildStatementCsv({
        bankName: "Sun National Bank",
        account: {
          accountNumber: statementData.account_number,
          accountType: statementData.account_type || "savings",
        },
        accountHolder: userName || "Account Holder",
        fromDate: statementData.from_date,
        toDate: statementData.to_date,
        currency: statementData.currency || "INR",
        closingBalance: statementData.current_balance,
        transactions: statementData.transactions,
      });

      console.log('✅ CSV generated successfully, length:', csv.length);

      const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      const filename = `snb_statement_${statementData.account_number}_${statementData.from_date}_to_${statementData.to_date}.csv`;
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
        <div className="chat-message__text">{message.content}</div>
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
  }).isRequired,
  userName: PropTypes.string.isRequired,
};

export default ChatMessage;
