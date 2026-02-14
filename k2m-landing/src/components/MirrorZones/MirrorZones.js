/**
 * Mirror Zones - Aquatic Echo + Spotlight Theater Animations
 *
 * Implements zone activation, whisper floating animations, and progress tracking
 * using GSAP ScrollTrigger for immersive scroll-linked effects.
 */

import { gsap, ScrollTrigger } from '../../utils/gsap-config.js';
import { enableGPU, disableGPU, isMobile } from '../../utils/performance-optimizations.js';

/**
 * Initialize Mirror Zones animations
 */
export function initMirrorZonesAnimations() {
  const zones = gsap.utils.toArray('.mirror-zone');
  const progressBar = document.querySelector('.progress-bar');
  const progressFill = progressBar?.querySelector('.fill');

  if (!zones.length || !progressBar || !progressFill) {
    console.warn('Mirror zones elements not found - skipping animations');
    return;
  }

  const totalZones = zones.length;
  const mobile = isMobile();

  // Progress bar visibility
  ScrollTrigger.create({
    trigger: '.hero',
    start: 'bottom top',
    onLeave: () => progressBar.classList.add('visible'),
    onEnterBack: () => progressBar.classList.remove('visible')
  });

  ScrollTrigger.create({
    trigger: zones[zones.length - 1], // Last zone
    start: 'bottom 80%',
    onEnter: () => progressBar.classList.remove('visible'),
    onLeaveBack: () => progressBar.classList.add('visible')
  });

  // Position whispers on desktop
  if (!mobile) {
    document.querySelectorAll('.whisper').forEach(whisper => {
      const x = whisper.dataset.x || 10;
      const y = whisper.dataset.y || 20;
      whisper.style.left = `${x}%`;
      whisper.style.top = `${y}%`;
    });
  }

  // Aquatic floating animation configs
  const driftConfigs = {
    slow: { yAmp: 15, xAmp: 8, duration: 7, rotation: 1.5 },
    medium: { yAmp: 20, xAmp: 12, duration: 5, rotation: 2 },
    fast: { yAmp: 25, xAmp: 15, duration: 4, rotation: 2.5 }
  };

  // Zone animations
  zones.forEach((zone, index) => {
    const whispers = zone.querySelectorAll('.whisper');
    const stage = zone.querySelector('.voice-stage');

    // Enable GPU acceleration
    if (stage) enableGPU(stage);
    whispers.forEach(w => enableGPU(w));

    ScrollTrigger.create({
      trigger: zone,
      start: 'top 55%',
      end: 'bottom 45%',
      onEnter: () => activateZone(zone, whispers, index),
      onEnterBack: () => activateZone(zone, whispers, index),
      onLeave: () => deactivateZone(zone, whispers),
      onLeaveBack: () => deactivateZone(zone, whispers)
    });
  });

  function activateZone(zone, whispers, index) {
    zones.forEach(z => z.classList.remove('active'));
    zone.classList.add('active');

    // Update progress
    const progress = ((index + 1) / totalZones) * 100;
    gsap.to(progressFill, { height: `${progress}%`, duration: 0.4 });

    // Animate whispers with aquatic float
    whispers.forEach((whisper, i) => {
      const drift = driftConfigs[whisper.dataset.drift] || driftConfigs.medium;

      // Reveal
      gsap.to(whisper, {
        opacity: 1,
        y: 0,
        scale: 1,
        duration: 0.7,
        delay: i * 0.12,
        ease: 'power2.out',
        onComplete: () => {
          whisper.classList.add('floating');

          // Desktop: add aquatic float animation
          if (!mobile) {
            // Kill any existing animation
            gsap.killTweensOf(whisper, 'y,x,rotation');

            // Create organic water-like movement
            gsap.to(whisper, {
              y: `+=${drift.yAmp}`,
              x: `+=${drift.xAmp * (Math.random() > 0.5 ? 1 : -1)}`,
              rotation: drift.rotation * (Math.random() > 0.5 ? 1 : -1),
              duration: drift.duration,
              ease: 'sine.inOut',
              yoyo: true,
              repeat: -1,
              delay: i * 0.3
            });
          }
        }
      });
    });
  }

  function deactivateZone(zone, whispers) {
    zone.classList.remove('active');

    whispers.forEach(whisper => {
      whisper.classList.remove('floating');
      gsap.killTweensOf(whisper);
      gsap.to(whisper, {
        opacity: 0,
        y: 20,
        scale: 0.95,
        duration: 0.4,
        ease: 'power2.in'
      });
    });
  }

  // Parallax effect on whispers during scroll (desktop only)
  if (!mobile) {
    zones.forEach(zone => {
      const whispers = zone.querySelectorAll('.whisper');

      whispers.forEach((whisper, i) => {
        const speed = 0.1 + (i * 0.05); // Varying parallax speeds

        gsap.to(whisper, {
          yPercent: -30 * speed,
          ease: 'none',
          scrollTrigger: {
            trigger: zone,
            start: 'top bottom',
            end: 'bottom top',
            scrub: 1
          }
        });
      });
    });
  }

  console.log('✅ Mirror zones animations initialized');
}

/**
 * Cleanup function
 */
export function cleanupMirrorZonesAnimations() {
  ScrollTrigger.getAll().forEach(trigger => {
    const triggerEl = trigger.trigger;
    if (triggerEl && triggerEl.classList.contains('mirror-zone')) {
      trigger.kill();
    }
  });
}
