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
                    TotalPrice();
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


   function TotalPriceCalculator(subtotal, shipping, tagId) {
       let total = parseFloat(subtotal) + parseFloat(shipping);
       if (parseFloat(subtotal) === 0) {total = 0}
       $("#" + tagId).text('$'+total);
   }


   function TotalPrice() {
       $.ajax({
           url: CartTotalPriceUrl,
           type:"GET",
           success: function (response) {
               $("#subtotal").text(response.total_price);
               TotalPriceCalculator(response.total_price, 10, 'total-price');
           }

       })
   }


   // calling functions
    TotalPriceCalculator($("#subtotal").data("value"), 10, 'total-price');
});
