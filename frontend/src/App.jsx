import { useState } from "react";
import AuthForm from "./AuthForm";
import Dashboard from "./Dashboard";

const TOKEN_KEY = "finance_tracker_token";

export default function App() {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY));

  function handleAuthenticated(newToken) {
    localStorage.setItem(TOKEN_KEY, newToken);
    setToken(newToken);
  }

  function handleLogout() {
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
  }

  return token ? (
    <Dashboard token={token} onLogout={handleLogout} />
  ) : (
    <AuthForm onAuthenticated={handleAuthenticated} />
  );
}
