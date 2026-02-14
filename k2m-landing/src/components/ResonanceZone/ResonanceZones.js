import { initResonanceZones } from './ResonanceZone.js';
import './ResonanceZones.css';

/**
 * Resonance Zones Container
 * Initializes all 5 emotional zones (Confusion → Confidence)
 * Echoes are defined in HTML — JS animates existing DOM elements.
 */

export function initResonanceZonesContainer() {
  initResonanceZones();

  // Expose zone elements for ProgressNav coordination
  if (typeof window !== 'undefined') {
    window.resonanceZoneElements = document.querySelectorAll('.resonance-zone[data-zone]');
  }

  console.log('✅ ResonanceZones container initialized');
}
