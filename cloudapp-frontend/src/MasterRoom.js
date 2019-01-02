//import 'bootstrap/dist/css/bootstrap.min.css';
import React, {Component} from 'react';
import SpotifyWebApi from 'spotify-web-api-node';
import './App.css';
import {Route, Switch, Link} from 'react-router-dom'
import SplitterLayout from 'react-splitter-layout';
import searchYouTube from 'youtube-api-search';
import SpotifyPlayer from 'react-spotify-player';
import YouTube from 'react-youtube';
import { Button, ListGroup, ListGroupItem } from 'react-bootstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';


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
    height: '500',
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
        if(this.props.cookies.get('accessToken')){
            spotifyApi.setAccessToken(this.props.cookies.get('accessToken'));
        }
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

    //search
    async handleSubmit(event) {
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

        if(this.props.cookies.get('accessToken')){
             console.log(this.props.cookies.get('accessToken'));
             console.log(spotifyApi.getAccessToken());
             var tracksCompleteResponse  = await spotifyApi.searchTracks(this.state.value, {limit: 6});
             var cnt;
             var tracks = [];
             console.log(tracksCompleteResponse);
             console.log(tracksCompleteResponse.body.tracks);
             for(cnt=0; cnt < tracksCompleteResponse.body.tracks.items.length; cnt++){
                var track = tracksCompleteResponse.body.tracks.items[cnt];
                 var newTrack = {
                     name: "",
                     link: "",
                     time: 0,
                 }
                 newTrack.name  = track.name;
                 newTrack.link = track.uri;
                 newTrack.time = track.duration_ms;
                 tracks.push(newTrack);
             }

            this.setState({
                searchResults: tracks.concat(this.state.searchResults)
            });
             console.log(this.state.searchResults);
        }
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

            <div className="container-fluid">
                <div className="row">
                    <div className="col">
                        <nav className="navbar navbar-dark bg-dark justify-content-between">
                            <a className="navbar-brand" style={{color:"white"}}>This is master</a>
                            <form className="form-inline" onSubmit={this.handleSubmit}>
                                <input className="form-control mr-sm-2" type="search" placeholder="Look up song"
                                       aria-label="Search" value={this.state.value} onChange={this.handleChange} style={{ width:"300px" }}></input>
                                <button className="btn btn-outline-success my-2 my-sm-0" type="submit"><FontAwesomeIcon icon="search"/>
                                </button>
                                <span> &nbsp;</span>
                                <div className="float-right"><button type="button" className="btn btn-success"  onClick={this.addSpotify}>Add<br/>
                                    Spotify</button></div>
                            </form>
                        </nav>
                    </div>
                </div>
                <div className="row">
                    <div className="col">{this.renderPlayer()}</div>
                </div>
                <div className="row">
                    <div className="col-4">{this.renderSongs()}</div>
                    <div className="col-8">
                        <ul className="list-group" style={{align:"left"}}>
                        {this.renderSearch()}
                        </ul>
                    </div>
                </div>
            </div>

        );
    }


    renderSearch(){
        var searchResults = this.state.searchResults;
        return searchResults.map(
            (song, i) =>



                    <li style={{border:"0"}} className="list-group-item" key = {i}  >


                        { !song.link.startsWith('spotify:') &&
                    <img src={require('./youtubeLogo.png')} width="50" height="40"/>
                    }
                        {  song.link.startsWith('spotify:') &&
                        <img src={require('./spotifyLogo.png')} width="40" height="40"/>
                        }
                        <span> </span>
                        {song.name}
                        <span> </span>
                        <button type="button" className="btn btn-success" onClick={() => this.addSongToQueue(i)}><FontAwesomeIcon icon="plus-square"/></button>
                        </li>


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
                <li className="list-group-item" key = {i} style={{border:"0"}}>
                    { !song.link.startsWith('spotify:') &&
                    <img src={require('./youtubeLogo.png')} width="50" height="40"/>
                    }
                    {  song.link.startsWith('spotify:') &&
                    <img src={require('./spotifyLogo.png')} width="40" height="40"/>
                    }
                    <span> </span>
                    {song.name}
                    <span> </span> Votes: {song.votes}
                    <span> </span>
                    <button type="button" className="btn btn-success" onClick={() => this.playSong(i)}> <FontAwesomeIcon icon="play-circle"/></button>
                    <span> </span>
                    <button type="button" className="btn btn-danger" onClick={() => this.removeSong(i)}><FontAwesomeIcon icon="trash-alt"/></button>

                </li>
        );}

}


export default MasterRoom;