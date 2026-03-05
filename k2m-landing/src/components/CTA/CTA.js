/**
 * CTA Section - Fog Emergence Animation
 * Fog fades IN as user scrolls into CTA section
 * Fog fades OUT as user scrolls toward footer
 * Text emerges from blur with staggered reveal
 * Task 7.1: "Enroll Now" button opens enrollment form modal
 */
import { gsap, ScrollTrigger } from '../../utils/gsap-config.js';

export function initCTAAnimations() {
  const fogContainer = document.querySelector('.fog-container');
  const fogEmergeEls = gsap.utils.toArray('.fog-emerge');
  const ctaSection = document.querySelector('.cta');
  const contactSection = document.querySelector('.contact');

  // Task 7.1: Bind "Enroll Now" button to enrollment form modal
  const enrollButton = document.getElementById('ctaEnrollButton');
  if (enrollButton && window.openEnrollmentForm) {
    enrollButton.addEventListener('click', () => {
      window.openEnrollmentForm();
    });
    console.log('✅ CTA enroll button linked to enrollment form');
  }

  if (!fogContainer || !fogEmergeEls.length || !ctaSection) {
    console.warn('CTA fog elements not found - skipping animations');
    return;
  }

  // Start fog invisible
  gsap.set(fogContainer, { opacity: 0 });

  // Fog FADES IN as you scroll into CTA section (scrub-linked)
  gsap.to(fogContainer, {
    opacity: 1,
    scrollTrigger: {
      trigger: ctaSection,
      start: 'top 90%',
      end: 'top 30%',
      scrub: 1
    }
  });

  // Fog FADES OUT as you scroll toward footer/contact
  if (contactSection) {
    gsap.to(fogContainer, {
      opacity: 0,
      scrollTrigger: {
        trigger: contactSection,
        start: 'top 80%',
        end: 'top 30%',
        scrub: 1
      }
    });
  }

  // Staggered text emergence from fog (blur -> clear)
  ScrollTrigger.create({
    trigger: ctaSection,
    start: 'top 55%',
    once: true,
    onEnter: () => {
      fogEmergeEls.forEach((el, i) => {
        gsap.to(el, {
          opacity: 1,
          filter: 'blur(0px)',
          y: 0,
          duration: 1.5,
          delay: i * 0.3,
          ease: 'power3.out'
        });
      });
    }
  });

  console.log('✅ CTA fog animations initialized (scroll-linked)');
}
