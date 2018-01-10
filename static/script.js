console.log("script loaded");

$(document).ready(function(){
	$('#hostLogin').on('click', function(){
		console.log("login pressed");
		$.get("/nonStatic/hostLogin", function(data){
			window.location = data.url;
		});
	});
	$('#guestLogin').on('click', function(){
		console.log("guest has attempted login");
		window.location = "/codeVerification.html";
	});
});