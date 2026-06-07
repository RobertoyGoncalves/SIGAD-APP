function showInViewportAnimations(animEls) {
  animEls.forEach((el) => {
    const rect = el.getBoundingClientRect();
    if (rect.top < window.innerHeight * 0.92) {
      el.classList.add('visible');
    }
  });
}

document.addEventListener('DOMContentLoaded', () => {
  const navbar = document.getElementById('landing-navbar');
  if (navbar) {
    const updateNavbar = () => {
      const scrolled = window.scrollY > 20;
      navbar.classList.toggle('scrolled', scrolled);
      navbar.classList.toggle('navbar-dark', !scrolled);
      navbar.classList.toggle('navbar-light', scrolled);
    };
    updateNavbar();
    window.addEventListener('scroll', updateNavbar, { passive: true });
  }

  const animEls = document.querySelectorAll('.fade-up, .fade-left, .fade-right');
  if (animEls.length && 'IntersectionObserver' in window) {
    document.documentElement.classList.add('js-anim');
    showInViewportAnimations(animEls);

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12 }
    );

    animEls.forEach((el) => {
      if (!el.classList.contains('visible')) {
        observer.observe(el);
      }
    });
  } else if (animEls.length) {
    animEls.forEach((el) => el.classList.add('visible'));
  }

  const container = document.getElementById('particles');
  if (container) {
    for (let i = 0; i < 18; i++) {
      const p = document.createElement('div');
      p.className = 'particle';
      const tx = (Math.random() - 0.5) * 600;
      const ty = (Math.random() - 0.5) * 600;
      p.style.left = `${Math.random() * 100}%`;
      p.style.top = `${Math.random() * 100}%`;
      p.style.setProperty('--tx', `${tx}px`);
      p.style.setProperty('--ty', `${ty}px`);
      p.style.animationDuration = `${10 + Math.random() * 15}s`;
      p.style.animationDelay = `${-Math.random() * 20}s`;
      p.style.opacity = `${0.3 + Math.random() * 0.4}`;
      container.appendChild(p);
    }
  }
});
