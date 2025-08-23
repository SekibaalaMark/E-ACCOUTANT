import React, { useState, useEffect } from "react";
import * as XLSX from 'xlsx';

interface Expense {
  id: number;
  title: string;
  amount: string;
  date: string;
}

const ExpenseTable: React.FC = () => {
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchExpenses = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch("https://e-accoutant.onrender.com/api/expenses/");
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data: Expense[] = await response.json();
      setExpenses(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch expenses");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExpenses();
  }, []);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    });
  };

  const formatAmount = (amount: string) => {
    return parseFloat(amount).toLocaleString("en-US", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  };

  const getTotalAmount = () => {
    return expenses.reduce((total, expense) => total + parseFloat(expense.amount), 0);
  };

  const exportToExcel = () => {
    if (expenses.length === 0) {
      alert("No data to export");
      return;
    }

    // Define the type for Excel data
    interface ExcelRow {
      'S/N': number | string;
      'ID': number | string;
      'Title': string;
      'Amount (UGX)': number;
      'Date': string;
    }

    // Prepare data for Excel
    const excelData: ExcelRow[] = expenses.map((expense, index) => ({
      'S/N': index + 1,
      'ID': expense.id,
      'Title': expense.title,
      'Amount (UGX)': parseFloat(expense.amount),
      'Date': formatDate(expense.date)
    }));

    // Add total row
    excelData.push({
      'S/N': '',
      'ID': '',
      'Title': 'TOTAL',
      'Amount (UGX)': getTotalAmount(),
      'Date': ''
    });

    // Create workbook and worksheet
    const ws = XLSX.utils.json_to_sheet(excelData);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Expenses");

    // Style the header row
    const range = XLSX.utils.decode_range(ws['!ref'] || 'A1');
    for (let col = range.s.c; col <= range.e.c; col++) {
      const cellAddress = XLSX.utils.encode_cell({ r: 0, c: col });
      if (!ws[cellAddress]) continue;
      ws[cellAddress].s = {
        font: { bold: true },
        fill: { fgColor: { rgb: "1976D2" } }
      };
    }

    // Auto-size columns
    const colWidths = [
      { wch: 8 },   // S/N
      { wch: 8 },   // ID
      { wch: 20 },  // Title
      { wch: 15 },  // Amount
      { wch: 20 }   // Date
    ];
    ws['!cols'] = colWidths;

    // Generate filename with current date
    const today = new Date().toISOString().split('T')[0];
    const filename = `expenses_${today}.xlsx`;

    // Save file
    XLSX.writeFile(wb, filename);
  };

  const exportToPDF = () => {
    if (expenses.length === 0) {
      alert("No data to export");
      return;
    }

    // Create a new window for PDF generation
    const printWindow = window.open('', '_blank');
    if (!printWindow) {
      alert("Please allow popups for PDF export");
      return;
    }

    const today = new Date().toLocaleDateString();
    const totalAmount = getTotalAmount();

    // Generate HTML content for PDF
    const htmlContent = `
      <!DOCTYPE html>
      <html>
        <head>
          <title>Expense Report</title>
          <style>
            body {
              font-family: Arial, sans-serif;
              margin: 20px;
              color: #333;
            }
            .header {
              text-align: center;
              margin-bottom: 30px;
              border-bottom: 2px solid #1976d2;
              padding-bottom: 10px;
            }
            .header h1 {
              color: #1976d2;
              margin: 0;
            }
            .header p {
              margin: 5px 0;
              color: #666;
            }
            .summary {
              background: #f5f5f5;
              padding: 15px;
              border-radius: 5px;
              margin-bottom: 20px;
              text-align: center;
            }
            .summary h3 {
              margin: 0;
              color: #1976d2;
            }
            table {
              width: 100%;
              border-collapse: collapse;
              margin-bottom: 20px;
            }
            th, td {
              border: 1px solid #ddd;
              padding: 12px;
              text-align: left;
            }
            th {
              background-color: #1976d2;
              color: white;
              font-weight: bold;
            }
            tr:nth-child(even) {
              background-color: #f9f9f9;
            }
            .amount {
              text-align: right;
            }
            .total-row {
              background-color: #e3f2fd !important;
              font-weight: bold;
            }
            .footer {
              margin-top: 30px;
              text-align: center;
              font-size: 12px;
              color: #666;
              border-top: 1px solid #ddd;
              padding-top: 10px;
            }
            @media print {
              body { margin: 0; }
              .no-print { display: none; }
            }
          </style>
        </head>
        <body>
          <div class="header">
            <h1>Expense Report</h1>
            <p>Generated on: ${today}</p>
            <p>Total Records: ${expenses.length}</p>
          </div>
          
          <div class="summary">
            <h3>Total Expenses: UGX ${formatAmount(totalAmount.toString())}</h3>
          </div>

          <table>
            <thead>
              <tr>
                <th>S/N</th>
                <th>ID</th>
                <th>Title</th>
                <th>Amount (UGX)</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              ${expenses.map((expense, index) => `
                <tr>
                  <td>${index + 1}</td>
                  <td>${expense.id}</td>
                  <td>${expense.title}</td>
                  <td class="amount">${formatAmount(expense.amount)}</td>
                  <td>${formatDate(expense.date)}</td>
                </tr>
              `).join('')}
              <tr class="total-row">
                <td colspan="3"><strong>TOTAL</strong></td>
                <td class="amount"><strong>${formatAmount(totalAmount.toString())}</strong></td>
                <td></td>
              </tr>
            </tbody>
          </table>

          <div class="footer">
            <p>This report was generated automatically from the E-Accountant system.</p>
          </div>

          <script>
            window.onload = function() {
              setTimeout(function() {
                window.print();
                window.close();
              }, 500);
            };
          </script>
        </body>
      </html>
    `;

    printWindow.document.write(htmlContent);
    printWindow.document.close();
  };

  if (loading) {
    return (
      <div className="dashboard-content large-form-content">
        <div className="loading">Loading expenses...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-content large-form-content">
        <div className="error">Error: {error}</div>
        <button 
          onClick={fetchExpenses}
          className="refresh-btn"
          style={{ marginTop: "1rem" }}
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="dashboard-content large-form-content">
      <div className="stock-stats-header">
        <h2>Expense Records</h2>
        <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
          <button 
            onClick={exportToExcel} 
            className="refresh-btn"
            style={{ 
              background: "#2e7d32",
              minWidth: "120px"
            }}
            disabled={expenses.length === 0}
          >
            Export Excel
          </button>
          <button 
            onClick={exportToPDF} 
            className="refresh-btn"
            style={{ 
              background: "#d32f2f",
              minWidth: "120px"
            }}
            disabled={expenses.length === 0}
          >
            Export PDF
          </button>
          <button onClick={fetchExpenses} className="refresh-btn">
            Refresh
          </button>
        </div>
      </div>

      {expenses.length === 0 ? (
        <div className="no-data">No expenses found</div>
      ) : (
        <>
          <div style={{ marginBottom: "1rem", fontSize: "1.1rem", fontWeight: "bold" }}>
            Total Expenses: UGX {formatAmount(getTotalAmount().toString())}
          </div>
          
          <div style={{ overflowX: "auto" }}>
            <table className="profit-table">
              <thead>
                <tr>
                  <th>S/N</th>
                  <th>ID</th>
                  <th>Title</th>
                  <th>Amount (UGX)</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {expenses.map((expense, index) => (
                  <tr key={expense.id}>
                    <td>{index + 1}</td>
                    <td>{expense.id}</td>
                    <td>{expense.title}</td>
                    <td>{formatAmount(expense.amount)}</td>
                    <td>{formatDate(expense.date)}</td>
                  </tr>
                ))}
                <tr style={{ background: "#e3f2fd", fontWeight: "bold" }}>
                  <td colSpan={3}><strong>TOTAL</strong></td>
                  <td><strong>{formatAmount(getTotalAmount().toString())}</strong></td>
                  <td></td>
                </tr>
              </tbody>
            </table>
          </div>

          <div style={{ 
            marginTop: "1rem", 
            fontSize: "0.9rem", 
            color: "#666", 
            textAlign: "center" 
          }}>
            Showing {expenses.length} expense{expenses.length !== 1 ? "s" : ""}
          </div>
        </>
      )}
    </div>
  );
};

export default ExpenseTable;