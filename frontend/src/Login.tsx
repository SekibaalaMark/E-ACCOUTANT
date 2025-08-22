import React, { useState } from "react";
import axios from "axios";

interface Props {
  onSignupClick: () => void;
}

const Login: React.FC<Props> = ({ onSignupClick }) => {
  const [form, setForm] = useState({ username: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await axios.post("https://e-accoutant.onrender.com/api/login/", form);
      // For now, just log the response. Later, redirect based on role.
      if (res.data.user.role === "admin") {
        alert("Login successful! Welcome, admin.");
        // TODO: Redirect to admin dashboard
      } else {
        alert("Only admin dashboard is available for now.");
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Login failed");
    }
    setLoading(false);
  };

  return (
    <div className="login-container">
      <form className="login-form" onSubmit={handleSubmit}>
        <h2>Login</h2>
        <input
          type="text"
          name="username"
          placeholder="Username"
          value={form.username}
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
        <button type="submit" disabled={loading}>
          {loading ? "Logging in..." : "Login"}
        </button>
        {error && <div className="error">{error}</div>}
        <div className="signup-link">
          Don't have an account?{" "}
          <button type="button" onClick={onSignupClick} className="link-btn">
            Sign Up
          </button>
        </div>
      </form>
    </div>
  );
};

export default Login;