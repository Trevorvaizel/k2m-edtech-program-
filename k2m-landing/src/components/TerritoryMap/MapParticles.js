import { gsap, ScrollTrigger } from '../../utils/gsap-config.js';

// ScrollTrigger is already registered in gsap-config.js

/**
 * MapParticleSystem - Chaos → Order particle animation for Territory Map
 *
 * Implements Story 2.2: Zone 0-1 (Wilderness) particle drift animation
 * Focus: Mystery → Curiosity emotional arc
 *
 * Disney Principles Applied:
 * 1. Anticipation: 0.3s pre-reveal scale pulse
 * 2. Staging: Sequential reveals (from: "start"), not random
 * 3. Timing: Varied durations (0.6s subtle, 0.4s bold)
 * 4. Follow-Through: Overshoot on bold particles (back.out(1.7))
 * 5. Overlapping Action: Text overlaps particle animation by 1.0s
 */
export class MapParticleSystem {
  constructor(containerSelector = '.particle-container') {
    this.container = document.querySelector(containerSelector);
    this.particles = [];
    this.scrollTrigger = null;
    this.timeline = null;
    this.particleCount = 0;
    this.isMobile = window.innerWidth < 768;
    this.isLowEnd = false;
    this.useSpiralMotion = true;
    this.startTime = performance.now();
  }

  /**
   * Initialize particle system
   * AC: Particle system initialization
   */
  init() {
    if (!this.container) {
      console.error('Particle container not found');
      return;
    }

    console.log('🎨 Initializing MapParticleSystem...');

    // Detect hardware capability
    const hardwareConcurrency = navigator.hardwareConcurrency || 2;
    this.isLowEnd = hardwareConcurrency < 4 || this.isMobile;

    // Set particle count based on device capability
    this.particleCount = this.isMobile ? 105 : 300; // 15 particles per zone × 7 zones

    // Reduce particle count by 50% on low-end devices
    if (this.isLowEnd) {
      this.particleCount = Math.floor(this.particleCount * 0.5);
      this.useSpiralMotion = false;
    }

    console.log(`📊 Creating ${this.particleCount} particles (mobile: ${this.isMobile}, low-end: ${this.isLowEnd})`);

    // Create particles
    this.createParticles();

    console.log(`✅ Created ${this.particles.length} particles`);

    // Setup FPS monitoring
    if (!this.isLowEnd) {
      this.startFPSMonitoring();
    }

    // Check for prefers-reduced-motion
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (prefersReducedMotion) {
      // Instant appearance, no animation
      this.instantAppear();
      console.log('♿ Accessibility mode: instant appearance');
    } else {
      // Full animation sequence
      this.animateFormation();
      console.log('🎬 Animation sequence initialized');
    }

    // Expose cleanup method globally for testing
    window.mapParticleSystem = this;
    console.log('✅ MapParticleSystem initialization complete');
  }

  /**
   * Create particle DOM elements
   * AC: Particle system initialization - Create particle DOM elements
   */
  createParticles() {
    // Zone definitions for target position calculation
    const zones = [
      { id: 0, centerX: -200, centerY: -100, radius: 150 }, // Zone 0
      { id: 1, centerX: -50, centerY: -150, radius: 120 },  // Zone 1
      { id: 2, centerX: 100, centerY: -100, radius: 130 },  // Zone 2
      { id: 3, centerX: 150, centerY: 50, radius: 140 },    // Zone 3
      { id: 4, centerX: 0, centerY: 100, radius: 160 },     // Zone 4
      { id: 5, centerX: -150, centerY: 50, radius: 110 },   // Zone 5 (Future)
      { id: 6, centerX: -250, centerY: 0, radius: 100 }     // Zone 6 (Future)
    ];

    // Apply 80/20 Emotional Punctuation Rule
    const boldCount = Math.floor(this.particleCount * 0.2); // 20% bold
    const subtleCount = this.particleCount - boldCount;      // 80% subtle

    for (let i = 0; i < this.particleCount; i++) {
      const particle = document.createElement('div');

      // Assign particle type (subtle or bold)
      const isBold = i < boldCount;
      particle.classList.add('map-particle');
      particle.classList.add(isBold ? 'bold' : 'subtle');

      // Set initial state
      particle.style.opacity = '0';
      particle.style.scale = '0';

      // Calculate target position based on zone distribution
      const zoneIndex = Math.floor(i / Math.floor(this.particleCount / 7)) % 7;
      const zone = zones[zoneIndex];

      // Random position within zone radius
      const angle = Math.random() * Math.PI * 2;
      const distance = Math.random() * zone.radius;

      const targetX = zone.centerX + Math.cos(angle) * distance;
      const targetY = zone.centerY + Math.sin(angle) * distance;

      // Initial chaos position
      const initialX = Math.random() * 2000 - 1000;
      const initialY = Math.random() * 2000 - 1000;

      // Store data on particle element for testing
      particle.targetX = targetX;
      particle.targetY = targetY;
      particle.initialX = initialX;
      particle.initialY = initialY;
      particle.zoneIndex = zoneIndex;
      particle.isBold = isBold;

      // Set initial position (chaos)
      particle.style.transform = `translate(${initialX}px, ${initialY}px)`;

      // Add to DOM
      this.container.appendChild(particle);
      this.particles.push(particle);
    }
  }

