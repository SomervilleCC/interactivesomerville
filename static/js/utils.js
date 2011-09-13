$(document).ready(function(){
	
	// Django CSRF AJAX helper (https://docs.djangoproject.com/en/dev/ref/contrib/csrf/#ajax)
	$('html').ajaxSend(function(event, xhr, settings) {
		function getCookie(name) {
			var cookieValue = null;
			if (document.cookie && document.cookie != '') {
				var cookies = document.cookie.split(';');
				for (var i = 0; i < cookies.length; i++) {
					var cookie = jQuery.trim(cookies[i]);
					// Does this cookie string begin with the name we want?
					if (cookie.substring(0, name.length + 1) == (name + '=')) {
						cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
						break;
					}
				}
			}
			return cookieValue;
		}
		if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
			// Only send the token to relative URLs i.e. locally.
			xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
		}
	});
	
	
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