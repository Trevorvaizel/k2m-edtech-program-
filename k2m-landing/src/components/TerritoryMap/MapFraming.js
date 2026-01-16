// MapFraming.js - Pre-map anticipation framing animations
// Story 2.0: Build Pre-Map Anticipation Framing

import { gsap, ScrollTrigger } from '../../utils/gsap-config.js';
import { enableGPU, disableGPU, monitorPerformance } from '../../utils/performance-optimizations.js';

/**
 * Initialize MapFraming animations
 * - Anticipatory pin with smooth slowdown
 * - Progressive text reveals (70%, 50%, 30% viewport triggers)
 * - Background dimming (#0A0A0A → #000000)
 * - Mobile-optimized with matchMedia
 */
export function initMapFramingAnimations() {
  // Start FPS monitoring
  monitorPerformance();

  // Select all framing text elements
  const framingElements = document.querySelectorAll('.framing-text');

  // Enable GPU acceleration for animated elements
  if (framingElements.length > 0) {
    enableGPU();
  }

  // Desktop animations (full experience)
  ScrollTrigger.matchMedia({
    // Desktop - Full anticipatory pin effect
    '(min-width: 769px)': function() {
      // Create main timeline for desktop
      const desktopTimeline = gsap.timeline({
        scrollTrigger: {
          trigger: '.map-framing',
          start: 'top top',
          end: '+=80vh', // Section spans 30-40% of scroll journey
          scrub: 1, // Smooth scroll-controlled animation
          anticipatePin: 1, // Gradual slowdown before pin
          pin: true, // Pin section during scroll
          onUpdate: (self) => {
            // Sync background dimming with scroll progress
            const darkness = self.progress; // 0 to 1
            const colorValue = Math.floor(10 * (1 - darkness));
            gsap.set('.map-framing', {
              backgroundColor: `rgb(${colorValue}, ${colorValue}, ${colorValue})`
            });
          }
        }
      });

      // Progressive text reveals - Desktop timing
      desktopTimeline
        .from('.framing-text-1', {
          y: 30,
          opacity: 0,
          duration: 1.5,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: '.framing-text-1',
            start: 'top 70%', // Trigger when element reaches 70% down viewport
            toggleActions: 'play none none reverse'
          }
        })
        .from('.framing-text-2', {
          y: 30,
          opacity: 0,
          duration: 1.5,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: '.framing-text-2',
            start: 'top 50%', // Trigger when element reaches 50% down viewport
            toggleActions: 'play none none reverse'
          }
        }, '-=0.5') // Overlap by 0.5s
        .from('.framing-text-3', {
          y: 30,
          opacity: 0,
          duration: 1.5,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: '.framing-text-3',
            start: 'top 30%', // Trigger when element reaches 30% down viewport
            toggleActions: 'play none none reverse'
          }
        }, '-=0.5'); // Overlap by 0.5s

      console.log('✅ MapFraming animations initialized (desktop)');
    },

    // Mobile - Optimized for smaller screens
    '(max-width: 768px)': function() {
      // Create mobile-specific timeline
      const mobileTimeline = gsap.timeline({
        scrollTrigger: {
          trigger: '.map-framing',
          start: 'top top',
          end: '+=50vh', // Shorter pin duration on mobile
          scrub: 1,
          anticipatePin: 1,
          pin: true,
          onUpdate: (self) => {
            // Simplified background dimming for mobile
            const darkness = self.progress;
            const colorValue = Math.floor(10 * (1 - darkness));
            gsap.set('.map-framing', {
              backgroundColor: `rgb(${colorValue}, ${colorValue}, ${colorValue})`
            });
          }
        }
      });

      // Progressive text reveals - Mobile timing (faster)
      mobileTimeline
        .from('.framing-text-1', {
          y: 20,
          opacity: 0,
          duration: 1, // Shorter duration on mobile
          ease: 'power3.out',
          scrollTrigger: {
            trigger: '.framing-text-1',
            start: 'top 70%',
            toggleActions: 'play none none reverse'
          }
        })
        .from('.framing-text-2', {
          y: 20,
          opacity: 0,
          duration: 1,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: '.framing-text-2',
            start: 'top 50%',
            toggleActions: 'play none none reverse'
          }
        }, '-=0.3') // Smaller overlap on mobile
        .from('.framing-text-3', {
          y: 20,
          opacity: 0,
          duration: 1,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: '.framing-text-3',
            start: 'top 30%',
            toggleActions: 'play none none reverse'
          }
        }, '-=0.3'); // Smaller overlap on mobile

      console.log('✅ MapFraming animations initialized (mobile)');
    }
  });

  // Cleanup function for memory management
  function cleanup() {
    // Disable GPU acceleration
    disableGPU();

    // Kill all ScrollTrigger instances
    ScrollTrigger.getAll().forEach(trigger => trigger.kill());

    console.log('✅ MapFraming animations cleaned up');
  }

  // Cleanup on page unload
  window.addEventListener('beforeunload', cleanup);

  return cleanup; // Return cleanup function for manual cleanup if needed
}
