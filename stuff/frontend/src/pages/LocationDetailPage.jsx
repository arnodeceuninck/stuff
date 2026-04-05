import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import {
  createItem,
  createLocation,
  deleteLocation,
  getLocation,
  updateLocation,
} from "../api";
import Modal from "../components/Modal";

const OWNERSHIP_OPTIONS = [
  { value: "OWNED", label: "Owned" },
  { value: "RENBOW", label: "Rented / Borrowed" },
  { value: "WANTED", label: "Wanted" },
  { value: "NEEDED", label: "Needed" },
];

export default function LocationDetailPage() {
  const { locationId } = useParams();
  const navigate = useNavigate();
  const [location, setLocation] = useState(null);
  const [error, setError] = useState("");

  // Edit location modal
  const [showEdit, setShowEdit] = useState(false);
  const [editName, setEditName] = useState("");
  const [editNote, setEditNote] = useState("");
  const [editSaving, setEditSaving] = useState(false);
  const [editError, setEditError] = useState("");

  // Delete location modal
  const [showDelete, setShowDelete] = useState(false);
  const [deleteError, setDeleteError] = useState("");
  const [deleting, setDeleting] = useState(false);

  // New sub-location modal
  const [showNewLoc, setShowNewLoc] = useState(false);
  const [newLocName, setNewLocName] = useState("");
  const [newLocNote, setNewLocNote] = useState("");
  const [newLocSaving, setNewLocSaving] = useState(false);
  const [newLocError, setNewLocError] = useState("");

  // New item modal
  const [showNewItem, setShowNewItem] = useState(false);
  const [newItemName, setNewItemName] = useState("");
  const [newItemDesc, setNewItemDesc] = useState("");
  const [newItemOwn, setNewItemOwn] = useState("OWNED");
  const [newItemSaving, setNewItemSaving] = useState(false);
  const [newItemError, setNewItemError] = useState("");

  async function load() {
    try {
      const data = await getLocation(locationId);
      setLocation(data);
      setError("");
    } catch (err) {
      setError(err.message || "Could not load location");
    }
  }

  useEffect(() => {
    load();
  }, [locationId]);

  function openEdit() {
    setEditName(location.name);
    setEditNote(location.note || "");
    setEditError("");
    setShowEdit(true);
  }

  async function handleEdit(e) {
    e.preventDefault();
    setEditSaving(true);
    setEditError("");
    try {
      await updateLocation(locationId, { name: editName.trim(), note: editNote.trim() || null });
      setShowEdit(false);
      await load();
    } catch (err) {
      setEditError(err.message || "Could not update location");
    } finally {
      setEditSaving(false);
    }
  }

  async function handleDelete() {
    setDeleting(true);
    setDeleteError("");
    try {
      await deleteLocation(locationId);
      const parentId = location.parent_location_id;
      navigate(parentId ? `/locations/${parentId}` : "/app");
    } catch (err) {
      setDeleteError(err.message || "Could not delete location");
      setDeleting(false);
    }
  }

  async function handleNewLoc(e) {
    e.preventDefault();
    if (!newLocName.trim()) return;
    setNewLocSaving(true);
    setNewLocError("");
    try {
      const created = await createLocation({
        name: newLocName.trim(),
        note: newLocNote.trim() || null,
        parent_location_id: locationId,
      });
      setShowNewLoc(false);
      setNewLocName("");
      setNewLocNote("");
      navigate(`/locations/${created.id}`);
    } catch (err) {
      setNewLocError(err.message || "Could not create location");
    } finally {
      setNewLocSaving(false);
    }
  }

  async function handleNewItem(e) {
    e.preventDefault();
    if (!newItemName.trim()) return;
    setNewItemSaving(true);
    setNewItemError("");
    try {
      const created = await createItem({
        name: newItemName.trim(),
        description: newItemDesc.trim() || null,
        ownership_type: newItemOwn,
        location_id: locationId,
      });
      setShowNewItem(false);
      setNewItemName("");
      setNewItemDesc("");
      setNewItemOwn("OWNED");
      navigate(`/items/${created.id}`);
    } catch (err) {
      setNewItemError(err.message || "Could not create item");
    } finally {
      setNewItemSaving(false);
    }
  }

  if (error) {
    return <p className="error-text">{error}</p>;
  }

  if (!location) {
    return <p className="loading-text">Loading location...</p>;
  }

  return (
    <div className="detail-grid">
      <section className="panel">
        <div className="crumbs">
          {location.breadcrumb.map((crumb) => (
            <Link key={crumb.id} to={`/locations/${crumb.id}`}>
              {crumb.name}
            </Link>
          ))}
        </div>
        <div className="section-header">
          <h1>{location.name}</h1>
          <div className="actions-row">
            <button className="btn ghost" onClick={openEdit}>
              Edit
            </button>
            <button className="btn-danger" onClick={() => { setDeleteError(""); setShowDelete(true); }}>
              Delete
            </button>
          </div>
        </div>
        {location.note ? (
          <div className="note-block" dangerouslySetInnerHTML={{ __html: location.note }} />
        ) : null}
      </section>

      <section className="panel">
        <div className="section-header">
          <h2>Sub locations</h2>
          <button className="btn" onClick={() => { setNewLocError(""); setShowNewLoc(true); }}>
            + Add
          </button>
        </div>
        {location.child_locations.length ? (
          <ul className="simple-list">
            {location.child_locations.map((child) => (
              <li key={child.id}>
                <Link to={`/locations/${child.id}`}>{child.name}</Link>
                <span className="muted"> {child.item_count} items</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="empty-state">No child locations.</p>
        )}
      </section>

      <section className="panel">
        <div className="section-header">
          <h2>Items here</h2>
          <button className="btn" onClick={() => { setNewItemError(""); setShowNewItem(true); }}>
            + Add
          </button>
        </div>
        {location.items.length ? (
          <ul className="simple-list">
            {location.items.map((item) => (
              <li key={item.id}>
                <Link to={`/items/${item.id}`}>{item.name}</Link>
                <span className="pill">{item.ownership_type}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="empty-state">No items in this location.</p>
        )}
      </section>

      {/* Edit location modal */}
      {showEdit && (
        <Modal title="Edit location" onClose={() => setShowEdit(false)}>
          <form className="form-grid" onSubmit={handleEdit}>
            <div className="field">
              <span>Name</span>
              <input
                autoFocus
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
                required
              />
            </div>
            <div className="field">
              <span>Note (optional)</span>
              <textarea
                rows={3}
                value={editNote}
                onChange={(e) => setEditNote(e.target.value)}
              />
            </div>
            {editError && <p className="error-text">{editError}</p>}
            <div className="modal-footer">
              <button type="button" className="btn ghost" onClick={() => setShowEdit(false)}>
                Cancel
              </button>
              <button type="submit" className="btn" disabled={editSaving}>
                {editSaving ? "Saving…" : "Save"}
              </button>
            </div>
          </form>
        </Modal>
      )}

      {/* Delete confirmation modal */}
      {showDelete && (
        <Modal title="Delete location?" onClose={() => setShowDelete(false)}>
          <p>
            Delete <strong>{location.name}</strong>? This only works if the location has no items or
            sub-locations.
          </p>
          {deleteError && <p className="error-text">{deleteError}</p>}
          <div className="modal-footer">
            <button className="btn ghost" onClick={() => setShowDelete(false)}>
              Cancel
            </button>
            <button className="btn-danger" disabled={deleting} onClick={handleDelete}>
              {deleting ? "Deleting…" : "Delete"}
            </button>
          </div>
        </Modal>
      )}

      {/* New sub-location modal */}
      {showNewLoc && (
        <Modal title="New sub-location" onClose={() => setShowNewLoc(false)}>
          <form className="form-grid" onSubmit={handleNewLoc}>
            <div className="field">
              <span>Name</span>
              <input
                autoFocus
                value={newLocName}
                onChange={(e) => setNewLocName(e.target.value)}
                placeholder="e.g. Shelf A"
                required
              />
            </div>
            <div className="field">
              <span>Note (optional)</span>
              <textarea
                rows={2}
                value={newLocNote}
                onChange={(e) => setNewLocNote(e.target.value)}
              />
            </div>
            {newLocError && <p className="error-text">{newLocError}</p>}
            <div className="modal-footer">
              <button type="button" className="btn ghost" onClick={() => setShowNewLoc(false)}>
                Cancel
              </button>
              <button type="submit" className="btn" disabled={newLocSaving}>
                {newLocSaving ? "Creating…" : "Create"}
              </button>
            </div>
          </form>
        </Modal>
      )}

      {/* New item modal */}
      {showNewItem && (
        <Modal title="New item" onClose={() => setShowNewItem(false)}>
          <form className="form-grid" onSubmit={handleNewItem}>
            <div className="field">
              <span>Name</span>
              <input
                autoFocus
                value={newItemName}
                onChange={(e) => setNewItemName(e.target.value)}
                placeholder="e.g. HDMI cable"
                required
              />
            </div>
            <div className="field">
              <span>Description (optional)</span>
              <textarea
                rows={2}
                value={newItemDesc}
                onChange={(e) => setNewItemDesc(e.target.value)}
              />
            </div>
            <div className="field">
              <span>Ownership</span>
              <select value={newItemOwn} onChange={(e) => setNewItemOwn(e.target.value)}>
                {OWNERSHIP_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>
                    {o.label}
                  </option>
                ))}
              </select>
            </div>
            {newItemError && <p className="error-text">{newItemError}</p>}
            <div className="modal-footer">
              <button type="button" className="btn ghost" onClick={() => setShowNewItem(false)}>
                Cancel
              </button>
              <button type="submit" className="btn" disabled={newItemSaving}>
                {newItemSaving ? "Creating…" : "Create"}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}

