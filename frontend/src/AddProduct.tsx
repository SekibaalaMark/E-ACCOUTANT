import React, { useState } from "react";
import axios from "axios";

const AddProduct: React.FC = () => {
  const [form, setForm] = useState({
    name: "",
    brand: "",
    stock: "",
    buying_price: "",
    selling_price: "",
  });
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
      await axios.post("https://e-accoutant.onrender.com/api/products/", {
        ...form,
        stock: Number(form.stock),
        buying_price: Number(form.buying_price),
        selling_price: Number(form.selling_price),
      });
      setSuccess(true);
      setForm({
        name: "",
        brand: "",
        stock: "",
        buying_price: "",
        selling_price: "",
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to add product");
    }
    setLoading(false);
  };

  return (
    <div className="dashboard-content large-form-content">
      <h2>Add Product</h2>
      <form className="product-form" onSubmit={handleSubmit}>
        <input
          type="text"
          name="name"
          placeholder="Product Name"
          value={form.name}
          onChange={handleChange}
          required
        />
        <input
          type="text"
          name="brand"
          placeholder="Brand"
          value={form.brand}
          onChange={handleChange}
          required
        />
        <input
          type="number"
          name="stock"
          placeholder="Stock"
          value={form.stock}
          onChange={handleChange}
          required
          min={0}
        />
        <input
          type="number"
          name="buying_price"
          placeholder="Buying Price"
          value={form.buying_price}
          onChange={handleChange}
          required
          min={0}
          step="0.01"
        />
        <input
          type="number"
          name="selling_price"
          placeholder="Selling Price"
          value={form.selling_price}
          onChange={handleChange}
          required
          min={0}
          step="0.01"
        />
        <button type="submit" disabled={loading}>
          {loading ? "Adding..." : "Add Product"}
        </button>
        {error && <div className="error">{error}</div>}
        {success && <div className="success">Product added successfully!</div>}
      </form>
    </div>
  );
};

export default AddProduct;