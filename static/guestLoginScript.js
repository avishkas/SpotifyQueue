$(document).ready(function(){
	$('#login').on('click', function(){
		var input = $('#codeContainer').val();
		if(input.length == 4){
			//send code to server
			$.get("/nonStatic/guestLogin/", {code:input}, function(data){
				console.log(data)
				if(data == 'Code_Not_Found'){
					//display code not found message on screen
				}else{
					//update page to show current songs in playlist
				}
			});
		}else{
			console.log("The entered code is of incorrect length.")
		}
	});
});