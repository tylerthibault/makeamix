/**
 * Side Navigation Component JavaScript
 * Handles mobile navigation toggle and active state management
 */

class SideNavigation {
  constructor() {
    this.sideNav = document.getElementById('sideNav');
    this.mobileToggle = document.getElementById('mobileNavToggle');
    this.overlay = document.getElementById('sideNavOverlay');
    this.navItems = document.querySelectorAll('.side-nav__item');
    
    this.init();
  }
  
  init() {
    if (!this.sideNav || !this.mobileToggle || !this.overlay) {
      return;
    }
    
    this.bindEvents();
    this.setActiveNavItem();
  }
  
  bindEvents() {
    // Mobile toggle functionality
    this.mobileToggle.addEventListener('click', () => this.toggleMobileNav());
    
    // Close navigation when clicking overlay
    this.overlay.addEventListener('click', () => this.closeMobileNav());
    
    // Handle window resize
    window.addEventListener('resize', () => this.handleResize());
    
    // Handle escape key to close mobile nav
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        this.closeMobileNav();
      }
    });
  }
  
  toggleMobileNav() {
    const isOpen = this.sideNav.classList.contains('side-nav--mobile-open');
    
    if (isOpen) {
      this.closeMobileNav();
    } else {
      this.openMobileNav();
    }
  }
  
  openMobileNav() {
    this.sideNav.classList.add('side-nav--mobile-open');
    this.overlay.classList.add('side-nav-overlay--active');
    document.body.style.overflow = 'hidden'; // Prevent scrolling when nav is open
  }
  
  closeMobileNav() {
    this.sideNav.classList.remove('side-nav--mobile-open');
    this.overlay.classList.remove('side-nav-overlay--active');
    document.body.style.overflow = ''; // Restore scrolling
  }
  
  handleResize() {
    // Close mobile navigation if window is resized to desktop size
    if (window.innerWidth > 768) {
      this.closeMobileNav();
    }
  }
  
  setActiveNavItem() {
    // Get current path
    const currentPath = window.location.pathname;
    
    // Remove active class from all nav items
    this.navItems.forEach(item => {
      item.classList.remove('side-nav__item--active');
    });
    
    // Find and set active nav item based on current path
    this.navItems.forEach(item => {
      const href = item.getAttribute('href');
      if (href && (href === currentPath || (href !== '#' && currentPath.includes(href)))) {
        item.classList.add('side-nav__item--active');
      }
    });
  }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  new SideNavigation();
});

// Export for potential use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = SideNavigation;
}