import React, { useState } from "react";
import Login from "./Login";
import Signup from "./Signup";
import "./App.css";

function App() {
  const [showSignup, setShowSignup] = useState(false);

  return (
    <div>
      {showSignup ? (
        <Signup />
      ) : (
        <Login onSignupClick={() => setShowSignup(true)} />
      )}
    </div>
  );
}

export default App;