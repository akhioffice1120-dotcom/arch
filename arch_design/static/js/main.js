// static/js/main.js
$(document).ready(function() {
    // Navbar scroll effect
    $(window).scroll(function() {
        if ($(this).scrollTop() > 50) {
            $('.navbar').addClass('scrolled');
        } else {
            $('.navbar').removeClass('scrolled');
        }
    });

    // Smooth scrolling for anchor links
    $('a[href*="#"]').not('[href="#"]').not('[href="#0"]').click(function(event) {
        if (location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') && 
            location.hostname == this.hostname) {
            var target = $(this.hash);
            target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
            if (target.length) {
                event.preventDefault();
                $('html, body').animate({
                    scrollTop: target.offset().top - 80
                }, 1000);
            }
        }
    });

    // Form validation
    $('.needs-validation').on('submit', function(event) {
        if (!this.checkValidity()) {
            event.preventDefault();
            event.stopPropagation();
        }
        $(this).addClass('was-validated');
    });

    // Image lazy loading
    $('img').each(function() {
        var dataSrc = $(this).data('src');
        if (dataSrc) {
            $(this).attr('src', dataSrc);
        }
    });

    // Tooltip initialization
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Popover initialization
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Counter animation for statistics
    $('.counter').each(function() {
        $(this).prop('Counter', 0).animate({
            Counter: $(this).text()
        }, {
            duration: 2000,
            easing: 'swing',
            step: function(now) {
                $(this).text(Math.ceil(now));
            }
        });
    });

    // Service filter
    $('.service-filter').click(function(e) {
        e.preventDefault();
        var category = $(this).data('category');
        
        $('.service-filter').removeClass('active');
        $(this).addClass('active');
        
        if (category === 'all') {
            $('.service-item').show();
        } else {
            $('.service-item').hide();
            $('.service-item[data-category="' + category + '"]').show();
        }
    });

    // Project gallery modal
    $('.project-gallery-item').click(function() {
        var imgSrc = $(this).data('image');
        var imgAlt = $(this).data('title');
        var imgDesc = $(this).data('description');
        
        $('#galleryModalImage').attr('src', imgSrc);
        $('#galleryModalImage').attr('alt', imgAlt);
        $('#galleryModalTitle').text(imgAlt);
        $('#galleryModalDescription').text(imgDesc);
        
        var galleryModal = new bootstrap.Modal(document.getElementById('galleryModal'));
        galleryModal.show();
    });

    // Newsletter subscription
    $('#newsletterForm').submit(function(e) {
        e.preventDefault();
        var email = $('#newsletterEmail').val();
        
        $.ajax({
            url: '/api/subscribe-newsletter/',
            method: 'POST',
            data: { email: email },
            success: function(response) {
                $('#newsletterForm')[0].reset();
                alert('Thank you for subscribing!');
            },
            error: function() {
                alert('Something went wrong. Please try again.');
            }
        });
    });

    // Search functionality
    $('#searchInput').keyup(function() {
        var query = $(this).val();
        if (query.length > 2) {
            $.ajax({
                url: '/search-autocomplete/',
                method: 'GET',
                data: { q: query },
                success: function(response) {
                    $('#searchResults').empty();
                    if (response.results.length > 0) {
                        $.each(response.results, function(index, result) {
                            $('#searchResults').append(
                                '<a href="' + result.url + '" class="list-group-item list-group-item-action">' +
                                '<strong>' + result.type + ':</strong> ' + result.title + '<br>' +
                                '<small class="text-muted">' + result.description + '</small>' +
                                '</a>'
                            );
                        });
                        $('#searchResults').show();
                    } else {
                        $('#searchResults').hide();
                    }
                }
            });
        } else {
            $('#searchResults').hide();
        }
    });

    // Close search results when clicking outside
    $(document).click(function(e) {
        if (!$(e.target).closest('#searchInput, #searchResults').length) {
            $('#searchResults').hide();
        }
    });

    // Initialize Wow.js for animations
    new WOW().init();

    // Back to top button
    var backToTop = $('#backToTop');
    $(window).scroll(function() {
        if ($(this).scrollTop() > 300) {
            backToTop.fadeIn();
        } else {
            backToTop.fadeOut();
        }
    });

    backToTop.click(function() {
        $('html, body').animate({ scrollTop: 0 }, 800);
        return false;
    });
});

// Debounce function for performance
function debounce(func, wait, immediate) {
    var timeout;
    return function() {
        var context = this, args = arguments;
        var later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        var callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}