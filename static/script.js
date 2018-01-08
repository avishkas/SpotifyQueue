console.log("script loaded");

$(document).ready(function(){
	$('#login').on('click', function(){
		console.log("login pressed");
		$.get("/nonStatic/hostLogin", function(data){
			window.location = data.url;
		});
	})
});