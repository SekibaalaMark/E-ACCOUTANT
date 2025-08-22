import React, { useState } from "react";
import axios from "axios";
import * as XLSX from "xlsx";
import { saveAs } from "file-saver";
import jsPDF from "jspdf";
// @ts-ignore
import autoTable from 'jspdf-autotable';

interface ProfitData {
  period: string;
  revenue: number;
  cogs: number;
  expenses: number;
  profit: number;
}

const ProfitReports: React.FC = () => {
  const [period, setPeriod] = useState<"daily" | "monthly" | "yearly">("daily");
  const [data, setData] = useState<ProfitData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get(
        `https://e-accoutant.onrender.com/api/profits/?period=${period}`
      );
      setData(res.data);
    } catch (err: any) {
      setError("Failed to fetch profit data");
    }
    setLoading(false);
  };

  const exportExcel = () => {
    const ws = XLSX.utils.json_to_sheet(data);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Profits");
    const excelBuffer = XLSX.write(wb, { bookType: "xlsx", type: "array" });
    const blob = new Blob([excelBuffer], { type: "application/octet-stream" });
    saveAs(blob, `profits_${period}.xlsx`);
  };

  const exportPDF = () => {
    const doc = new jsPDF();
    doc.text(`Profit Report (${period})`, 14, 16);
    
    autoTable(doc, {
      startY: 22,
      head: [["Period", "Revenue", "COGS", "Expenses", "Profit"]],
      body: data.map((row) => [
        row.period,
        row.revenue.toLocaleString(),
        row.cogs.toLocaleString(),
        row.expenses.toLocaleString(),
        row.profit.toLocaleString(),
      ]),
      styles: { fontSize: 8 },
      headStyles: { fillColor: [25, 118, 210] },
    });
    
    doc.save(`profits_${period}.pdf`);
  };

  return (
    <div className="dashboard-content large-form-content">
      <h2>Profit Reports</h2>
      <div style={{ display: "flex", gap: "1rem", marginBottom: "1.5rem" }}>
        <select
          value={period}
          onChange={(e) => setPeriod(e.target.value as any)}
          style={{ padding: "0.7rem", fontSize: "1rem" }}
        >
          <option value="daily">Daily</option>
          <option value="monthly">Monthly</option>
          <option value="yearly">Yearly</option>
        </select>
        <button onClick={fetchData} style={{ padding: "0.7rem 1.5rem" }}>
          Get Report
        </button>
        {data.length > 0 && (
          <>
            <button onClick={exportExcel} style={{ padding: "0.7rem 1.5rem" }}>
              Export Excel
            </button>
            <button onClick={exportPDF} style={{ padding: "0.7rem 1.5rem" }}>
              Export PDF
            </button>
          </>
        )}
      </div>
      {loading && <div>Loading...</div>}
      {error && <div className="error">{error}</div>}
      {data.length > 0 && (
        <div style={{ overflowX: "auto" }}>
          <table className="profit-table">
            <thead>
              <tr>
                <th>Period</th>
                <th>Revenue</th>
                <th>COGS</th>
                <th>Expenses</th>
                <th>Profit</th>
              </tr>
            </thead>
            <tbody>
              {data.map((row, idx) => (
                <tr key={idx}>
                  <td>{row.period}</td>
                  <td>{row.revenue.toLocaleString()}</td>
                  <td>{row.cogs.toLocaleString()}</td>
                  <td>{row.expenses.toLocaleString()}</td>
                  <td>{row.profit.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default ProfitReports;