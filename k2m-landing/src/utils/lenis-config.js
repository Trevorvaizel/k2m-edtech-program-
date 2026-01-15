// Lenis Smooth Scroll Configuration
// Provides luxurious smooth scroll with GSAP integration

import Lenis from '@studio-freight/lenis';
import { gsap, ScrollTrigger } from './gsap-config.js';

/**
 * Detect if current browser is Safari
 * Used to apply Safari-specific smooth scroll optimizations
 * @returns {boolean} True if browser is Safari
 */
const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);

/**
 * Lenis smooth scroll configuration
 * Provides luxurious smooth feel with duration: 1.2s
 * Safari detection enables lerp smoothing to prevent jitter
 */
const lenisConfig = {
  duration: 1.2,        // Luxurious smooth feel (1.2 seconds)
  smooth: true,
  direction: "vertical",
  smoothWheel: true,    // Smooth mouse wheel scrolling
  smoothTouch: false,   // Use native touch scroll on mobile (feels better)
  touchMultiplier: 2    // Faster scroll on mobile
};

// Apply Safari-specific configuration to prevent jitter and "snap back" (AC: 6)
if (isSafari) {
  lenisConfig.lerp = 0.1;  // Lower = smoother, reduces jitter on Safari
  console.log('🍎 Safari detected: Applied smooth scroll optimizations');
}

// Create Lenis instance with configuration
const lenis = new Lenis(lenisConfig);

// Integrate Lenis with GSAP ticker for seamless updates (AC: 3)
gsap.ticker.add((time) => {
  lenis.raf(time * 1000);
});

// Disable GSAP lag smoothing (Lenis handles it)
gsap.ticker.lagSmoothing(0);

// Update ScrollTrigger on Lenis scroll (AC: 3)
lenis.on('scroll', ScrollTrigger.update);

// Export Lenis instance for initialization in main.js
export { lenis };
