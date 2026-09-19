/*
  Hasten Business Solutions LLP — script.js
  Phase 4: navbar scroll state, mobile menu auto-close, scroll-spy active link.
  Phase 5: hero video play/pause + mute/unmute controls.
  Phase 9: service detail modal "Enquire" flow.
  Phase 12: testimonials carousel (responsive item grouping).
  Phase 14: contact form validation + success state.
  Phase 16: footer dynamic copyright year.
  Phase 20: scroll-reveal animations (hero load, service cards, about
  image, CTA section) and reduced-motion handling.
*/

document.addEventListener("DOMContentLoaded", function () {
  initNavScrollState();
  initNavMobileAutoClose();
  initNavScrollSpy();
  initHeroVideoControls();
  initServiceModalEnquire();
  initTestimonialsCarousel();
  initContactForm();
  initFooterYear();
  initScrollReveal();
});

function initNavScrollState() {
  var nav = document.getElementById("siteNav");
  if (!nav) return;

  var SCROLL_THRESHOLD = 40;

  function updateState() {
    nav.classList.toggle("is-scrolled", window.scrollY > SCROLL_THRESHOLD);
  }

  updateState();
  window.addEventListener("scroll", updateState, { passive: true });
}

function initNavMobileAutoClose() {
  var collapseEl = document.getElementById("siteNavCollapse");
  if (!collapseEl) return;

  var links = collapseEl.querySelectorAll("[data-nav-link]");
  links.forEach(function (link) {
    link.addEventListener("click", function () {
      if (collapseEl.classList.contains("show") && window.bootstrap) {
        var instance = window.bootstrap.Collapse.getOrCreateInstance(collapseEl);
        instance.hide();
      }
    });
  });
}

function initNavScrollSpy() {
  var navLinks = document.querySelectorAll(".site-nav__links [data-nav-link]");
  var sections = Array.from(document.querySelectorAll("main section[id]"));

  if (!navLinks.length || !sections.length || !("IntersectionObserver" in window)) {
    return;
  }

  var observer = new IntersectionObserver(setActiveLink, {
    rootMargin: "-45% 0px -50% 0px",
    threshold: 0,
  });

  sections.forEach(function (section) {
    observer.observe(section);
  });

  function setActiveLink(entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;

      var id = entry.target.getAttribute("id");
      var activeLink = document.querySelector('.site-nav__links [data-nav-link][href="#' + id + '"]');
      if (!activeLink) return;

      navLinks.forEach(function (link) {
        link.classList.remove("active");
        link.removeAttribute("aria-current");
      });
      activeLink.classList.add("active");
      activeLink.setAttribute("aria-current", "page");
    });
  }
}

function initHeroVideoControls() {
  var video = document.querySelector(".hero__video");
  var playBtn = document.getElementById("heroPlayToggle");
  var muteBtn = document.getElementById("heroMuteToggle");
  if (!video || !playBtn || !muteBtn) return;

  var prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var userAllowedPlay = !prefersReducedMotion;

  if (prefersReducedMotion) {
    video.pause();
  }

  // Autoplay can start asynchronously after this script runs, racing an
  // upfront pause() call. Re-assert the pause on every "play" event until
  // the visitor explicitly presses play themselves.
  video.addEventListener("play", function () {
    if (prefersReducedMotion && !userAllowedPlay) {
      video.pause();
    }
  });

  function syncPlayState() {
    var isPaused = video.paused;
    playBtn.querySelector("i").className = isPaused ? "bi bi-play-fill" : "bi bi-pause-fill";
    playBtn.setAttribute("aria-label", isPaused ? "Play background video" : "Pause background video");
  }

  function syncMuteState() {
    muteBtn.querySelector("i").className = video.muted ? "bi bi-volume-mute-fill" : "bi bi-volume-up-fill";
    muteBtn.setAttribute("aria-label", video.muted ? "Unmute background video" : "Mute background video");
  }

  playBtn.addEventListener("click", function () {
    if (video.paused) {
      userAllowedPlay = true;
      video.play();
    } else {
      video.pause();
    }
  });

  muteBtn.addEventListener("click", function () {
    video.muted = !video.muted;
    syncMuteState();
  });

  video.addEventListener("play", syncPlayState);
  video.addEventListener("pause", syncPlayState);

  syncPlayState();
  syncMuteState();
}

