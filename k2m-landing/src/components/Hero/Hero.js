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
          start: 'top top', // Start when hero top hits viewport top
          end: '+=1200', // Scroll 1200px to complete (slower, more luxurious feel)
          scrub: 1, // Smooth scroll-linked animation
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

      // Ocean mint glow - spans entire scroll for maximum visibility
      if (glowTexts.length > 0) {
        tl.fromTo(glowTexts,
          {
            textShadow: '0 0 0px rgba(64, 224, 208, 0)'
          },
          {
            textShadow: '0 0 60px rgba(64, 224, 208, 0.9), 0 0 90px rgba(64, 224, 208, 0.5)', // Simplified 2-layer glow
            duration: 1.0,
            ease: 'power2.inOut'
          }, 0);
      }

      // Living typography with 3-layer parallax (DISABLED for performance)
      // createParallaxLayers(heroTitle, tl);

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
          start: 'top top', // Start when hero top hits viewport top
          end: '+=1200', // Scroll 1200px to complete (slower, more luxurious feel)
          scrub: 1, // Smooth scroll-linked animation
        }
      });

      // Subtitle and body reveal with mobile timing
      tl.to(heroSubtitle, {
        opacity: 1,
        y: 0,
        duration: 0.3,
        ease: 'power3.out'
      }, 0)
      .to(heroBody, {
        opacity: 1,
        y: 0,
        duration: 0.6, // Longer duration for better visibility
        ease: 'power3.out'
      }, 0.1); // Mobile stagger: 0.1s

      // Ocean mint glow - full scroll for visibility
      if (glowTexts.length > 0) {
        console.log(`🎨 Mobile: Animating ${glowTexts.length} glow text elements`);
        tl.fromTo(glowTexts,
          {
            textShadow: '0 0 0px rgba(64, 224, 208, 0)'
          },
          {
            textShadow: '0 0 60px rgba(64, 224, 208, 0.9), 0 0 100px rgba(64, 224, 208, 0.6)',  // Stronger glow
            duration: 1.0, // Full scroll duration
            ease: 'power2.inOut'
          }, 0); // Start immediately
      } else {
        console.warn('⚠️ Mobile: No glow text elements found!');
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

  // Note: visibilitychange listener handled globally in main.js (not duplicated here)
  // Task 3: Performance monitoring (applies to both desktop and mobile)
  const stopMonitoring = monitorPerformance();

  // Store cleanup function on hero section (always available, not inside matchMedia)
  heroSection._cleanup = () => {
    // Note: visibilitychange listener removed by main.js, not duplicated here

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
  // Layer 1: Shadow (background) - NO BLUR for performance
  const layer1 = document.createElement('span');
  layer1.textContent = text;
  layer1.style.cssText = `
    position: absolute;
    opacity: 0.25;
    z-index: 1;
    pointer-events: none;
    will-change: transform, opacity;
  `;

  // Layer 2: Semi-transparent (middle) - NO BLUR for performance
  const layer2 = document.createElement('span');
  layer2.textContent = text;
  layer2.style.cssText = `
    position: absolute;
    opacity: 0.5;
    z-index: 2;
    pointer-events: none;
    will-change: transform, opacity;
  `;

  // Layer 3: Sharp (foreground) - this is the original element
  element.style.position = 'relative';
  element.style.zIndex = '3';

  // Insert layers before the original element
  element.parentNode.insertBefore(layer1, element);
  element.parentNode.insertBefore(layer2, element);

  // Enable GPU acceleration on parallax layers
  enableGPU(layer1);
  enableGPU(layer2);

  // Animate layers at different speeds for parallax effect
  // Layer 1 moves -20px (slowest, background) - REDUCED from -30px
  tl.to(layer1, {
    y: -20,
    ease: 'none',
    duration: 1
  }, 0);

  // Layer 2 moves -10px (medium) - REDUCED from -15px
  tl.to(layer2, {
    y: -10,
    ease: 'none',
    duration: 1
  }, 0);

  // Layer 3 (original) stays at y: 0 (fastest, foreground)
  // Already handled by the text reveal animation above

  // Disable GPU acceleration after animations complete
  tl.eventCallback('onComplete', () => {
    disableGPU(layer1);
    disableGPU(layer2);
  });
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

