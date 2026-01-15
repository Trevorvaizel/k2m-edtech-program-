// GSAP + ScrollTrigger Configuration
// Centralized setup for all GSAP animations in the project

import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

// Register ScrollTrigger plugin
gsap.registerPlugin(ScrollTrigger);

// Configure global defaults (AC: 2)
gsap.defaults({
  ease: "power2.out",
  duration: 0.8
});

// Configure ScrollTrigger with mobile-friendly settings (AC: 2)
ScrollTrigger.config({
  ignoreMobileResize: true,  // Prevents resize issues on mobile URL bar
  autoRefreshEvents: "visibilitychange,DOMContentLoaded,load"
});

// Export for use in components
export { gsap, ScrollTrigger };
