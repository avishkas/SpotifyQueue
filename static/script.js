console.log("script loaded");

$(document).ready(function(){
	$('#login').on('click', function(){
		console.log("login pressed");
		$.post("/hostLogin", function(data){
			console.log("hostlogin called");
		});
	})
});