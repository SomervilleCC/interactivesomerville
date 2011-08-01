$(document).ready(function(){
	// post commentForm
	$("#commentForm").submit(function() {
		// serialize comment form
		var commentData = $("#commentForm").serialize();
		// comment content
		var commentTxt = $("#id_comment").val();
		$.ajax({
			type: "POST",
			url: "/comments/post/",
			data: commentData,
			success: function(msg){
				$("ul.comments").append("<li><span class='title'>You</span>: " + commentTxt + "<div class='meta'>Posted now</div></li>");
				if ($("h3.comments").length === 0) { 
					// insert the header in case of first comment
					$("ul.comments").before("<h3 class='comments'>Discussion</h3>");
				}
				// empty textarea
				$("#id_comment").val("");
			}
		}).responseText;
		// don't really POST
		return false;
	});
});