function initServiceModalEnquire() {
  document.addEventListener("click", function (event) {
    var button = event.target.closest(".service-modal__enquire");
    if (!button) return;

    var modalEl = button.closest(".modal");
    if (!modalEl || !window.bootstrap) return;

    // Order matters: close the modal first, then scroll once it has
    // actually finished closing (avoids fighting the modal's own
    // focus/scroll handling mid-transition).
    modalEl.addEventListener(
      "hidden.bs.modal",
      function onHidden() {
        var contact = document.getElementById("contact");
        if (contact) {
          contact.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      },
      { once: true }
    );

    var instance = window.bootstrap.Modal.getOrCreateInstance(modalEl);
    instance.hide();
  });
}

function initTestimonialsCarousel() {
  var carouselEl = document.getElementById("testimonialsCarousel");
  var track = document.getElementById("testimonialsInner");
  var indicatorsEl = document.getElementById("testimonialsIndicators");
  if (!carouselEl || !track || !indicatorsEl || !window.bootstrap) return;

  var TESTIMONIAL_COUNT = 6;
  var bsCarousel = null;
  var currentSize = null;

  function testimonialCardHTML() {
    return (
      '<div class="testimonial-card">' +
      '<i class="bi bi-quote testimonial-card__quote-icon" aria-hidden="true"></i>' +
      '<p class="testimonial-card__quote">Add your approved client testimonial here.</p>' +
      '<div class="testimonial-card__footer">' +
      '<span class="testimonial-card__avatar"><i class="bi bi-person-fill" aria-hidden="true"></i></span>' +
      '<div>' +
      '<p class="testimonial-card__name">Client Name</p>' +
      '<p class="testimonial-card__role">Designation, Company Name</p>' +
      "</div>" +
      "</div>" +
      "</div>"
    );
  }

  function itemsPerSlide() {
    var w = window.innerWidth;
    if (w >= 992) return 3;
    if (w >= 768) return 2;
    return 1;
  }

  function chunk(count, size) {
    var groups = [];
    for (var i = 0; i < count; i += size) {
      groups.push(Math.min(size, count - i));
    }
    return groups;
  }

  function render() {
    var size = itemsPerSlide();
    if (size === currentSize) return;
    currentSize = size;

    var groups = chunk(TESTIMONIAL_COUNT, size);

    track.innerHTML = groups
      .map(function (groupSize, i) {
        var cards = new Array(groupSize).fill(0).map(testimonialCardHTML).join("");
        return (
          '<div class="carousel-item' + (i === 0 ? " active" : "") + '">' +
          '<div class="testimonials__row">' +
          cards +
          "</div>" +
          "</div>"
        );
      })
      .join("");

    indicatorsEl.innerHTML = groups
      .map(function (_, i) {
        return (
          '<button type="button" data-bs-target="#testimonialsCarousel" data-bs-slide-to="' +
          i +
          '"' +
          (i === 0 ? ' class="active" aria-current="true"' : "") +
          ' aria-label="Testimonials, page ' +
          (i + 1) +
          '"></button>'
        );
      })
      .join("");

    if (bsCarousel) {
      bsCarousel.dispose();
    }
    bsCarousel = new window.bootstrap.Carousel(carouselEl, { ride: false, touch: true });
  }

  render();

  // The indicators live outside #testimonialsCarousel (grouped with the
  // prev/next buttons below the cards instead of overlaid on them), so
  // Bootstrap's built-in indicator sync — which only looks for
  // .carousel-indicators as a descendant of the carousel root — never finds
  // them. Sync their active state manually instead.
  carouselEl.addEventListener("slid.bs.carousel", function (event) {
    var buttons = indicatorsEl.querySelectorAll("[data-bs-slide-to]");
    buttons.forEach(function (btn) {
      var isActive = Number(btn.getAttribute("data-bs-slide-to")) === event.to;
      btn.classList.toggle("active", isActive);
      if (isActive) {
        btn.setAttribute("aria-current", "true");
      } else {
        btn.removeAttribute("aria-current");
      }
    });
  });

  var resizeTimer;
  window.addEventListener(
    "resize",
    function () {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(render, 200);
    },
    { passive: true }
  );
}

function initContactForm() {
  var form = document.getElementById("contactForm");
  var successPanel = document.querySelector(".contact-form__success");
  if (!form || !successPanel) return;

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    event.stopPropagation();

    if (!form.checkValidity()) {
      form.classList.add("was-validated");
      return;
    }

    form.classList.remove("was-validated");
    form.hidden = true;
    successPanel.hidden = false;
    successPanel.focus();
  });
}

function initFooterYear() {
  var yearEl = document.getElementById("copyrightYear");
  if (!yearEl) return;
  yearEl.textContent = new Date().getFullYear();
}

function initScrollReveal() {
  // Hero: fade up shortly after load. The hidden starting state is CSS
  // (.js .hero__text), applied before first paint by the inline script in
  // <head>, so this only ever adds the "reveal" class — it never toggles
  // the class that does the hiding, which keeps a JS error here from
  // leaving the hero permanently invisible.
  var heroText = document.querySelector(".hero__text");
  if (heroText) {
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        heroText.classList.add("is-visible");
      });
    });
  }

  // Scroll-triggered: service cards, the about image, and the CTA content.
  // The .reveal (hidden) class is only ever added here, immediately before
  // observing — so if this function doesn't run at all, nothing starts
  // hidden.
  if (!("IntersectionObserver" in window)) return;

  var targets = document.querySelectorAll(".service-card, .about__media, .cta__content");
  if (!targets.length) return;

  var observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    },
    { threshold: 0.15, rootMargin: "0px 0px -60px 0px" }
  );

  targets.forEach(function (el) {
    el.classList.add("reveal");
    observer.observe(el);
  });
}
