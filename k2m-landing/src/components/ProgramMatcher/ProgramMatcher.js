/**
 * Program Matcher Component - GSAP Animation Controller
 * Appears after Zone 4 (Voice of Confidence) with ScrollTrigger
 * VIP velvet rope experience with smooth card reveals
 */

import { gsap, ScrollTrigger } from '../../utils/gsap-config.js';

export function initProgramMatcher() {
  const matcher = document.getElementById('programMatcher');
  const cards = document.querySelectorAll('.program-card');

  if (!matcher || cards.length === 0) {
    console.warn('Program matcher or cards not found - skipping initialization');
    return;
  }

  // Find Zone 4 to trigger animation
  const zone4 = document.querySelector('.resonance-zone[data-zone="4"]');
  if (!zone4) {
    console.warn('Zone 4 not found - using default scroll trigger');
    setupDefaultTrigger(matcher, cards);
  } else {
    setupZoneTrigger(matcher, cards, zone4);
  }

  // Add hover effects with GSAP
  setupHoverEffects(cards);

  console.log('✅ Program matcher initialized (GSAP + ScrollTrigger)');
}

/**
 * Setup ScrollTrigger for Zone 4 detection
 */
function setupZoneTrigger(matcher, cards, zone4) {
  // Animate matcher container when Zone 4 is in view
  ScrollTrigger.create({
    trigger: zone4,
    start: 'top 60%',
    end: 'bottom 40%',
    onEnter: () => revealMatcher(matcher, cards),
    once: true
  });
}

/**
 * Setup default ScrollTrigger (fallback)
 */
function setupDefaultTrigger(matcher, cards) {
  ScrollTrigger.create({
    trigger: matcher,
    start: 'top 80%',
    onEnter: () => revealMatcher(matcher, cards),
    once: true
  });
}

/**
 * Reveal matcher container and cards
 */
function revealMatcher(matcher, cards) {
  // Reveal container
  gsap.to(matcher.querySelector('.matcher-container'), {
    opacity: 1,
    y: 0,
    duration: 1,
    ease: 'power3.out'
  });

  // Stagger reveal cards
  gsap.to(cards, {
    opacity: 1,
    y: 0,
    duration: 0.8,
    stagger: 0.15,
    ease: 'power3.out',
    delay: 0.3,
    onStart: () => {
      cards.forEach(card => card.classList.add('card-revealed'));
    }
  });
}

/**
 * Setup hover effects for cards
 */
function setupHoverEffects(cards) {
  cards.forEach(card => {
    const button = card.querySelector('.card-button');
    if (!button) return;

    // Subtle scale on hover
    card.addEventListener('mouseenter', () => {
      gsap.to(card, {
        scale: 1.02,
        duration: 0.3,
        ease: 'power2.out'
      });
    });

    card.addEventListener('mouseleave', () => {
      gsap.to(card, {
        scale: 1,
        duration: 0.3,
        ease: 'power2.out'
      });
    });

    // Button click animation
    button.addEventListener('click', (e) => {
      // Add click ripple effect
      gsap.fromTo(button,
        { scale: 0.95 },
        {
          scale: 1,
          duration: 0.3,
          ease: 'elastic.out(1, 0.5)'
        }
      );

      // TODO: Handle actual CTA actions
      handleCardAction(card.dataset.segment);
    });
  });
}

/**
 * Handle card CTA actions
 * Task 7.1: Open enrollment form for all segments
 */
import { openEnrollmentFormForSegment } from '../EnrollmentForm/EnrollmentForm.js';

function handleCardAction(segment) {
  console.log(`CTA clicked for segment: ${segment}`);

  // Open enrollment form with profession pre-selected (Task 7.1)
  openEnrollmentFormForSegment(segment);
}

/**
 * Highlight specific card (for future personalization)
 */
export function highlightCard(segment) {
  const card = document.querySelector(`.program-card[data-segment="${segment}"]`);
  if (!card) return;

  // Remove highlight from all cards
  document.querySelectorAll('.program-card').forEach(c => {
    c.classList.remove('card-highlighted');
  });

  // Add highlight to target card
  card.classList.add('card-highlighted');

  // Scroll card into view smoothly
  gsap.to(card, {
    scrollTrigger: {
      trigger: card,
      start: 'top 80%'
    },
    y: -8,
    duration: 0.4,
    ease: 'power2.out'
  });
}

/**
 * Cleanup program matcher animations
 */
export function cleanupProgramMatcher() {
  const matcher = document.getElementById('programMatcher');
  const cards = document.querySelectorAll('.program-card');

  if (matcher) {
    ScrollTrigger.getAll().forEach(trigger => {
      if (trigger.trigger === matcher || trigger.trigger === document.querySelector('.resonance-zone[data-zone="4"]')) {
        trigger.kill();
      }
    });
  }

  cards.forEach(card => {
    gsap.killTweensOf(card);
  });
}
