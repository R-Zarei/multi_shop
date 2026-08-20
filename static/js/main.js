(function ($) {
    "use strict";

    // Dropdown on mouse hover
    $(document).ready(function () {
        function toggleNavbarMethod() {
            if ($(window).width() > 992) {
                $('.navbar .dropdown').on('mouseover', function () {
                    $('.dropdown-toggle', this).trigger('click');
                }).on('mouseout', function () {
                    $('.dropdown-toggle', this).trigger('click').blur();
                });
            } else {
                $('.navbar .dropdown').off('mouseover').off('mouseout');
            }
        }

        toggleNavbarMethod();
        $(window).resize(toggleNavbarMethod);
    });


    // Back to top button
    $(window).scroll(function () {
        if ($(this).scrollTop() > 100) {
            $('.back-to-top').fadeIn('slow');
        } else {
            $('.back-to-top').fadeOut('slow');
        }
    });
    $('.back-to-top').click(function () {
        $('html, body').animate({scrollTop: 0}, 1500, 'easeInOutExpo');
        return false;
    });


    // Vendor carousel
    $('.vendor-carousel').owlCarousel({
        loop: true,
        margin: 29,
        nav: false,
        autoplay: true,
        smartSpeed: 1000,
        responsive: {
            0: {
                items: 2
            },
            576: {
                items: 3
            },
            768: {
                items: 4
            },
            992: {
                items: 5
            },
            1200: {
                items: 6
            }
        }
    });


    // Related carousel
    $('.related-carousel').owlCarousel({
        loop: true,
        margin: 29,
        nav: false,
        autoplay: true,
        smartSpeed: 1000,
        responsive: {
            0: {
                items: 1
            },
            576: {
                items: 2
            },
            768: {
                items: 3
            },
            992: {
                items: 4
            }
        }
    });


    // Product Quantity
    $('.quantity button').on('click', function () {
        var button = $(this);
        let input = button.parent().parent().find('input')
        var oldValue = input.val();
        if (button.hasClass('btn-plus')) {
            var newVal = parseFloat(oldValue) + 1;
        } else {
            if (oldValue > 1) {
                var newVal = parseFloat(oldValue) - 1;
            } else {
                var newVal = 1;
            }
        }
        input.data('old-value', oldValue);
        input.val(newVal);
    });

})(jQuery);

// ==========================================
// Advanced search with Dropdown Controller (jQuery)
// ==========================================

