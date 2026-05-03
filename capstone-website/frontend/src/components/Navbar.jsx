import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'motion/react'

const NAV_SECTIONS = [
  { id: 'overview',       label: 'Overview'     },
  { id: 'pipeline',       label: 'Pipeline'     },
  { id: 'difficulty',     label: 'Difficulty'   },
  { id: 'formula',        label: 'Formula'      },
  { id: 'models',         label: 'Models'       },
  { id: 'tasks',          label: 'Tasks'        },
  { id: 'methodology',    label: 'Methodology'  },
  { id: 'research',       label: 'Research'     },
  { id: 'visualizations', label: 'Visualizations' },
  { id: 'limitations',    label: 'Limitations'  },
  { id: 'user-study',     label: 'User Study'   },
  { id: 'references',     label: 'References'   },
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
          <motion.div
            whileHover={{ scale: 1.08, filter: 'drop-shadow(0 0 8px #00FFE0)' }}
            transition={{ type: 'spring', stiffness: 300, damping: 20 }}
            style={{
              width: 36, height: 36,
              background: 'linear-gradient(135deg, rgba(0,255,224,0.15), rgba(0,180,216,0.1))',
              border: '1.5px solid rgba(0,255,224,0.5)',
              borderRadius: 8,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontFamily: 'var(--font-mono)',
              fontSize: 14, fontWeight: 900,
              letterSpacing: '-0.04em',
              color: '#00FFE0',
              textShadow: '0 0 12px rgba(0,255,224,0.8)',
              flexShrink: 0,
            }}
          >
            BB
          </motion.div>
          <div>
            <div className="nav-logo-title">Bayesian Benchmark</div>
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

      {/* Mobile drawer + tap-outside backdrop */}
      <AnimatePresence>
        {menuOpen && (
          <>
            <motion.div
              key="nav-drawer-backdrop"
              className="nav-drawer-backdrop"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              onClick={() => setMenuOpen(false)}
              aria-hidden="true"
            />
            <motion.div
              key="nav-drawer"
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
          </>
        )}
      </AnimatePresence>
    </>
  )
}
