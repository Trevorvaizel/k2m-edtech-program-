import { gsap, ScrollTrigger } from '../../utils/gsap-config.js';

/**
 * Resonance Zone - Direct DOM animation
 * Echoes are defined in HTML with data-delay attributes.
 * This JS simply animates the existing elements on scroll.
 */

let allZones = [];

export function initResonanceZones() {
  const zones = document.querySelectorAll('.resonance-zone[data-zone]');

  if (!zones.length) {
    console.warn('Resonance zones not found - skipping animations');
    return;
  }

  allZones = Array.from(zones);
  const progressDots = document.querySelectorAll('.progress-dot');

  zones.forEach((zone, index) => {
    const echoes = zone.querySelectorAll('.echo');
    const voiceStage = zone.querySelector('.voice-stage');

    // Match mockup trigger windows
    ScrollTrigger.create({
      trigger: zone,
      start: 'top 55%',
      end: 'bottom 45%',
      onEnter: () => activateZone(zone, index, echoes, progressDots),
      onEnterBack: () => activateZone(zone, index, echoes, progressDots),
      onLeave: () => deactivateZone(zone, echoes),
      onLeaveBack: () => deactivateZone(zone, echoes)
    });
  });

  // Echo highlight on hover (desktop)
  document.querySelectorAll('.echo').forEach(echo => {
    echo.addEventListener('mouseenter', () => echo.classList.add('highlight'));
    echo.addEventListener('mouseleave', () => echo.classList.remove('highlight'));
  });

  console.log(`✅ Initialized ${zones.length} ResonanceZones (direct DOM)`);
}

function activateZone(zone, index, echoes, progressDots) {
  // Don't deactivate other zones' echoes - let them linger
  allZones.forEach(z => {
    if (z !== zone && z.classList.contains('in-focus')) {
      z.classList.remove('in-focus');
    }
  });

  // Always add in-focus (even if already set)
  // CSS transitions handle voice-stage animation
  zone.classList.add('in-focus');

  // Update progress dots directly (matching mockup approach)
  if (progressDots && progressDots.length) {
    progressDots.forEach((dot, i) => {
      dot.classList.toggle('active', i === index);
    });
  }

  // Staggered echo reveal with floating
  echoes.forEach((echo, i) => {
    const delay = parseFloat(echo.dataset.delay) || i * 0.1;
    gsap.to(echo, {
      opacity: 1,
      y: 0,
      scale: 1,
      duration: 0.6,
      delay: delay,
      ease: 'power2.out',
      onComplete: () => {
        echo.classList.add('visible', 'floating');
      }
    });
  });
}

function deactivateZone(zone, echoes) {
  // CSS transitions handle voice-stage deactivation
  zone.classList.remove('in-focus');

  // Don't hide echoes - let them linger for ambient effect
  // They'll fade naturally with CSS transition
}
