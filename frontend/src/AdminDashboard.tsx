import React, { useState } from "react";
import AddProduct from "./AddProduct";
import AddSale from "./AddSale";
import "./AdminDashboard.css";

const AdminDashboard: React.FC = () => {
  const [active, setActive] = useState("add-product");

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
        </ul>
      </aside>
      <main className="dashboard-main">
        {active === "add-product" && <AddProduct />}
        {active === "add-sale" && <AddSale />}
      </main>
    </div>
  );
};

export default AdminDashboard;