from flask import Flask, current_app, request, redirect, render_template, make_response, jsonify
from random import choice
from string import ascii_uppercase, digits
import json
import urllib
import requests
import dbManager
app = Flask(__name__)

clientID = "e30c552da1264f94a0414906a89b6eb8"
clientSecret = "b12914ccec2449258eb4e5f23f7e3e67"
clientCodeRelations = {}


@app.route('/nonStatic/hostLogin', methods=['GET', 'POST'])
def hostLogin():
	#redirects user to login page
	query = {'response_type':'code', 'client_id':clientID, 'scope':'playlist-modify-public', 'redirect_uri':'http://localhost:80/nonStatic/afterLogin'}
	call = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode(query)

	authenticationURL = {'url' : call}

	return jsonify(authenticationURL)


@app.route('/nonStatic/afterLogin')
def afterLogin():
	print("afterlogin called")
	#called after user has entered credintials
	 
	#get acess token using code generated by user login
	code = request.args.get('code')
	params = {'grant_type' : 'authorization_code', 'code' : code, 'redirect_uri' : 'http://localhost:80/nonStatic/afterLogin', 'client_id': clientID, 'client_secret' : clientSecret}
	resp = requests.post('https://accounts.spotify.com/api/token', params)

	if code == None:
		return "We need you to login sorry!"

	#use code to retrieve access token

	responseData = resp.json()
	accessToken = responseData['access_token']

	#use access token to retrieve spotify user ID
	#set header first
	headerVal = responseData['token_type'] + " " + accessToken
	headers = {'Authorization' : headerVal}
	userIDResponse = requests.get('https://api.spotify.com/v1/me', headers=headers).json() #retrieve ID
	userName = userIDResponse['id']
	
	# resp2 = requests.get('https://api.spotify.com/v1/me/playlists', headers=headers)

	#first check if there is a spotify playlist called spotify queue

	#create playlist for current user if playlist doesn't already exist
	playlistURI = 'https://api.spotify.com/v1/users/' + userName + '/playlists'
	headers = {'Authorization' : headerVal, 'Content-Type' : 'application/json'}
	params = {'name' : 'SPOTIFY_QUEUE', 'description' : 'Playlist to which Spotify Queue adds and removes songs'}
	playlistObj = requests.post(playlistURI, json.dumps(params), headers=headers).json() #playlist object to add and delete songs

	#generate code
	userAssociatedCode = ''.join(choice(string.ascii_uppercase + string.digits) for i in range(4))
	print(userAssociatedCode)

	#add code, accessToken, and userName to database

	return render_template('./hostPage.html') #host page should eventually have the 'code' and songs in queue

@app.route('/guestLogin')
def guestLogin():
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


if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0', port=80)
