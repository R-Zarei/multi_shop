$(document).ready(function () {

   // request to load_cities view and send province id and resave cities list.
   function send_load_city_request(provinceSelect, citySelect, selectCityName) {
      let provinceId = provinceSelect.val();
      $.ajax({
         url: $("#loadCityUrl").val(),
         type: "GET",
         data: {
            "province_id": provinceId
         },
         dataType: "json",
         success: function (response) {
            // let citySelect = $("#id_city");
            citySelect.empty();
            citySelect.append("<option value selected>City</option>");
            $.each(response, function (index, city) {
               citySelect.append('<option value="' + city.id + '">' + city.name + '</option>');
            });

            if (selectCityName) {
                citySelect.find('option').filter(function(){return $(this).text() === selectCityName;}).prop('selected', true);
            }
         },
         error: function () {
            alert("Something went wrong! Please try again.")
         }
      });
   }
   function load_cities (provinceSelect, citySelect, selectCityName = null) {
      provinceSelect.change(function () {
        send_load_city_request(provinceSelect, citySelect, selectCityName);
      });
   }


   // sends the address id to delete this address
   function remove_address () {
      $(document).on("click", ".delete-btn", function () {
         let delBtn = $(this);
         delBtn.prop("disabled", true);  // disable delete btn.

         let box = delBtn.closest(".bg-light");
         let addressId = box.data("address-id");
         let csrfToken = $("input[name='csrfmiddlewaretoken']").val();

        $.ajax({
           url: $("#removeAddressUrl").val(),
           type: "POST",
           data: {
              "address_id": addressId,
           },
           headers: {
              "X-CSRFToken": csrfToken,
           },
           success: function (response) {
              if (response.success === true) {
                 box.fadeOut(600, function () {
                    $(this).remove();
                 });
              }
              else {
                 alert("Something went wrong! Please try again.");
              }
           },
           error: function () {
              alert("Something went wrong! Please try again.");
           },
           complete: function () {
              delBtn.prop("disabled", false);  //enable delete btn.
           }
        });
      });
   }


   // send address
   function send_address () {
      $("#add-address-form").submit(function (event) {
         event.preventDefault();  // Prevent the default form submission.
         let submitBtn = $("#submit-btn");
         submitBtn.prop("disabled", true);  // disable submit btn.
         let data = $(this).serialize();  // Collect form data.
         let csrfToken = $("input[name='csrfmiddlewaretoken']").val();

         $.ajax({
            type: "POST",
            url: window.location.pathname,
            data: data,
            headers: {"X-CSRFToken": csrfToken},
            success: function (response) {
               $('#add-address-block').find("div.alert-danger").remove();  // remove previous errors.
               if (response.error) {
                  for (let key in response.error_s) {
                     $("#add-address-form").before('<div class="alert alert-danger">'+ response.error_s[key] +'</div>');
                  }
               }
               else {
                  // address display box html code.
                  let newAddressBox = '<div data-address-id="' + response.id + '" class="bg-light p-30 mb-4 address-box" name="address-box">' +
                      '<h5 class="section-title position-relative text-uppercase mb-3">' +
                      '<span class="bg-secondary pr-3">Your Address</span>' +
                      '</h5>' +
                      '<div class="d-flex align-items-start mb-3">' +
                      '<i class="fa fa-map-marker-alt text-primary mr-3 mt-1"></i>' +
                      '<div>' +
                      '<h6 class="font-weight-semi-bold mb-1">Address</h6>' +
                      '<p class="mb-0 address-text">' + response.province + ', ' + response.city + ', ' + response.addr + '</p>' +
                      '</div>' +
                      '</div>' +
                      '<div class="d-flex align-items-start mb-3">' +
                      '<i class="fa fa-mail-bulk text-primary mr-3 mt-1"></i>' +
                      '<div>' +
                      '<h6 class="font-weight-semi-bold mb-1">Postal Code</h6>' +
                      '<p class="mb-0 zip-text">' + response.zipcode + '</p>' +
                      '</div>' +
                      '</div>' +
                      '<div class="d-flex">' +
                      '<button class="btn btn-sm btn-primary mr-2 edit-btn"><i class="fa fa-edit mr-1"></i>Edit</button>' +
                      '<button class="btn btn-sm btn-danger delete-btn"><i class="fa fa-trash-alt mr-1"></i>Delete' +
                      '</button>' +
                      '</div>' +
                      '</div>';

                  // Last address display box.
                  let box = $('[name="address-box"]');
                  if (box.length > 0) {
                     box.last().after(newAddressBox);
                  } else {
                     $("#address-boxes").append(newAddressBox);
                  }
                  $("#id_address").val("");
                  $("#id_zipcode").val("");
               }
            },
            error: function (response) {
               alert("Something went wrong! Please try again.");
            },
            complete: function () {
               submitBtn.prop("disabled", false);  // enable submit btn.
            }
         });
      });
   }


   // edit address
   function edit_address () {
      // open form for edit address
      $("#address-boxes").off('click', '.edit-btn').on('click', '.edit-btn', function (){
         $("#edit-address-form div.alert-danger").remove();  // remove previous errors.
         // select address box.
         // let addressBox = $(this).closest('[name="address-box"]');
         let addressBox = $(this).closest('div.address-box');
         // assign part of address
         let addressText = addressBox.find("p.address-text").text();
         let postalCode = addressBox.find("p.zip-text").text();
         let addressParts = addressText.split(", ");
         let province = addressParts[0];
         let city = addressParts[1];
         let provinceSelect = $(".edit-province");

         // insert part of address to edit form
         $("#address_id").val(addressBox.data('address-id'));
         $('.edit-province option').filter(function(){return $(this).text() === province;}).prop('selected', true);
         send_load_city_request(provinceSelect, $(".edit-city"), city);
         $(".edit-address").val(addressParts.slice(2).join(", ").trim());
         $(".edit-zipcode").val(postalCode);

         // show edit form
         $('#overlay').fadeIn();
         $('#edit-address-form').show().fadeIn();
      });

      // close from with click close bottom
      $("#close-btn").off('click').on('click', function () {
         $('#overlay').fadeOut();
         $('#edit-address-form').hide().fadeOut();
      });

      // close form with click on overlay
      $('#overlay').off('click').on('click', function () {
         $('#overlay').fadeOut();
         $('#edit-address-form').hide().fadeOut();
      });

      // lode cities with select province in edit form
      load_cities($(".edit-province"), $(".edit-city"));

      // send data to edit address
      $("#submit-edit-btn").off('click').on("click", function (event) {
         $("#edit-address-form div.alert-danger").remove();  // remove previous errors.
         let editBtn = $(this);
         editBtn.prop("disabled", true);  // disable submit form btn.
         event.preventDefault();  // Prevent the default form submission.
         let formData = $("#edit-address").serialize();

         $.ajax({
            type: "POST",
            url: $("#editAddressUrl").val(),
            dataType: "JSON",
            data: formData,
            headers: {"X-CSRFToken": $("input[name='csrfmiddlewaretoken']").val()},
            success: function (response) {
               if (response.error) {
                  for (let key in response.error_s) {
                     // alert(response.error_s[key]);
                     $("#edit-address-form").find("h5.section-title").after('<div class="alert alert-danger">'+ response.error_s[key] +'</div>');
                  }
               }
               else {
                  let addressBox = $('[data-address-id="' + response.address_id + '"]');
                  addressBox.find("p.mb-0").first().text(response.province + ', ' + response.city + ', ' + response.addr);
                  addressBox.find("p.mb-0").last().text(response.zipcode);
                  $('#overlay').fadeOut();
                  $('#edit-address-form').hide().fadeOut();
               }
            },
            error: function () {
               alert("Something went wrong! Please try again.");
            },
            complete: function () {
               editBtn.prop("disabled", false);  // enable submit form btn.
            }
         });
      });
   }


   // Calling Functions

   // calling load_cities function
   load_cities($("#id_province"), $("#id_city"));

   // calling remove_address function
   remove_address();

   // calling send_address function.
   send_address();

   // calling address_edit function.
   edit_address();

});
