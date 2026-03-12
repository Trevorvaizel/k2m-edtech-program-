import { gsap, ScrollTrigger } from '../../utils/gsap-config.js';

/**
 * Resonance Zone - Direct DOM animation
 * Uses CSS classes for state (in-focus, visible, floating).
 * GSAP only used for initial stagger timing + Zone 4 special effect.
 * No fromTo — avoids conflicts on scroll back/forth.
 */

function isMobile() {
  return window.innerWidth <= 768;
}

let allZones = [];

export function initResonanceZones() {
  const zones = document.querySelectorAll('.resonance-zone[data-zone]');

  if (!zones.length) {
    console.warn('Resonance zones not found - skipping animations');
    return;
  }

  allZones = Array.from(zones);
  const progressDots = document.querySelectorAll('.progress-dot');

  // Activate first zone immediately on page load
  if (zones.length > 0) {
    const firstZone = zones[0];
    firstZone.classList.add('in-focus');
    revealEchoes(firstZone);
  }

  // ScrollTrigger for all zones
  zones.forEach((zone, index) => {
    ScrollTrigger.create({
      trigger: zone,
      start: 'top 75%',
      end: 'bottom 25%',
      onEnter: () => activateZone(zone, index, progressDots),
      onEnterBack: () => activateZone(zone, index, progressDots),
      onLeave: () => deactivateZone(zone),
      onLeaveBack: () => deactivateZone(zone)
    });
  });

  // Echo highlight on hover (desktop)
  document.querySelectorAll('.echo').forEach(echo => {
    echo.addEventListener('mouseenter', () => echo.classList.add('highlight'));
    echo.addEventListener('mouseleave', () => echo.classList.remove('highlight'));
  });

  console.log(`✅ Initialized ${zones.length} ResonanceZones`);
}

/**
 * Activate a zone: add in-focus class, reveal echoes with stagger
 */
function activateZone(zone, index, progressDots) {
  // Remove focus from all other zones
  allZones.forEach(z => {
    if (z !== zone) z.classList.remove('in-focus');
  });

  // Focus this zone (CSS transitions handle voice-stage card)
  zone.classList.add('in-focus');

  // Update progress nav
  if (typeof window !== 'undefined' && window.progressNav) {
    window.progressNav.setActiveZone(index);
  } else if (progressDots && progressDots.length) {
    progressDots.forEach((dot, i) => {
      dot.classList.toggle('active', i === index);
    });
  }

  // Reveal echoes (staggered via CSS transition-delay or GSAP)
  revealEchoes(zone);

  // Zone 4 special fog effect (only once)
  if (index === 4) {
    createZone4WHOAEffect(zone);
  }
}

/**
 * Deactivate a zone: remove in-focus, hide echoes
 */
function deactivateZone(zone) {
  zone.classList.remove('in-focus');
  hideEchoes(zone);
}

/**
 * Reveal echoes with staggered timing.
 * Only clears GSAP-managed props (opacity, transform) — preserves inline position styles.
 */
function revealEchoes(zone) {
  const echoes = zone.querySelectorAll('.echo');

  echoes.forEach((echo, i) => {
    // If already visible, skip
    if (echo.classList.contains('visible')) return;

    const delay = parseFloat(echo.dataset.delay) || i * 0.1;

    // Kill any running tweens, clear only GSAP-managed properties
    gsap.killTweensOf(echo);
    gsap.set(echo, { clearProps: 'opacity,transform,scale,x,y,rotation' });

    // Stagger the reveal via setTimeout so CSS transition handles the animation
    setTimeout(() => {
      echo.classList.add('visible');
      // Add floating after the reveal transition completes
      setTimeout(() => {
        echo.classList.add('floating');
      }, 600);
    }, delay * 1000);
  });
}

/**
 * Hide echoes by removing CSS classes.
 * Only clears GSAP-managed props — preserves inline position styles (top, left, etc).
 */
