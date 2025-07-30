(function ($) {

    "use strict";

    // === Analytics Variables ===
    let startTime = Date.now();
    let maxScrollDepth = 0;
    const userId = 'user_' + Math.random().toString(36).substr(2, 9); // Anonymous ID
    const currentPage = window.location.pathname || '/';

    // Track scroll depth (0–100%)
    $(window).on('scroll', function () {
        const scrollTop = $(window).scrollTop();
        const docHeight = $(document).height();
        const winHeight = $(window).height();
        const scrollPercent = (scrollTop / (docHeight - winHeight)) * 100;
        maxScrollDepth = Math.max(maxScrollDepth, scrollPercent);
    });

    // === Page View: Log when page loads ===
    $(window).on('load', function () {
        $('#js-preloader').addClass('loaded');

        // Send initial page view
        const loadTime = new Date().toISOString();
        const eventData = {
            timestamp: loadTime,
            page: currentPage,
            event_type: 'page_view',
            user_id: userId,
            duration: 0,
            scroll_depth: 0
        };

        // Use sendBeacon-compatible method or fallback
        if (navigator.sendBeacon) {
            const blob = new Blob([JSON.stringify(eventData)], { type: 'application/json' });
            navigator.sendBeacon('/analytics', blob);
        } else {
            // Fallback for older browsers
            $.ajax({
                url: '/analytics',
                type: 'POST',
                data: JSON.stringify(eventData),
                contentType: 'application/json',
                async: true // Don't block
            });
        }
    });

    // === Page Exit: Log duration and final scroll depth ===
    $(window).on('beforeunload', function () {
        const now = Date.now();
        const durationMs = now - startTime;
        const durationSec = (durationMs / 1000).toFixed(2);

        const exitData = {
            timestamp: new Date().toISOString(),
            page: currentPage,
            event_type: 'page_exit',
            user_id: userId,
            duration: parseFloat(durationSec),
            scroll_depth: Math.round(maxScrollDepth)
        };

        // Send via sendBeacon to ensure delivery during unload
        const blob = new Blob([JSON.stringify(exitData)], { type: 'application/json' });
        navigator.sendBeacon('/analytics', blob);
    });


    // === Existing UI/UX Scripts Below ===

    $(window).scroll(function () {
        var scroll = $(window).scrollTop();
        var box = $('.header-text').height();
        var header = $('header').height();

        if (scroll >= box - header) {
            $("header").addClass("background-header");
        } else {
            $("header").removeClass("background-header");
        }
    });

    var width = $(window).width();
    $(window).resize(function () {
        if (width > 767 && $(window).width() < 767) {
            location.reload();
        } else if (width < 767 && $(window).width() > 767) {
            location.reload();
        }
    });

    const elem = document.querySelector('.trending-box');
    const filtersElem = document.querySelector('.trending-filter');
    if (elem) {
        const rdn_events_list = new Isotope(elem, {
            itemSelector: '.trending-items',
            layoutMode: 'masonry'
        });
        if (filtersElem) {
            filtersElem.addEventListener('click', function (event) {
                if (!event.target.matches('a')) {
                    return;
                }
                const filterValue = event.target.getAttribute('data-filter');
                rdn_events_list.arrange({ filter: filterValue });
                filtersElem.querySelector('.is_active').classList.remove('is_active');
                event.target.classList.add('is_active');
                event.preventDefault();
            });
        }
    }

    // Menu Dropdown Toggle
    if ($('.menu-trigger').length) {
        $(".menu-trigger").on('click', function () {
            $(this).toggleClass('active');
            $('.header-area .nav').slideToggle(200);
        });
    }

    // Menu elevator animation
    $('.scroll-to-section a[href*=\\#]:not([href=\\#])').on('click', function () {
        if (location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') && location.hostname == this.hostname) {
            var target = $(this.hash);
            target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
            if (target.length) {
                var width = $(window).width();
                if (width < 991) {
                    $('.menu-trigger').removeClass('active');
                    $('.header-area .nav').slideUp(200);
                }
                $('html,body').animate({
                    scrollTop: (target.offset().top) - 80
                }, 700);
                return false;
            }
        }
    });

    // Page loading animation
    $(window).on('load', function () {
        if ($('.cover').length) {
            $('.cover').parallax({
                imageSrc: $('.cover').data('image'),
                zIndex: '1'
            });
        }

        $("#preloader").animate({
            'opacity': '0'
        }, 600, function () {
            setTimeout(function () {
                $("#preloader").css("visibility", "hidden").fadeOut();
            }, 300);
        });
    });

})(window.jQuery);
