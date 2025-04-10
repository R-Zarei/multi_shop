$(document).ready(function() {
    updateKey(); // اجرا هنگام لود صفحه

    // اضافه کردن رویداد تغییر به رادیو باتن‌ها و فیلد product_id
    $('input[name="color"], input[name="size"], #product_id').change(function() {
        updateKey();
    });
});

function updateKey() {
    let selectedColor = $('input[name="color"]:checked').val() || "None";
    let selectedSize = $('input[name="size"]:checked').val() || "None";
    let productId = $('#product_id').val();

    let key = productId + "-" + selectedColor + "-" + selectedSize;
    // $('#product_key').val(key);

    // بررسی مقدار JSON
    let cartItems = {};
    try {
        cartItems = JSON.parse($('#cart_data').text());
    } catch (error) {
        console.error("Error parsing cart_data:", error);
    }

    // تغییر دکمه بر اساس وضعیت سبد خرید
    let button = $('#submit-button');
    if (cartItems.hasOwnProperty(key)) {
        button.removeClass('btn-primary').addClass('btn-danger');
        button.html('<i class="fa fa-trash mr-1"></i> Remove From Cart');
    } else {
        button.removeClass('btn-danger').addClass('btn-primary');
        button.html('<i class="fa fa-shopping-cart mr-1"></i> Add To Cart');
    }
}
