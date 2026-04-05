import { useEffect, useRef } from "react";

function runCommand(command, value) {
  document.execCommand(command, false, value);
}

export default function RichTextEditor({ value, onChange }) {
  const editorRef = useRef(null);

  useEffect(() => {
    if (!editorRef.current) {
      return;
    }

    // Do not rewrite content while user is editing, which can reset caret/selection.
    if (document.activeElement === editorRef.current) {
      return;
    }

    if (editorRef.current.innerHTML !== value) {
      editorRef.current.innerHTML = value || "";
    }
  }, [value]);

  function handleInput() {
    onChange(editorRef.current?.innerHTML || "");
  }

  function handleLink() {
    const url = window.prompt("Enter link URL");
    if (url) {
      runCommand("createLink", url);
      handleInput();
    }
  }

  function keepEditorFocus(event) {
    event.preventDefault();
    editorRef.current?.focus();
  }

  return (
    <div className="wysiwyg-wrap">
      <div className="wysiwyg-toolbar">
        <button type="button" className="btn ghost" onMouseDown={keepEditorFocus} onClick={() => runCommand("bold")}>B</button>
        <button type="button" className="btn ghost" onMouseDown={keepEditorFocus} onClick={() => runCommand("italic")}>I</button>
        <button type="button" className="btn ghost" onMouseDown={keepEditorFocus} onClick={() => runCommand("insertUnorderedList")}>UL</button>
        <button type="button" className="btn ghost" onMouseDown={keepEditorFocus} onClick={() => runCommand("insertOrderedList")}>OL</button>
        <button type="button" className="btn ghost" onMouseDown={keepEditorFocus} onClick={handleLink}>Link</button>
      </div>
      <div
        ref={editorRef}
        className="wysiwyg-editor"
        contentEditable
        role="textbox"
        aria-multiline="true"
        onInput={handleInput}
        suppressContentEditableWarning
      />
    </div>
  );
}
