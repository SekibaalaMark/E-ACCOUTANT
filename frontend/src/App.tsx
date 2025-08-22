import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./Login";
import Signup from "./Signup";
import AdminDashboard from "./AdminDashboard";
import "./App.css";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/signup" element={<Signup />} />
        <Route path="/admin" element={<AdminDashboard />} />
        <Route path="/" element={<Login />} />
      </Routes>
    </Router>
  );
}

export default App;