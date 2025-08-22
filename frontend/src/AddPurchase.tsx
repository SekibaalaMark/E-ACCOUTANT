import React, { useEffect, useState } from "react";
import axios from "axios";

interface Product {
  id: number;
  name: string;
  brand: string;
}

const AddPurchase: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [form, setForm] = useState({ product: "", quantity: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    axios
      .get("https://e-accoutant.onrender.com/api/products/")
      .then((res) => setProducts(res.data))
      .catch(() => setProducts([]));
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement | HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);
    try {
      await axios.post("https://e-accoutant.onrender.com/api/purchases/", {
        product: Number(form.product),
        quantity: Number(form.quantity),
      });
      setSuccess(true);
      setForm({ product: "", quantity: "" });
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to add purchase");
    }
    setLoading(false);
  };

  return (
    <div className="dashboard-content">
      <h2>Add Purchase</h2>
      <form className="product-form" onSubmit={handleSubmit}>
        <select
          name="product"
          value={form.product}
          onChange={handleChange}
          required
        >
          <option value="">Select Product</option>
          {products.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name} ({p.brand})
            </option>
          ))}
        </select>
        <input
          type="number"
          name="quantity"
          placeholder="Quantity"
          value={form.quantity}
          onChange={handleChange}
          required
          min={1}
        />
        <button type="submit" disabled={loading}>
          {loading ? "Adding..." : "Add Purchase"}
        </button>
        {error && <div className="error">{error}</div>}
        {success && <div className="success">Purchase added successfully!</div>}
      </form>
    </div>
  );
};

export default AddPurchase;