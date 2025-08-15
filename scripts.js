// Portfolio Scripts
let currentSlideIndex = 1;
const totalSlides = 3;

function showSlide(n) {
    const slides = document.querySelectorAll('.blog-slide');
    const dots = document.querySelectorAll('.dot');
    
    if (n > totalSlides) { currentSlideIndex = 1; }
    if (n < 1) { currentSlideIndex = totalSlides; }
    
    slides.forEach(slide => slide.classList.remove('active'));
    dots.forEach(dot => dot.classList.remove('active'));
    
    slides[currentSlideIndex - 1].classList.add('active');
    dots[currentSlideIndex - 1].classList.add('active');
}

function changeSlide(n) {
    currentSlideIndex += n;
    showSlide(currentSlideIndex);
}

function currentSlide(n) {
    currentSlideIndex = n;
    showSlide(currentSlideIndex);
}

// Auto-slide functionality
function autoSlide() {
    currentSlideIndex++;
    if (currentSlideIndex > totalSlides) {
        currentSlideIndex = 1;
    }
    showSlide(currentSlideIndex);
}

// Start auto-slide when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Initialize first slide
    showSlide(currentSlideIndex);
    
    // Auto-slide every 5 seconds
    setInterval(autoSlide, 5000);
    
    // Pause auto-slide when user hovers over the slider
    const slider = document.querySelector('.blog-slider-container');
    let autoSlideInterval;
    
    if (slider) {
        slider.addEventListener('mouseenter', function() {
            clearInterval(autoSlideInterval);
        });
        
        slider.addEventListener('mouseleave', function() {
            autoSlideInterval = setInterval(autoSlide, 5000);
        });
    }

    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add loading animation for sections
    const sections = document.querySelectorAll('section');
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    sections.forEach(section => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        section.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(section);
    });
});

// Keyboard navigation for slider
document.addEventListener('keydown', function(e) {
    if (e.key === 'ArrowLeft') {
        changeSlide(-1);
    } else if (e.key === 'ArrowRight') {
        changeSlide(1);
    }
});
