// Lenis Smooth Scroll Configuration
// DISABLED - Native scroll works better with ScrollTrigger

import Lenis from '@studio-freight/lenis';
import { gsap, ScrollTrigger } from './gsap-config.js';

const lenisConfig = {
  duration: 1.2,
  smooth: false,  // DISABLED - native scroll works better
  direction: "vertical",
  smoothWheel: false,
  smoothTouch: false,
  touchMultiplier: 2
};

const lenis = new Lenis(lenisConfig);

gsap.ticker.add((time) => {
  lenis.raf(time * 1000);
});

gsap.ticker.lagSmoothing(0);

lenis.on('scroll', ScrollTrigger.update);

export { lenis };
