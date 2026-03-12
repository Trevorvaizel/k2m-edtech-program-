/**
 * Hero Component - GSAP text reveal animations
 * Eyebrow fades in → Title slides in horizontally → "Not anymore" ScrambleText → Subtitle slides in → Prompt fades
 */

import { gsap, ScrollTrigger } from '../../utils/gsap-config.js';

export function initHeroAnimations() {
  const heroSection = document.querySelector('.hero');
  if (!heroSection) {
    console.warn('Hero section not found - skipping animations');
    return;
  }

  // Text reveal timeline
  initTextReveal();

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

  console.log('✅ Hero animations initialized (GSAP reveal)');
}

/**
 * Text reveal timeline - staggered entrance with ScrambleText
 */
function initTextReveal() {
  const eyebrow = document.querySelector('.hero-eyebrow');
  const title = document.querySelector('.hero-title');
  const titleStrong = title?.querySelector('strong');
  const sub = document.querySelector('.hero-sub');
  const prompt = document.querySelector('.hero-prompt');

  if (!title) return;

  const tl = gsap.timeline({ delay: 0.3 });

  // 1. Eyebrow fades in from above
  if (eyebrow) {
    tl.fromTo(eyebrow, {
      opacity: 0,
      y: -15
    }, {
      opacity: 1,
      y: 0,
      duration: 0.6,
      ease: 'power2.out'
    });
  }

  // 2. Title slides in from the left
  tl.fromTo(title, {
    opacity: 0,
    x: -60
  }, {
    opacity: 1,
    x: 0,
    duration: 0.9,
    ease: 'power3.out'
  }, eyebrow ? '-=0.2' : 0);

  // 3. ScrambleText on "Not anymore." - the payoff moment
  if (titleStrong) {
    const originalText = titleStrong.textContent;
    // Hide it initially, then scramble reveal
    gsap.set(titleStrong, { opacity: 0 });

    tl.to(titleStrong, {
      opacity: 1,
      duration: 0.1
    }, '-=0.3');

    tl.to(titleStrong, {
      duration: 1.4,
      scrambleText: {
        text: originalText,
        chars: 'upperCase',
        revealDelay: 0.3,
        speed: 0.4,
        newClass: 'scramble-active'
      },
      ease: 'none'
    }, '-=0.2');
  }

  // 4. Subtitle slides in from the right
  if (sub) {
    tl.fromTo(sub, {
      opacity: 0,
      x: 40
    }, {
      opacity: 1,
      x: 0,
      duration: 0.8,
      ease: 'power2.out'
    }, '-=0.6');
  }

  // 5. Prompt fades up gently
  if (prompt) {
    tl.fromTo(prompt, {
      opacity: 0,
      y: 15
    }, {
      opacity: 1,
      y: 0,
      duration: 0.6,
      ease: 'power2.out'
    }, '-=0.3');
  }
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
