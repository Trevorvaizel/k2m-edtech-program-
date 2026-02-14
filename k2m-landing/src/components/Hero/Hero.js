/**
 * Hero Component - Logo animation + scroll cue fadeout
 * Text reveals are handled by CSS animations (fade-up with staggered delays).
 * GSAP only handles the logo hover and scroll-cue fade.
 */

import { gsap, ScrollTrigger } from '../../utils/gsap-config.js';

export function initHeroAnimations() {
  const heroSection = document.querySelector('.hero');
  if (!heroSection) {
    console.warn('Hero section not found - skipping animations');
    return;
  }

  // Logo hover animation
  initLogoAnimation();

  // Fade out scroll cue when user starts scrolling
  const scrollCue = document.querySelector('.scroll-cue');
  if (scrollCue) {
    gsap.to(scrollCue, {
      opacity: 0,
      scrollTrigger: {
        trigger: heroSection,
        start: 'top top',
        end: '+=200',
        scrub: true
      }
    });
  }

  console.log('✅ Hero animations initialized (CSS auto-play)');
}

/**
 * Logo hover animation - revolve on hover
 */
function initLogoAnimation() {
  const logo = document.querySelector('.k2m-logo');
  if (!logo) return;

  let rotationTween = null;

  logo.addEventListener('mouseenter', () => {
    if (rotationTween) rotationTween.kill();
    rotationTween = gsap.to(logo, {
      rotation: 360,
      duration: 4,
      ease: 'none',
      repeat: -1
    });
  });

  logo.addEventListener('mouseleave', () => {
    if (rotationTween) {
      rotationTween.repeat(0);
      rotationTween = null;
    }
  });
}

export function cleanupHeroAnimations() {
  const heroSection = document.querySelector('.hero');
  if (heroSection && heroSection._cleanup) {
    heroSection._cleanup();
  }
}
