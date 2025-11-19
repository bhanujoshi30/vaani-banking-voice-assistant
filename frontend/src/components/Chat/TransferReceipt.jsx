import React, { useRef } from 'react';
import html2canvas from 'html2canvas';
import './TransferReceipt.css';

const TransferReceipt = ({ receipt, language = 'en-IN' }) => {
  const receiptRef = useRef(null);
  
  if (!receipt) return null;

  const formatDate = (timestamp) => {
    if (!timestamp) return '—';
    try {
      const date = new Date(timestamp);
      return date.toLocaleString(language === 'hi-IN' ? 'hi-IN' : 'en-IN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        timeZone: 'Asia/Kolkata'
      });
    } catch (e) {
      return timestamp;
    }
  };

  const formatAmount = (amount) => {
    return `₹${parseFloat(amount).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  const handleSaveReceipt = async () => {
    if (!receiptRef.current) return;

    try {
      // Hide the save button before capturing
      const saveButton = receiptRef.current.querySelector('.transfer-receipt__save-btn');
      if (saveButton) {
        saveButton.style.display = 'none';
      }

      // Capture the receipt as canvas
      const canvas = await html2canvas(receiptRef.current, {
        backgroundColor: '#ffffff',
        scale: 2, // Higher quality
        logging: false,
        useCORS: true,
      });

      // Convert canvas to blob
      canvas.toBlob((blob) => {
        if (!blob) {
          alert(language === 'hi-IN' ? 'रसीद सहेजने में त्रुटि' : 'Error saving receipt');
          return;
        }

        // Create download link
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        
        // Generate filename with timestamp and reference number
        const timestamp = receipt.timestamp 
          ? new Date(receipt.timestamp).toISOString().split('T')[0]
          : new Date().toISOString().split('T')[0];
        const refId = receipt.referenceId || 'N/A';
        link.download = `transfer_receipt_${timestamp}_${refId}.png`;
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
      }, 'image/png');
      
      // Show the save button again after capturing
      if (saveButton) {
        saveButton.style.display = '';
      }
    } catch (error) {
      console.error('Error saving receipt:', error);
      alert(language === 'hi-IN' ? 'रसीद सहेजने में त्रुटि' : 'Error saving receipt');
      
      // Make sure to show button again even on error
      const saveButton = receiptRef.current?.querySelector('.transfer-receipt__save-btn');
      if (saveButton) {
        saveButton.style.display = '';
      }
    }
  };

  return (
    <div className="transfer-receipt" ref={receiptRef}>
      <div className="transfer-receipt__header">
        <h3 className="transfer-receipt__title">
          {language === 'hi-IN' ? 'ट्रांसफर रसीद' : 'Transfer Receipt'}
        </h3>
        <div className="transfer-receipt__status">
          <span className="transfer-receipt__status-badge transfer-receipt__status-badge--success">
            {language === 'hi-IN' ? 'सफल' : 'Success'}
          </span>
        </div>
      </div>
      
      <div className="transfer-receipt__content">
        <table className="transfer-receipt__table">
          <tbody>
            <tr>
              <td className="transfer-receipt__label">
                {language === 'hi-IN' ? 'राशि' : 'Amount'}
              </td>
              <td className="transfer-receipt__value transfer-receipt__value--amount">
                {formatAmount(receipt.amount)}
              </td>
            </tr>
            <tr>
              <td className="transfer-receipt__label">
                {language === 'hi-IN' ? 'से खाता' : 'From Account'}
              </td>
              <td className="transfer-receipt__value">
                {receipt.sourceAccountNumber || '—'}
              </td>
            </tr>
            <tr>
              <td className="transfer-receipt__label">
                {language === 'hi-IN' ? 'लाभार्थी' : 'Beneficiary'}
              </td>
              <td className="transfer-receipt__value">
                {receipt.beneficiaryName || '—'}
              </td>
            </tr>
            <tr>
              <td className="transfer-receipt__label">
                {language === 'hi-IN' ? 'लाभार्थी खाता संख्या' : 'Beneficiary Account'}
              </td>
              <td className="transfer-receipt__value">
                {receipt.destinationAccountNumber || '—'}
              </td>
            </tr>
            <tr>
              <td className="transfer-receipt__label">
                {language === 'hi-IN' ? 'समय' : 'Time'}
              </td>
              <td className="transfer-receipt__value">
                {formatDate(receipt.timestamp)}
              </td>
            </tr>
            <tr>
              <td className="transfer-receipt__label">
                {language === 'hi-IN' ? 'संदर्भ संख्या' : 'Reference Number'}
              </td>
              <td className="transfer-receipt__value transfer-receipt__value--reference">
                {receipt.referenceId || '—'}
              </td>
            </tr>
            {receipt.description && (
              <tr>
                <td className="transfer-receipt__label">
                  {language === 'hi-IN' ? 'विवरण' : 'Description'}
                </td>
                <td className="transfer-receipt__value">
                  {receipt.description}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      
      <div className="transfer-receipt__actions">
        <button
          type="button"
          className="transfer-receipt__save-btn"
          onClick={handleSaveReceipt}
          title={language === 'hi-IN' ? 'रसीद को छवि के रूप में सहेजें' : 'Save receipt as image'}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 12V19H5V12H3V19C3 20.1 3.9 21 5 21H19C20.1 21 21 20.1 21 19V12H19Z" fill="currentColor"/>
            <path d="M13 12.67L15.59 10.09L17 11.5L12 16.5L7 11.5L8.41 10.09L11 12.67V3H13V12.67Z" fill="currentColor"/>
          </svg>
          {language === 'hi-IN' ? 'रसीद सहेजें' : 'Save Receipt'}
        </button>
      </div>
    </div>
  );
};

export default TransferReceipt;

