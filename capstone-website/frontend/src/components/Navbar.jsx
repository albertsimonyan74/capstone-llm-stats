import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'motion/react'

const NAV_SECTIONS = [
  { id: 'overview',      label: 'Overview'     },
  { id: 'about',         label: 'Research'     },
  { id: 'benchmark',     label: 'How It Works' },
  { id: 'models',        label: 'Models'       },
  { id: 'tasks',         label: 'Tasks'        },
  { id: 'visualizations',label: 'Visualizations' },
  { id: 'user-study',    label: 'User Study'   },
]

export default function Navbar() {
  const [active,      setActive]      = useState('overview')
  const [menuOpen,    setMenuOpen]    = useState(false)
  const [scrolled,    setScrolled]    = useState(false)
  const observerRef = useRef(null)

  // ── IntersectionObserver for active section ───────────────
  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', handleScroll, { passive: true })

    observerRef.current = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) setActive(e.target.id)
        })
      },
      { rootMargin: '-20% 0px -70% 0px', threshold: 0 }
    )

    NAV_SECTIONS.forEach(({ id }) => {
      const el = document.getElementById(id)
      if (el) observerRef.current.observe(el)
    })

    return () => {
      window.removeEventListener('scroll', handleScroll)
      observerRef.current?.disconnect()
    }
  }, [])

  const scrollTo = (id) => {
    const el = document.getElementById(id)
    if (!el) return
    const offset = 80
    const top = el.getBoundingClientRect().top + window.scrollY - offset
    window.scrollTo({ top, behavior: 'smooth' })
    setActive(id)
    setMenuOpen(false)
  }

  return (
    <>
      <motion.header
        className={`navbar${scrolled ? ' navbar-scrolled' : ''}`}
        initial={{ y: -80, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
      >
        {/* Logo */}
        <div className="nav-logo" onClick={() => scrollTo('overview')} role="button" tabIndex={0} aria-label="Go to top" onKeyDown={e => e.key === 'Enter' && scrollTo('overview')}>
          <motion.svg
            width="28" height="28" viewBox="0 0 30 30" fill="none"
            whileHover={{ rotate: 180 }}
            transition={{ type: 'spring', stiffness: 200, damping: 18 }}
          >
            <polygon points="15,3 27,24 3,24" stroke="#00FFE0" strokeWidth="2" fill="rgba(0,255,224,0.08)"/>
            <polygon points="15,9 23,24 7,24" stroke="#00B4D8" strokeWidth="1.2" fill="none"/>
          </motion.svg>
          <div>
            <div className="nav-logo-title">LLM Benchmark</div>
            <div className="nav-logo-sub">DS 299 · Capstone</div>
          </div>
        </div>

        {/* Desktop links */}
        <motion.nav
          className="nav-links"
          initial="hidden"
          animate="visible"
          variants={{ visible: { transition: { staggerChildren: 0.07, delayChildren: 0.4 } } }}
          aria-label="Site navigation"
        >
          {NAV_SECTIONS.map(({ id, label }) => (
            <motion.button
              key={id}
              className={`nav-btn${active === id ? ' active' : ''}`}
              onClick={() => scrollTo(id)}
              variants={{ hidden: { opacity: 0, y: -8 }, visible: { opacity: 1, y: 0 } }}
              whileTap={{ scale: 0.95 }}
            >
              {label}
              <AnimatePresence>
                {active === id && (
                  <motion.span
                    key="underline"
                    className="nav-underline"
                    layoutId="nav-underline"
                    initial={{ scaleX: 0 }}
                    animate={{ scaleX: 1 }}
                    exit={{ scaleX: 0 }}
                    transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                  />
                )}
              </AnimatePresence>
            </motion.button>
          ))}
        </motion.nav>

        {/* Mobile hamburger */}
        <button
          className="nav-hamburger"
          onClick={() => setMenuOpen(!menuOpen)}
          aria-label={menuOpen ? 'Close menu' : 'Open menu'}
          aria-expanded={menuOpen}
        >
          <span className={`hamburger-line${menuOpen ? ' open' : ''}`}/>
          <span className={`hamburger-line${menuOpen ? ' open' : ''}`}/>
          <span className={`hamburger-line${menuOpen ? ' open' : ''}`}/>
        </button>
      </motion.header>

      {/* Mobile drawer */}
      <AnimatePresence>
        {menuOpen && (
          <motion.div
            className="nav-drawer"
            initial={{ opacity: 0, y: -16 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -16 }}
            transition={{ duration: 0.25, ease: 'easeOut' }}
          >
            {NAV_SECTIONS.map(({ id, label }) => (
              <button
                key={id}
                className={`nav-drawer-btn${active === id ? ' active' : ''}`}
                onClick={() => scrollTo(id)}
              >
                {label}
              </button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}
