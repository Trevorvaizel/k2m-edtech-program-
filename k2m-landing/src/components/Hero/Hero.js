/**
 * Hero Component - Cinematic Text Reveal Animations
 *
 * Implements staggered text reveals, ocean mint glow effects, and parallax typography
 * using GSAP ScrollTrigger for scroll-linked animations.
 */

import { gsap, ScrollTrigger } from '../../utils/gsap-config.js';
import { enableGPU, disableGPU, isMobile, monitorPerformance } from '../../utils/performance-optimizations.js';

/**
 * Initialize Hero animations with mobile-specific optimizations
 * Uses ScrollTrigger.matchMedia() for responsive performance
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

  // Track timeline for cleanup
  let timeline = null;

  // Task 1: Mobile-specific optimizations with matchMedia
  ScrollTrigger.matchMedia({
    // Desktop (min-width: 769px) - Full animation complexity
    '(min-width: 769px)': function() {
      console.log('Desktop animations initialized - full complexity');

      // Create main timeline with ScrollTrigger
      const tl = gsap.timeline({
        scrollTrigger: {
          trigger: '.hero',
          start: 'top top',
          end: 'bottom center',
          scrub: 1,
        }
      });

      // Subtitle and body reveal with desktop timing (1.0s total)
      tl.to(heroSubtitle, {
        opacity: 1,
        y: 0,
        duration: 0.6,
        ease: 'power3.out'
      }, 0)
      .to(heroBody, {
        opacity: 1,
        y: 0,
        duration: 0.8,
        ease: 'power3.out'
      }, 0.2); // Desktop stagger: 0.2s

      // Ocean mint glow - full duration (1.5s)
      if (glowTexts.length > 0) {
        tl.fromTo(glowTexts,
          {
            textShadow: '0 0 0px rgba(64, 224, 208, 0)'
          },
          {
            textShadow: '0 0 60px rgba(64, 224, 208, 1), 0 0 100px rgba(64, 224, 208, 0.6), 0 0 140px rgba(64, 224, 208, 0.3)',
            duration: 1.5,
            ease: 'power2.inOut'
          }, 0.2);
      }

      // Living typography with 3-layer parallax (desktop only)
      createParallaxLayers(heroTitle, tl);

      // Performance optimization
      tl.eventCallback('onComplete', () => {
        animatedElements.forEach(el => {
          if (el) disableGPU(el);
        });
      });

      // Store timeline reference for cleanup
      timeline = tl;
    },

    // Mobile (max-width: 768px) - Simplified animations
    '(max-width: 768px)': function() {
      console.log('Mobile animations initialized - simplified for performance');

      // Create main timeline with ScrollTrigger
      const tl = gsap.timeline({
        scrollTrigger: {
          trigger: '.hero',
          start: 'top top',
          end: 'bottom center',
          scrub: 1,
        }
      });

      // Subtitle and body reveal with mobile timing (0.5s total)
      tl.to(heroSubtitle, {
        opacity: 1,
        y: 0,
        duration: 0.3,  // Mobile: 0.5x desktop duration
        ease: 'power3.out'
      }, 0)
      .to(heroBody, {
        opacity: 1,
        y: 0,
        duration: 0.4,  // Mobile: 0.5x desktop duration
        ease: 'power3.out'
      }, 0.1); // Mobile stagger: 0.1s (50% of desktop)

      // Ocean mint glow - simplified (0.75s vs 1.5s desktop)
      if (glowTexts.length > 0) {
        tl.fromTo(glowTexts,
          {
            textShadow: '0 0 0px rgba(64, 224, 208, 0)'
          },
          {
            textShadow: '0 0 40px rgba(64, 224, 208, 0.8), 0 0 70px rgba(64, 224, 208, 0.4)',  // Single layer glow on mobile
            duration: 0.75,  // Mobile: 0.5x desktop duration
            ease: 'power2.inOut'
          }, 0.15); // Mobile timing: 0.15s
      }

      // Skip 3-layer parallax on mobile (already handled in createParallaxLayers)

      // Performance optimization
      tl.eventCallback('onComplete', () => {
        animatedElements.forEach(el => {
          if (el) disableGPU(el);
        });
      });

      // Store timeline reference for cleanup
      timeline = tl;
    }
  });

  // Task 2: Safari compatibility - pause on tab hidden (applies to both desktop and mobile)
  document.addEventListener('visibilitychange', handleVisibilityChange);

  // Task 3: Performance monitoring (applies to both desktop and mobile)
  const stopMonitoring = monitorPerformance();

  // Store cleanup function on hero section (always available, not inside matchMedia)
  heroSection._cleanup = () => {
    // Remove visibility change listener
    document.removeEventListener('visibilitychange', handleVisibilityChange);

    // Stop performance monitoring
    if (stopMonitoring) stopMonitoring();

    // Kill timeline if it exists
    if (timeline) {
      timeline.kill();
    }

    // Kill all ScrollTriggers for hero section
    ScrollTrigger.getAll().forEach(trigger => {
      if (trigger.trigger === heroSection) {
        trigger.kill();
      }
    });

    // Disable GPU acceleration on all animated elements
    animatedElements.forEach(el => {
      if (el) disableGPU(el);
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

