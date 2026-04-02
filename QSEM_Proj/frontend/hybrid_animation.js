class HybridKeyAnimator {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.particles = {
            qkd: [],
            mlkem: [],
            ecdh: []
        };
        this.superKey = null;
        this.animationId = null;
        this.isAnimating = false;
        this.animationPhase = 0; // 0: setup, 1: particles, 2: merging, 3: complete
        
        this.init();
    }

    init() {
        console.log('🎭 Initializing Hybrid Key Animation System...');
        this.setupScene();
        this.setupEventListeners();
    }

    setupScene() {
        const canvas = document.getElementById('hybrid-animation-canvas');
        if (!canvas) {
            console.error('❌ Animation canvas not found');
            return;
        }

        // Scene setup
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x0a0a0a);

        // Camera setup
        this.camera = new THREE.PerspectiveCamera(75, canvas.offsetWidth / canvas.offsetHeight, 0.1, 1000);
        this.camera.position.z = 15;

        // Renderer setup
        this.renderer = new THREE.WebGLRenderer({ 
            canvas: canvas, 
            antialias: true, 
            alpha: true 
        });
        this.renderer.setSize(canvas.offsetWidth, canvas.offsetHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);

        // Handle window resize
        window.addEventListener('resize', () => this.onWindowResize());
    }

    setupEventListeners() {
        // Close modal on completion
        document.addEventListener('animationComplete', () => {
            setTimeout(() => {
                this.hideModal();
            }, 2000);
        });

        // Close button
        const closeBtn = document.getElementById('close-hybrid-modal');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                this.hideModal();
            });
        }

        // Close on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const modal = document.getElementById('hybrid-key-modal');
                if (modal && !modal.classList.contains('hidden')) {
                    this.hideModal();
                }
            }
        });
    }

    onWindowResize() {
        const canvas = document.getElementById('hybrid-animation-canvas');
        if (!canvas) return;

        this.camera.aspect = canvas.offsetWidth / canvas.offsetHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(canvas.offsetWidth, canvas.offsetHeight);
    }

    // Main animation trigger
    async startAnimation(keyTypes = ['qkd', 'mlkem', 'ecdh']) {
        if (this.isAnimating) return;
        
        console.log('🚀 Starting Hybrid Key Animation...');
        this.isAnimating = true;
        this.animationPhase = 0;
        
        this.showModal();
        this.clearScene();
        
        // Animation sequence
        await this.phase1_InitializeParticles(keyTypes);
        await this.phase2_StreamParticles();
        await this.phase3_MergeToSuperKey();
        await this.phase4_CompleteSuperKey();
        
        this.isAnimating = false;
        document.dispatchEvent(new CustomEvent('animationComplete'));
    }

    showModal() {
        const modal = document.getElementById('hybrid-key-modal');
        if (modal) {
            modal.classList.remove('hidden');
            document.body.style.overflow = 'hidden';
        }
    }

    hideModal() {
        const modal = document.getElementById('hybrid-key-modal');
        if (modal) {
            modal.classList.add('hidden');
            document.body.style.overflow = '';
            this.stopAnimation();
        }
    }

    clearScene() {
        // Remove all existing particles
        Object.values(this.particles).forEach(particleArray => {
            particleArray.forEach(particle => {
                this.scene.remove(particle);
            });
        });
        
        // Reset particle arrays
        this.particles = { qkd: [], mlkem: [], ecdh: [] };
        
        // Remove super key if exists
        if (this.superKey) {
            this.scene.remove(this.superKey);
            this.superKey = null;
        }
    }

    async phase1_InitializeParticles(keyTypes) {
        this.updateStatus('Initializing quantum channels...');
        this.updateProgress(10);
        
        const particleCount = 200; // Reduced from 1000 for performance
        
        for (const keyType of keyTypes) {
            await this.createParticleSystem(keyType, particleCount);
            await this.delay(300);
        }
        
        this.updateProgress(30);
    }

    createParticleSystem(keyType, count) {
        return new Promise((resolve) => {
            const colors = {
                qkd: 0x00ff88,     // Green
                mlkem: 0x8b5cf6,   // Purple  
                ecdh: 0x3b82f6     // Blue
            };

            const positions = {
                qkd: { x: -8, y: 4 },
                mlkem: { x: -8, y: 0 },
                ecdh: { x: -8, y: -4 }
            };

            const geometry = new THREE.SphereGeometry(0.05, 8, 6);
            const material = new THREE.MeshBasicMaterial({ 
                color: colors[keyType],
                transparent: true,
                opacity: 0.8
            });

            for (let i = 0; i < count; i++) {
                const particle = new THREE.Mesh(geometry, material);
                
                // Start position (left side)
                const startPos = positions[keyType];
                particle.position.set(
                    startPos.x + (Math.random() - 0.5) * 2,
                    startPos.y + (Math.random() - 0.5) * 1,
                    (Math.random() - 0.5) * 2
                );
                
                // Animation properties
                particle.userData = {
                    type: keyType,
                    speed: 0.02 + Math.random() * 0.02,
                    targetX: 0, // Center
                    targetY: 0,
                    targetZ: 0,
                    phase: 'streaming'
                };
                
                this.scene.add(particle);
                this.particles[keyType].push(particle);
            }
            
            this.updateStatus(`Generated ${keyType.toUpperCase()} particles...`);
            resolve();
        });
    }

    async phase2_StreamParticles() {
        this.updateStatus('Streaming cryptographic keys...');
        this.animationPhase = 1;
        
        return new Promise((resolve) => {
            const startTime = Date.now();
            const duration = 2000; // 2 seconds
            
            const animate = () => {
                const elapsed = Date.now() - startTime;
                const progress = Math.min(elapsed / duration, 1);
                
                // Update progress
                this.updateProgress(30 + progress * 40);
                
                // Move particles toward center
                Object.values(this.particles).forEach(particleArray => {
                    particleArray.forEach(particle => {
                        if (particle.userData.phase === 'streaming') {
                            // Smooth movement toward center
                            particle.position.x += (particle.userData.targetX - particle.position.x) * particle.userData.speed;
                            particle.position.y += (particle.userData.targetY - particle.position.y) * particle.userData.speed;
                            particle.position.z += (particle.userData.targetZ - particle.position.z) * particle.userData.speed;
                            
                            // Add slight rotation
                            particle.rotation.x += 0.02;
                            particle.rotation.y += 0.01;
                        }
                    });
                });
                
                this.renderer.render(this.scene, this.camera);
                
                if (progress < 1) {
                    this.animationId = requestAnimationFrame(animate);
                } else {
                    resolve();
                }
            };
            
            animate();
        });
    }

    async phase3_MergeToSuperKey() {
        this.updateStatus('Merging quantum keys...');
        this.animationPhase = 2;
        this.updateProgress(70);
        
        return new Promise((resolve) => {
            const startTime = Date.now();
            const duration = 1500; // 1.5 seconds
            
            const animate = () => {
                const elapsed = Date.now() - startTime;
                const progress = Math.min(elapsed / duration, 1);
                
                // Accelerate particles toward center and fade them
                Object.values(this.particles).forEach(particleArray => {
                    particleArray.forEach(particle => {
                        // Faster convergence
                        particle.position.lerp(new THREE.Vector3(0, 0, 0), 0.1);
                        
                        // Scale down particles as they merge
                        const scale = 1 - progress * 0.8;
                        particle.scale.setScalar(scale);
                        
                        // Fade opacity
                        particle.material.opacity = 0.8 * (1 - progress);
                    });
                });
                
                this.renderer.render(this.scene, this.camera);
                
                if (progress < 1) {
                    this.animationId = requestAnimationFrame(animate);
                } else {
                    resolve();
                }
            };
            
            animate();
        });
    }

    async phase4_CompleteSuperKey() {
        this.updateStatus('Quantum super-key generated!');
        this.animationPhase = 3;
        
        // Remove all particles
        this.clearScene();
        
        // Create super-key
        const superKeyGeometry = new THREE.SphereGeometry(1, 32, 24);
        const superKeyMaterial = new THREE.MeshBasicMaterial({
            color: 0x8b5cf6, // Violet
            transparent: true,
            opacity: 0
        });
        
        this.superKey = new THREE.Mesh(superKeyGeometry, superKeyMaterial);
        this.scene.add(this.superKey);
        
        // Animate super-key appearance
        return new Promise((resolve) => {
            const startTime = Date.now();
            const duration = 1000;
            
            const animate = () => {
                const elapsed = Date.now() - startTime;
                const progress = Math.min(elapsed / duration, 1);
                
                // Fade in super-key
                this.superKey.material.opacity = progress * 0.9;
                this.superKey.scale.setScalar(progress);
                
                // Pulse effect
                const pulse = 1 + Math.sin(elapsed * 0.005) * 0.1;
                this.superKey.scale.setScalar(progress * pulse);
                
                // Rotation
                this.superKey.rotation.y += 0.02;
                this.superKey.rotation.x += 0.01;
                
                // Progress update
                this.updateProgress(90 + progress * 10);
                
                this.renderer.render(this.scene, this.camera);
                
                if (progress < 1) {
                    this.animationId = requestAnimationFrame(animate);
                } else {
                    this.updateStatus('Hybrid encryption ready!');
                    this.updateSuperKeyStatus('256-bit Super-Key');
                    resolve();
                }
            };
            
            animate();
        });
    }

    updateStatus(message) {
        const statusElement = document.getElementById('animation-status');
        if (statusElement) {
            statusElement.textContent = message;
        }
        console.log(`🎭 ${message}`);
    }

    updateProgress(percentage) {
        const progressBar = document.getElementById('progress-bar');
        const progressText = document.getElementById('progress-percentage');
        
        if (progressBar) {
            progressBar.style.width = `${percentage}%`;
        }
        
        if (progressText) {
            progressText.textContent = `${Math.round(percentage)}%`;
        }
    }

    updateSuperKeyStatus(status) {
        const statusElement = document.querySelector('#super-key-status span');
        if (statusElement) {
            statusElement.textContent = status;
        }
    }

    stopAnimation() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
        this.isAnimating = false;
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Initialize the animator when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Wait a bit for Three.js to load
    setTimeout(() => {
        if (typeof THREE !== 'undefined') {
            window.hybridAnimator = new HybridKeyAnimator();
            console.log('✅ Hybrid Key Animator initialized');
        } else {
            console.error('❌ Three.js not loaded');
        }
    }, 100);
});

// Export for global access
window.HybridKeyAnimator = HybridKeyAnimator;
window.hybridAnimator = null;

// Helper function for external triggering
window.showHybridKeyAnimation = (keyTypes = ['qkd', 'mlkem', 'ecdh']) => {
    if (window.hybridAnimator) {
        window.hybridAnimator.startAnimation(keyTypes);
    } else {
        console.error('❌ Hybrid animator not initialized');
        console.log('💡 Attempting to initialize now...');
        
        // Try to initialize immediately
        if (typeof THREE !== 'undefined') {
            window.hybridAnimator = new HybridKeyAnimator();
            console.log('✅ Hybrid Key Animator initialized on-demand');
            // Try again
            setTimeout(() => {
                if (window.hybridAnimator) {
                    window.hybridAnimator.startAnimation(keyTypes);
                }
            }, 100);
        }
    }
};
