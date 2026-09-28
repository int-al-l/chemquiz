import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, HashRouter } from 'react-router-dom'
import './index.css'
import App from './App.jsx'

/**
 * Material Symbols draws an icon from a *ligature*, so when the font fails to
 * arrive the browser renders the ligature's own name instead -- "bookmark_add"
 * spelled out inside a 52px tile. Icons therefore stay hidden until the font is
 * confirmed working; the CSS reserves their box either way, so nothing shifts.
 *
 * The check is a measurement, not `document.fonts.check()`: with the stylesheet
 * blocked no @font-face is ever registered, and check() then reports true
 * because a fallback family is available. Rendering a long ligature and looking
 * at its width is unambiguous -- one glyph is narrow, the spelled-out word is
 * not.
 */
function iconFontWorks() {
  const probe = document.createElement('span')
  probe.className = 'material-symbols-outlined'
  probe.textContent = 'bookmark_add'
  probe.style.cssText =
    'position:absolute;left:-9999px;top:0;visibility:hidden;' +
    'width:auto;height:auto;overflow:visible;font-size:24px;white-space:nowrap'
  document.body.appendChild(probe)
  const width = probe.getBoundingClientRect().width
  probe.remove()
  // A single glyph is about one em wide; the twelve-character fallback is far wider.
  return width > 0 && width < 40
}

function markIconsReady() {
  if (iconFontWorks()) {
    document.documentElement.classList.add('icons-ready')
    return true
  }
  return false
}

if (!markIconsReady()) {
  // The stylesheet may simply not have arrived yet.
  const ready = document.fonts?.ready ?? Promise.resolve()
  ready.then(markIconsReady).catch(() => {})
  window.setTimeout(markIconsReady, 1200)
  window.setTimeout(markIconsReady, 3500)
}

// The demo build is served as static files from any path, so it routes on the
// URL hash instead of the path.
createRoot(document.getElementById('root')).render(
  <StrictMode>
    {import.meta.env.VITE_DEMO ? (
      <HashRouter>
        <App />
      </HashRouter>
    ) : (
      <BrowserRouter>
        <App />
      </BrowserRouter>
    )}
  </StrictMode>,
)
