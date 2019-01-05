import 'bootstrap/dist/css/bootstrap.min.css';
import React, {Component} from 'react';
import SpotifyWebApi from 'spotify-web-api-node';
import './App.css';
import SpotifyPlayer from './SpotifyPlayer';
import YouTube from 'react-youtube';
import { Table, Button, ListGroup, ListGroupItem } from 'react-bootstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import Search from './Search'
import publicIP from 'react-native-public-ip';
import SongList from "./SongList";
import axios from "axios/index";


const testId = 'https://cloud-app-dev-227512.appspot.com/';
var scopes = ['user-modify-playback-state', 'user-read-currently-playing', 'app-remote-control', 'streaming', 'user-read-playback-state'],
    clientId = '1811c9058bad498b8d829cd37564fdc6', //my own code, will prbs be changed
    //can be used for security, CSRF shit
    state = 'some-state-of-my-choice';

var spotifyApi = new SpotifyWebApi({
    clientId: clientId
});

var users = ["Monkey", "Octopus", "Giraffe", "Rabbit", "Cat"];


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
        //Obtains the User's IP and saves it in the cookie
        console.log("Reading cookie from master: identification cookie", this.props.cookies.get("identificationCookie"));
        console.log("Reading cookie from master: room id", this.props.cookies.get("id"));

        this.saveIP();

        if(this.props.cookies.get('accessToken')){
            spotifyApi.setAccessToken(this.props.cookies.get('accessToken'));
        }
        //TODO: use roomId to retrieve data : queue, search/access token for spotify/YT
        this.updateStateForServer();
    }

    saveIP = () => {
        publicIP()
            .then(ip => {
                //add the user IP to the cookie
                this.props.cookies.set('ip', ip, { path: '/', maxAge: 3600 });
                console.log("User IP: ", ip);
            })
            .catch(error => {
                console.log(error);
            })
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
        //if we dont have spotify enabled, we skip the song
        if(this.state.queue[songNumberInQueue].type === 's' && !spotifyApi.getAccessToken()){
            this.removeSong(songNumberInQueue);
            this.playNextSong();
            return;
        }
        this.setState({currentlyPlaying: true});
        this.setState({currentSong: this.state.queue[songNumberInQueue]});
        this.setState({songsPlayed: this.state.songsPlayed+1});
        this.removeSong(songNumberInQueue);
    }

    removeSong = async (songNumberInQueue) => {
        this.setState({
            queue: this.state.queue.slice(0, songNumberInQueue).concat(
                this.state.queue.slice(songNumberInQueue+1, this.state.queue.length))
        });
        // Now we have to remove the song from the queue from the server
        // API.delete("/id/songLink", body should contain the position of the song = songNumberInQueue)
        const linkToSend = testId + this.props.cookies.get('roomId') + '/dequeue-song';
        const data = {
            Authorization : this.props.cookies.get('MasterCookie'),
            body: {
                name : this.state.queue[songNumberInQueue].name,
                url : this.state.queue[songNumberInQueue].url
            }
        }
        const response = await axios.post(linkToSend, code);


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


    handleDeleteRoom = async () => {
        var postLink = testId + this.props.cookies.get('roomId') + '/delete';
        var code  = {
            Authorization : this.props.cookies.get('MasterCookie'),
            body: {
                MasterId: this.props.cookies.get('MasterCookie')
            }
        };
        const response = await axios.post(postLink, code);
    }

    handleKick = async (e) => {
        var userToKick = e.target.value;
        //TODO: api call for kicking a user
        //TODO: api call for list of users (to update users)

        console.log("Kicking user: ", e.target.value);
    }

    handleBlock = (e) => {
        var userToBlock = e.target.value;
        //TODO: api call for blocking a user
        //TODO: api call for list of users (to update users)

        console.log("Blocking user: ", e.target.value);
    };

    render() {
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
                    <div className="col-3">
                        <SongList
                            queue={this.state.queue}
                            play={this.playSong}
                            remove={this.renderSongs}/>
                    </div>
                    <div className="col-7">
                        <ul className="list-group" style={{align:"left"}}>
                            <Search ref={this.child} />
                        </ul>
                    </div>
                    <div className="col-2">{this.renderUsersTable()}</div>
                </div>
            </div>

        );
    }


    renderUsersTable() {
        return <div>
            <Table striped bordered condensed hover>
                <thead>
                <tr>
                    <th colSpan="3">Admin Panel</th>
                </tr>
                <tr>
                    <th>Nickname</th>
                    <th>Kick</th>
                    <th>Block</th>
                </tr>

                </thead>
                <tbody>
                {users.map(
                    (user)=>
                        <tr>
                            <td>{user}</td>
                            <td><Button value={user} onClick={this.handleKick}>Kick</Button></td>
                            <td><Button value={user} onClick={this.handleBlock}>Block</Button></td>
                        </tr>
                )}
                </tbody>
            </Table>;
        </div>
    }



    // the songs played part ensures that the player gets refreshed at the end of a song
    renderPlayer() {
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

}


export default MasterRoom;