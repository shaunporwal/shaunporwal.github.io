/** Motion for the site: scroll reveal, header state, the sliding nav indicator, the pointer light and the card pictures. Every page works without it. */
const REVEAL_SELECTOR = "[data-reveal-item]"
const REVEAL_MARGIN = "0px 0px -8% 0px"
const VIEWPORT_FRACTION = 0.92
const STAGGER_MS = 70
const MAX_STAGGER_STEPS = 3
const SCROLLED_AFTER_PX = 8
const NAV_SELECTOR = "[data-nav-links]"
const HOVER_QUERY = "(hover: hover) and (pointer: fine)"
const PICTURE_SELECTOR = ".card-media"
const PICTURE_THRESHOLD = 0.35
const GLOW_TARGETS = [
  { selector: ".btn, .card", x: "--gx", y: "--gy" },
  { selector: ".hero", x: "--hx", y: "--hy" },
]
let revealObserver = null

function prefersReducedMotion() {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches
}

function isInView(element) {
  return element.getBoundingClientRect().top < window.innerHeight * VIEWPORT_FRACTION
}

function isEntering(entry) {
  return entry.isIntersecting
}

function settleReveal(event) {
  if (event.target !== event.currentTarget || event.propertyName !== "transform") return
  const element = event.currentTarget
  element.removeEventListener("transitionend", settleReveal)
  element.style.removeProperty("--reveal-delay")
  delete element.dataset.reveal
}

function markShown(element, source) {
  element.dataset.reveal = "shown"
  element.addEventListener("transitionend", settleReveal)
  source.unobserve(element)
}

function onIntersect(entries, source) {
  for (const entry of entries.filter(isEntering)) markShown(entry.target, source)
}

function staggerDelay(element) {
  const index = Array.prototype.indexOf.call(element.parentElement.children, element)
  return `${Math.min(index, MAX_STAGGER_STEPS) * STAGGER_MS}ms`
}

function armItem(element) {
  if (isInView(element)) return
  element.style.setProperty("--reveal-delay", staggerDelay(element))
  element.dataset.reveal = "pending"
  revealObserver.observe(element)
}

function armReveal() {
  if (prefersReducedMotion()) return
  revealObserver = new IntersectionObserver(onIntersect, { rootMargin: REVEAL_MARGIN })
  for (const element of document.querySelectorAll(REVEAL_SELECTOR)) armItem(element)
}

function setScrolled() {
  const header = document.querySelector(".site-header")
  if (header) header.dataset.scrolled = String(window.scrollY > SCROLLED_AFTER_PX)
}

function armHeader() {
  setScrolled()
  window.addEventListener("scroll", setScrolled, { passive: true })
}

function enableAt(nav, link) {
  nav.style.setProperty("--indicator-x", `${link.offsetLeft}px`)
  nav.style.setProperty("--indicator-w", String(link.offsetWidth))
  if (nav.dataset.indicator !== "on") void nav.offsetWidth
  nav.dataset.indicator = "on"
}

function moveIndicator(nav, link) {
  if (link) enableAt(nav, link)
  else nav.dataset.indicator = "off"
}

function previewLink(event) {
  const link = event.currentTarget
  moveIndicator(link.closest(NAV_SELECTOR), link)
}

function settleIndicator() {
  const nav = document.querySelector(NAV_SELECTOR)
  if (nav) moveIndicator(nav, nav.querySelector("[aria-current]"))
}

function armLink(link) {
  link.addEventListener("pointerenter", previewLink)
  link.addEventListener("focus", previewLink)
}

function armNav() {
  const nav = document.querySelector(NAV_SELECTOR)
  if (!nav) return
  for (const link of nav.querySelectorAll(".nav-link")) armLink(link)
  nav.addEventListener("pointerleave", settleIndicator)
  nav.addEventListener("focusout", settleIndicator)
  window.addEventListener("resize", settleIndicator)
  settleIndicator()
}

function canFollowPointer() {
  return window.matchMedia(HOVER_QUERY).matches && !prefersReducedMotion()
}

function placeGlow(event, element, target) {
  const box = element.getBoundingClientRect()
  element.style.setProperty(target.x, `${Math.round(event.clientX - box.left)}px`)
  element.style.setProperty(target.y, `${Math.round(event.clientY - box.top)}px`)
}

function followTarget(event, target) {
  const element = event.target.closest(target.selector)
  if (element) placeGlow(event, element, target)
}

function followPointer(event) {
  for (const target of GLOW_TARGETS) followTarget(event, target)
}

function armGlow() {
  if (canFollowPointer()) document.addEventListener("pointermove", followPointer, { passive: true })
}

function saveDataOn() {
  return Boolean(navigator.connection && navigator.connection.saveData)
}

function canPlayPictures() {
  return !prefersReducedMotion() && !saveDataOn()
}

function ignoreRejection() {
  // A play request that a later pause cancels is expected. The still stays on screen.
}

function startClip(clip) {
  const started = clip.play()
  if (started) started.catch(ignoreRejection)
}

function setPlaying(media, playing) {
  media.dataset.playing = String(playing)
  const clip = media.querySelector("video")
  if (!clip) return
  if (playing) startClip(clip)
  else clip.pause()
}

function isShowing(media) {
  return media.dataset.onscreen === "true" && !document.hidden
}

function syncPlayback(media) {
  setPlaying(media, isShowing(media))
}

function onPictureIntersect(entries) {
  for (const entry of entries) {
    entry.target.dataset.onscreen = String(entry.isIntersecting)
    syncPlayback(entry.target)
  }
}

function onVisibilityChange() {
  for (const media of document.querySelectorAll(PICTURE_SELECTOR)) syncPlayback(media)
}

function armPictures() {
  if (!canPlayPictures()) return
  const observer = new IntersectionObserver(onPictureIntersect, { threshold: PICTURE_THRESHOLD })
  for (const media of document.querySelectorAll(PICTURE_SELECTOR)) observer.observe(media)
  document.addEventListener("visibilitychange", onVisibilityChange)
}

function start() {
  armReveal()
  armHeader()
  armNav()
  armGlow()
  armPictures()
}

start()
