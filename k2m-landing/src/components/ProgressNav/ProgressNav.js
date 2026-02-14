import { gsap, ScrollTrigger } from '../../utils/gsap-config.js';
import './ProgressNav.css';

/**
 * Progress Navigation Component
 * Right-side navigation dots showing current zone
 *
 * Features:
 * - Fixed positioning on right side
 * - Active state tracking (scale + glow)
 * - Click-to-scroll navigation
 * - Hover labels (desktop only)
 * - Mobile optimization (smaller dots, no labels)
 */

export class ProgressNav {
  constructor(element, data) {
    this.element = element;
    this.data = data;
    this.dots = [];
    this.currentZone = -1;
  }

  /**
   * Initialize progress navigation
   */
  init() {
    // Create dots from data
    this.createDots();

    // Setup visibility toggle (show after hero, hide after bridge)
    this.setupVisibilityTriggers();

    console.log(`✅ ProgressNav initialized with ${this.dots.length} zones`);
  }

  /**
   * Create navigation dots from data
   */
  createDots() {
    this.data.forEach(zoneData => {
      const dot = document.createElement('div');
      dot.classList.add('progress-dot');
      dot.dataset.zone = zoneData.zoneNumber;
      dot.dataset.label = zoneData.label;
      dot.title = zoneData.label;

      // Click to scroll to zone
      dot.addEventListener('click', () => {
        this.scrollToZone(zoneData.zoneNumber);
      });

      this.element.appendChild(dot);
      this.dots.push(dot);
    });
  }

  /**
   * Scroll to specific zone
   */
  scrollToZone(zoneNumber) {
    const zones = document.querySelectorAll('.resonance-zone');
    const targetZone = zones[zoneNumber];

    if (targetZone) {
      targetZone.scrollIntoView({
        behavior: 'smooth',
        block: 'center'
      });
    }
  }

  /**
   * Update active state for a zone
   */
  setActiveZone(zoneNumber) {
    this.currentZone = zoneNumber;

    this.dots.forEach((dot, index) => {
      dot.classList.toggle('active', index === zoneNumber);
    });
  }

  /**
   * Setup visibility triggers
   * Show after Hero, hide after Bridge section
   */
  setupVisibilityTriggers() {
    // Show after Hero
    ScrollTrigger.create({
      trigger: '.hero',
      start: 'top top',
      end: 'bottom top',
      onLeave: () => {
        this.element.classList.add('visible');
      },
      onEnterBack: () => {
        this.element.classList.remove('visible');
      }
    });

    // Hide after Bridge (or last zone)
    const lastZoneIndex = this.dots.length - 1;
    const lastZone = document.querySelectorAll('.resonance-zone')[lastZoneIndex];

    if (lastZone) {
      ScrollTrigger.create({
        trigger: lastZone,
        start: 'bottom center',
        onEnter: () => {
          this.element.classList.remove('visible');
        },
        onLeaveBack: () => {
          this.element.classList.add('visible');
        }
      });
    }
  }

  /**
   * Cleanup method for memory management
   */
  cleanup() {
    // Kill all ScrollTriggers
    ScrollTrigger.getAll().forEach(st => {
      if (st.trigger === this.element ||
          st.trigger === document.querySelector('.hero') ||
          st.trigger === document.querySelector('.resonance-zone:last-of-type')) {
        st.kill();
      }
    });

    // Remove event listeners
    this.dots.forEach(dot => {
      dot.replaceWith(dot.cloneNode(true));
    });

    console.log('✅ ProgressNav cleaned up');
  }
}

/**
 * Initialize progress navigation on page
 */
export function initProgressNav(zoneData) {
  const element = document.querySelector('.progress-nav');

  if (!element) {
    console.warn('ProgressNav element not found');
    return null;
  }

  const progressNav = new ProgressNav(element, zoneData);
  progressNav.init();

  // Expose for testing/cleanup
  if (typeof window !== 'undefined') {
    window.progressNav = progressNav;
  }

  return progressNav;
}
