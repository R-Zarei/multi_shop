$(document).ready(function () {

    let editingCommentId = null;

    // Sending comment and after resave reply adding new comment to the page.
    function sendComment() {
        $("#comment-form").submit(function (event) {
            event.preventDefault();  // Prevent default form submission
            let submitBtn = $("#send-comment-btn");
            submitBtn.prop("disabled", true);   // disabling submit button.
            let commentText = $("#comment-message-box");
            if (!commentText.val().trim()) {
                $('#alter-modal-title').text('Please enter the comment text!');
                // $('#alter-modal-text').text('Please enter the comment text!');
                $("#alert-modal").modal('show');
                submitBtn.prop('disabled', false);
                return;
            }
            let url = $(this).attr('action');
            let data = $(this).serialize();  // collect form data;
            if(editingCommentId !== null) {  // If editing comment.
                // $(`[data-comment-id="${editingCommentId}"]`).parent().siblings(".comment-text").text()
                url = editCommentUrl;
                data = {
                    'comment_id': editingCommentId,
                    'text': $("#comment-message-box").val(),
                };
            }

            $.ajax({
                type: 'POST',
                url: url,
                data: data,
                headers: {"X-CSRFToken": csrfToken},
                success: function (response) {
                    if (response.success) {
                        if (editingCommentId === null) {    // If adding comment.
                            let newCommentBox = `
                            <div class="media mb-4 comment-box">
                                <div class="media-body">
                                    <div class="d-flex justify-content-between align-items-start">
                                        <div>
                                            <h6 class="mb-0">
                                                <span style="color: #ffd333;">Your Comment</span>
                                                <small> - <i>${response.date}</i></small>
                                            </h6>
                                        </div>
                                        <div class="d-flex" data-comment-id="${response.id}">
                                            <!-- دکمه ادیت با کلاس custom-btn-warning -->
                                            <button class="edit-comment-btn btn custom-btn-warning btn-sm mr-2">
                                                <i class="fa fa-edit"></i> Edit
                                            </button>
                                            <!-- دکمه دیلیت با کلاس custom-btn-danger -->
                                            <button class="btn custom-btn-danger btn-sm delete-comment-btn"
                                                    data-toggle="modal" data-target="#deleteModal">
                                                <i class="fa fa-trash"></i> Delete
                                            </button>
                                        </div>
                                    </div>
                                    <p class="mt-2 comment-text">${response.text}</p>
                                </div>
                            </div>`;

                            let box = $(".comment-box");
                            if (box.length > 0) {
                                box.first().before(newCommentBox);
                            } else {
                                $("#start-comments").after(newCommentBox);
                            }
                            console.log('Comment Added!');
                            $("#reviews-count").text(`Reviews (${response.comment_count})`);
                            commentText.val('');
                        }else {    // If editing comment.
                            $(`[data-comment-id="${editingCommentId}"]`).parent().siblings(".comment-text").text(response.text);
                            $(`[data-comment-id="${editingCommentId}"]`).parent().find("h6 i").text(response.last_modified);
                            editingCommentId = null;
                            $("#comment-message-box").val('');
                            $("#send-comment-btn").val("Leave Your Review");
                            $("#cancel-edit-comment-btn").hide();
                        }
                    } else {
                        alert(`Comment not add!: ${response.error}`);
                    }
                },
                error: function (response) {
                    // alert(response.responseJSON.error);
                    $('#alter-modal-title').text(response.status);
                    $('#alter-modal-text').text(response.responseJSON.error);
                    $("#alert-modal").modal('show');
                },
                complete: function () {
                    submitBtn.prop("disabled", false);  // enable submit btn.
                }
            });
        });
    }


    function deleteComment() {
        let commentBox = null;
        let commentId = null;

        $(document).on('click', '.delete-comment-btn', function () {
            commentBox = $(this).closest(".comment-box");
            commentId = $(this).closest("[data-comment-id]").data("comment-id");
        });

        $(document).on('click', '#confirm-delete-btn', function () {
            $('#deleteModal').modal('hide');
            $.ajax({
                method: "POST",
                url: deleteCommentUrl,
                data: {'comment_id': commentId},
                headers: {'X-CSRFToken': csrfToken},
                success: function (response) {
                    if (response.success) {
                        // let commentId = response.id;
                        commentBox.remove();
                        console.log('Comment Deleted!');
                        $("#reviews-count").text(`Reviews (${response.comment_count})`);
                    } else {
                        alert(`Comment not deleted!: ${response.error}`);
                    }
                },
                error: function (response) {
                    // alert(response.responseJSON.error);
                    $('#alter-modal-title').text(response.status);
                    $('#alter-modal-text').text(response.responseJSON.error);
                    $("#alert-modal").modal('show');
                },
            });
        });
    }


        function editComment() {
            $(document).on('click', '.edit-comment-btn', function () {
                let commentText = $(this).closest(".comment-box").find(".comment-text").text().trim();
                editingCommentId = $(this).closest("[data-comment-id]").data("comment-id");
                $("#comment-message-box").val(commentText);
                $("#send-comment-btn").val("Edit Comment");
                $("#cancel-edit-comment-btn").show();
            });

            $("#cancel-edit-comment-btn").click(function() {
                editingCommentId = null;
                $("#comment-message-box").val('');
                $("#send-comment-btn").val("Leave Your Review");
                $("#cancel-edit-comment-btn").hide();
            });

        }



    sendComment();
    deleteComment();
    editComment();
});