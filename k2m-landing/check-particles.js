// Debug script to check particle initialization
const fs = require('fs');
const path = require('path');

console.log('=== Checking Particle Container ===');

// Check if TerritoryMap.html contains particle-container
const htmlPath = path.join(__dirname, 'src/components/TerritoryMap/TerritoryMap.html');
const html = fs.readFileSync(htmlPath, 'utf8');

if (html.includes('particle-container')) {
  console.log('✅ particle-container found in TerritoryMap.html');
} else {
  console.log('❌ particle-container NOT found in TerritoryMap.html');
}

// Check if MapParticles is imported in main.js
const mainPath = path.join(__dirname, 'src/main.js');
const main = fs.readFileSync(mainPath, 'utf8');

if (main.includes('MapParticleSystem')) {
  console.log('✅ MapParticleSystem imported in main.js');
} else {
  console.log('❌ MapParticleSystem NOT imported in main.js');
}

if (main.includes('new MapParticleSystem')) {
  console.log('✅ MapParticleSystem instantiation found');
} else {
  console.log('❌ MapParticleSystem instantiation NOT found');
}

if (main.includes('particleSystem.init()')) {
  console.log('✅ particleSystem.init() call found');
} else {
  console.log('❌ particleSystem.init() call NOT found');
}

console.log('\n=== Checking GSAP Import ===');
if (main.includes("gsap-config.js")) {
  console.log('✅ gsap-config.js imported');
} else {
  console.log('❌ gsap-config.js NOT imported');
}

// Check MapParticles.js import
const particlesPath = path.join(__dirname, 'src/components/TerritoryMap/MapParticles.js');
const particles = fs.readFileSync(particlesPath, 'utf8');

if (particles.includes('gsap-config.js')) {
  console.log('✅ MapParticles.js imports from gsap-config.js');
} else {
  console.log('❌ MapParticles.js does NOT import from gsap-config.js');
}
