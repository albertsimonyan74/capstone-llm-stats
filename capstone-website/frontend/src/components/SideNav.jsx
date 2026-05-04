import { useEffect, useState } from 'react'
import { createPortal } from 'react-dom'

const SECTIONS = [
  { id: 'overview',       label: 'Overview'       },
  { id: 'pipeline',       label: 'Pipeline'       },
  { id: 'models',         label: 'Models'         },
  { id: 'difficulty',     label: 'Difficulty'     },
  { id: 'tasks',          label: 'Tasks'          },
  { id: 'methodology',    label: 'Methodology'    },
  { id: 'research',       label: 'Research'       },
  { id: 'visualizations', label: 'Visualizations' },
  { id: 'limitations',    label: 'Limitations'    },
  { id: 'user-study',     label: 'User Study'     },
  { id: 'references',     label: 'References'     },
]

export default function SideNav() {
  const [visible, setVisible] = useState(false)
  const [active, setActive] = useState(SECTIONS[0].id)
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [isMobile, setIsMobile] = useState(false)

  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 1100)
    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  useEffect(() => {
    const handleScroll = () => {
      setVisible(window.scrollY > 400)

      const TRIGGER = 100
      let activeId = SECTIONS[0].id
      for (const s of SECTIONS) {
        const el = document.getElementById(s.id)
        if (!el) continue
        const top = el.getBoundingClientRect().top
        if (top <= TRIGGER) activeId = s.id
      }
      setActive(activeId)
    }

    window.addEventListener('scroll', handleScroll, { passive: true })
    handleScroll()
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  useEffect(() => {
    if (drawerOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => {
      document.body.style.overflow = ''
    }
  }, [drawerOpen])

  useEffect(() => {
    if (!drawerOpen) return
    const handleEscape = (e) => {
      if (e.key === 'Escape') setDrawerOpen(false)
    }
    window.addEventListener('keydown', handleEscape)
    return () => window.removeEventListener('keydown', handleEscape)
  }, [drawerOpen])

  const handleSectionClick = (id, e) => {
    e.preventDefault()
    const el = document.getElementById(id)
    if (el) {
      const offset = 80
      const top = el.getBoundingClientRect().top + window.scrollY - offset
      window.scrollTo({ top, behavior: 'smooth' })
    }
    if (isMobile) {
      setTimeout(() => setDrawerOpen(false), 150)
    }
  }

  const desktopRail = (
    <nav
      className={`sidenav${visible ? ' sidenav--visible' : ''}`}
      aria-label="Section navigation"
    >
      <div className="sidenav__track" aria-hidden="true" />
      <ul className="sidenav__list">
        {SECTIONS.map(s => (
          <li key={s.id} className="sidenav__item">
            <a
              href={`#${s.id}`}
              className={`sidenav__link${active === s.id ? ' sidenav__link--active' : ''}`}
              onClick={(e) => handleSectionClick(s.id, e)}
            >
              <span className="sidenav__label">{s.label}</span>
              <span className="sidenav__dot" aria-hidden="true" />
            </a>
          </li>
        ))}
      </ul>
    </nav>
  )

  const mobileFab = (
    <>
      <button
        className={`sidenav-fab${visible ? ' sidenav-fab--visible' : ''}`}
        onClick={() => setDrawerOpen(true)}
        aria-label="Open section navigation"
        aria-expanded={drawerOpen}
        type="button"
      >
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
          <line x1="4" y1="6" x2="20" y2="6" />
          <line x1="4" y1="12" x2="20" y2="12" />
          <line x1="4" y1="18" x2="20" y2="18" />
        </svg>
      </button>

      {drawerOpen && (
        <div
          className="sidenav-drawer-backdrop"
          onClick={() => setDrawerOpen(false)}
          aria-hidden="true"
        />
      )}

      <nav
        className={`sidenav-drawer${drawerOpen ? ' sidenav-drawer--open' : ''}`}
        aria-label="Section navigation drawer"
        aria-hidden={!drawerOpen}
      >
        <div className="sidenav-drawer__header">
          <span className="sidenav-drawer__title">Sections</span>
          <button
            className="sidenav-drawer__close"
            onClick={() => setDrawerOpen(false)}
            aria-label="Close navigation"
            type="button"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        <ul className="sidenav-drawer__list">
          {SECTIONS.map(s => (
            <li key={s.id} className="sidenav-drawer__item">
              <a
                href={`#${s.id}`}
                className={`sidenav-drawer__link${active === s.id ? ' sidenav-drawer__link--active' : ''}`}
                onClick={(e) => handleSectionClick(s.id, e)}
              >
                <span className="sidenav-drawer__dot" aria-hidden="true" />
                <span className="sidenav-drawer__label">{s.label}</span>
              </a>
            </li>
          ))}
        </ul>
      </nav>
    </>
  )

  if (typeof document === 'undefined') return null
  return createPortal(isMobile ? mobileFab : desktopRail, document.body)
}
