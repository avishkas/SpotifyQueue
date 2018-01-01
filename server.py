from flask import Flask, current_app, request, redirect, render_template
import json
import urllib
import requests
import dbManager
app = Flask(__name__)

clientID = ""
clientSecret = ""
clientCodeRelations = {}

@app.route('/')
def homepage():
	return current_app.send_static_file('index.html')

@app.route('/hostLogin')
def hostLogin():
	#redirects user to login page
	query = {'client_id' : clientID, 'response_type' : 'code','redirect_uri' : 'http://localhost:5000/afterLogin', 'scope' : 'playlist-modify-public'}
	call = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode(query)
	return redirect(call, code=302)

@app.route('/afterLogin')
def afterLogin():
	#called after user has entered credintials
	
	#get acess token using code generated by user login
	code = request.args.get('code')
	params = {'grant_type' : 'authorization_code', 'code' : code, 'redirect_uri' : 'http://localhost:5000/afterLogin', 'client_id': clientID, 'client_secret' : clientSecret}
	resp = requests.post('https://accounts.spotify.com/api/token', params)

	if code == None:
		return "We need you to login sorry!"

	#use access token to access Spotify API

	responseData = resp.json()
	accessToken = responseData['access_token']
	headerVal = responseData['token_type'] + " " + accessToken
	headers = {'Authorization' : headerVal}

	#get spotify id of user
	userIDResponse = requests.get('https://api.spotify.com/v1/me', headers=headers).json()
	print(userIDResponse)
	userName = userIDResponse['id']
	
	# resp2 = requests.get('https://api.spotify.com/v1/me/playlists', headers=headers)

	#first check if there is a spotify playlist called spotify queue

	#create playlist for current user
	playlistURI = 'https://api.spotify.com/v1/users/' + userName + '/playlists'
	headers = {'Authorization' : headerVal, 'Content-Type' : 'application/json'}
	params = {'name' : 'SPOTIFY_QUEUE', 'description' : 'Playlist to which Spotify Queue adds and removes songs'}
	playlistObj = requests.post(playlistURI, json.dumps(params), headers=headers).json() #playlist object to add and delete songs

	#add code and responseToken to database

	return render_template('./hostPage.html') #host page should eventually have the 'code' and songs in queue

@app.route('/client')
def clientLogin():
	return render_template('/guestLogin.html')

@app.route('/addSong/')
def addSong(value):
	#get code and song id
	code = request.args.get('code')
	songId = requst.args.get('songId')

	accessToken = dbManager.getValue('hosts.db', code)

	if(acesstoken == None):
		return "Client does not exist"

	#add song to playlist
	

@app.route('/client/<code>')
def clientLogin(code):
	#check if code exists in database
	if(dbManager.getValue('hosts.db', code) == none):
		return "incorrect code sorry"
	else:
		return render_template('guestPage.html')


@app.route('/script.js')
def returnScript():
	return current_app.send_static_file('script.js');

if __name__ == "__main__":
	app.run(debug=True)
