// Performance Optimization Utilities
// GPU acceleration helpers and performance monitoring

/**
 * Enable GPU acceleration for an element
 * Adds will-change property to promote element to GPU layer
 * @param {HTMLElement} element - The element to accelerate
 */
export function enableGPU(element) {
  if (element && element.style) {
    element.style.willChange = 'transform, opacity';
  }
}

/**
 * Disable GPU acceleration for an element
 * Resets will-change to auto to free GPU resources
 * @param {HTMLElement} element - The element to reset
 */
export function disableGPU(element) {
  if (element && element.style) {
    element.style.willChange = 'auto';
  }
}

/**
 * Detect if current device is mobile
 * @returns {boolean} True if screen width <= 768px
 */
export function isMobile() {
  return window.innerWidth <= 768;
}

/**
 * Monitor performance with FPS counter
 * Logs FPS every second and warns if drops below 30
 * @returns {Function} Cleanup function to stop monitoring
 */
export function monitorPerformance() {
  let frameCount = 0;
  let lastTime = performance.now();
  let fps = 0;
  let rafId = null;
  let isMonitoring = true;

  function measureFrame(currentTime) {
    if (!isMonitoring) return;

    frameCount++;

    // Update FPS every second
    if (currentTime >= lastTime + 1000) {
      fps = Math.round((frameCount * 1000) / (currentTime - lastTime));

      // Log FPS
      console.log(`Performance: ${fps} FPS`);

      // Warning if FPS drops below 30
      if (fps < 30) {
        console.warn(`⚠️ Low FPS detected: ${fps} FPS (Target: 60fps desktop, 45fps mobile)`);
      }

      // Reset counters
      frameCount = 0;
      lastTime = currentTime;
    }

    rafId = requestAnimationFrame(measureFrame);
  }

  // Start monitoring
  rafId = requestAnimationFrame(measureFrame);

  // Return cleanup function that actually stops the loop
  return function stopMonitoring() {
    isMonitoring = false;
    if (rafId) {
      cancelAnimationFrame(rafId);
      rafId = null;
    }
    console.log('Performance monitoring stopped');
  };
}
