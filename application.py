from flask import Flask, current_app, request, redirect, render_template, make_response, jsonify
import random, string
import json
import urllib
import requests
import dbManager
app = Flask(__name__)

clientID = ""
clientSecret = ""
clientCodeRelations = {}

#on start create database if it doesn't already exist
dbManager.createTable("User_Table.db")

#baseDNS = "http://localhost:5500"
baseDNS = "http://ec2-18-218-7-55.us-east-2.compute.amazonaws.com"


#redirects user to login page
@app.route('/nonStatic/hostLogin', methods=['GET', 'POST'])
def hostLogin():
	query = {'response_type':'code', 'client_id':clientID, 'scope':'playlist-modify-public', 'redirect_uri':baseDNS+'/nonStatic/afterLogin'}
	call = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode(query)

	authenticationURL = {'url' : call}

	return jsonify(authenticationURL)

#called after user has entered credintials
@app.route('/nonStatic/afterLogin')
def afterLogin():
	 
	#get access token using code generated by user login
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

	#first check if there is a spotify playlist called spotify queue
	headers = {'Authorization' : 'Bearer ' + accessToken}
	response = requests.get('https://api.spotify.com/v1/users/' + userID + '/playlists', headers=headers).json()
	userPlaylists = response['items']
	playlistID = ''

	for playlist in userPlaylists:
		if playlist['name'] == 'SPOTIFY_QUEUE':
			playlistID = playlist['id']
			break

	#create playlist for current user if playlist doesn't already exist
	if(playlistID == ''):
		playlistURI = 'https://api.spotify.com/v1/users/' + userID + '/playlists'
		headers = {'Authorization' : headerVal, 'Content-Type' : 'application/json'}
		params = {'name' : 'SPOTIFY_QUEUE', 'description' : 'Playlist to which Spotify Queue adds and removes songs'}
		playlistObj = requests.post(playlistURI, json.dumps(params), headers=headers).json() #playlist object to add and delete songs
		playlistID = playlistObj['id']

	#generate code, check if it exists in the table
	userAssociatedCode = ''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(4))
	#keep refreshing code until a unique is found
	while(dbManager.codeIsDuplicate('User_Table.db', userAssociatedCode) == True):
		userAssociatedCode = ''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(4))

	#add code, accessToken, userID, and playlistID to database
	dbManager.addClient('User_Table.db', userAssociatedCode, accessToken, userID, playlistID)

	return render_template('./hostPage.html', code=userAssociatedCode) #host page should eventually have the 'code' and songs in queue
	
#endpoint called when guest enters code
@app.route('/nonStatic/guestLogin/')
def guestLogin():
	#retrieve code
	code = request.args.get('code').upper()
	#check if the code exists in the database
	if(dbManager.codeIsDuplicate('User_Table.db', code) == True):
		#accessToken, code, userID, playlistID
		hostData = dbManager.getData('User_Table.db', code)
		playlistID = hostData[3]
		accessToken = hostData[0]
		userID = hostData[2]

		#make request to spotify api to get playlist object
		headers = {'Authorization' : 'Bearer ' + accessToken}
		playlistResponse = requests.get('https://api.spotify.com/v1/users/'+userID+'/playlists/'+playlistID+'/tracks', headers=headers).json()

		#return a list of songs and their artists
		songArtistsList = {}

		for songs in playlistResponse['items']:
			songName = songs['track']['name']
			artists = songs['track']['artists']
			songArtistsList[songName] = artists

		return jsonify(songArtistsList)

	#return error if no code found
	return "Code_Not_Found"

#queries spotify database for song searched by user
@app.route('/nonStatic/getQueryResults')
def getQueryResults():
	#get search input
	parameters = request.args
	query = parameters.get('q')

	queryType = parameters.get('type')
	queryOffset = parameters.get('offset')
	code = parameters.get('code').upper()
	userAccessToken = dbManager.getData('User_Table.db', code)[0]

	#setup headers and send search requrest to Spotify API
	params = {"q": query, "type": "track", "offset": queryOffset}
	headers = {'Authorization' : 'Bearer ' + userAccessToken}
	trackQuery = requests.get('https://api.spotify.com/v1/search', params, headers=headers).json()

	songSet = {}

	#parse returned JSon data into only array of tracks
	for trackObject in trackQuery['tracks']['items']:
		songSet[trackObject['id']] = {'name': trackObject['name'], 'artists': trackObject['artists']}

	return jsonify(songSet)

#add given song ID's to playlist
@app.route('/nonStatic/addToPlaylist', methods=['POST'])
def addToPlaylist():
	#get code
	parameters = request.get_json(force=True)
	code = parameters['code'].upper()

	#parse all trackID's from client input
	spotifyTrackIDs = []
	for trackID in parameters['trackIDs']:
		spotifyTrackIDs.append("spotify:track:"+trackID)

	params = {"uris":spotifyTrackIDs}
	
	#query required info from user_database
	hostData = dbManager.getData('User_Table.db', code)
	hostSpotifyID = hostData[2]
	hostPlaylistID = hostData[3]
	hostAccessToken = hostData[0]

	headers = {'Authorization' : 'Bearer ' + hostAccessToken, 'Content-Type':'application/json'}
	queryStringData = requests.post('https://api.spotify.com/v1/users/'+hostSpotifyID+"/playlists/"+hostPlaylistID+"/tracks", json.dumps(params), headers=headers)

	return json.dumps({'success':True}, 200, {'ContentType':'application/json'})


if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0', port=5500)
