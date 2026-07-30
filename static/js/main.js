document.addEventListener('DOMContentLoaded', () => {
    
    // --- 1. Dark/Light Theme Switcher ---
    const themeToggleBtn = document.getElementById('theme-toggle');
    const themeIcon = themeToggleBtn.querySelector('i');
    
    // Check saved theme or system preference
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedTheme === 'light' || (!savedTheme && !systemPrefersDark)) {
        document.documentElement.setAttribute('data-theme', 'light');
        themeIcon.className = 'fas fa-moon';
    } else {
        document.documentElement.setAttribute('data-theme', 'dark');
        themeIcon.className = 'fas fa-sun';
    }
    
    themeToggleBtn.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        if (currentTheme === 'light') {
            document.documentElement.setAttribute('data-theme', 'dark');
            themeIcon.className = 'fas fa-sun';
            localStorage.setItem('theme', 'dark');
        } else {
            document.documentElement.setAttribute('data-theme', 'light');
            themeIcon.className = 'fas fa-moon';
            localStorage.setItem('theme', 'light');
        }
    });

    // --- 2. Typewriter Effect ---
    const typewriterEl = document.querySelector('.typewriter-text');
    if (typewriterEl) {
        const words = [
            "Artificial Intelligence Engineer",
            "Machine Learning Engineer",
            "Data Science Engineer",
            "Python & SQL Developer"
        ];
        let wordIndex = 0;
        let charIndex = 0;
        let isDeleting = false;
        let typingDelay = 100;
        let deletingDelay = 50;
        let wordTransitionDelay = 2000;
        
        function type() {
            const currentWord = words[wordIndex];
            if (isDeleting) {
                typewriterEl.textContent = currentWord.substring(0, charIndex - 1);
                charIndex--;
                typingDelay = deletingDelay;
            } else {
                typewriterEl.textContent = currentWord.substring(0, charIndex + 1);
                charIndex++;
                typingDelay = 100;
            }
            
            if (!isDeleting && charIndex === currentWord.length) {
                isDeleting = true;
                typingDelay = wordTransitionDelay;
            } else if (isDeleting && charIndex === 0) {
                isDeleting = false;
                wordIndex = (wordIndex + 1) % words.length;
                typingDelay = 500;
            }
            
            setTimeout(type, typingDelay);
        }
        setTimeout(type, 1000);
    }

    // --- 3. Mobile Navigation Menu Toggle ---
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const navLinks = document.getElementById('nav-links');
    
    if (mobileMenuBtn && navLinks) {
        mobileMenuBtn.addEventListener('click', () => {
            navLinks.classList.toggle('active');
            const icon = mobileMenuBtn.querySelector('i');
            if (navLinks.classList.contains('active')) {
                icon.className = 'fas fa-times';
            } else {
                icon.className = 'fas fa-bars';
            }
        });
        
        // Close menu on link click
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                navLinks.classList.remove('active');
                mobileMenuBtn.querySelector('i').className = 'fas fa-bars';
            });
        });
    }

    // --- 4. Active Navigation Highlighting on Scroll ---
    const sections = document.querySelectorAll('section');
    const navLinksList = document.querySelectorAll('.nav-links a');
    
    function highlightNav() {
        let scrollY = window.pageYOffset;
        
        sections.forEach(section => {
            const sectionHeight = section.offsetHeight;
            const sectionTop = section.offsetTop - 100;
            const sectionId = section.getAttribute('id');
            
            if (scrollY > sectionTop && scrollY <= sectionTop + sectionHeight) {
                navLinksList.forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === `#${sectionId}`) {
                        link.classList.add('active');
                    }
                });
            }
        });
    }
    window.addEventListener('scroll', highlightNav);

    // --- 5. Custom Canvas Particle Background ---
    const canvas = document.getElementById('particle-canvas');
    if (canvas) {
        const ctx = canvas.getContext('2d');
        let particles = [];
        let numParticles = 70;
        
        // Match dimensions to client window
        function resizeCanvas() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            if (canvas.width < 768) {
                numParticles = 30;
            } else {
                numParticles = 70;
            }
        }
        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();
        
        class Particle {
            constructor() {
                this.x = Math.random() * canvas.width;
                this.y = Math.random() * canvas.height;
                this.vx = (Math.random() - 0.5) * 0.4;
                this.vy = (Math.random() - 0.5) * 0.4;
                this.radius = Math.random() * 2 + 1;
            }
            
            update() {
                this.x += this.vx;
                this.y += this.vy;
                
                // Boundaries handling
                if (this.x < 0 || this.x > canvas.width) this.vx = -this.vx;
                if (this.y < 0 || this.y > canvas.height) this.vy = -this.vy;
            }
            
            draw() {
                const theme = document.documentElement.getAttribute('data-theme');
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.fillStyle = theme === 'light' ? 'rgba(99, 67, 230, 0.2)' : 'rgba(123, 97, 255, 0.4)';
                ctx.fill();
            }
        }
        
        function initParticles() {
            particles = [];
            for (let i = 0; i < numParticles; i++) {
                particles.push(new Particle());
            }
        }
        initParticles();
        
        function drawLines() {
            const theme = document.documentElement.getAttribute('data-theme');
            const lineColor = theme === 'light' ? 'rgba(99, 67, 230, ' : 'rgba(123, 97, 255, ';
            
            for (let i = 0; i < particles.length; i++) {
                for (let j = i + 1; j < particles.length; j++) {
                    const dist = Math.hypot(particles[i].x - particles[j].x, particles[i].y - particles[j].y);
                    if (dist < 120) {
                        const alpha = (1 - dist / 120) * 0.15;
                        ctx.beginPath();
                        ctx.moveTo(particles[i].x, particles[i].y);
                        ctx.lineTo(particles[j].x, particles[j].y);
                        ctx.strokeStyle = lineColor + alpha + ')';
                        ctx.lineWidth = 0.5;
                        ctx.stroke();
                    }
                }
            }
        }
        
        function animate() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            particles.forEach(p => {
                p.update();
                p.draw();
            });
            drawLines();
            requestAnimationFrame(animate);
        }
        animate();
    }

    // --- 6. Stats Counter Up Animation ---
    const statsSection = document.getElementById('achievements');
    const statValues = document.querySelectorAll('.stat-card .value');
    
    if (statsSection && statValues.length > 0) {
        let hasAnimated = false;
        
        const countUp = (element) => {
            const target = parseInt(element.getAttribute('data-count'), 10);
            let count = 0;
            const duration = 2000; // 2 seconds
            const interval = 20;
            const step = target / (duration / interval);
            
            const timer = setInterval(() => {
                count += step;
                if (count >= target) {
                    element.textContent = target + (element.getAttribute('data-suffix') || '');
                    clearInterval(timer);
                } else {
                    element.textContent = Math.floor(count) + (element.getAttribute('data-suffix') || '');
                }
            }, interval);
        };
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !hasAnimated) {
                    statValues.forEach(val => countUp(val));
                    hasAnimated = true;
                }
            });
        }, { threshold: 0.3 });
        
        observer.observe(statsSection);
    }

    // --- 7. Skills Progress Bar Reveal Animation ---
    const skillsSection = document.getElementById('skills');
    const progressFills = document.querySelectorAll('.skill-progress-fill');
    
    if (skillsSection && progressFills.length > 0) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    progressFills.forEach(fill => {
                        const percent = fill.getAttribute('data-percent');
                        fill.style.width = percent + '%';
                    });
                }
            });
        }, { threshold: 0.2 });
        
        observer.observe(skillsSection);
    }

    // --- 8. Projects Search and Category Filtering ---
    const filterButtons = document.querySelectorAll('.filter-btn');
    const projectCards = document.querySelectorAll('.project-card');
    const searchInput = document.getElementById('project-search');
    
    function filterProjects() {
        const activeFilter = document.querySelector('.filter-btn.active').getAttribute('data-filter').toLowerCase();
        const searchText = searchInput ? searchInput.value.toLowerCase() : '';
        
        projectCards.forEach(card => {
            const category = card.getAttribute('data-category').toLowerCase();
            const name = card.querySelector('h3').textContent.toLowerCase();
            const desc = card.querySelector('p').textContent.toLowerCase();
            const tags = Array.from(card.querySelectorAll('.tag')).map(t => t.textContent.toLowerCase());
            
            const matchesCategory = (activeFilter === 'all' || category === activeFilter);
            const matchesSearch = name.includes(searchText) || desc.includes(searchText) || tags.some(t => t.includes(searchText));
            
            if (matchesCategory && matchesSearch) {
                card.style.display = 'flex';
            } else {
                card.style.display = 'none';
            }
        });
    }
    
    filterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            filterButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            filterProjects();
        });
    });
    
    if (searchInput) {
        searchInput.addEventListener('input', filterProjects);
    }

    // --- 9. Floating Back to Top Button ---
    const backToTopBtn = document.getElementById('back-to-top');
    if (backToTopBtn) {
        window.addEventListener('scroll', () => {
            if (window.pageYOffset > 500) {
                backToTopBtn.classList.add('visible');
            } else {
                backToTopBtn.classList.remove('visible');
            }
        });
        
        backToTopBtn.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // --- 10. AJAX Contact Form Submission ---
    const contactForm = document.getElementById('contact-form');
    const statusMsg = document.getElementById('form-status');
    
    if (contactForm && statusMsg) {
        contactForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(contactForm);
            statusMsg.style.display = 'block';
            statusMsg.className = 'form-status-msg';
            statusMsg.textContent = 'Sending message...';
            
            try {
                const response = await fetch('/contact', {
                    method: 'POST',
                    body: formData
                });
                const result = await response.json();
                
                if (response.ok && result.success) {
                    statusMsg.classList.add('status-success');
                    statusMsg.textContent = result.message;
                    contactForm.reset();
                } else {
                    statusMsg.classList.add('status-error');
                    statusMsg.textContent = result.message || 'An error occurred. Please try again.';
                }
            } catch (err) {
                statusMsg.classList.add('status-error');
                statusMsg.textContent = 'Network error. Failed to reach the server.';
            }
            
            // Hide notification after 5 seconds
            setTimeout(() => {
                statusMsg.style.display = 'none';
            }, 5000);
        });
    }
});
