/**
 * CTA Section - Fog Emergence Animation
 * Text emerges from blur through fog layers that slowly dissipate
 */

import { gsap, ScrollTrigger } from '../../utils/gsap-config.js';

export function initCTAAnimations() {
  const fogContainer = document.querySelector('.fog-container');
  const fogEmergeEls = gsap.utils.toArray('.fog-emerge');

  if (!fogContainer || !fogEmergeEls.length) {
    console.warn('CTA fog elements not found - skipping animations');
    return;
  }

  // Staggered text emergence from fog (blur -> clear)
  ScrollTrigger.create({
    trigger: '.cta',
    start: 'top 65%',
    once: true,
    onEnter: () => {
      const tl = gsap.timeline();

      // Each element emerges with stagger
      fogEmergeEls.forEach((el, i) => {
        tl.to(el, {
          opacity: 1,
          filter: 'blur(0px)',
          y: 0,
          duration: 2,
          ease: 'power3.out'
        }, i * 0.4);
      });

      // Fog lingers, then slowly dissipates after text is mostly revealed
      tl.to(fogContainer, {
        opacity: 0,
        duration: 6,
        ease: 'power1.inOut'
      }, 1.2);
    }
  });

  console.log('✅ CTA fog animations initialized');
}
