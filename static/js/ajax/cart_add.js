$(document).ready(function() {

    // Add and remove the product from the cart, and change submit button.
    $("#add-to-cart-form").submit(function(event) {
        event.preventDefault();  // Prevent the default form submission

        var submit_button_name = $("#submit-button").attr("name")
        if (submit_button_name === "add-to-cart-button") {
            var actionUrl = $(this).attr("action"); // Get the form action URL
            var formData = $(this).serialize(); // Collect form data
            formData += "&csrfmiddlewaretoken=" + csrfToken; // Append CSRF token to form data

            $.ajax({
                type: "POST",
                url: actionUrl,
                data: formData,
                success: function (response) {
                    $("#cart-num").text(response.cart_quantity); // Assign input value to span

                    var button = $("#submit-button");
                    button.attr("class", "btn btn-danger px-3");
                    button.blur();
                    button.html('<i id="submit-icon" class="fa fa-trash mr-1"></i> Remove From Cart');
                    button.attr("name", "del-form-cart-button");
                },
                error: function (xhr, status, error) {
                    alert("Error adding product to the cart!"); // Show error message
                }
            });
        }
        else {
            var formData = new FormData(this); // Collect form data
            var productId = $("#product-id").val();
            var size = formData.get('size') || 'None';
            $.ajax({
                type: "POST",
                url: removeFromCartUrl,
                data: {
                    "product_id": productId + "-" + formData.get('color') + "-" + size,
                    "csrfmiddlewaretoken": csrfToken
                },
                success: function (response) {
                    $("#cart-num").text(response.cart_quantity);

                    var button = $("#submit-button");
                    button.attr("class", "btn btn-primary px-3");
                    button.blur();
                    button.html('<i id="submit-icon" class="fa fa-shopping-cart mr-1"></i> Add To Cart');
                    button.attr("name", "add-to-cart-button");
                }
            });
        }
    });

    // Calling the checkProduct function by refreshing page
    checkProduct();

    // Calling the checkProduct function by changing a radio button
    $('input[type="radio"]').change(function () {
       checkProduct();
    });

    // Check the product in the cart and change submit button
    function checkProduct() {
        var color = $('input[name="color"]:checked').val();
        var size = $('input[name="size"]:checked').val();
        var product_id = $("#product-id").val() + '-' + color + '-' + size;
        console.log(product_id);
        $.ajax({
            type: 'POST',
            url: $('#checkCartUrl').val(),
            data: {
                'product_id': product_id,
                'csrfmiddlewaretoken': csrfToken
            },
            success: function (response) {
                console.log(response);
                var button = $("#submit-button");
                if (response.is_in) {
                    button.attr("class", "btn btn-danger px-3");
                    button.blur();
                    button.html('<i id="submit-icon" class="fa fa-trash mr-1"></i> Remove From Cart');
                    button.attr("name", "del-form-cart-button");
                }
                else {
                    button.attr("class", "btn btn-primary px-3");
                    button.blur();
                    button.html('<i id="submit-icon" class="fa fa-shopping-cart mr-1"></i> Add To Cart');
                    button.attr("name", "add-to-cart-button");
                }
            },
            error: function () {
                alert('Something rong try again!');
            }
        });
    }

});
