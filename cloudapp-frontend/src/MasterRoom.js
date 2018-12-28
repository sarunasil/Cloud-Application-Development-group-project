import React, {Component} from 'react';
import SpotifyWebApi from 'spotify-web-api-node';
import './App.css';
import {Route, Switch, Link} from 'react-router-dom'
import SplitterLayout from 'react-splitter-layout';
import searchYouTube from 'youtube-api-search';
import SpotifyPlayer from 'react-spotify-player';
import YouTube from 'react-youtube';
import { Button, ListGroup, ListGroupItem } from 'react-bootstrap';


var scopes = ['user-modify-playback-state', 'user-read-currently-playing', 'app-remote-control', 'streaming', 'user-read-playback-state'],
    clientId = '1811c9058bad498b8d829cd37564fdc6', //my own code, will prbs be changed
    //can be used for security, CSRF shit
    state = 'some-state-of-my-choice';

var spotifyApi = new SpotifyWebApi({
    clientId: clientId
});


const size = {
    width: '100%',
    height: '390',
};
const view = 'list'; // or 'coverart'
const theme = 'black'; // or 'white'
const youtubeOptions = {
    height: '390',
    width: '100%',
    playerVars: { // https://developers.google.com/youtube/player_parameters
        autoplay: 1
    }
};

class MasterRoom extends Component {
    constructor(props) {
        super(props);
        this.state = {
            roomId : "123newRoom",
            title : "Current room",
            spotifyAppToken : "",
            spotifyAccessToken: "",
            youtubeAppToken: "",
            queue: [],
            currentlyPlaying : false,
            currentSong: {
                name : "",
                link : "",
                time : "",
                type : "",
                votes: "0"

            },
            songsPlayed: 0,
            test: "",
            searchResults: [],
            value: ""
        };

        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
        let timerId = setInterval(() => this.updateStateForServer('tick'), 2000);
        //TODO: will become our domain name
        spotifyApi.setRedirectURI('http://localhost:3000/callback');

    }

    componentDidMount(){
        //TODO: use roomId to retrieve data : queue, search/access token for spotify/YT
    }

    addSpotify = () => {
        // Create the authorization URL
        var authorizeURL = spotifyApi.createAuthorizeURL(scopes, state);

        //set cookie with the room ID to be used in the callback component
        this.props.cookies.set('roomId', this.props.match.params.id, { path: '/', maxAge: 120 });
        window.location = authorizeURL;
    }

    updateStateForServer() {
        // this function periodically updates the queue from the server
        // the server should send be a json like
        // we could only send the changes and, from time to time, send the full state, but for now we should keep this simple
        var newState = {
            title : "Current room",
            spotifyAppToken : "",
            spotifyAccessToken: "",
            youtubeAppToken: "AIzaSyCIoanDddBkwWAVQRmFl62ZmVwQ184Ggls",
            queue: [
                {
                    name : "Song 1",
                    link : "spotify:track:2SL6oP2YAEQbqsrkOzRGO4",
                    time: "150", // time in seconds
                    votes: "0"
                },
                {
                    name : "Song 2",
                    link : "2g811Eo7K8U",
                    time: "150", // time in seconds
                    votes: "0"
                }
            ]
        }

        //newState = API.get(this.roomId, emptyBody)
        for(cnt = 0; cnt < newState.queue.length; cnt++){
            if(this.isSpotifySong(newState.queue[cnt].link)){
                newState.queue[cnt].type = "s";
            }else{
                newState.queue[cnt].type = "y";
            }
        }
        this.setState(newState);
        var cnt;

        // if user is master
        if(this.state.currentlyPlaying == false){
            this.playNextSong();
        }
    }

    isSpotifySong(songLink){
        return songLink.startsWith("spotify:");
    }

    //check if the queue contains a playable song and then
    playNextSong() {
        if (this.state.queue === undefined || this.state.queue.length == 0) {
            this.setState({currentlyPlaying: false});
        } else {
            var possibleSong;
            for(possibleSong = 0; possibleSong < this.state.queue.length; possibleSong++){
                if(this.state.queue[possibleSong].type === "s" ){
                    if( this.state.spotifyAccessToken === ""){
                        //skip song
                    }else{
                        break;
                    }
                }else{
                    break;
                }
            }
            if(possibleSong < this.state.queue.length) {
                this.playSong(possibleSong);
            }
        }
    }

    playSong(songNumberInQueue){
        this.setState({currentlyPlaying: true});
        this.setState({currentSong: this.state.queue[songNumberInQueue]});
        this.setState({songsPlayed: this.state.songsPlayed+1});
        this.removeSong(songNumberInQueue);
    }

    removeSong(songNumberInQueue){
        this.state.queue.splice(songNumberInQueue, 1);
        // Now we have to remove the song from the queue from the server
        // API.delete("/id/songLink", body should contain the position of the song = songNumberInQueue)
    }

