import React, { useState } from "react";
import axios from "axios";

const AddExpense: React.FC = () => {
  const [form, setForm] = useState({ title: "", amount: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);
    try {
      await axios.post("https://e-accoutant.onrender.com/api/expenses/", {
        title: form.title,
        amount: Number(form.amount),
      });
      setSuccess(true);
      setForm({ title: "", amount: "" });
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to add expense");
    }
    setLoading(false);
  };

  return (
    <div className="dashboard-content expense-content">
      <h2>Add Expense</h2>
      <form className="expense-form" onSubmit={handleSubmit}>
        <input
          type="text"
          name="title"
          placeholder="Expense Title"
          value={form.title}
          onChange={handleChange}
          required
        />
        <input
          type="number"
          name="amount"
          placeholder="Amount"
          value={form.amount}
          onChange={handleChange}
          required
          min={0}
          step="0.01"
        />
        <button type="submit" disabled={loading}>
          {loading ? "Adding..." : "Add Expense"}
        </button>
        {error && <div className="error">{error}</div>}
        {success && <div className="success">Expense added successfully!</div>}
      </form>
    </div>
  );
};

export default AddExpense;