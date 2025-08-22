import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import AddProduct from "./AddProduct";
import AddSale from "./AddSale";
import AddPurchase from "./AddPurchase";
import AddExpense from "./AddExpense";
import ProfitReports from "./ProfitReports";
import StockStats from "./StockStats";
import "./AdminDashboard.css";

const AdminDashboard: React.FC = () => {
  const [active, setActive] = useState("add-product");
  const navigate = useNavigate();

  const handleLogout = () => {
    // Clear any stored tokens
    localStorage.removeItem('userToken');
    navigate("/");
  };

  return (
    <div className="dashboard-container">
      <aside className="dashboard-sidebar">
        <h3>Admin</h3>
        <ul>
          <li className={active === "add-product" ? "active" : ""} onClick={() => setActive("add-product")}>
            Add Product
          </li>
          <li className={active === "add-sale" ? "active" : ""} onClick={() => setActive("add-sale")}>
            Add Sale
          </li>
          <li className={active === "add-purchase" ? "active" : ""} onClick={() => setActive("add-purchase")}>
            Add Purchase
          </li>
          <li className={active === "add-expense" ? "active" : ""} onClick={() => setActive("add-expense")}>
            Add Expense
          </li>
          <li className={active === "profit-reports" ? "active" : ""} onClick={() => setActive("profit-reports")}>
            Profit Reports
          </li>
          <li className={active === "stock-stats" ? "active" : ""} onClick={() => setActive("stock-stats")}>
            Stock Stats
          </li>
        </ul>
        <button className="logout-btn" onClick={handleLogout}>
          LOGOUT
        </button>
      </aside>
      <main className="dashboard-main">
        {active === "add-product" && <AddProduct />}
        {active === "add-sale" && <AddSale />}
        {active === "add-purchase" && <AddPurchase />}
        {active === "add-expense" && <AddExpense />}
        {active === "profit-reports" && <ProfitReports />}
        {active === "stock-stats" && <StockStats />}
      </main>
    </div>
  );
};

export default AdminDashboard;