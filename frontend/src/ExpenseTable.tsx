import React, { useState, useEffect } from "react";

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
        <button onClick={fetchExpenses} className="refresh-btn">
          Refresh
        </button>
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
                  <th>ID</th>
                  <th>Title</th>
                  <th>Amount (UGX)</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {expenses.map((expense) => (
                  <tr key={expense.id}>
                    <td>{expense.id}</td>
                    <td>{expense.title}</td>
                    <td>{formatAmount(expense.amount)}</td>
                    <td>{formatDate(expense.date)}</td>
                  </tr>
                ))}
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