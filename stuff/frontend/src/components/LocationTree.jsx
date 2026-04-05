import { Link } from "react-router-dom";

function Node({ location }) {
  return (
    <li className="tree-node">
      <div className="tree-card">
        <Link className="tree-title" to={`/locations/${location.id}`}>
          {location.name}
        </Link>
        <p className="tree-meta">
          {location.item_count} items, {location.child_location_count} child locations
        </p>
        {location.note ? <p className="tree-note">{location.note}</p> : null}
      </div>
      {location.children?.length ? (
        <ul className="tree-children">
          {location.children.map((child) => (
            <Node key={child.id} location={child} />
          ))}
        </ul>
      ) : null}
    </li>
  );
}

export default function LocationTree({ locations }) {
  if (!locations.length) {
    return <p className="empty-state">No locations yet.</p>;
  }

  return (
    <ul className="tree-list">
      {locations.map((location) => (
        <Node key={location.id} location={location} />
      ))}
    </ul>
  );
}
