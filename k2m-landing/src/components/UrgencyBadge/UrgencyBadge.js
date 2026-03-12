/**
 * Urgency Badge Component - GSAP Animation Controller
 * Appears after Hero section animations complete
 * Elegant, non-intrusive urgency signaling
 */

import { gsap, ScrollTrigger } from '../../utils/gsap-config.js';

export function initUrgencyBadge() {
  const badge = document.getElementById('urgencyBadge');
  if (!badge) {
    console.warn('Urgency badge not found - skipping initialization');
    return;
  }

  // Wait for Hero animations to complete, then reveal badge
  // Hero animations take ~3 seconds total (delay: 0.3s + duration: ~2.7s)
  setTimeout(() => {
    revealBadge(badge);
  }, 3500);

  // Add subtle pulse animation after reveal
  setTimeout(() => {
    const badgeContainer = badge.querySelector('.badge-container');
    if (badgeContainer) {
      badgeContainer.classList.add('pulsing');
    }
  }, 4500);

  // Optional: Make badge dismissible
  const badgeContainer = badge.querySelector('.badge-container');
  if (badgeContainer) {
    badgeContainer.style.cursor = 'pointer';
    badgeContainer.addEventListener('click', () => {
      dismissBadge(badge);
    });
  }

  console.log('✅ Urgency badge initialized (GSAP + auto-reveal)');
}

/**
 * Reveal badge with smooth GSAP animation
 */
function revealBadge(badge) {
  gsap.to(badge, {
    opacity: 1,
    y: 0,
    duration: 0.8,
    ease: 'power3.out'
  });
}

/**
 * Dismiss badge when clicked
 */
function dismissBadge(badge) {
  gsap.to(badge, {
    opacity: 0,
    y: -20,
    x: 20,
    duration: 0.5,
    ease: 'power2.in',
    onComplete: () => {
      badge.classList.add('dismissed');
    }
  });
}

/**
 * Cleanup urgency badge animations
 */
export function cleanupUrgencyBadge() {
  const badge = document.getElementById('urgencyBadge');
  if (badge) {
    gsap.killTweensOf(badge);
    const badgeContainer = badge.querySelector('.badge-container');
    if (badgeContainer) {
      badgeContainer.classList.remove('pulsing');
    }
  }
}
