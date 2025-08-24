


import React, { useState, useEffect } from "react";
//import * as XLSX from 'xlsx';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, ChartData } from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const COLORS = [
  '#1976d2', '#388e3c', '#f57c00', '#d32f2f', '#7b1fa2', '#00796b', '#c2185b', '#5d4037', '#616161', '#455a64'
];

interface MonthlySalesData {
  product: string;
  month: string;
  total_sales: string;
  total_quantity: number;
}

export const MonthlySalesStats: React.FC = () => {
  const [salesData, setSalesData] = useState<MonthlySalesData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedMonth, setSelectedMonth] = useState<string>("all");

  const fetchMonthlySales = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch("https://e-accoutant.onrender.com/api/monthly-sales/");
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data: MonthlySalesData[] = await response.json();
      setSalesData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch monthly sales data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMonthlySales();
  }, []);

  const formatAmount = (amount: string | number) => {
    const numAmount = typeof amount === 'string' ? parseFloat(amount) : amount;
    return numAmount.toLocaleString("en-US", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  };

  const formatMonthYear = (monthString: string) => {
    const [year, month] = monthString.split('-');
    const date = new Date(parseInt(year), parseInt(month) - 1);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "long"
    });
  };

  const getUniqueMonths = () => {
    const months = Array.from(new Set(salesData.map(item => item.month))).sort();
    return months;
  };

  const getFilteredData = () => {
    if (selectedMonth === "all") {
      return salesData;
    }
    return salesData.filter(item => item.month === selectedMonth);
  };

  // Chart data preparation (Line Chart for Sales)
  const getChartData = (): ChartData<"line", number[], string> => {
    const uniqueMonths = getUniqueMonths();
    const uniqueProducts = Array.from(new Set(salesData.map(item => item.product))).sort();
    const filteredData = getFilteredData();

    const datasets = uniqueProducts.map((product, index) => {
      const color = COLORS[index % COLORS.length];
      const salesDataArr = uniqueMonths.map(month => {
        const item = filteredData.find(d => d.month === month && d.product === product);
        return item ? parseFloat(item.total_sales) : 0;
      });
      return {
        label: `${product} Sales (UGX)`,
        data: salesDataArr,
        borderColor: color,
        backgroundColor: color + "33",
        tension: 0.3,
        fill: false,
        pointRadius: 4,
        pointHoverRadius: 6,
      };
    });

    return {
      labels: uniqueMonths.map(month => formatMonthYear(month)),
      datasets
    };
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: selectedMonth === "all"
          ? 'Monthly Sales Trend by Product'
          : `Product Sales for ${formatMonthYear(selectedMonth)}`,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Sales (UGX)',
        },
      },
      x: {
        title: {
          display: true,
          text: 'Month'
        }
      }
    },
  };

  if (loading) {
    return (
      <div className="dashboard-content stock-stats-container">
        <div className="loading">Loading monthly sales data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-content stock-stats-container">
        <div className="error">Error: {error}</div>
        <button 
          onClick={fetchMonthlySales}
          className="refresh-btn"
          style={{ marginTop: "1rem" }}
        >
          Retry
        </button>
      </div>
    );
  }

  const uniqueMonths = getUniqueMonths();
  const filteredData = getFilteredData();

  return (
    <div className="dashboard-content stock-stats-container">
      <div className="stock-stats-header">
        <h2>Monthly Sales Statistics</h2>
        <div style={{ display: "flex", gap: "10px", flexWrap: "wrap", alignItems: "center" }}>
          <select 
            value={selectedMonth} 
            onChange={(e) => setSelectedMonth(e.target.value)}
            style={{
              padding: "0.5rem",
              borderRadius: "4px",
              border: "1px solid #ccc",
              minWidth: "150px"
            }}
          >
            <option value="all">All Months</option>
            {uniqueMonths.map(month => (
              <option key={month} value={month}>
                {formatMonthYear(month)}
              </option>
            ))}
          </select>
          <button 
            onClick={fetchMonthlySales} 
            className="refresh-btn"
          >
            Refresh
          </button>
        </div>
      </div>

      {salesData.length === 0 ? (
        <div className="no-data">No sales data found</div>
      ) : (
        <>
          <div style={{ 
            marginBottom: "1rem", 
            fontSize: "1.1rem", 
            fontWeight: "bold",
            display: "flex",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: "10px"
          }}>
            <span>
              Showing: {selectedMonth === "all" ? "All Months" : formatMonthYear(selectedMonth)}
            </span>
          </div>

          {/* Chart Section */}
          <div style={{ margin: "2rem 0", maxWidth: "900px", marginLeft: "auto", marginRight: "auto" }}>
            <Line data={getChartData()} options={chartOptions} />
          </div>

          {/* Data Table */}
          <div style={{ overflowX: "auto" }}>
            <table className="profit-table">
              <thead>
                <tr>
                  <th>S/N</th>
                  <th>Product</th>
                  <th>Month</th>
                  <th>Total Sales (UGX)</th>
                  <th>Total Quantity</th>
                  <th>Avg Price/Unit</th>
                </tr>
              </thead>
              <tbody>
                {filteredData.map((item, index) => (
                  <tr key={`${item.product}-${item.month}`}>
                    <td>{index + 1}</td>
                    <td>{item.product}</td>
                    <td>{formatMonthYear(item.month)}</td>
                    <td>{formatAmount(item.total_sales)}</td>
                    <td>{item.total_quantity}</td>
                    <td>{formatAmount(parseFloat(item.total_sales) / item.total_quantity)}</td>
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
            Showing {filteredData.length} record{filteredData.length !== 1 ? "s" : ""} 
            {selectedMonth !== "all" && ` for ${formatMonthYear(selectedMonth)}`}
          </div>
        </>
      )}
    </div>
  );
};

export default MonthlySalesStats;