function hideEchoes(zone) {
  const echoes = zone.querySelectorAll('.echo');

  echoes.forEach(echo => {
    gsap.killTweensOf(echo);
    gsap.set(echo, { clearProps: 'opacity,transform,scale,x,y,rotation' });
    echo.classList.remove('visible', 'floating');
  });
}

/**
 * Zone 4 WHOA Effect - Dramatic fog emergence (desktop only, runs once)
 */
function createZone4WHOAEffect(zone) {
  if (zone.dataset.whoaEffect === 'true') return;
  zone.dataset.whoaEffect = 'true';

  const mobile = isMobile();
  const whoaTimeline = gsap.timeline();

  // Scale pulse
  whoaTimeline.fromTo(zone, {
    scale: 0.95,
    filter: mobile ? 'brightness(0.8)' : 'brightness(0.8) blur(4px)'
  }, {
    scale: 1,
    filter: mobile ? 'brightness(1.4)' : 'brightness(1.4) blur(0px)',
    duration: mobile ? 0.8 : 1.2,
    ease: 'power3.out'
  });

  // Fog layers (desktop only)
  if (!mobile) {
    const fogContainer = document.createElement('div');
    fogContainer.className = 'zone-4-fog-container';
    fogContainer.style.cssText = `
      position: absolute;
      inset: -60px;
      pointer-events: none;
      overflow: hidden;
      z-index: 3;
      -webkit-mask-image: radial-gradient(ellipse 70% 60% at 50% 50%, black 30%, transparent 80%);
      mask-image: radial-gradient(ellipse 70% 60% at 50% 50%, black 30%, transparent 80%);
    `;
    zone.style.position = 'relative';
    zone.appendChild(fogContainer);

    for (let i = 1; i <= 2; i++) {
      const fogLayer = document.createElement('div');
      fogLayer.className = `zone-4-fog-layer zone-4-fog-layer-${i}`;
      fogLayer.style.cssText = `
        position: absolute;
        width: 200%;
        height: 120%;
        top: ${-10 + (i * 5)}%;
        left: -50%;
        background: url("data:image/svg+xml,%3Csvg viewBox='0 0 800 800' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='z4f'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.005' numOctaves='2' seed='${i}'/%3E%3CfeColorMatrix values='0 0 0 9 -4 0 0 0 9 -4 0 0 0 9 -4 0 0 0 0 0.15'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23z4f)'/%3E%3C/svg%3E");
        background-size: 900px 900px;
        opacity: ${0.45 - (i * 0.05)};
        filter: blur(${12 + (i * 2)}px);
        will-change: transform;
        contain: layout style;
      `;
      fogContainer.appendChild(fogLayer);

      const driftDirection = i === 1 ? 0 : -50;
      const driftEnd = i === 1 ? -50 : 0;

      gsap.set(fogLayer, { x: driftDirection });
      gsap.to(fogLayer, {
        x: driftEnd,
        duration: 65 + (i * 15),
        repeat: -1,
        ease: 'none'
      });
    }

    const mistTint = document.createElement('div');
    mistTint.className = 'zone-4-mist-tint';
    mistTint.style.cssText = `
      position: absolute;
      inset: 0;
      background: radial-gradient(ellipse 80% 50% at 50% 50%, rgba(139,92,246,0.15) 0%, transparent 70%);
      mix-blend-mode: screen;
      opacity: 0;
      pointer-events: none;
    `;
    fogContainer.appendChild(mistTint);

    whoaTimeline.fromTo(fogContainer, { opacity: 1 }, {
      opacity: 0, duration: 6, ease: 'power1.inOut', delay: 1
    }, '-=0.6');

    whoaTimeline.to(mistTint, {
      opacity: 1, duration: 0.8, ease: 'power2.out'
    }, '-=3.5');

    whoaTimeline.to(mistTint, {
      opacity: 0, duration: 2, ease: 'power1.inOut'
    }, '-=1.5');
  }

  console.log('✨ Zone 4 WHOA fog effect created');
}
