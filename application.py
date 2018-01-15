from flask import Flask, current_app, request, redirect, render_template, make_response, jsonify
import random, string
import json
import urllib
import requests
import dbManager
app = Flask(__name__)

clientID = "e30c552da1264f94a0414906a89b6eb8"
clientSecret = "b12914ccec2449258eb4e5f23f7e3e67"
clientCodeRelations = {}

#on start create database if it doesn't already exist
dbManager.createTable("User_Table.db")

baseDNS = "http://ec2-18-218-7-55.us-east-2.compute.amazonaws.com"


@app.route('/nonStatic/hostLogin', methods=['GET', 'POST'])
def hostLogin():
	#redirects user to login page
	query = {'response_type':'code', 'client_id':clientID, 'scope':'playlist-modify-public', 'redirect_uri':baseDNS+'/nonStatic/afterLogin'}
	call = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode(query)

	authenticationURL = {'url' : call}

	return jsonify(authenticationURL)


@app.route('/nonStatic/afterLogin')
def afterLogin():
	print('working')
	#called after user has entered credintials
	 
	#get acess token using code generated by user login
	code = request.args.get('code')
	if code == None:
		return "We need you to login sorry!"

	params = {'grant_type' : 'authorization_code', 'code' : code, 'redirect_uri' :baseDNS+'/nonStatic/afterLogin', 'client_id': clientID, 'client_secret' : clientSecret}
	resp = requests.post('https://accounts.spotify.com/api/token', params)

	

	#use code to retrieve access token

	responseData = resp.json()
	accessToken = responseData['access_token']

	#use access token to retrieve spotify user ID
	#set header first
	headerVal = responseData['token_type'] + " " + accessToken
	headers = {'Authorization' : headerVal}
	userIDResponse = requests.get('https://api.spotify.com/v1/me', headers=headers).json() #retrieve ID

	userID = userIDResponse['id']
	
	# resp2 = requests.get('https://api.spotify.com/v1/me/playlists', headers=headers)

	#first check if there is a spotify playlist called spotify queue

	#create playlist for current user if playlist doesn't already exist
	playlistURI = 'https://api.spotify.com/v1/users/' + userID + '/playlists'
	headers = {'Authorization' : headerVal, 'Content-Type' : 'application/json'}
	params = {'name' : 'SPOTIFY_QUEUE', 'description' : 'Playlist to which Spotify Queue adds and removes songs'}
	playlistObj = requests.post(playlistURI, json.dumps(params), headers=headers).json() #playlist object to add and delete songs

	#generate code, check if it exists in the table
	userAssociatedCode = ''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(4))
	#keep refreshing code until a unique is found
	while(dbManager.codeIsDuplicate('User_Table.db', userAssociatedCode) == True):
		userAssociatedCode = ''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(4))

	#add code, accessToken, userID, and playlistID to database
	dbManager.addClient('User_Table.db', userAssociatedCode, accessToken, userID, playlistObj['id'])

	return render_template('./hostPage.html', code=userAssociatedCode) #host page should eventually have the 'code' and songs in queue

@app.route('/addSong/')
def addSong(value):
	#get code and song id
	code = request.args.get('code')
	songId = requst.args.get('songId')

	accessToken = dbManager.getValue('hosts.db', code)

	if(acesstoken == None):
		return "Client does not exist"

	#add song to playlist
	

@app.route('/nonStatic/guestLogin/')
def guestLogin():
	#check if code exists in database
	
	code = request.args.get('code').upper()
	print("code:", code)
	if(dbManager.codeIsDuplicate('User_Table.db', code) == True):
		print('code found')
		#redirect to page with list of songs in playlist

		#get the playlist
		#accessToken, code, userID, playlistID
		hostData = dbManager.getData('User_Table.db', code)
		playlistID = hostData[3]
		accessToken = hostData[0]
		userID = hostData[2]

		print("playlistID:", playlistID, "accessToken:", accessToken, "userID:", userID)
		#make request to spotify api to get playlist object
		print("making request")
		headers = {'Authorization' : 'Bearer ' + accessToken}
		playlistResponse = requests.get('https://api.spotify.com/v1/users/'+userID+'/playlists/'+playlistID+'/tracks', headers=headers).json()
		print(json.dumps(playlistResponse, indent=4))

		#return a list of songs and their artists
		songArtistsList = {}

		for songs in playlistResponse['items']:
			songName = songs['track']['name']
			artists = songs['track']['artists']
			songArtistsList[songName] = artists

			print(songArtistsList)

		return jsonify(songArtistsList)

	return "Code_Not_Found"

@app.route('/nonStatic/getQueryResults')
def getQueryResults():
	parameters = request.args
	query = parameters.get('q')

	queryType = parameters.get('type')
	queryOffset = parameters.get('offset')
	code = parameters.get('code').upper()
	print(code)
	userAccessToken = dbManager.getData('User_Table.db', code)[0]
	print(userAccessToken)


	params = {"q": query, "type": queryType, "offset": queryOffset}
	headers = {'Authorization' : 'Bearer ' + userAccessToken}
	trackQuery = requests.get('https://api.spotify.com/v1/search', params, headers=headers).json()
	print(trackQuery.items)

	songSet = {}

	for trackObject in trackQuery['tracks']['items']:
		songSet[trackObject['id']] = {'name': trackObject['name'], 'artists': trackObject['artists']}

	return jsonify(songSet)

@app.route('/nonStatic/addToPlaylist', methods=['POST'])
def addToPlaylist():
	
	parameters = request.get_json(force=True)
	code = parameters['code'].upper()

	spotifyTrackIDs = []
	for trackID in parameters['trackIDs']:
		spotifyTrackIDs.append("spotify:track:"+trackID)

	params = {"uris":spotifyTrackIDs}
	
	hostData = dbManager.getData('User_Table.db', code)
	hostSpotifyID = hostData[2]
	hostPlaylistID = hostData[3]
	hostAccessToken = hostData[0]

	print(params)

	headers = {'Authorization' : 'Bearer ' + hostAccessToken, 'Content-Type':'application/json'}
	queryStringData = requests.post('https://api.spotify.com/v1/users/'+hostSpotifyID+"/playlists/"+hostPlaylistID+"/tracks", json.dumps(params), headers=headers)
	print(queryStringData.url)
	print(queryStringData.content)

	return json.dumps({'success':True}, 200, {'ContentType':'application/json'})


if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0', port=5500)
