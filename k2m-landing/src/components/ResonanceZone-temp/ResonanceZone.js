import { gsap, ScrollTrigger } from '../../utils/gsap-config.js';
import { EchoBubble } from '../EchoBubble/EchoBubble.js';
import './ResonanceZone.css';

/**
 * Resonance Zone Component
 * Single emotional zone container with echo bubbles and voice stage card
 *
 * Features:
 * - ScrollTrigger zone activation (start: top 55%, end: bottom 45%)
 * - Staggered echo bubble reveals
 * - Voice stage card content transitions
 * - Spotlight and vignette effects
 * - Mobile-responsive layout
 */

export class ResonanceZone {
  constructor(element, data) {
    this.element = element;
    this.data = data;
    this.echoes = [];
    this.isActive = false;

    // Find child elements
    this.spotlightLayer = element.querySelector('.spotlight-layer');
    this.vignette = element.querySelector('.vignette');
    this.echoesContainer = element.querySelector('.echoes-container');
    this.voiceStage = element.querySelector('.voice-stage');
  }

  /**
   * Initialize the zone
   */
  init() {
    // Create and initialize echo bubbles
    this.createEchoBubbles();

    // Setup ScrollTrigger for zone activation
    ScrollTrigger.create({
      trigger: this.element,
      start: 'top 55%',
      end: 'bottom 45%',
      onEnter: () => this.activate(),
      onEnterBack: () => this.activate(),
      onLeave: () => this.deactivate(),
      onLeaveBack: () => this.deactivate()
    });

    console.log(`✅ ResonanceZone ${this.data.zoneNumber} initialized (${this.data.echoes.length} echoes)`);
  }

  /**
   * Create echo bubble elements
   */
  createEchoBubbles() {
    this.data.echoes.forEach(echoData => {
      const echoElement = document.createElement('div');
      echoElement.classList.add('echo');
      echoElement.textContent = echoData.text;

      // Position on desktop
      if (echoData.top) echoElement.style.top = echoData.top;
      if (echoData.left) echoElement.style.left = echoData.left;
      if (echoData.right) echoElement.style.right = echoData.right;
      if (echoData.bottom) echoElement.style.bottom = echoData.bottom;

      // Set delay for staggered reveal
      echoElement.dataset.delay = echoData.delay || 0;

      this.echoesContainer.appendChild(echoElement);

      // Create EchoBubble component
      const bubble = new EchoBubble(echoElement);
      bubble.init();
      this.echoes.push(bubble);
    });
  }

  /**
   * Activate zone (on scroll enter)
   */
  activate() {
    // Add in-focus class for CSS transitions
    this.element.classList.add('in-focus');
    this.isActive = true;

    // Reveal all echo bubbles with staggered delays
    this.echoes.forEach(echo => {
      echo.reveal();
    });
  }

  /**
   * Deactivate zone (on scroll leave)
   */
  deactivate() {
    // Remove in-focus class
    this.element.classList.remove('in-focus');
    this.isActive = false;

    // Hide all echo bubbles
    this.echoes.forEach(echo => {
      echo.hide();
    });
  }

  /**
   * Cleanup method for memory management
   */
  cleanup() {
    // Kill ScrollTrigger
    ScrollTrigger.getAll().forEach(st => {
      if (st.trigger === this.element) {
        st.kill();
      }
    });

    // Cleanup echo bubbles
    this.echoes.forEach(echo => echo.cleanup());

    // Remove in-focus class
    this.element.classList.remove('in-focus');

    console.log(`✅ ResonanceZone ${this.data.zoneNumber} cleaned up`);
  }
}

/**
 * Initialize all resonance zones on the page
 */
export function initResonanceZones(zoneDataArray) {
  const zoneElements = document.querySelectorAll('.resonance-zone');
  const zones = [];

  zoneElements.forEach((element, index) => {
    const data = zoneDataArray[index];
    if (!data) {
      console.warn(`No data provided for zone ${index}`);
      return;
    }

    const zone = new ResonanceZone(element, data);
    zone.init();
    zones.push(zone);
  });

  console.log(`✅ Initialized ${zones.length} ResonanceZone components`);

  // Expose for testing/cleanup
  if (typeof window !== 'undefined') {
    window.resonanceZones = zones;
  }

  return zones;
}
