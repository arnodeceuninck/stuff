import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { login, register } from "../api";
import { setToken } from "../auth";

function AuthForm({ title, submitLabel, onSubmit }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      await onSubmit(email, password);
    } catch (err) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="auth-panel">
      <h2>{title}</h2>
      <form onSubmit={handleSubmit} className="form-grid">
        <label className="field">
          <span>Email</span>
          <input
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />
        </label>
        <label className="field">
          <span>Password</span>
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
            minLength={8}
          />
        </label>
        {error ? <p className="error-text">{error}</p> : null}
        <button type="submit" className="btn" disabled={loading}>
          {loading ? "Please wait..." : submitLabel}
        </button>
      </form>
    </section>
  );
}

export default function HomePage() {
  const navigate = useNavigate();

  async function authenticate(authFn, email, password) {
    const response = await authFn(email, password);
    setToken(response.access_token);
    navigate("/app");
  }

  return (
    <div className="home-stage">
      <div className="home-banner">
        <p className="kicker">Know where your things live.</p>
        <h1>Stuff Atlas</h1>
        <p>
          Track locations, item notes, and comments in one place. Start with an account
          or log in to continue.
        </p>
      </div>
      <div className="auth-grid">
        <AuthForm
          title="Login"
          submitLabel="Login"
          onSubmit={(email, password) => authenticate(login, email, password)}
        />
        <AuthForm
          title="Register"
          submitLabel="Create account"
          onSubmit={(email, password) => authenticate(register, email, password)}
        />
      </div>
    </div>
  );
}