  /**
   * Instant appearance for reduced motion preference
   * AC: Accessibility support
   */
  instantAppear() {
    this.particles.forEach((particle) => {
      gsap.set(particle, {
        opacity: 1,
        scale: 1,
        x: particle.targetX,
        y: particle.targetY,
        willChange: 'auto'
      });
    });
  }

  /**
   * Animate particles from chaos to order
   * AC: Chaos → Order animation (Zone 0-1 Wilderness Focus)
   */
  animateFormation() {
    // Create ScrollTrigger configuration
    this.timeline = gsap.timeline({
      scrollTrigger: {
        trigger: '.territory-map',
        start: 'top center',
        end: 'center center',
        scrub: 0.3, // FAST scrub for mystery → curiosity (Zone 0-1)
        anticipatePin: 1
      }
    });

    // Phase 1: Pre-Reveal Anticipation (Disney Principle 1)
    this.timeline.to('.map-particle', {
      scale: 0.02,
      duration: 0.3,
      ease: 'sine.inOut'
    });

    // Separate subtle and bold particles
    const boldParticles = this.particles.filter(p => p.isBold);
    const subtleParticles = this.particles.filter(p => !p.isBold);

    // Phase 2: Sequential Coalescence (Disney Principle 4: STAGING)

    // Subtle particles: Gentle coalescence
    this.timeline.to(subtleParticles, {
      opacity: 1,
      scale: 1,
      x: (i, target) => target.targetX,
      y: (i, target) => target.targetY,
      duration: 0.6,
      stagger: {
        amount: 1.0,
        from: 'start' // SEQUENTIAL, not random (Disney's Staging)
      },
      ease: 'power2.inOut' // Gentle motion
    });

    // Bold particles: Dramatic arrival (emotional punctuation)
    this.timeline.fromTo(boldParticles, {
      opacity: 0,
      scale: 0,
      x: (i, target) => target.initialX,
      y: (i, target) => target.initialY
    }, {
      opacity: 1,
      scale: 1,
      x: (i, target) => target.targetX,
      y: (i, target) => target.targetY,
      duration: 0.4, // Faster than subtle
      stagger: {
        amount: 0.3,
        from: 'center' // Explode from center
      },
      ease: 'back.out(1.7)', // Overshoot for drama
    }, '-=0.5'); // Overlap by 0.5s (The Stitch Pattern)

    // Phase 3: Text Crystallization Effect
    this.animateTextCrystallization();

    // Store ScrollTrigger reference for cleanup
    this.scrollTrigger = this.timeline.scrollTrigger;
  }

  /**
   * Animate text crystallization (heavy blur → sharp)
   * AC: Text crystallization
   */
  animateTextCrystallization() {
    // Find all zone texts
    const zoneTexts = document.querySelectorAll('.zone-text');

    if (zoneTexts.length === 0) {
      console.warn('No zone text elements found for crystallization effect');
      return;
    }

    // Zone 0-1 text: Heavy blur → sharp
    this.timeline.fromTo(zoneTexts, {
      filter: 'blur(12px)',
      opacity: 0.3
    }, {
      filter: 'blur(0px)',
      opacity: 1,
      duration: 1.5,
      ease: 'power2.inOut',
      stagger: 0.2
    }, '-=1.0'); // Overlap with particle animation
  }

  /**
   * Start FPS monitoring for performance safeguards
   * AC: Performance safeguards
   */
  startFPSMonitoring() {
    let fps = 60;
    let frameCount = 0;
    let lastTime = performance.now();

    const measureFPS = () => {
      frameCount++;
      const currentTime = performance.now();

      if (currentTime >= lastTime + 1000) {
        fps = frameCount;
        frameCount = 0;
        lastTime = currentTime;

        // If FPS < 30 for 2+ seconds, reduce complexity
        if (fps < 30 && performance.now() - this.startTime > 2000) {
          this.simplifyAnimation();
        }
      }

      requestAnimationFrame(measureFPS);
    };

    requestAnimationFrame(measureFPS);
  }

  /**
   * Simplify animation if performance is poor
   * AC: Performance safeguards
   */
  simplifyAnimation() {
    // Kill spiral motion
    gsap.killTweensOf('.map-particle');

    // Simple fade-in fallback
    gsap.to('.map-particle', {
      opacity: 1,
      duration: 0.3,
      ease: 'power1.out'
    });
  }

  /**
   * Cleanup method for memory management
   * AC: Memory management
   */
  cleanup() {
    // Kill ScrollTrigger
    if (this.scrollTrigger) {
      this.scrollTrigger.kill();
      this.scrollTrigger = null;
    }

    // Kill timeline
    if (this.timeline) {
      this.timeline.kill();
      this.timeline = null;
    }

    // Clear will-change to release GPU resources
    gsap.set('.map-particle', {
      willChange: 'auto'
    });

    // Clear transform values
    gsap.set('.map-particle', {
      clearProps: 'transform, opacity'
    });

    // Remove particles from DOM
    this.particles.forEach(p => p.remove());
    this.particles = [];
  }
}

