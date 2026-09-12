$(document).ready(function () {
    const $productsWrapper = $('#products-wrapper');
    const $filterForm = $('#filter-form');

    function fetchProducts(url) {
        $productsWrapper.css({
            'opacity': '0.4',
            'pointer-events': 'none',
            'transition': 'opacity 0.2s ease'
        });

        $.ajax({
            url: url,
            type: 'GET',
            headers: {'X-Requested-With': 'XMLHttpRequest'},
            success: function (response) {
                $productsWrapper.html(response.html).css({
                    'opacity': '1',
                    'pointer-events': 'auto'
                });

                // Update URL without page reload
                window.history.pushState({ path: url }, '', url);

                $('html, body').animate({
                    scrollTop: $productsWrapper.offset().top - 80
                }, 300);
            },
            error: function (xhr) {
                console.error('Filter request failed:', xhr.statusText);
                $productsWrapper.css({
                    'opacity': '1',
                    'pointer-events': 'auto'
                });
            }
        });
    }

    // Trigger filters on form input changes
    $filterForm.on('change', 'input', function () {
        const filterData = $filterForm.serialize();
        const targetUrl = `${window.location.pathname}?${filterData}`;
        fetchProducts(targetUrl);
    });

    // Pagination click handler
    $(document).on('click', '#products-wrapper .pagination a', function (e) {
        e.preventDefault();
        const targetUrl = $(this).attr('href');

        if (targetUrl && targetUrl !== '#' && !$(this).parent().hasClass('disabled')) {
            fetchProducts(targetUrl);
        }
    });

    // Handle browser back/forward buttons
    window.addEventListener('popstate', function () {
        fetchProducts(window.location.href);
    });
});