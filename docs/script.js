// DOM Elements
const navbar = document.querySelector('.navbar');
const navLinks = document.querySelectorAll('.nav-link');
const hamburger = document.querySelector('.hamburger');
const navMenu = document.querySelector('.nav-menu');
const contactForm = document.getElementById('contactForm');
const skillBars = document.querySelectorAll('.skill-progress');
const heroBrain = document.querySelector('.ai-brain');
const floatingIcons = document.querySelectorAll('.floating-icon');
const typingTexts = document.querySelectorAll('.typing-text');
const aiCards = document.querySelectorAll('.ai-card');
const projectCards = document.querySelectorAll('.project-card');

// Navigation Scroll Effect
window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
        navbar.style.background = 'rgba(255, 255, 255, 0.98)';
        navbar.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.1)';
    } else {
        navbar.style.background = 'rgba(255, 255, 255, 0.95)';
        navbar.style.boxShadow = 'none';
    }
});

// Smooth Scrolling for Navigation Links
navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const targetId = link.getAttribute('href');
        const targetSection = document.querySelector(targetId);

        if (targetSection) {
            const offsetTop = targetSection.offsetTop - 70;
            window.scrollTo({
                top: offsetTop,
                behavior: 'smooth'
            });
        }

        // Close mobile menu if open
        navMenu.classList.remove('active');
        hamburger.classList.remove('active');
    });
});

// Mobile Menu Toggle
hamburger.addEventListener('click', () => {
    navMenu.classList.toggle('active');
    hamburger.classList.toggle('active');
});

// Active Navigation Link on Scroll
const sections = document.querySelectorAll('section');