$(document).ready(function () {
    var $searchInput = $('#searchInput');
    var $searchDropdown = $('#searchDropdown');
    var $searchToggle = $('#searchToggle');
    let $perSearch = $("#perSearch");
    var $searchResults = $('#searchResults');
    var $searchLoading = $('#searchLoading');
    var $searchEmpty = $('#searchEmpty');
    var isOpen = false;
    var searchTimeout = null;
    // var $items = $('.search-item');
    var currentIndex = -1;

    // ---------- Toggle Dropdown ----------
    function toggleDropdown(show) {
        if (show === undefined) {
            isOpen = !isOpen;
        } else {
            isOpen = show;
        }

        if (isOpen && $searchInput.val().length > 0) {
            $searchDropdown.slideDown(200);
            search($searchInput.val());
        } else if (isOpen && $searchInput.val().length === 0) {
            $searchDropdown.slideDown(200);
            showPerSearch();
        } else {
            $searchDropdown.slideUp(200);
            resetKeyboardSelection();
            $searchInput.val('');
        }
    }

    // ---------- Show Default Suggestions ----------
    function showPerSearch() {
        $perSearch.show();
        $searchResults.hide();
        $searchLoading.hide();
        $searchEmpty.hide();
        // resetKeyboardSelection();
    }

    // ---------- Search ----------
    function search(query) {
        $perSearch.hide();
        $searchResults.hide();
        $searchLoading.show();
        $searchEmpty.hide();

        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(function () {
            // $searchLoading.hide();

            if (query.length > 1) {
                $.ajax({
                    method: 'POST',
                    url: searchSuggestionsUrl,
                    data: {'query': query},
                    headers: {'X-CSRFToken': csrfToken},
                    success: function (response) {
                        $searchLoading.hide();

                        let hasResults =
                            response.products.length > 0 ||
                            response.brands.length > 0 ||
                            response.categories.length > 0;

                        if (hasResults) {
                            $searchResults.empty();

                            // products
                            if (response.products.length > 0) {
                                let html = `<div class="search-section"> 
                                                        <h6 class="search-section-title">products</h6>`;

                                response.products.forEach(function (product) {
                                    html += `<a href="${product.url}" class="search-item">
                                                <span>${product.title}</span>
                                             </a>`;
                                });

                                html += '</div>';

                                $searchResults.append(html);
                            }

                            // brands
                            if (response.brands.length > 0) {
                                let html = `<div class="search-section">
                                                        <h6 class="search-section-title">brands</h6>`;

                                response.brands.forEach(function (brand) {
                                    html += `<a href="${brand.url}" class="search-item">
                                                <span>${brand.title}</span>
                                            </a>`;
                                });

                                html += '</div>';

                                $searchResults.append(html);
                            }

                            // categories
                            if (response.categories.length > 0) {
                                let html = `<div class="search-section">
                                                        <h6 class="search-section-title">categories</h6>`;

                                response.categories.forEach(function (category) {
                                    html += `<a href="${category.url}" class="search-item">
                                                <span>${category.title}</span>
                                             </a>`;
                                });

                                html += '</div>';

                                $searchResults.append(html);
                            }

                            let popularAndViewAllResults = `
                                <!-- tags section -->
                                <div class="search-section">
                                    <h6 class="search-section-title">popular tags</h6>
                                    <div class="search-tags">
                                        <span class="search-tag">#5g</span>
                                        <span class="search-tag">#ai</span>
                                        <span class="search-tag">#oled</span>
                                        <span class="search-tag">#gaming</span>
                                        <span class="search-tag">#flagship</span>
                                    </div>
                                </div>

                                <!-- view all results button -->
                                <div class="search-footer">
                                    <a href="${searchProductsUrl}?q=${$searchInput.val()}" class="search-view-all">
                                        view all results
                                        <i class="fas fa-arrow-right"></i>
                                    </a>
                                </div>`;
                            $searchResults.append(popularAndViewAllResults);

                            $searchResults.show();
                            $searchEmpty.hide();
                            $perSearch.hide();

                        } else {
                            $searchResults.hide();
                            $perSearch.hide();
                            $searchEmpty.show();
                        }

                        resetKeyboardSelection();
                    },
                    error: function () {
                        $searchLoading.hide();
                        $searchResults.hide();
                        $perSearch.hide();
                        $searchEmpty.show();
                    }
                });
            } else {       // *======================> ? <=======================*
                $searchResults.hide();
                $perSearch.show();
                $searchEmpty.hide();
                $searchLoading.hide();
                // $('.search-item').show();
            }

            // reset keyboard selection after filtering
            resetKeyboardSelection();
        }, 400);
    }

    // ---------- Keyboard Navigation ----------
    // for scroll and select on items with arrows.
    function navigateItems(direction) {
        let visibleItems = $('.search-item:visible');
        if (visibleItems.length === 0) return;

        // Remove active class from all. Items that have the active class are highlighted.
        $('.search-item').removeClass('active');

        // Calculate new index
        if (direction === 'down') {
            currentIndex = (currentIndex + 1) % visibleItems.length;
        } else if (direction === 'up') {
            currentIndex = (currentIndex - 1 + visibleItems.length) % visibleItems.length;
        }

        // Add active class to current item
        $(visibleItems[currentIndex]).addClass('active');

        // Scroll to visible item if needed
        let $activeItem = $(visibleItems[currentIndex]);
        let dropdownHeight = $searchDropdown.height();
        let itemTop = $activeItem.position().top;
        let itemHeight = $activeItem.outerHeight();

        if (itemTop + itemHeight > dropdownHeight) {
            $searchDropdown.scrollTop($searchDropdown.scrollTop() + itemHeight);
        } else if (itemTop < 0) {
            $searchDropdown.scrollTop($searchDropdown.scrollTop() + itemTop);
        }
    }

    function resetKeyboardSelection() {
        $('.search-item').removeClass('active');
        currentIndex = -1;
    }

    function selectCurrentItem() {
        let $activeItem = $('.search-item.active');
        if ($activeItem.length > 0) {
            window.location.href = $activeItem.attr('href');
        }
    }

    // ---------- Event Handlers ----------

    // Click on search button
    $searchToggle.on('click', function (e) {
        e.preventDefault();
        let input = $searchInput.val();
        if (input.length > 0) {
            window.location.href = `${searchProductsUrl}?q=${input}`;
        }
    });

    // Typing in search input
    $searchInput.on('input', function () {
        let query = $(this).val().trim();
        resetKeyboardSelection();

        if (query.length > 0) {
            if (!isOpen) {
                toggleDropdown(true);
            } else {
                search(query);
            }
        } else {
            if (isOpen) {
                showPerSearch();
                // $('.search-item').show();
            }
        }
    });

    // Focus on search input
    $searchInput.on('focus', function () {
        if ($(this).val().length > 0 || !isOpen) {
            toggleDropdown(true);
            resetKeyboardSelection();
        }
    });

    // ---------- Keyboard Events ----------
    $searchInput.on('keydown', function (e) {
        // Down arrow
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            if (!isOpen) {
                toggleDropdown(true);
            } else {
                navigateItems('down');
            }
        }
        // Up arrow
        else if (e.key === 'ArrowUp') {
            e.preventDefault();
            if (isOpen) {
                navigateItems('up');
            }
        }
        // Enter key
        else if (e.key === 'Enter') {
            e.preventDefault();
            if (isOpen) {
                selectCurrentItem();
            }
        }
        // Escape key
        else if (e.key === 'Escape') {
            if (isOpen) {
                toggleDropdown(false);
                resetKeyboardSelection();
                $searchInput.blur();
            }
        }
    });

    // // ---------- Click on search items ----------
    // $('.search-item').on('click', function () {
    //     var text = $(this).find('span').text() || '';
    //     $searchInput.val(text);
    //     toggleDropdown(false);
    //     resetKeyboardSelection();
    // });

    // ---------- Click on tags ----------
    $('.search-tag').on('click', function () {
        var text = $(this).text().trim();
        $searchInput.val(text);
        toggleDropdown(true);
        search(text);
        resetKeyboardSelection();
    });

    // // ---------- Click on view all ----------
    // $('.search-view-all').on('click', function (e) {
    //     e.preventDefault();
    //     alert('Redirect to full results page with: ' + ($searchInput.val() || 'all'));
    //     toggleDropdown(false);
    //     resetKeyboardSelection();
    // });

    // ---------- Close on outside click ----------
    $(document).on('click', function (e) {
        if (!$(e.target).closest('.search-wrapper').length) {
            if (isOpen) {
                toggleDropdown(false);
                resetKeyboardSelection();
            }
        }
    });

    // ---------- Close on scroll ----------
    $(window).on('scroll', function () {
        if (isOpen) {
            toggleDropdown(false);
            resetKeyboardSelection();
        }
    });

    // Prevent closing when clicking inside dropdown
    $searchDropdown.on('click', function (e) {
        e.stopPropagation();
    });
});