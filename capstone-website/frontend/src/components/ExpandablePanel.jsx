import { useEffect, useState } from 'react'
import { createPortal } from 'react-dom'

export default function ExpandablePanel({ children, title }) {
  const [expanded, setExpanded] = useState(false)

  useEffect(() => {
    if (!expanded) return
    const onKey = (e) => { if (e.key === 'Escape') setExpanded(false) }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [expanded])

  const onActivate = () => setExpanded(true)
  const onKeyDown = (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      setExpanded(true)
    }
  }

  return (
    <>
      <div
        className="expandable-panel"
        onClick={onActivate}
        role="button"
        tabIndex={0}
        onKeyDown={onKeyDown}
        aria-label={title ? `Expand ${title}` : 'Expand panel'}
      >
        {children}
        <div className="expandable-hint" aria-hidden="true">
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none">
            <path
              d="M3 8V3H8M16 3H21V8M21 16V21H16M8 21H3V16"
              stroke="currentColor"
              strokeWidth="2.4"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          click to expand
        </div>
      </div>

      {expanded && createPortal(
        <div
          className="expandable-overlay"
          onClick={() => setExpanded(false)}
          role="dialog"
          aria-modal="true"
        >
          <div
            className="expandable-modal-content"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              className="expandable-close"
              onClick={() => setExpanded(false)}
              aria-label="Close"
            >✕</button>
            <div className="expandable-modal-inner">{children}</div>
          </div>
        </div>,
        document.body,
      )}
    </>
  )
}
