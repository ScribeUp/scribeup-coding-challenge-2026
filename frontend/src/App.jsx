import { useEffect, useState } from "react";
import { fetchTransactions, fetchUsers } from "./api.js";

export default function App() {
  const [userIds, setUserIds] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchUsers()
      .then((data) => {
        setUserIds(data.user_ids);
        if (data.user_ids.length) setSelectedUser(data.user_ids[0]);
      })
      .catch((e) => setError(e.message));
  }, []);

  useEffect(() => {
    if (selectedUser == null) return;
    setLoading(true);
    setError(null);
    fetchTransactions(selectedUser)
      .then((data) => setTransactions(data.transactions))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [selectedUser]);

  return (
    <div style={styles.page}>
      <h1 style={styles.h1}>ScribeUp Take-Home</h1>

      <label style={styles.label}>
        User:&nbsp;
        <select
          value={selectedUser ?? ""}
          onChange={(e) => setSelectedUser(Number(e.target.value))}
          style={styles.select}
        >
          {userIds.map((id) => (
            <option key={id} value={id}>
              User {id}
            </option>
          ))}
        </select>
      </label>

      {/* TODO (candidate): render detected subscriptions for the selected user here. */}

      <h2 style={styles.h2}>Transactions</h2>
      {loading && <div>Loading…</div>}
      {error && <div style={styles.error}>Error: {error}</div>}
      {!loading && !error && (
        <table style={styles.table}>
          <thead>
            <tr>
              <th style={styles.th}>Date</th>
              <th style={styles.th}>Merchant</th>
              <th style={styles.th}>Amount</th>
            </tr>
          </thead>
          <tbody>
            {transactions.map((t) => (
              <tr key={t.id}>
                <td style={styles.td}>{t.charged_at.slice(0, 10)}</td>
                <td style={styles.td}>{t.merchant_name}</td>
                <td style={styles.td}>${t.amount}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

const styles = {
  page: { fontFamily: "system-ui, sans-serif", maxWidth: 720, margin: "40px auto", padding: 16 },
  h1: { fontSize: 24, marginBottom: 16 },
  h2: { fontSize: 18, marginTop: 24, marginBottom: 8 },
  label: { display: "block", marginBottom: 16 },
  select: { padding: 6, fontSize: 14 },
  table: { width: "100%", borderCollapse: "collapse", fontSize: 14 },
  th: { textAlign: "left", borderBottom: "1px solid #ddd", padding: 8 },
  td: { borderBottom: "1px solid #f0f0f0", padding: 8 },
  error: { color: "crimson" },
};
