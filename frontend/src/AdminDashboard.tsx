import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import AddProduct from "./AddProduct";
import AddSale from "./AddSale";
import AddPurchase from "./AddPurchase";
import "./AdminDashboard.css";

const AdminDashboard: React.FC = () => {
  const [active, setActive] = useState("add-product");
  const navigate = useNavigate();

  const handleLogout = () => {
    // Clear any stored tokens here if you use them
    navigate("/");
  };

  return (
    <div className="dashboard-container">
      <aside className="dashboard-sidebar">
        <h3>Admin</h3>
        <ul>
          <li
            className={active === "add-product" ? "active" : ""}
            onClick={() => setActive("add-product")}
          >
            Add Product
          </li>
          <li
            className={active === "add-sale" ? "active" : ""}
            onClick={() => setActive("add-sale")}
          >
            Add Sale
          </li>
          <li
            className={active === "add-purchase" ? "active" : ""}
            onClick={() => setActive("add-purchase")}
          >
            Add Purchase
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
      </main>
    </div>
  );
};

export default AdminDashboard;