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
			//display error message
			$('#codeNotFoundIndicator').html('Incorrect Code Length')
		}
	});

	$('#executeQuery').on('click', function(){
		if($('#searchQueryInput').val()){
			//send get request to server to retrieve query results
			var typeSelected = $('#serachQuerySelector').val();
			var input = $('#searchQueryInput.').val();
			$.get('/nonStatic/getQueryResults', {q:$('searchQueryInput').val(), type:$('serachQuerySelector').val(), offset:0}, function(data){
				for(var spotifyTrackID in data){
					//filter out meta-information
					if(data.hasOwnProperty(spotifyTrackID)){
						var songName = data.spotifyTrackID.songName;
						//concatinate artist names
						var artistName = data.spotifyTrackID.artistName[0];
						for(int i = 1; i < data.spotifyTrackID.artistName.length; i++){
							artistName += data.spotifyTrackID.artistName[i];
						}
						//append songs to table
						$('#queriedSongs').append(`<tr>
							<td><input class="form-check-input" type="checkbox" value="${spotifyTrackID}" id="${spotifyTrackID}"></td>
							<td>${songName}</td>
							<td>${artistName}</td>
							</tr>`);
					}
				}
			});

		}else{
			$('#searchQueryInput').attr("placeholder", "please entery query");
		}
	});
});