$(document).ready(function () {
    $(document).on("click", "#del-button", function () {
        var row = $(this).closest("tr");  // Get the closest tr element
        var productId = row.data("product-id"); // Get product id from tr

        $.ajax({
            url: removeFromCartUrl, // Update the URL if necessary
            type: "POST",
            data: {
                "product_id": productId,
            },
            headers: {
                "X-CSRFToken": csrfToken,
            },
            success: function (response) {
                    row.fadeOut(300, function () {
                        $(this).remove(); // Remove the entire row
                    });
                    // console.log(response)
                        $("#cart-num").text(response.cart_quantity);
            },
            error: function () {
                alert("Something went wrong! Please try again.");
            }
        });
    });
});