    _onEnd = async event => {
        this.playNextSong();
    }

    handleChange(event) {
        this.setState({value: event.target.value});
    }

    handleSubmit(event) {
        event.preventDefault();
        var ytResults;
        searchYouTube({key: this.state.youtubeAppToken, term: this.state.value, maxResults: 6}, (videos) => {
            console.log("asdasdasdasd")
            console.log(videos);
            var cnt = 0;
            var newEntryList = [];
            for(cnt = 0; cnt < videos.length; cnt++){
                var newEntry =
                    {
                        link: "",
                        name: ""
                    };
                newEntry.link = videos[cnt].id.videoId;
                newEntry.name = videos[cnt].snippet.title;
                newEntryList.push(newEntry);
            }
            console.log(newEntryList);
            this.setState({searchResults: newEntryList});
        });
        // add after spotify search
    }

    addSongToQueue(position) {
        var currentSong = {
            name : this.state.searchResults[position].name,
            link : this.state.searchResults[position].link,
            votes : 0,
            time : "100"
        }
        var newQueue = this.state.queue;
        newQueue.push(currentSong);
        this.setState({newQueue: this.state.queue});
        // API call to add the song to queue,
    }

    render() {
        return (
            <div >
                <SplitterLayout>
                    <div>
                        <h1>THis is master room</h1>
                        <Button onClick={this.addSpotify}>Add Spotify</Button>
                        {this.renderPlayer()}
                        <form onSubmit={this.handleSubmit}>
                            <label>
                                Song name:
                                <input type="text" value={this.state.value} onChange={this.handleChange} />
                            </label>
                            <input type="submit" value="Submit" />
                        </form>

                        <ListGroup>
                            {this.renderSearch()}
                        </ListGroup>
                    </div>

                    <div>
                        {this.renderSongs()}
                    </div>
                </SplitterLayout>

            </div>
        );
    }


    renderSearch(){
        var searchResults = this.state.searchResults;
        return searchResults.map(
            (song, i) =>
                <ListGroupItem key = {i}>
                    { !song.link.startsWith('spotify:') &&
                    <img src={require('./youtubeLogo.png')} width="50" height="50"/>
                    }
                    {  song.link.startsWith('spotify:') &&
                    <img src={require('./spotifyLogo.png')} width="50" height="50"/>
                    }
                    <Button bsStyle="primary" onClick={() => this.addSongToQueue(i)}>
                        Add to queue
                    </Button>
                    {song.name}
                </ListGroupItem>
        );}

    // the songs played part ensures that the player gets refreshed at the end of a song
    renderPlayer(){
        return(
            <div>
                { this.state.currentSong.type === "s" && this.state.songsPlayed % 2 === 1 &&
                <SpotifyPlayer
                    uri= {this.state.currentSong.link}
                    allow="encrypted-media"
                    size={size}
                    view={view}
                    theme={theme}
                />
                }
                { this.state.currentSong.type === "s" && this.state.songsPlayed %2 === 0 &&
                <SpotifyPlayer
                    uri= {this.state.currentSong.link}
                    allow="encrypted-media"
                    size={size}
                    view={view}
                    theme={theme}
                />
                }
                {this.state.currentSong.type === "y" &&  this.state.songsPlayed %2 === 0 &&
                <YouTube
                    videoId= {this.state.currentSong.link}
                    opts={youtubeOptions}
                    onEnd={this._onEnd}
                />

                }
                {this.state.currentSong.type === "y" && this.state.songsPlayed %2 === 1 &&
                <YouTube
                    videoId= {this.state.currentSong.link}
                    opts={youtubeOptions}
                    onEnd={this._onEnd}

                />
                }
            </div>
        );
    }

    renderSongs(){
        return(
            <div className = "songs">
                <ListGroup>
                    {this.renderSongList()}
                </ListGroup>
            </div>
        );
    }

    renderSongList(){
        var currentSongsInQueue = this.state.queue;
        return currentSongsInQueue.map(
            (song, i) =>
                <ListGroupItem key = {i}>
                    { !song.link.startsWith('spotify:') &&
                    <img src={require('./youtubeLogo.png')} width="50" height="50"/>
                    }
                    {  song.link.startsWith('spotify:') &&
                    <img src={require('./spotifyLogo.png')} width="50" height="50"/>
                    }
                    <Button bsStyle="primary" onClick={() => this.playSong(i)}>
                        Play
                    </Button>
                    {song.name}
                    <span> </span> Votes: {song.votes}
                    <Button bsStyle="primary" onClick={() => this.removeSong(i)}>
                        Remove
                    </Button>
                </ListGroupItem>
        );}

}


export default MasterRoom;