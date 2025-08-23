$(document).ready(function () {
    // Send POST request for delete item from cart.
    $(document).on("click", "#del-button", function () {
        var row = $(this).closest("tr");  // Get the closest tr element
        var productId = row.data("product-id"); // Get product id from tr

        $.ajax({
            url: removeFromCartUrl,
            type: "POST",
            data: {
                "product_id": productId,
            },
            headers: {
                "X-CSRFToken": csrfToken,
            },
            success: function (response) {
                // GetTotalPrice();
                ChangeTotal(response.total_price);
                row.fadeOut(300, function () {
                    $(this).remove(); // Remove the entire row
                });
                // console.log(response)
                $("#cart-num").text(response.cart_quantity);
            },
            error: function (jqXHR, textStatus, errorTheron) {
                // Handel error
                console.error("Error: ", textStatus, errorTheron);
                // jqXHR provides details about the error, including status code and responseText
                console.log("Status Code: ", jqXHR.status);
                console.log("Response Text: ", jqXHR.responseText);
                // Display an error message to user
                alert("Something went wrong! Please try again.");
            }
        });
    });

    // Calculate cart total price and put them in cart page.
    function TotalPriceCalculator(subtotal, shipping, tagId) {
        let total = parseFloat(subtotal) + parseFloat(shipping);
        if (parseFloat(subtotal) === 0) {
            total = 0
        }
        $("#" + tagId).text('$' + total);
    }

    // send GET request for resave cart total price
    // function GetTotalPrice(callback) {
    //     $.ajax({
    //         url: CartTotalPriceUrl,
    //         type:"GET",
    //         success: function (response) {
    //             $("#subtotal").text(response.total_price);
    //             TotalPriceCalculator(response.total_price, 10, 'total-price');
    //             callback(response.total_price);
    //         },
    //         error: function (jqXHR, textStatus, errorTheron) {
    //             // Handel error
    //             console.error("Error: ",textStatus, errorTheron);
    //             // jqXHR provides details about the error, including status code and responseText
    //             console.log("Status Code: ", jqXHR.status);
    //             console.log("Response Text: ", jqXHR.responseText);
    //             callback(null);
    //         }
    //     });
    // }

    function ChangeTotal(newPrice) {
        $("#subtotal").text(newPrice);
        TotalPriceCalculator(newPrice, 10, 'total-price');
    }

    function ChangeCartItemQuantity() {
        let debounceTimer;
        $(document).on("click", ".btn-plus, .btn-minus", function () {
            let button = $(this);
            let input = $(this).closest(".quantity").find("input");
            let uniqueId = $(this).closest("tr").data("product-id");
            let oldValue = input.data('old-value');
            let newValue = input.val();
            if (oldValue !== newValue) {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(function () {
                    $.ajax({
                        url: cartItemQuantityChangeUrl,
                        type: "POST",
                        data: {
                            "uid": uniqueId,
                            "quantity": newValue
                        },
                        headers: {
                            "X-CSRFToken": csrfToken,
                        },
                        success: function (response) {
                            // GetTotalPrice();
                            ChangeTotal(response.total_price);
                            button.closest("tr").find(".item-total-price").text("$" + response.item_total_price);
                            console.log("Quantity update: ", response);
                        },
                        error: function (jqXHR, textStatus, errorTheron) {
                            // Handel error
                            console.error("Error: ", textStatus, errorTheron);
                            // jqXHR provides details about the error, including status code and responseText
                            console.log("Status Code: ", jqXHR.status);
                            console.log("Response Text: ", jqXHR.responseText);
                            // Display an error message to user
                            alert("Error updating cart!");
                        }
                    });
                }, 700);
            }
        });
    }


    // calling functions
    TotalPriceCalculator($("#subtotal").data("value"), 10, 'total-price');

    // calling function
    ChangeCartItemQuantity();

});
