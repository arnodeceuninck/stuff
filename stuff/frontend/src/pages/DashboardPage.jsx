import { useEffect, useState } from "react";

import { createLocation, getDashboard } from "../api";
import LocationTree from "../components/LocationTree";
import MetricCard from "../components/MetricCard";
import Modal from "../components/Modal";

export default function DashboardPage() {
  const [dashboard, setDashboard] = useState(null);
  const [error, setError] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState("");
  const [newNote, setNewNote] = useState("");
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState("");

  async function load() {
    try {
      const data = await getDashboard();
      setDashboard(data);
      setError("");
    } catch (err) {
      setError(err.message || "Could not load dashboard");
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleCreate(e) {
    e.preventDefault();
    if (!newName.trim()) return;
    setSaving(true);
    setSaveError("");
    try {
      await createLocation({ name: newName.trim(), note: newNote.trim() || null });
      setShowCreate(false);
      setNewName("");
      setNewNote("");
      await load();
    } catch (err) {
      setSaveError(err.message || "Could not create location");
    } finally {
      setSaving(false);
    }
  }

  if (error) {
    return <p className="error-text">{error}</p>;
  }

  if (!dashboard) {
    return <p className="loading-text">Loading dashboard...</p>;
  }

  return (
    <div className="dashboard-grid">
      <section className="panel">
        <h1>Welcome {dashboard.display_name || "there"}</h1>
        <p className="muted">Currency: {dashboard.preferred_currency}</p>
        <div className="metric-grid">
          <MetricCard
            label="Total items"
            value={dashboard.total_item_count}
            hint="Across all your locations"
          />
          <MetricCard
            label="Total locations"
            value={dashboard.total_location_count}
            hint="Including nested spaces"
          />
        </div>
      </section>
      <section className="panel">
        <div className="section-header">
          <h2>Top level locations + one level below</h2>
          <button className="btn" onClick={() => setShowCreate(true)}>
            + New location
          </button>
        </div>
        <LocationTree locations={dashboard.top_level_locations} />
      </section>

      {showCreate && (
        <Modal title="New top-level location" onClose={() => setShowCreate(false)}>
          <form className="form-grid" onSubmit={handleCreate}>
            <div className="field">
              <span>Name</span>
              <input
                autoFocus
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                placeholder="e.g. Living room"
                required
              />
            </div>
            <div className="field">
              <span>Note (optional)</span>
              <textarea
                rows={2}
                value={newNote}
                onChange={(e) => setNewNote(e.target.value)}
                placeholder="Any description…"
              />
            </div>
            {saveError && <p className="error-text">{saveError}</p>}
            <div className="modal-footer">
              <button type="button" className="btn ghost" onClick={() => setShowCreate(false)}>
                Cancel
              </button>
              <button type="submit" className="btn" disabled={saving}>
                {saving ? "Creating…" : "Create"}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}
