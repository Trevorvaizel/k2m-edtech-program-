/**
 * Hero Component - Cinematic Text Reveal Animations
 *
 * Implements staggered text reveals, ocean mint glow effects, and parallax typography
 * using GSAP ScrollTrigger for scroll-linked animations.
 */

import { gsap, ScrollTrigger } from '../../utils/gsap-config.js';
import { enableGPU, disableGPU, isMobile, monitorPerformance } from '../../utils/performance-optimizations.js';

/**
 * Initialize Hero animations
 * Creates cinematic text reveal with stagger, ocean mint glow, and parallax effects
 */
export function initHeroAnimations() {
  // DOM Elements
  const heroSection = document.querySelector('.hero');
  const heroTitle = document.querySelector('.hero-title');
  const heroSubtitle = document.querySelector('.hero-subtitle');
  const heroBody = document.querySelector('.hero-body p');
  const glowTexts = document.querySelectorAll('.glow-text');

  // Early return if elements don't exist
  if (!heroSection || !heroTitle || !heroSubtitle) {
    console.warn('Hero elements not found - skipping animations');
    return;
  }

  // Enable GPU acceleration before animations
  const animatedElements = [heroTitle, heroSubtitle, heroBody, ...glowTexts];
  animatedElements.forEach(el => {
    if (el) enableGPU(el);
  });

  // Create main timeline with ScrollTrigger
  const tl = gsap.timeline({
    scrollTrigger: {
      trigger: '.hero',
      start: 'top top',
      end: 'bottom center',
      scrub: 1,
    }
  });

  // Task 2: Surprise reveal - Headline visible, subtitle/body fade UP on scroll
  // Subtitle and body reveal in quick succession
  tl.to(heroSubtitle, {
    opacity: 1,
    y: 0,
    duration: 0.6,
    ease: 'power3.out'
  }, 0) // Start immediately as scroll begins
  .to(heroBody, {
    opacity: 1,
    y: 0,
    duration: 0.8,
    ease: 'power3.out'
  }, 0.1); // Tight stagger - body follows quickly

  // Task 3: Ocean mint glow PULSES dramatically as you scroll
  // Grows from nothing to prominent glowing effect
  if (glowTexts.length > 0) {
    tl.fromTo(glowTexts,
      {
        textShadow: '0 0 0px rgba(64, 224, 208, 0)'  // No glow initially
      },
      {
        textShadow: '0 0 60px rgba(64, 224, 208, 1), 0 0 100px rgba(64, 224, 208, 0.6), 0 0 140px rgba(64, 224, 208, 0.3)',  // Dramatic multi-layer glow
        duration: 1.5,
        ease: 'power2.inOut'
      }, 0.2);  // Starts slightly after text begins revealing
  }

  // Task 4: Living typography with 3-layer parallax
  // Creates depth by animating text layers at different speeds
  createParallaxLayers(heroTitle, tl);

  // Task 5: Performance optimization
  // Disable GPU acceleration after animations complete
  tl.eventCallback('onComplete', () => {
    animatedElements.forEach(el => {
      if (el) disableGPU(el);
    });
  });

  // Task 6: Safari compatibility - pause on tab hidden
  document.addEventListener('visibilitychange', handleVisibilityChange);

  // Task 7: Optional performance monitoring
  const stopMonitoring = monitorPerformance();

  // Store cleanup function on the element for later use
  heroSection._cleanup = () => {
    document.removeEventListener('visibilitychange', handleVisibilityChange);
    if (stopMonitoring) stopMonitoring();
    tl.kill();
    ScrollTrigger.getAll().forEach(trigger => {
      if (trigger.trigger === heroSection) {
        trigger.kill();
      }
    });
  };
}

/**
 * Create 3-layer parallax effect for living typography
 * @param {HTMLElement} element - The text element to animate
 * @param {GSAPTimeline} tl - The timeline to add animations to
 */
function createParallaxLayers(element, tl) {
  if (!element) return;

  // Skip parallax on mobile for performance (Task 8)
  if (isMobile()) {
    console.log('Mobile detected - skipping parallax for better performance');
    return;
  }

  // Get original text
  const text = element.textContent;

  // Create 3 layers for parallax effect
  // Layer 1: Shadow (background)
  const layer1 = document.createElement('span');
  layer1.textContent = text;
  layer1.style.cssText = `
    position: absolute;
    opacity: 0.3;
    filter: blur(4px);
    z-index: 1;
    pointer-events: none;
  `;

  // Layer 2: Blur (middle)
  const layer2 = document.createElement('span');
  layer2.textContent = text;
  layer2.style.cssText = `
    position: absolute;
    opacity: 0.6;
    filter: blur(1px);
    z-index: 2;
    pointer-events: none;
  `;

  // Layer 3: Sharp (foreground) - this is the original element
  element.style.position = 'relative';
  element.style.zIndex = '3';

  // Insert layers before the original element
  element.parentNode.insertBefore(layer1, element);
  element.parentNode.insertBefore(layer2, element);

  // Animate layers at different speeds for parallax effect
  // Layer 1 moves -30px (slowest, background)
  tl.to(layer1, {
    y: -30,
    ease: 'none',
    duration: 1
  }, 0);

  // Layer 2 moves -15px (medium)
  tl.to(layer2, {
    y: -15,
    ease: 'none',
    duration: 1
  }, 0);

  // Layer 3 (original) stays at y: 0 (fastest, foreground)
  // Already handled by the text reveal animation above
}

/**
 * Handle visibility change for Safari compatibility
 * Pauses animations when tab is hidden, resumes when visible
 */
function handleVisibilityChange() {
  if (document.hidden) {
    // Pause all GSAP animations
    gsap.globalTimeline.pause();
  } else {
    // Resume animations
    gsap.globalTimeline.play();
  }
}

/**
 * Cleanup function to remove animations and event listeners
 * Useful for SPA navigation or component unmounting
 */
export function cleanupHeroAnimations() {
  const heroSection = document.querySelector('.hero');
  if (heroSection && heroSection._cleanup) {
    heroSection._cleanup();
  }
}

// Auto-initialize if this file is loaded directly
if (typeof window !== 'undefined') {
  window.addEventListener('load', () => {
    initHeroAnimations();
  });
}
