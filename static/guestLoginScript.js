var code = 0;

$(document).ready(function(){
	$('#login').on('click', function(){
		var input = $('#codeContainer').val();
		if(input.length == 4){
			//send code to server
			$.get("/nonStatic/guestLogin/", {code:input}, function(data){
				console.log(data)
				if(data == 'Code_Not_Found'){
					//display code not found message on screen
					$('#codeNotFoundIndicator').html('Code Not Found');
				}else{
					//
					code = input;
					$('#codeInput').remove();
					$('#playlistElements').show();
				}
			});
		}else{
			$('#codeNotFoundIndicator').html('Incorrect Code Length')
		}
	});

	$('#executeQuery').on('click', function(){
		if($('#searchQueryInput').val()){
			//send get request to server to retrieve query results
			var typeSelected = $('#serachQuerySelector').val();
			var input = $('#searchQueryInput.').val();
			$.get('/nonStatic/getQueryResults', {})			
		}else{
			$('#searchQueryInput').attr("placeholder", "please entery query");
		}
	});
});