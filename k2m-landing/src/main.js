import './styles/token.css'
import './style.css'
import './components/Hero/Hero.css'
import './components/TerritoryMap/MapFraming.css'

// Import Hero component HTML
import heroHtml from './components/Hero/Hero.html?raw';
import mapFramingHtml from './components/TerritoryMap/MapFraming.html?raw';

// K2M Landing Page Entry Point
// Hero section integrated (Story 1.3)
// Animation infrastructure initialized with GSAP + Lenis

// Load Hero and MapFraming HTML into app container
const app = document.getElementById('app');
if (app) {
  app.innerHTML = heroHtml + mapFramingHtml;
  console.log('✅ Hero section loaded');
  console.log('✅ MapFraming section loaded');
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

// Import and initialize Hero animations
import { initHeroAnimations } from './components/Hero/Hero.js';

// Import and initialize MapFraming animations
import { initMapFramingAnimations } from './components/TerritoryMap/MapFraming.js';

// Initialize Hero and MapFraming animations after page load
window.addEventListener('load', () => {
  try {
    initHeroAnimations();
    console.log('✅ Hero animations initialized');
  } catch (error) {
    console.error('❌ Error initializing Hero animations:', error);
  }

  try {
    initMapFramingAnimations();
    console.log('✅ MapFraming animations initialized');
  } catch (error) {
    console.error('❌ Error initializing MapFraming animations:', error);
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

