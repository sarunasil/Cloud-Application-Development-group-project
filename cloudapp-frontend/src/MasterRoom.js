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
import api from './api.js';

const testId = 'https://cloud-app-dev-227512.appspot.com/';
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
        if(!this.props.cookies.get('MasterCookie')){
            var roomCode = window.location.href.substring(window.location.href.lastIndexOf("/") + 1);
            this.props.history.push('/' + roomCode);
        }
        this.state = {
            query: '',
            queue: [],
            currentlyPlaying : false,
            currentSong: {
                name : "",
                url : "",
                time : "",
                type : "",
                score: 0

            },
            songsPlayed: 0,
            users: ["Monkey", "Octopus", "Giraffe", "Rabbit", "Cat"]
        };
        this.child = React.createRef();

        let timerId = setInterval(() => this.updateStateForServer('tick'), 3000);
        this.playSong= this.playSong.bind(this);
        this.removeSong = this.removeSong.bind(this);
        //TODO: will become our domain name
        spotifyApi.setRedirectURI('http://localhost:3000/callback');

        //spotifyApi.setRedirectURI('http://cad-nqme.s3-website.eu-west-2.amazonaws.com/callback');

    }

    componentDidMount(){
        //Obtains the User's IP and saves it in the cookie
        this.saveIP();

        //TODO: Uncommnet to populate table with users
        this.updateUsersTable();

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

     updateStateForServer = async ()=> {
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
                    url : "2g811Eo7K8U",
                    time: "150", // time in seconds
                    votes: "0"
                },

                {
                    name : "Song 3",
                    url : "spotify:track:47YfeZOuxkGsiFwY97ubRQ",
                    time: "150", // time in seconds
                    votes: "0"
                },
                {
                    name : "Song 4",
                    url : "3KL9mRus19o",
                    time: "150", // time in seconds
                    votes: "0"
                }
            ]
        }

        var url = testId + this.props.cookies.get('roomId')+ '/pending-songs';
        const response = await api.get(url, this.props.cookies.get('userId'));
        console.log(response);
        var newQueue =  response.data.success ? response.data.success.queue : [];
        this.setState({queue: newQueue});

         //TODO: Uncomment to update the users table as well
         this.updateUsersTable();


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

    async playSong(songNumberInQueue){
        console.log(this.state.queue[songNumberInQueue]);
        if(this.state.queue[songNumberInQueue].url.startsWith('spoti')){
            this.state.queue[songNumberInQueue].type = 's';
        }else{
            this.state.queue[songNumberInQueue].type = 'y';
        }
        if(this.state.queue[songNumberInQueue].type === 's' && !spotifyApi.getAccessToken()){
            await this.removeSong(songNumberInQueue);
            this.playNextSong();
            return;
        }else {
            this.setState({currentlyPlaying: true});
            this.setState({currentSong: this.state.queue[songNumberInQueue]});
            this.setState({songsPlayed: this.state.songsPlayed + 1});
            this.removeSong(songNumberInQueue);
        }
    }

    removeSong = async (songNumberInQueue) => {
        var linkToSend;
        if(songNumberInQueue === 0){
            linkToSend = testId + this.props.cookies.get('roomId') + '/dequeue-song';
        }else{
            linkToSend = testId + this.props.cookies.get('roomId') + '/remove-song';
        }
        const data = {
            name : this.state.queue[songNumberInQueue].name,
            url : this.state.queue[songNumberInQueue].url
        }

        const response = await api.post(linkToSend, this.props.cookies.get('MasterCookie'), data);
        console.log("aaa");
        console.log(response);
        this.setState({
            queue: this.state.queue.slice(0, songNumberInQueue).concat(
                this.state.queue.slice(songNumberInQueue+1, this.state.queue.length))
        });
    }

    _onEnd = async event => {
        // pause spotify player here
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
        // HOW THIS SHOULD WORK:
        //1. Call API for all users (done)
        //2. Go through all users and find the id of the nickname that we want to kick (done)
        //3. Call Kick API for the found id (step 2)  (done, cannot test)
        //4. call all users to update the table


        var nicknameToKick = e.target.value;


        //Calling API for all users
        var url = testId + this.props.cookies.get('roomId')+ '/get-members';
        const response = await api.post(url, this.props.cookies.get('MasterCookie'));

        const usersList = response.data.success;

        // Going through all users to find the ID of the user to kick (searching by Nickname)
        // Why? Because the API to kick a user requires an ID, not a nickname
        var idToKick = null
        for (var id in usersList){
            var currentNickname = usersList[id]["nickname"];
            if(currentNickname=== nicknameToKick) {
                idToKick = id;
            }
        }

        if(idToKick == null) {
            alert("Could not find user " + nicknameToKick + " in the database!");
            return;
        }

        //Calling API to kick the user
        var urlKick = testId + this.props.cookies.get('roomId')+ '/kick';
        let body = {
            userId: idToKick
        };
        console.log("Calling Kick API");
        const responseKick = await api.post(urlKick, this.props.cookies.get('MasterCookie'), body);
        console.log("Response Kick: ", responseKick);
        if(responseKick.status === 200) {
            alert("User " + nicknameToKick + " was kicked!")
        } else {
            alert("Could not kick user!");
        }

        // update the table
        this.updateUsersTable();

    }

    handleBlock = async (e) => {
        // HOW THIS SHOULD WORK:
        //1. Call API for all users (done)
        //2. Go through all users and find the id of the nickname that we want to block (done)
        //3. Call Block API for the found id (step 2)  (done, cannot test)
        //TODO: 4. call all users to update the table

        var nicknameToBlock = e.target.value;


        //Calling API for all users
        var url = testId + this.props.cookies.get('roomId')+ '/get-members';
        const response = await api.post(url, this.props.cookies.get('MasterCookie'));

        const usersList = response.data.success;

        // Going through all users to find the ID of the user to block (searching by Nickname)
        // Why? Because the API to block a user requires an ID, not a nickname
        var idToBlock = null
        for (var id in usersList){
            var currentNickname = usersList[id]["nickname"];
            if(currentNickname === nicknameToBlock) {
                idToBlock = id;
            }
        }

        if(idToBlock == null) {
            alert("Could not find user " + nicknameToBlock + " in the database!");
            return;
        }

        //Calling API to block the user
        var urlBlock = testId + this.props.cookies.get('roomId')+ '/block';
        let body = {
            userId: idToBlock
        };
        const responseBlock = await api.post(urlBlock, this.props.cookies.get('MasterCookie'), body);
        if(responseBlock.status === 200) {
            alert("User " + nicknameToBlock + " was blocked!")
        } else {
            alert("Could not block user!");
        }

        //update the table
        this.updateUsersTable();
    };

    updateUsersTable = async () => {
        // HOW THIS Works:
        // 1. The API to get all users is called
        // 2. The users table is populated with all the users (except for the master)

        var users = [];

        //Calling API for all users
        var url = testId + this.props.cookies.get('roomId')+ '/get-members';
        const response = await api.post(url, this.props.cookies.get('MasterCookie'));

        const usersList = response.data.success;

        for (var id in usersList){

            var currentNickname = usersList[id]["nickname"];
            if(currentNickname != "Master") {
                // var realNickname = currentNickname.data.success.nickname;
                users.push(currentNickname);
            }
        }


        this.setState({
            users: users
        })

    }

    render() {
        return (

            <div className="container-fluid">
                <div className="row">
                    <div className="col">
                        <nav className="navbar navbar-dark bg-dark justify-content-between">
                            <a className="navbar-brand" style={{color:"white"}}>You are the host</a>
                            <form className="form-inline" onSubmit={this.handleSubmit}>
                                <input className="form-control mr-sm-2" type="search" placeholder="Look up song"
                                       aria-label="Search" value={this.state.query} onChange={this.setQuery} style={{ width:"300px" }}></input>
                                <button className="btn btn-success" type="submit"><FontAwesomeIcon icon="search"/>
                                </button>
                                <span> &nbsp;</span>
                                <button className="btn btn-info" onClick = {this.updateStateForServer}><FontAwesomeIcon icon="sync-alt"/></button>

                                <span> &nbsp;</span><span> &nbsp;</span><span> &nbsp;</span>

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
                            remove={this.removeSong}
                            cookies = {this.props.cookies}
                        />
                    </div>
                    <div className="col-6">
                        <ul className="list-group" style={{align:"left"}}>
                            <Search ref={this.child} cookies = {this.props.cookies} />
                        </ul>
                    </div>
                    <div className="col-3"> <div>
                            <ul className="list-group" style={{textAlign:"left"}}>
                                {this.renderUsersTable()}
                            </ul>
                        </div> </div>
                </div>
            </div>

        );
    }


    renderUsersTable() {
                    return this.state.users.map(
                    (user, i) =>

                        <li className="list-group-item" key = {i} style={{align:"left", border:"0", background: "transparent",fontWeight:"900", color:"white"}}>
                            {user}
                            <div className="float-right">
                                <div className="btn-group" role="group">
                                    <td> <button type="button" className="btn btn-info" value={user} onClick={this.handleKick}>Kick</button></td>
                                    <td><button type="button" className="btn btn-danger"value={user} onClick={this.handleBlock}>Block</button></td>

                                </div>
                            </div>

                        </li>




                    );


    }



    // the songs played part ensures that the player gets refreshed at the end of a song
    renderPlayer() {
        return(
            <div>
                { this.state.currentSong.type === "s" && spotifyApi.getAccessToken() &&
                <SpotifyPlayer
                    spotifyToken={spotifyApi.getAccessToken()}
                    songUri={this.state.currentSong.url}
                    songName={this.state.currentSong.name}
                    next={this._onEnd}

                />
                }

                {this.state.currentSong.type === "y" &&
                <YouTube
                    videoId= {this.state.currentSong.url}
                    opts={youtubeOptions}
                    onEnd={this._onEnd}

                />
                }
            </div>
        );
    }

}


export default MasterRoom;