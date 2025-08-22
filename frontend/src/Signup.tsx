import React, { useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";

const Signup: React.FC = () => {
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    confirm_password: "",
    role: "cashier",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);
    try {
      await axios.post("https://e-accoutant.onrender.com/api/register/", form);
      setSuccess(true);
      setForm({
        username: "",
        email: "",
        password: "",
        confirm_password: "",
        role: "cashier",
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || "Signup failed");
    }
    setLoading(false);
  };

  return (
    <div className="signup-container">
      <form className="signup-form" onSubmit={handleSubmit}>
        <h2>Sign Up</h2>
        <input
          type="text"
          name="username"
          placeholder="Username"
          value={form.username}
          onChange={handleChange}
          required
        />
        <input
          type="email"
          name="email"
          placeholder="Email"
          value={form.email}
          onChange={handleChange}
          required
        />
        <input
          type="password"
          name="password"
          placeholder="Password"
          value={form.password}
          onChange={handleChange}
          required
        />
        <input
          type="password"
          name="confirm_password"
          placeholder="Confirm Password"
          value={form.confirm_password}
          onChange={handleChange}
          required
        />
        <select name="role" value={form.role} onChange={handleChange} required>
          <option value="admin">Admin</option>
          <option value="cashier">Cashier</option>
        </select>
        <button type="submit" disabled={loading}>
          {loading ? "Signing Up..." : "Sign Up"}
        </button>
        {error && <div className="error">{error}</div>}
        {success && <div className="success">Signup successful!</div>}
        <div className="signup-link">
          Already have an account?{" "}
          <Link to="/" className="link-btn">
            Login
          </Link>
        </div>
      </form>
    </div>
  );
};

export default Signup;