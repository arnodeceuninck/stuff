import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { createItemComment, getItem, patchItem } from "../api";
import RichTextEditor from "../components/RichTextEditor";

const OWNERSHIP_OPTIONS = ["OWNED", "RENBOW", "WANTED", "NEEDED"];

function getOwnershipLabel(value) {
  const labels = {
    OWNED: "Owned",
    RENBOW: "Rented / Borrowed",
    WANTED: "Wanted",
    NEEDED: "Needed",
  };

  return labels[value] || value;
}

function formatCommentTimestamp(value) {
  if (!value) {
    return "No timestamp";
  }

  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }

  return parsed.toLocaleString();
}

export default function ItemDetailPage() {
  const { itemId } = useParams();
  const [item, setItem] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [description, setDescription] = useState("");
  const [name, setName] = useState("");
  const [ownershipType, setOwnershipType] = useState("OWNED");
  const [newComment, setNewComment] = useState("");
  const [saving, setSaving] = useState(false);
  const [commentSaving, setCommentSaving] = useState(false);
  const [editStatus, setEditStatus] = useState("");
  const [commentStatus, setCommentStatus] = useState("");
  const [loadError, setLoadError] = useState("");
  const [editError, setEditError] = useState("");
  const [commentError, setCommentError] = useState("");

  function syncEditFields(data) {
    setDescription(data.description || "");
    setName(data.name);
    setOwnershipType(data.ownership_type);
  }

  useEffect(() => {
    let active = true;

    async function loadItem() {
      try {
        const data = await getItem(itemId);
        if (active) {
          setItem(data);
          syncEditFields(data);
          setLoadError("");
        }
      } catch (err) {
        if (active) {
          setLoadError(err.message || "Could not load item");
        }
      }
    }

    loadItem();
    return () => {
      active = false;
    };
  }, [itemId]);

  function handleEditStart() {
    if (!item) {
      return;
    }

    syncEditFields(item);
    setEditError("");
    setEditStatus("");
    setIsEditing(true);
  }

  function handleEditCancel() {
    if (item) {
      syncEditFields(item);
    }

    setEditError("");
    setEditStatus("");
    setIsEditing(false);
  }

  async function handleSave(event) {
    event.preventDefault();
    setSaving(true);
    setEditStatus("");
    setEditError("");

    try {
      const payload = {
        name,
        description,
        ownership_type: ownershipType,
      };

      const updated = await patchItem(itemId, payload);
      setItem(updated);
      syncEditFields(updated);
      setEditStatus("Saved");
      setIsEditing(false);
    } catch (err) {
      setEditError(err.message || "Could not save item");
    } finally {
      setSaving(false);
    }
  }

  async function handleCommentSubmit(event) {
    event.preventDefault();

    if (!newComment.trim()) {
      setCommentError("Comment cannot be empty");
      setCommentStatus("");
      return;
    }

    setCommentSaving(true);
    setCommentError("");
    setCommentStatus("");

    try {
      const createdComment = await createItemComment(itemId, {
        content: newComment.trim(),
      });
      setItem((currentItem) => {
        if (!currentItem) {
          return currentItem;
        }

        return {
          ...currentItem,
          comments: [...currentItem.comments, createdComment],
        };
      });
      setNewComment("");
      setCommentStatus("Comment added");
    } catch (err) {
      setCommentError(err.message || "Could not add comment");
    } finally {
      setCommentSaving(false);
    }
  }

  if (loadError) {
    return <p className="error-text">{loadError}</p>;
  }

  if (!item) {
    return <p className="loading-text">Loading item...</p>;
  }

  return (
    <div className="detail-grid">
      <section className="panel">
        <div className="section-header">
          <div>
            <h1>{item.name}</h1>
            {item.location ? (
              <p className="muted">
                In <Link to={`/locations/${item.location.id}`}>{item.location.name}</Link>
              </p>
            ) : null}
          </div>
          <div className="actions-row">
            {isEditing ? (
              <button type="button" className="btn ghost" onClick={handleEditCancel}>
                Cancel
              </button>
            ) : (
              <button type="button" className="btn" onClick={handleEditStart}>
                Edit item
              </button>
            )}
          </div>
        </div>
        {isEditing ? (
          <form onSubmit={handleSave} className="form-grid detail-form-stack">
            <label className="field">
              <span>Name</span>
              <input value={name} onChange={(event) => setName(event.target.value)} required />
            </label>
            <label className="field">
              <span>Ownership</span>
              <select
                value={ownershipType}
                onChange={(event) => setOwnershipType(event.target.value)}
              >
                {OWNERSHIP_OPTIONS.map((value) => (
                  <option key={value} value={value}>
                    {getOwnershipLabel(value)}
                  </option>
                ))}
              </select>
            </label>
            <div className="field">
              <span>Description note (WYSIWYG)</span>
              <RichTextEditor value={description} onChange={setDescription} />
            </div>
            {editError ? <p className="error-text">{editError}</p> : null}
            <div className="actions-row">
              <button type="submit" className="btn" disabled={saving}>
                {saving ? "Saving..." : "Save changes"}
              </button>
              {editStatus ? <p className="success-text">{editStatus}</p> : null}
            </div>
          </form>
        ) : (
          <div className="detail-form-stack">
            <div className="detail-meta-row">
              <span className="pill">{getOwnershipLabel(item.ownership_type)}</span>
            </div>
            {item.description ? (
              <div className="note-block" dangerouslySetInnerHTML={{ __html: item.description }} />
            ) : (
              <p className="empty-state">No description yet.</p>
            )}
            {editStatus ? <p className="success-text">{editStatus}</p> : null}
          </div>
        )}
      </section>
      <section className="panel">
        <div className="section-header">
          <h2>Comments</h2>
        </div>
        <form className="form-grid detail-form-stack" onSubmit={handleCommentSubmit}>
          <label className="field">
            <span>Add comment</span>
            <textarea
              value={newComment}
              onChange={(event) => setNewComment(event.target.value)}
              rows={4}
              placeholder="Leave a comment"
            />
          </label>
          {commentError ? <p className="error-text">{commentError}</p> : null}
          <div className="actions-row">
            <button type="submit" className="btn" disabled={commentSaving}>
              {commentSaving ? "Posting..." : "Post comment"}
            </button>
            {commentStatus ? <p className="success-text">{commentStatus}</p> : null}
          </div>
        </form>
        {item.comments.length ? (
          <ul className="simple-list">
            {item.comments.map((comment) => (
              <li key={comment.id}>
                <p>{comment.content}</p>
                <p className="muted">{formatCommentTimestamp(comment.created_at)}</p>
              </li>
            ))}
          </ul>
        ) : (
          <p className="empty-state">No comments yet.</p>
        )}
      </section>
    </div>
  );
}
