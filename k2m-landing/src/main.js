import './styles/token.css'
import './style.css'
import './components/Hero/Hero.css'
import './components/ResonanceZone/resonanceZone.css'
import './components/Bridge/Bridge.css'
import './components/CTA/CTA.css'
import './components/Contact/Contact.css'
import './components/Footer/Footer.css'

// Import component HTML
import heroHtml from './components/Hero/Hero.html?raw';
import resonanceZonesHtml from './components/ResonanceZone/ResonanceZones.html?raw';
import bridgeHtml from './components/Bridge/Bridge.html?raw';
import ctaHtml from './components/CTA/CTA.html?raw';
import contactHtml from './components/Contact/Contact.html?raw';
import footerHtml from './components/Footer/Footer.html?raw';

// K2M Landing Page Entry Point
// Full page flow: Hero → Resonance Zones → Bridge → CTA → Contact → Footer

// Progress nav (fixed position, injected before app content)
const progressNavHtml = '<nav class="progress-nav"></nav>';

// Load all section HTML into app container
const app = document.getElementById('app');
if (app) {
  app.innerHTML = heroHtml + progressNavHtml + resonanceZonesHtml + bridgeHtml + ctaHtml + contactHtml + footerHtml;
  console.log('✅ All sections loaded');
} else {
  console.error('❌ App container not found');
}

// Import GSAP and ScrollTrigger for global availability
import { gsap, ScrollTrigger } from './utils/gsap-config.js';

// Import and initialize Lenis smooth scroll
import { lenis } from './utils/lenis-config.js';

// RequestAnimationFrame loop for Lenis updates (AC: 5)
function raf(time) {
  lenis.raf(time);
  requestAnimationFrame(raf);
}

// Start the animation loop
requestAnimationFrame(raf);

// Create background star field
function createStarField() {
  const starfield = document.getElementById('starfield');
  if (!starfield) return;
  for (let i = 0; i < 150; i++) {
    const star = document.createElement('div');
    star.className = 'star';
    star.style.left = `${Math.random() * 100}%`;
    star.style.top = `${Math.random() * 100}%`;
    star.style.width = `${1 + Math.random() * 2}px`;
    star.style.height = star.style.width;
    star.style.setProperty('--duration', `${2 + Math.random() * 4}s`);
    star.style.setProperty('--delay', `${Math.random() * 3}s`);
    star.style.setProperty('--min-opacity', `${0.1 + Math.random() * 0.3}`);
    star.style.setProperty('--max-opacity', `${0.6 + Math.random() * 0.4}`);
    starfield.appendChild(star);
  }
}
createStarField();

// Import and initialize Hero animations
import { initHeroAnimations } from './components/Hero/Hero.js';

// Import and initialize Resonance Zones and ProgressNav
import { initResonanceZonesContainer } from './components/ResonanceZone/ResonanceZones.js';
import { initProgressNav } from './components/ProgressNav/ProgressNav.js';

// Import Bridge and CTA animations
import { initBridgeAnimations } from './components/Bridge/Bridge.js';
import { initCTAAnimations } from './components/CTA/CTA.js';

// Initialize all components after page load
window.addEventListener('load', () => {
  try {
    initHeroAnimations();
    console.log('✅ Hero animations initialized');
  } catch (error) {
    console.error('❌ Error initializing Hero animations:', error);
  }

  try {
    const resonanceZones = initResonanceZonesContainer();
    console.log('✅ Resonance Zones initialized');

    // Initialize ProgressNav with zone data
    const progressNavData = [
      { zoneNumber: 0, label: 'Confusion' },
      { zoneNumber: 1, label: 'Curiosity' },
      { zoneNumber: 2, label: 'Trial & Error' },
      { zoneNumber: 3, label: 'Collaboration' },
      { zoneNumber: 4, label: 'Confidence' }
    ];
    initProgressNav(progressNavData);
    console.log('✅ ProgressNav initialized');
  } catch (error) {
    console.error('❌ Error initializing Resonance Zones:', error);
  }

  try {
    initBridgeAnimations();
  } catch (error) {
    console.error('❌ Error initializing Bridge animations:', error);
  }

  try {
    initCTAAnimations();
  } catch (error) {
    console.error('❌ Error initializing CTA animations:', error);
  }

  // Fade starfield out approaching footer
  const starfield = document.getElementById('starfield');
  const contactSection = document.querySelector('.contact');
  if (starfield && contactSection) {
    gsap.to(starfield, {
      opacity: 0,
      scrollTrigger: {
        trigger: contactSection,
        start: 'top 80%',
        end: 'top 20%',
        scrub: true
      }
    });
  }
});

// Log successful initialization
console.log('✅ GSAP + Lenis initialized successfully');
console.log('✅ Smooth scroll active');

// Document visibility detection for tab switching (AC: 6, 7)
// Pause animations when tab is hidden to prevent sync issues and save resources
document.addEventListener("visibilitychange", () => {
  if (document.hidden) {
    // Tab is hidden - pause Lenis and GSAP
    try {
      lenis.stop();
      gsap.globalTimeline.pause();
      console.log('⏸️ Animations paused (tab hidden)');
    } catch (error) {
      console.error('Error pausing animations:', error);
    }
  } else {
    // Tab is visible again - resume Lenis and GSAP
    try {
      lenis.start();
      gsap.globalTimeline.resume();
      console.log('▶️ Animations resumed (tab visible)');
    } catch (error) {
      console.error('Error resuming animations:', error);
    }
  }
});
