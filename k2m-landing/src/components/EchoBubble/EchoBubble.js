import { gsap, ScrollTrigger } from '../../utils/gsap-config.js';
import './EchoBubble.css';

/**
 * EchoBubble Component
 * Floating thought/quote bubbles with desktop float animation and mobile stack layout
 *
 * Desktop: Absolute positioning with organic float animation
 * Mobile: Stacked flex layout with alternating left/right alignment
 *
 * Features:
 * - ScrollTrigger reveal with staggered delays
 * - Float animation when visible (desktop only)
 * - Hover highlight effect (desktop only)
 * - Responsive layout switching
 */

export class EchoBubble {
  constructor(element) {
    this.element = element;
    this.delay = parseFloat(element.dataset.delay) || 0;
    this.isVisible = false;
  }

  /**
   * Initialize echo bubble animations
   */
  init() {
    // Add hover effect for desktop
    this.element.addEventListener('mouseenter', () => {
      this.element.classList.add('highlight');
    });

    this.element.addEventListener('mouseleave', () => {
      this.element.classList.remove('highlight');
    });

    console.log(`✅ EchoBubble initialized with ${this.delay}s delay`);
  }

  /**
   * Reveal the echo bubble with animation
   * Called by parent ResonanceZone component
   */
  reveal() {
    gsap.to(this.element, {
      opacity: 1,
      y: 0,
      scale: 1,
      duration: 0.6,
      delay: this.delay,
      ease: 'power2.out',
      onComplete: () => {
        this.element.classList.add('visible');

        // Only add float animation on desktop (not mobile)
        if (window.innerWidth >= 769) {
          this.element.classList.add('floating');
        }

        this.isVisible = true;
      }
    });
  }

  /**
   * Hide the echo bubble
   * Called by parent ResonanceZone component when zone deactivates
   */
  hide() {
    this.element.classList.remove('visible', 'floating');
    this.isVisible = false;

    gsap.set(this.element, {
      opacity: 0,
      y: 20,
      scale: 0.95
    });
  }

  /**
   * Cleanup method for memory management
   */
  cleanup() {
    this.element.classList.remove('visible', 'floating', 'highlight');
    gsap.set(this.element, {
      clearProps: 'transform, opacity'
    });
  }
}

/**
 * Initialize all echo bubbles on the page
 */
export function initEchoBubbles() {
  const echoElements = document.querySelectorAll('.echo');
  const bubbles = [];

  echoElements.forEach(element => {
    const bubble = new EchoBubble(element);
    bubble.init();
    bubbles.push(bubble);
  });

  console.log(`✅ Initialized ${bubbles.length} EchoBubble components`);

  // Expose for testing/cleanup
  if (typeof window !== 'undefined') {
    window.echoBubbles = bubbles;
  }

  return bubbles;
}