window.addEventListener('scroll', () => {
    let current = '';

    sections.forEach(section => {
        const sectionTop = section.offsetTop - 100;
        const sectionHeight = section.clientHeight;

        if (pageYOffset >= sectionTop) {
            current = section.getAttribute('id');
        }
    });

    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${current}`) {
            link.classList.add('active');
        }
    });
});

// Animate Skill Bars on Scroll
const animateSkillBars = () => {
    const skillsSection = document.querySelector('.skills');
    const skillsTop = skillsSection.offsetTop - window.innerHeight + 100;

    if (window.pageYOffset > skillsTop) {
        skillBars.forEach(bar => {
            const progress = bar.style.width;
            bar.style.width = '0%';
            setTimeout(() => {
                bar.style.width = progress;
            }, 200);
        });
        window.removeEventListener('scroll', animateSkillBars);
    }
};

window.addEventListener('scroll', animateSkillBars);

// Intersection Observer for Fade-in Animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('fade-in-up');
        }
    });
}, observerOptions);

// Observe all project cards and skill categories
document.querySelectorAll('.project-card, .skill-category, .contact-item, .highlight-item').forEach(el => {
    observer.observe(el);
});

// Contact Form Handling
contactForm.addEventListener('submit', (e) => {
    e.preventDefault();

    const formData = new FormData(contactForm);
    const data = Object.fromEntries(formData);

    // Simulate form submission (replace with actual submission logic)
    const submitBtn = contactForm.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;

    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
    submitBtn.disabled = true;

    // Simulate API call
    setTimeout(() => {
        submitBtn.innerHTML = '<i class="fas fa-check"></i> Sent!';
        submitBtn.style.background = '#10b981';

        // Reset form
        setTimeout(() => {
            contactForm.reset();
            submitBtn.innerHTML = originalText;
            submitBtn.style.background = '';
            submitBtn.disabled = false;
        }, 2000);
    }, 1500);
});

// Typing Animation for Hero Code
const codeLines = document.querySelectorAll('.code-line');
let currentLine = 0;
let currentChar = 0;
let isTyping = true;

const typeWriter = () => {
    if (!isTyping) return;

    const currentLineElement = codeLines[currentLine];
    const text = currentLineElement.textContent;

    if (currentChar < text.length) {
        currentLineElement.textContent = text.substring(0, currentChar + 1);
        currentChar++;
        setTimeout(typeWriter, 50);
    } else {
        currentChar = 0;
        currentLine++;
        if (currentLine < codeLines.length) {
            setTimeout(typeWriter, 500);
        } else {
            // Restart typing animation
            setTimeout(() => {
                codeLines.forEach(line => line.textContent = '');
                currentLine = 0;
                currentChar = 0;
                typeWriter();
            }, 2000);
        }
    }
};

// Start typing animation when page loads
window.addEventListener('load', () => {
    setTimeout(typeWriter, 1000);
});

// Particle Background Effect (optional)
const createParticles = () => {
    const hero = document.querySelector('.hero');
    const particleCount = 50;

    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.cssText = `
            position: absolute;
            width: 4px;
            height: 4px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 50%;
            pointer-events: none;
            left: ${Math.random() * 100}%;
            top: ${Math.random() * 100}%;
            animation: float ${3 + Math.random() * 4}s linear infinite;
        `;

        hero.appendChild(particle);

        // Remove particle after animation
        setTimeout(() => {
            particle.remove();
        }, 7000);
    }
};

// Floating animation for particles
const style = document.createElement('style');
style.textContent = `
    @keyframes float {
        0% {
            transform: translateY(0px) rotate(0deg);
            opacity: 0;
        }
        10% {
            opacity: 1;
        }
        90% {
            opacity: 1;
        }
        100% {
            transform: translateY(-100vh) rotate(360deg);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Create particles every 3 seconds
setInterval(createParticles, 3000);

// Project Cards Hover Effect Enhancement
document.querySelectorAll('.project-card').forEach(card => {
    card.addEventListener('mouseenter', () => {
        card.style.transform = 'translateY(-10px) scale(1.02)';
    });

    card.addEventListener('mouseleave', () => {
        card.style.transform = 'translateY(0) scale(1)';
    });
});

// Scroll Progress Indicator
const scrollProgress = document.createElement('div');
scrollProgress.className = 'scroll-progress';
scrollProgress.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 0%;
    height: 3px;
    background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
    z-index: 1001;
    transition: width 0.3s ease;
`;

document.body.appendChild(scrollProgress);

window.addEventListener('scroll', () => {
    const totalHeight = document.documentElement.scrollHeight - window.innerHeight;
    const progress = (window.pageYOffset / totalHeight) * 100;
    scrollProgress.style.width = `${progress}%`;
});

// Theme Toggle (optional dark mode)
const themeToggle = document.createElement('button');
themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
themeToggle.className = 'theme-toggle';
themeToggle.style.cssText = `
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background: var(--primary-color);
    color: white;
    border: none;
    cursor: pointer;
    z-index: 1000;
    box-shadow: var(--shadow);
    transition: var(--transition);
`;

themeToggle.addEventListener('mouseenter', () => {
    themeToggle.style.transform = 'scale(1.1)';
});

themeToggle.addEventListener('mouseleave', () => {
    themeToggle.style.transform = 'scale(1)';
});

// Comment out theme toggle for now as it requires additional CSS variables
// document.body.appendChild(themeToggle);

// Performance Optimization: Lazy load images
const imageObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const img = entry.target;
            // Add loading="lazy" if not already present
            if (!img.hasAttribute('loading')) {
                img.setAttribute('loading', 'lazy');
            }
            imageObserver.unobserve(img);
        }
    });
});

// Observe all images
document.querySelectorAll('img').forEach(img => {
    imageObserver.observe(img);
});

// Add loading animation for page transitions
window.addEventListener('beforeunload', () => {
    document.body.style.opacity = '0.5';
});

// Error handling for form submission
window.addEventListener('unhandledrejection', (event) => {
    console.error('Form submission error:', event.reason);
    // You could show a user-friendly error message here
});

// Accessibility: Keyboard navigation for mobile menu
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && navMenu.classList.contains('active')) {
        navMenu.classList.remove('active');
        hamburger.classList.remove('active');
    }
});

// AI Brain Interaction
if (heroBrain) {
    heroBrain.addEventListener('click', () => {
        const nodes = heroBrain.querySelectorAll('.node');
        nodes.forEach(node => {
            node.style.animation = 'none';
            setTimeout(() => {
                node.style.animation = '';
            }, 100);
        });
    });
}

// AI Card Hover Effects
aiCards.forEach((card, index) => {
    card.addEventListener('mouseenter', () => {
        card.style.transform = 'translateY(-10px) scale(1.02)';
        const icon = card.querySelector('.ai-icon');
        if (icon) {
            icon.style.transform = 'scale(1.1) rotate(5deg)';
            icon.style.boxShadow = '0 12px 35px rgba(99, 102, 241, 0.4)';
        }
    });

    card.addEventListener('mouseleave', () => {
        card.style.transform = 'translateY(0) scale(1)';
        const icon = card.querySelector('.ai-icon');
        if (icon) {
            icon.style.transform = 'scale(1) rotate(0deg)';
            icon.style.boxShadow = '0 8px 25px rgba(99, 102, 241, 0.3)';
        }
    });
});

// Typing Animation for Terminal
let typingIndex = 0;
let charIndex = 0;
const typingSpeed = 100;

function typeText() {
    if (typingIndex < typingTexts.length) {
        const text = typingTexts[typingIndex];
        const fullText = text.textContent;

        if (charIndex < fullText.length) {
            text.textContent = fullText.substring(0, charIndex + 1);
            charIndex++;
            setTimeout(typeText, typingSpeed);
        } else {
            typingIndex++;
            charIndex = 0;
            if (typingIndex < typingTexts.length) {
                setTimeout(typeText, 1000);
            }
        }
    }
}

// Start typing animation
setTimeout(typeText, 2000);

// Neural Network Animation
function createNeuralConnections() {
    const brainNodes = document.querySelectorAll('.brain-nodes .node');
    const connections = document.querySelector('.connections');

    if (brainNodes.length > 0 && connections) {
        brainNodes.forEach((node, index) => {
            node.style.animationDelay = `${index * 0.2}s`;
        });
    }
}

// Magnetic Effect for Floating Icons
document.addEventListener('mousemove', (e) => {
    floatingIcons.forEach((icon, index) => {
        const rect = icon.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;

        const deltaX = (e.clientX - centerX) * 0.02;
        const deltaY = (e.clientY - centerY) * 0.02;

        icon.style.transform = `translate(${deltaX}px, ${deltaY}px)`;
    });
});

// AI Thinking Animation
function aiThinkingAnimation() {
    const aiIcons = document.querySelectorAll('.ai-icon i');
    aiIcons.forEach((icon, index) => {
        setTimeout(() => {
            icon.style.transform = 'scale(1.2)';
            setTimeout(() => {
                icon.style.transform = 'scale(1)';
            }, 500);
        }, index * 200);
    });
}

// Project Card AI Glow Effect
projectCards.forEach((card) => {
    card.addEventListener('mouseenter', () => {
        const icon = card.querySelector('.project-main-icon');
        if (icon) {
            icon.style.filter = 'drop-shadow(0 0 20px rgba(99, 102, 241, 0.8))';
        }
    });

    card.addEventListener('mouseleave', () => {
        const icon = card.querySelector('.project-main-icon');
        if (icon) {
            icon.style.filter = 'drop-shadow(0 4px 8px rgba(0, 0, 0, 0.2))';
        }
    });
});

// AI Status Pulse
const statusDot = document.querySelector('.status-dot');
if (statusDot) {
    setInterval(() => {
        statusDot.style.transform = 'scale(1.2)';
        setTimeout(() => {
            statusDot.style.transform = 'scale(1)';
        }, 500);
    }, 3000);
}

// Scroll-triggered AI Effects
const aiObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            if (entry.target.classList.contains('ai-showcase')) {
                aiThinkingAnimation();
            }
            aiObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.3 });

const aiShowcase = document.querySelector('.ai-showcase');
if (aiShowcase) {
    aiObserver.observe(aiShowcase);
}

// Dynamic Background Particles
function createAIParticles() {
    const particleContainer = document.createElement('div');
    particleContainer.className = 'ai-particles';
    particleContainer.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: -1;
    `;

    for (let i = 0; i < 20; i++) {
        const particle = document.createElement('div');
        particle.style.cssText = `
            position: absolute;
            width: 2px;
            height: 2px;
            background: rgba(99, 102, 241, 0.3);
            border-radius: 50%;
            left: ${Math.random() * 100}%;
            top: ${Math.random() * 100}%;
            animation: aiParticleFloat ${3 + Math.random() * 4}s linear infinite;
        `;
        particleContainer.appendChild(particle);
    }

    document.body.appendChild(particleContainer);
}

const aiParticleStyle = document.createElement('style');
aiParticleStyle.textContent = `
    @keyframes aiParticleFloat {
        0% {
            transform: translateY(0px) translateX(0px);
            opacity: 0;
        }
        10% {
            opacity: 1;
        }
        90% {
            opacity: 1;
        }
        100% {
            transform: translateY(-100vh) translateX(${Math.random() * 200 - 100}px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(aiParticleStyle);

// Initialize AI Features
document.addEventListener('DOMContentLoaded', () => {
    createNeuralConnections();
    createAIParticles();

    // AI Welcome Message
    setTimeout(() => {
        console.log(`
🤖 AI Developer Portfolio Initialized
🚀 Full-Stack Developer | AI Specialist
🧠 Machine Learning | Computer Vision | NLP
📧 Contact: your.email@example.com
🔗 GitHub: https://github.com/nonshenz007/portfolio-fullstack-developer

⚡ Neural Networks: Online
🎯 AI Models: Loaded
💡 Innovation: Activated
        `);
    }, 1000);
});
