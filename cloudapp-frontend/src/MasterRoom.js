import 'bootstrap/dist/css/bootstrap.min.css';
import React, {Component} from 'react';
import SpotifyWebApi from 'spotify-web-api-node';
import './App.css';
import SpotifyPlayer from './SpotifyPlayer';
import YouTube from 'react-youtube';
import { Button, ListGroup, ListGroupItem } from 'react-bootstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import Search from './Search'

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
            query: '',
            queue: [],
            currentlyPlaying : false,
            currentSong: {
                name : "",
                link : "",
                time : "",
                type : "",
                votes: "0"

            },
            songsPlayed: 0
        };
        this.child = React.createRef();

        //let timerId = setInterval(() => this.updateStateForServer('tick'), 2000);

        //TODO: will become our domain name
        spotifyApi.setRedirectURI('http://localhost:3000/callback');

    }

    componentDidMount(){
        if(this.props.cookies.get('accessToken')){
            spotifyApi.setAccessToken(this.props.cookies.get('accessToken'));
        }
        //TODO: use roomId to retrieve data : queue, search/access token for spotify/YT
        this.updateStateForServer();
        spotifyApi.setAccessToken('BQC3TnftTzQiz7xgoYPC4rSj6juA8hTk7SRiG8BmXA9o8XQhOjNRzmkaq8bjJPc2rYLtTJZMStRfIyOH00Q-J8hY79SkB2Q4coMS851MHCTnpt0ShiwvZFcsO4GiXHm5c0nPIIXgyJ51J5XF3YJ3Z97CFNQow6eviIpCtK3CcF_ChNIg5YCIK0PrkVHB')
    }

    addSpotify = () => {
        // Create the authorization URL
        var authorizeURL = spotifyApi.createAuthorizeURL(scopes, state);

        //set cookie with the room ID to be used in the callback component
        this.props.cookies.set('roomId', this.props.match.params.id, { path: '/', maxAge: 120 });
        window.location = authorizeURL;
    }

    async updateStateForServer() {
        // this function periodically updates the queue from the server
        // the server should send be a json like
        // we could only send the changes and, from time to time, send the full state, but for now we should keep this simple
        var newState = {
            queue: [
                // {
                //     name : "Song 1",
                //     link : "spotify:track:2SL6oP2YAEQbqsrkOzRGO4",
                //     time: "150", // time in seconds
                //     votes: "0"
                // },
                {
                    name : "Song 2",
                    link : "2g811Eo7K8U",
                    time: "150", // time in seconds
                    votes: "0"
                },

                {
                    name : "Song 3",
                    link : "spotify:track:47YfeZOuxkGsiFwY97ubRQ",
                    time: "150", // time in seconds
                    votes: "0"
                },
                {
                    name : "Song 4",
                    link : "3KL9mRus19o",
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
        await this.setState(newState);
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
        if(this.state.queue[0]) {
            this.playSong(0);
        }
        else {
            this.setState({currentlyPlaying: false});
        }
    }

    playSong(songNumberInQueue){
        this.setState({currentlyPlaying: true});
        this.setState({currentSong: this.state.queue[songNumberInQueue]});
        this.setState({songsPlayed: this.state.songsPlayed+1});
        this.removeSong(songNumberInQueue);
    }

    removeSong(songNumberInQueue){
        this.setState({
            queue: this.state.queue.slice(0, songNumberInQueue).concat(
                this.state.queue.slice(songNumberInQueue+1, this.state.queue.length))
        });
        // Now we have to remove the song from the queue from the server
        // API.delete("/id/songLink", body should contain the position of the song = songNumberInQueue)
    }

    _onEnd = async event => {
        this.playNextSong();
    }

    setQuery = (e) => {
        this.setState({ query: e.target.value });
    }

    handleSubmit = (e) => {
        e.preventDefault();
        this.child.current.search(this.state.query)
    }

    render() {
        const spTkn = 'BQC7cmdorLg82wSM7a2bXD25PjS6DAtgDLTAQV3EifbqIypnU5PEw0HaCLSXTaky7_13VlsMRfwJNCX6Whg'
        return (

            <div className="container-fluid">
                <div className="row">
                    <div className="col">
                        <nav className="navbar navbar-dark bg-dark justify-content-between">
                            <a className="navbar-brand" style={{color:"white"}}>This is master</a>
                            <form className="form-inline" onSubmit={this.handleSubmit}>
                                <input className="form-control mr-sm-2" type="search" placeholder="Look up song"
                                       aria-label="Search" value={this.state.query} onChange={this.setQuery} style={{ width:"300px" }}></input>
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
                            <Search ref={this.child} />
                        </ul>
                    </div>
                </div>
            </div>

        );
    }



    // the songs played part ensures that the player gets refreshed at the end of a song
    renderPlayer(){
        return(
            <div>
                { spotifyApi.getAccessToken() &&
                <SpotifyPlayer
                    spotifyToken={spotifyApi.getAccessToken()}
                    songUri={this.state.currentSong.type === "s" ? this.state.currentSong.link : ''}
                    songName={this.state.currentSong.name}
                    next={this._onEnd}
                />
                }

                {this.state.currentSong.type === "y" &&
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
                    <div className="float-right">
                    <div className="btn-group" role="group">
                        <button type="button" className="btn btn-success" onClick={() => this.playSong(i)}> <FontAwesomeIcon icon="play-circle"/></button>
                        <button type="button" className="btn btn-danger" onClick={() => this.removeSong(i)}><FontAwesomeIcon icon="trash-alt"/></button>
                        <button type="button" className="btn btn-info"><FontAwesomeIcon icon="thumbs-up"/></button>
                    </div>
                    </div>

                </li>
        );}

}


export default MasterRoom;