import React, { useState, useEffect } from "react";
import * as XLSX from 'xlsx';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ChartData } from 'chart.js';
import { Chart } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

interface MonthlySalesData {
  product: string;
  month: string;
  total_sales: string;
  total_quantity: number;
}

interface MonthlyTotals {
  [month: string]: {
    totalSales: number;
    totalQuantity: number;
    products: MonthlySalesData[];
  };
}

const MonthlySalesStats: React.FC = () => {
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

  const getMonthlyTotals = (): MonthlyTotals => {
    const totals: MonthlyTotals = {};
    
    salesData.forEach((item) => {
      if (!totals[item.month]) {
        totals[item.month] = {
          totalSales: 0,
          totalQuantity: 0,
          products: []
        };
      }
      
      totals[item.month].totalSales += parseFloat(item.total_sales);
      totals[item.month].totalQuantity += item.total_quantity;
      totals[item.month].products.push(item);
    });
    
    return totals;
  };

  const getUniqueMonths = () => {
    const months = Array.from(new Set(salesData.map(item => item.month))).sort().reverse();
    return months;
  };

  const getFilteredData = () => {
    if (selectedMonth === "all") {
      return salesData;
    }
    return salesData.filter(item => item.month === selectedMonth);
  };

  const getGrandTotals = () => {
    const totalSales = salesData.reduce((sum, item) => sum + parseFloat(item.total_sales), 0);
    const totalQuantity = salesData.reduce((sum, item) => sum + item.total_quantity, 0);
    return { totalSales, totalQuantity };
  };

  // Chart data preparation
  const getChartData = (): ChartData<"bar", number[], string> => {
    const uniqueMonths = getUniqueMonths();
    const uniqueProducts = Array.from(new Set(salesData.map(item => item.product))).sort();
    const filteredData = getFilteredData();
    
    // Filter months based on selectedMonth
    const monthsToShow = selectedMonth === "all" ? uniqueMonths : [selectedMonth];
    
    // Prepare datasets for each product (sales and quantity)
    const datasets: any[] = [];
    const colors = ['#1976d2', '#388e3c', '#f57c00', '#d32f2f', '#7b1fa2', '#00796b', '#c2185b', '#5d4037', '#616161', '#455a64'];

    uniqueProducts.forEach((product, index) => {
      const color = colors[index % colors.length];
      
      // Sales dataset for this product
      const salesData = monthsToShow.map(month => {
        const item = filteredData.find(d => d.month === month && d.product === product);
        return item ? parseFloat(item.total_sales) : 0;
      });

      // Quantity dataset for this product
      const quantityData = monthsToShow.map(month => {
        const item = filteredData.find(d => d.month === month && d.product === product);
        return item ? item.total_quantity : 0;
      });

      // Add sales dataset
      datasets.push({
        type: 'bar' as const,
        label: `${product} Sales (UGX)`,
        data: salesData,
        backgroundColor: color,
        yAxisID: 'y',
        barThickness: 20,
        categoryPercentage: 0.4,
        barPercentage: 0.45
      });

      // Add quantity dataset
      datasets.push({
        type: 'bar' as const,
        label: `${product} Quantity`,
        data: quantityData,
        backgroundColor: `rgba(${parseInt(color.slice(1, 3), 16)}, ${parseInt(color.slice(3, 5), 16)}, ${parseInt(color.slice(5, 7), 16)}, 0.3)`,
        yAxisID: 'y1',
        barThickness: 20,
        categoryPercentage: 0.4,
        barPercentage: 0.45
      });
    });

    return {
      labels: monthsToShow.map(month => formatMonthYear(month)),
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
        text: selectedMonth === "all" ? 'Sales and Quantities by Product per Month' : `Product Performance for ${formatMonthYear(selectedMonth)}`,
      },
    },
    scales: {
      y: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        title: {
          display: true,
          text: 'Sales (UGX)',
        },
      },
      y1: {
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        title: {
          display: true,
          text: 'Quantity',
        },
        grid: {
          drawOnChartArea: false,
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

  const exportToExcel = () => {
    if (salesData.length === 0) {
      alert("No data to export");
      return;
    }

    interface ExcelRow {
      'S/N': number | string;
      'Product': string;
      'Month': string;
      'Total Sales (UGX)': number;
      'Total Quantity': number;
    }

    const filteredData = getFilteredData();
    const excelData: ExcelRow[] = filteredData.map((item, index) => ({
      'S/N': index + 1,
      'Product': item.product,
      'Month': formatMonthYear(item.month),
      'Total Sales (UGX)': parseFloat(item.total_sales),
      'Total Quantity': item.total_quantity
    }));

    if (selectedMonth === "all") {
      const monthlyTotals = getMonthlyTotals();
      
      excelData.push({
        'S/N': '',
        'Product': '',
        'Month': '',
        'Total Sales (UGX)': 0,
        'Total Quantity': 0
      });

      excelData.push({
        'S/N': '',
        'Product': 'MONTHLY SUMMARY',
        'Month': '',
        'Total Sales (UGX)': 0,
        'Total Quantity': 0
      });

      Object.entries(monthlyTotals).forEach(([month, data]) => {
        excelData.push({
          'S/N': '',
          'Product': formatMonthYear(month),
          'Month': '',
          'Total Sales (UGX)': data.totalSales,
          'Total Quantity': data.totalQuantity
        });
      });
    }

    const grandTotals = selectedMonth === "all" ? getGrandTotals() : 
      filteredData.reduce((acc, item) => ({
        totalSales: acc.totalSales + parseFloat(item.total_sales),
        totalQuantity: acc.totalQuantity + item.total_quantity
      }), { totalSales: 0, totalQuantity: 0 });

    excelData.push({
      'S/N': '',
      'Product': 'GRAND TOTAL',
      'Month': '',
      'Total Sales (UGX)': grandTotals.totalSales,
      'Total Quantity': grandTotals.totalQuantity
    });

    const ws = XLSX.utils.json_to_sheet(excelData);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Monthly Sales");

    const colWidths = [
      { wch: 8 },   // S/N
      { wch: 20 },  // Product
      { wch: 15 },  // Month
      { wch: 18 },  // Total Sales
      { wch: 15 }   // Total Quantity
    ];
    ws['!cols'] = colWidths;

    const today = new Date().toISOString().split('T')[0];
    const monthFilter = selectedMonth === "all" ? "all" : selectedMonth;
    const filename = `monthly_sales_${monthFilter}_${today}.xlsx`;

    XLSX.writeFile(wb, filename);
  };

  const exportToPDF = () => {
    if (salesData.length === 0) {
      alert("No data to export");
      return;
    }

    const printWindow = window.open('', '_blank');
    if (!printWindow) {
      alert("Please allow popups for PDF export");
      return;
    }

    const today = new Date().toLocaleDateString();
    const filteredData = getFilteredData();
    const monthlyTotals = getMonthlyTotals();
    const grandTotals = selectedMonth === "all" ? getGrandTotals() : 
      filteredData.reduce((acc, item) => ({
        totalSales: acc.totalSales + parseFloat(item.total_sales),
        totalQuantity: acc.totalQuantity + item.total_quantity
      }), { totalSales: 0, totalQuantity: 0 });

    const htmlContent = `
      <!DOCTYPE html>
      <html>
        <head>
          <title>Monthly Sales Report</title>
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
            .amount, .quantity {
              text-align: right;
            }
            .total-row, .monthly-header {
              background-color: #e3f2fd !important;
              font-weight: bold;
            }
            .grand-total-row {
              background-color: #1976d2 !important;
              color: white;
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
            }
          </style>
        </head>
        <body>
          <div class="header">
            <h1>Monthly Sales Report</h1>
            <p>Generated on: ${today}</p>
            <p>Filter: ${selectedMonth === "all" ? "All Months" : formatMonthYear(selectedMonth)}</p>
            <p>Total Records: ${filteredData.length}</p>
          </div>
          
          <div class="summary">
            <h3>Grand Total Sales: UGX ${formatAmount(grandTotals.totalSales)} | Total Quantity: ${grandTotals.totalQuantity}</h3>
          </div>

          <table>
            <thead>
              <tr>
                <th>S/N</th>
                <th>Product</th>
                <th>Month</th>
                <th>Total Sales (UGX)</th>
                <th>Total Quantity</th>
              </tr>
            </thead>
            <tbody>
              ${filteredData.map((item, index) => `
                <tr>
                  <td>${index + 1}</td>
                  <td>${item.product}</td>
                  <td>${formatMonthYear(item.month)}</td>
                  <td class="amount">${formatAmount(item.total_sales)}</td>
                  <td class="quantity">${item.total_quantity}</td>
                </tr>
              `).join('')}
              
              ${selectedMonth === "all" ? `
                <tr><td colspan="5" style="border: none; padding: 20px;"></td></tr>
                <tr class="monthly-header">
                  <td colspan="5" style="text-align: center;"><strong>MONTHLY SUMMARY</strong></td>
                </tr>
                ${Object.entries(monthlyTotals).map(([month, data]) => `
                  <tr class="total-row">
                    <td></td>
                    <td><strong>${formatMonthYear(month)}</strong></td>
                    <td></td>
                    <td class="amount"><strong>${formatAmount(data.totalSales)}</strong></td>
                    <td class="quantity"><strong>${data.totalQuantity}</strong></td>
                  </tr>
                `).join('')}
              ` : ''}
              
              <tr class="grand-total-row">
                <td colspan="3"><strong>GRAND TOTAL</strong></td>
                <td class="amount"><strong>${formatAmount(grandTotals.totalSales)}</strong></td>
                <td class="quantity"><strong>${grandTotals.totalQuantity}</strong></td>
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

  const monthlyTotals = getMonthlyTotals();
  const uniqueMonths = getUniqueMonths();
  const filteredData = getFilteredData();
  const grandTotals = getGrandTotals();

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
            onClick={exportToExcel} 
            className="refresh-btn"
            style={{ 
              background: "#2e7d32",
              minWidth: "120px"
            }}
            disabled={salesData.length === 0}
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
            disabled={salesData.length === 0}
          >
            Export PDF
          </button>
          <button onClick={fetchMonthlySales} className="refresh-btn">
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
            <span>
              Total Sales: UGX {formatAmount(selectedMonth === "all" ? grandTotals.totalSales : 
                filteredData.reduce((sum, item) => sum + parseFloat(item.total_sales), 0))}
            </span>
          </div>

          {/* Chart Section */}
          <div style={{ margin: "2rem 0", maxWidth: "800px", marginLeft: "auto", marginRight: "auto" }}>
            <Chart type="bar" data={getChartData()} options={chartOptions} />
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
                
                {selectedMonth === "all" && Object.keys(monthlyTotals).length > 1 && (
                  <>
                    <tr><td colSpan={6} style={{ border: "none", padding: "10px" }}></td></tr>
                    <tr style={{ background: "#e3f2fd", fontWeight: "bold" }}>
                      <td colSpan={6} style={{ textAlign: "center" }}>
                        <strong>📊 MONTHLY SUMMARY</strong>
                      </td>
                    </tr>
                    {Object.entries(monthlyTotals).map(([month, data]) => (
                      <tr key={`total-${month}`} style={{ background: "#f0f8ff", fontWeight: "bold" }}>
                        <td></td>
                        <td><strong>{formatMonthYear(month)}</strong></td>
                        <td></td>
                        <td><strong>{formatAmount(data.totalSales)}</strong></td>
                        <td><strong>{data.totalQuantity}</strong></td>
                        <td><strong>{formatAmount(data.totalSales / data.totalQuantity)}</strong></td>
                      </tr>
                    ))}
                  </>
                )}
                
                <tr style={{ background: "#1976d2", color: "white", fontWeight: "bold" }}>
                  <td colSpan={3}><strong>🎯 GRAND TOTAL</strong></td>
                  <td><strong>{formatAmount(selectedMonth === "all" ? grandTotals.totalSales : 
                    filteredData.reduce((sum, item) => sum + parseFloat(item.total_sales), 0))}</strong></td>
                  <td><strong>{selectedMonth === "all" ? grandTotals.totalQuantity : 
                    filteredData.reduce((sum, item) => sum + item.total_quantity, 0)}</strong></td>
                  <td><strong>{formatAmount((selectedMonth === "all" ? grandTotals.totalSales : 
                    filteredData.reduce((sum, item) => sum + parseFloat(item.total_sales), 0)) /
                    (selectedMonth === "all" ? grandTotals.totalQuantity : 
                    filteredData.reduce((sum, item) => sum + item.total_quantity, 0)))}</strong></td>
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
            Showing {filteredData.length} record{filteredData.length !== 1 ? "s" : ""} 
            {selectedMonth !== "all" && ` for ${formatMonthYear(selectedMonth)}`}
          </div>
        </>
      )}
    </div>
  );
};

export default MonthlySalesStats;