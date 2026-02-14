/**
 * Constellation Zones - Star Field & Connected Thoughts Animations
 *
 * Implements star field background, constellation line drawing, and zone activation
 * using GSAP ScrollTrigger for cosmic visual experience.
 */

import { gsap, ScrollTrigger } from '../../utils/gsap-config.js';
import { enableGPU, disableGPU, isMobile } from '../../utils/performance-optimizations.js';

/**
 * Initialize Constellation Zones animations
 */
export function initConstellationZonesAnimations() {
  // Create background stars
  createStarField();

  // Zone animations and constellation lines
  const zones = document.querySelectorAll('.constellation-zone[data-zone]');

  if (!zones.length) {
    console.warn('Constellation zones not found - skipping animations');
    return;
  }

  const mobile = isMobile();

  // Position thought stars and draw constellation lines
  zones.forEach(zone => {
    const starPool = zone.querySelector('.star-pool-mobile');
    const stars = starPool ? starPool.querySelectorAll('.thought-star') : zone.querySelectorAll('.thought-star');
    const canvas = zone.querySelector('.constellation-canvas');

    if (!canvas || stars.length === 0) return;

    // Enable GPU acceleration
    stars.forEach(s => enableGPU(s));
    const nebula = zone.querySelector('.voice-nebula');
    if (nebula) enableGPU(nebula);

    // Position stars
    stars.forEach(star => {
      if (mobile) {
        // Mobile: Squeeze constellation pattern - cluster above/below center
        // Transform positions to concentrate around vertical center
        const x = parseFloat(star.dataset.x);
        const y = parseFloat(star.dataset.y);

        // Compress horizontal spread (move closer to center)
        // Adjust vertical to be clearly above/below nebula (nebula is at ~50%)
        let mobileX, mobileY;

        if (y < 50) {
          // Top stars: position well above nebula (10-30% from top)
          mobileX = 25 + (x / 100) * 50; // Compress to 25-75% width
          mobileY = 10 + (y / 50) * 20;  // 10-30% from top (above nebula)
        } else {
          // Bottom stars: position well below nebula (70-90% from top)
          mobileX = 25 + (x / 100) * 50; // Compress to 25-75% width
          mobileY = 70 + ((y - 50) / 50) * 20;  // 70-90% from top (below nebula)
        }

        star.style.left = `${mobileX}%`;
        star.style.top = `${mobileY}%`;
      } else {
        // Desktop: Use original positions
        star.style.left = `${star.dataset.x}%`;
        star.style.top = `${star.dataset.y}%`;
      }
    });

    // Draw constellation lines (connect all stars in a pattern)
    const positions = Array.from(stars).map(s => {
      // Get the actual positioned coordinates (after mobile adjustment)
      const left = parseFloat(s.style.left) || parseFloat(s.dataset.x);
      const top = parseFloat(s.style.top) || parseFloat(s.dataset.y);
      return { x: left, y: top };
    });

    // Create SVG lines connecting stars
    if (positions.length >= 2) {
      // Connect in a meaningful pattern (not just sequential)
      const connections = [
        [0, 1], [1, 3], [3, 2], [2, 0], // Outer square
        [0, 3], [1, 2] // Cross lines
      ];

      connections.forEach(([a, b]) => {
        if (positions[a] && positions[b]) {
          const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
          line.setAttribute('x1', `${positions[a].x}%`);
          line.setAttribute('y1', `${positions[a].y}%`);
          line.setAttribute('x2', `${positions[b].x}%`);
          line.setAttribute('y2', `${positions[b].y}%`);
          line.classList.add('constellation-line');
          canvas.appendChild(line);
        }
      });
    }

    // ScrollTrigger for zone activation
    ScrollTrigger.create({
      trigger: zone,
      start: 'top 55%',
      end: 'bottom 45%',
      onEnter: () => activateZone(zone, stars, nebula),
      onEnterBack: () => activateZone(zone, stars, nebula),
      onLeave: () => deactivateZone(zone, stars),
      onLeaveBack: () => deactivateZone(zone, stars)
    });
  });

  function activateZone(zone, stars, nebula) {
    zones.forEach(z => z.classList.remove('active'));
    zone.classList.add('active');

    // Stagger star reveals
    stars.forEach((star, i) => {
      setTimeout(() => star.classList.add('visible'), i * 200);
    });
  }

  function deactivateZone(zone, stars) {
    zone.classList.remove('active');
    stars.forEach(s => s.classList.remove('visible'));
  }

  console.log('✅ Constellation zones animations initialized');
}

/**
 * Create background star field
 */
function createStarField() {
  const starfield = document.getElementById('starfield');
  if (!starfield) return;

  for (let i = 0; i < 150; i++) {
    const star = document.createElement('div');
    star.className = 'star';
    star.style.left = `${Math.random() * 100}%`;
    star.style.top = `${Math.random() * 100}%`;
    star.style.width = `${1 + Math.random() * 2}px`;
    star.style.height = star.style.width;
    star.style.setProperty('--duration', `${2 + Math.random() * 4}s`);
    star.style.setProperty('--delay', `${Math.random() * 3}s`);
    star.style.setProperty('--min-opacity', `${0.1 + Math.random() * 0.3}`);
    star.style.setProperty('--max-opacity', `${0.6 + Math.random() * 0.4}`);
    starfield.appendChild(star);
  }
}

/**
 * Cleanup function
 */
export function cleanupConstellationZonesAnimations() {
  ScrollTrigger.getAll().forEach(trigger => {
    const triggerEl = trigger.trigger;
    if (triggerEl && triggerEl.classList.contains('constellation-zone')) {
      trigger.kill();
    }
  });
}
