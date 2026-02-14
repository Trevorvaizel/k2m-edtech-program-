/**
 * Bridge Section - Post-Recognition Emotional Arc Animations
 * 4 beats: Validation, Promise, Belonging, Invitation
 */

import { gsap, ScrollTrigger } from '../../utils/gsap-config.js';

export function initBridgeAnimations() {
  const bridgeBeats = gsap.utils.toArray('.bridge-beat');

  if (!bridgeBeats.length) {
    console.warn('Bridge beats not found - skipping animations');
    return;
  }

  bridgeBeats.forEach((beat) => {
    gsap.to(beat, {
      opacity: 1,
      y: 0,
      duration: 0.9,
      ease: 'power2.out',
      scrollTrigger: {
        trigger: beat,
        start: 'top 75%',
        onEnter: () => beat.classList.add('visible'),
        onLeaveBack: () => beat.classList.remove('visible')
      }
    });

    // Transformation visual animation (Promise beat)
    if (beat.classList.contains('promise')) {
      const zoneFrom = beat.querySelector('.zone-from');
      const zoneTo = beat.querySelector('.zone-to');

      ScrollTrigger.create({
        trigger: beat,
        start: 'top 65%',
        onEnter: () => {
          gsap.from(zoneFrom, {
            scale: 0.8,
            opacity: 0,
            duration: 0.5,
            ease: 'back.out(1.5)'
          });

          gsap.from(zoneTo, {
            scale: 0.8,
            opacity: 0,
            duration: 0.5,
            delay: 0.4,
            ease: 'back.out(1.5)'
          });
        }
      });
    }

    // Cluster dots animation (Belonging beat)
    if (beat.classList.contains('belonging')) {
      ScrollTrigger.create({
        trigger: beat,
        start: 'top 65%',
        onEnter: () => {
          const centerDot = beat.querySelector('.dot.center');
          if (centerDot) {
            gsap.to(centerDot, {
              scale: 1.3,
              duration: 0.8,
              ease: 'sine.inOut',
              yoyo: true,
              repeat: -1,
              delay: 0.6
            });
          }
        },
        onLeaveBack: () => {
          const centerDot = beat.querySelector('.dot.center');
          if (centerDot) {
            gsap.killTweensOf(centerDot);
            gsap.set(centerDot, { scale: 1 });
          }
        }
      });
    }

    // Final invitation beat
    if (beat.classList.contains('invitation')) {
      const statement = beat.querySelector('.beat-statement-final');

      ScrollTrigger.create({
        trigger: beat,
        start: 'top 60%',
        onEnter: () => {
          gsap.from(statement, {
            scale: 0.95,
            opacity: 0,
            duration: 1,
            ease: 'power3.out'
          });
        }
      });
    }
  });

  console.log('✅ Bridge animations initialized');
}
