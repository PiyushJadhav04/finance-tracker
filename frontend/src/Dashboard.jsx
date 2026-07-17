import { useEffect, useState } from "react";
import { createTransaction, deleteTransaction, getSummary, listTransactions } from "./api";

export default function Dashboard({ token, onLogout }) {
  const [transactions, setTransactions] = useState([]);
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState(null);
  const [form, setForm] = useState({ amount: "", description: "", date: "" });

  async function refresh() {
    try {
      const [txns, summaryData] = await Promise.all([
        listTransactions(token),
        getSummary(token),
      ]);
      setTransactions(txns);
      setSummary(summaryData);
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleAdd(e) {
    e.preventDefault();
    setError(null);
    try {
      await createTransaction(token, {
        amount: form.amount,
        description: form.description || null,
        date: form.date,
      });
      setForm({ amount: "", description: "", date: "" });
      await refresh();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDelete(id) {
    try {
      await deleteTransaction(token, id);
      await refresh();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="dashboard">
      <header>
        <h1>Finance Tracker</h1>
        <button type="button" onClick={onLogout}>
          Log out
        </button>
      </header>

      {error && <p className="error">{error}</p>}

      {summary && (
        <section className="summary">
          <h2>
            Summary — {summary.year}/{String(summary.month).padStart(2, "0")}
          </h2>
          <p>Total spend: {summary.total_spend}</p>
          <ul>
            {summary.by_category.map((c) => (
              <li key={c.category_name}>
                {c.category_name}: {c.total}
              </li>
            ))}
          </ul>
        </section>
      )}

      <section>
        <h2>Add transaction</h2>
        <form onSubmit={handleAdd}>
          <label>
            Amount
            <input
              type="number"
              step="0.01"
              value={form.amount}
              onChange={(e) => setForm({ ...form, amount: e.target.value })}
              required
            />
          </label>
          <label>
            Date
            <input
              type="date"
              value={form.date}
              onChange={(e) => setForm({ ...form, date: e.target.value })}
              required
            />
          </label>
          <label>
            Description
            <input
              type="text"
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
            />
          </label>
          <button type="submit">Add</button>
        </form>
      </section>

      <section>
        <h2>Transactions</h2>
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Amount</th>
              <th>Description</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {transactions.map((t) => (
              <tr key={t.id}>
                <td>{t.date}</td>
                <td>{t.amount}</td>
                <td>{t.description}</td>
                <td>
                  <button type="button" onClick={() => handleDelete(t.id)}>
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}
