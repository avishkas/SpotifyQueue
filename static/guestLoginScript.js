var code = "0";

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
		if(code == "0"){
			return;
		}
		if($('#searchQueryInput').val()){
			//send get request to server to retrieve query results
			var typeSelected = $('#searchQuerySelector').val();
			var input = $('#searchQueryInput').val();
			$.get('/nonStatic/getQueryResults', {"q":input, "type":typeSelected, "offset":0, "code":code}, function(data){
				console.log(data);

				$('.currentSearch').remove();

				for(var spotifyTrackID in data){
					//filter out meta-information
					if(data.hasOwnProperty(spotifyTrackID)){
						var songName = data[spotifyTrackID].name;
						//concatinate artist names
						var artistList = data[spotifyTrackID].artists;
						var artistName = data[spotifyTrackID]['artists'][0]['name'];

						for(var i = 1; i < artistList.length; i++){
							artistName += ", "+ data[spotifyTrackID]['artists'][i]['name'];
						}
						//append songs to table
						$('#queriedSongs tr:last').after(`<tr class="currentSearch">
							<td><input class="form-check-input currentSearch" type="checkbox" value="${spotifyTrackID}" id="${spotifyTrackID}"></td>
							<td class="currentSearch">${songName}</td>
							<td class="currentSearch">${artistName}</td>
							</tr>`);
					}
				}
			});

		}else{
			$('#searchQueryInput').attr("placeholder", "please entery query");
		}
	});
	$('#addSelectedSongs').on('click', function(){
		console.log('being called');
		//assemble list of selected spotify track ids
		selectedTrackIDs = [];
		$('input[type=checkbox]:checked').each(function(){
			selectedTrackIDs.push($(this).val());
		});
		console.log(selectedTrackIDs);

		$.post('/nonStatic/addToPlaylist', JSON.stringify({"code":code, "trackIDs":selectedTrackIDs}), function(data){});

		//call server and send data
	});
});