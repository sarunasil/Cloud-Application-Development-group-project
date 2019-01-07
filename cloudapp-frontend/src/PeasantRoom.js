import React, {Component} from 'react';
import SpotifyWebApi from 'spotify-web-api-node';
import './App.css';
import searchYouTube from 'youtube-api-search';
import { Button, ListGroup, ListGroupItem } from 'react-bootstrap';
import publicIP from "react-native-public-ip";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import SongList from "./SongList";
import Search from "./Search";
import api from './api.js'

const testId = 'https://cloud-app-dev-227512.appspot.com/';
var timerId = null;

class PeasantRoom extends Component {
    constructor(props) {
        super(props)
        var roomLink = window.location.href.substring(window.location.href.lastIndexOf("/") + 1);
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
            roomCode : roomLink
        };
        this.child = React.createRef();
        console.log("aaaa");
        console.log(this.state.roomCode);
        console.log(window.location.href.lastIndexOf("/", 0));



    }

    async getTokensAndInfo(){
        var ip = await publicIP()
            .then(ip => {
                console.log("User IP: ", ip);
                return ip;
            })
            .catch(error => {
                console.log(error);
            });

        const nicknameResponse = await api.get(testId + this.state.roomCode + "/nickname", "");
        console.log("nickname");
        if(nicknameResponse.status === 200){
            var nickname = nicknameResponse.data.success["nickname"];
            const link = testId + this.state.roomCode;
            const dataToSend = {
                IP: ip,
                nickname : nickname
            }
            console.log("aaa");
            const response = await api.post(link, "", dataToSend);
            if(response.status === 200){
                console.log(response);
                console.log("Nickname, ", nickname);
                this.props.cookies.set('nickname', nickname, { path: '/', maxAge: 3600 });
                this.props.cookies.set('userName', response.data.success.UserId, { path: '/', maxAge: 36000 });
                this.props.cookies.set('userId', response.data.success.UserCookie, { path: '/', maxAge: 36000 });
                this.props.cookies.set('SpotifySearchToken', response.data.success.SpotifySearchToken, { path: '/', maxAge: 36000 });
                this.props.cookies.set('YoutubeSearchToken', response.data.success.YoutubeSearchToken, { path: '/', maxAge: 36000 });
                this.props.cookies.set('roomId', this.state.roomCode, { path: '/', maxAge: 3600 });
                //this.props.history.push('/' + this.state.roomCode);
            } else {
                alert("Such Room Does not exist or you may have been blocked from it!");
            }
            // const response = await axios.post(
            //     'http://127.0.0.1:5000/' + room,

            console.log(this.state.roomCode);
        } else{
            alert("Could not retreive nickname");
        }
    }

    async componentDidMount(){
        // Obtains the user IP and adds it to the cookie
        this.saveIP();
        if(!this.props.cookies.get('nickname')) {
            await this.getTokensAndInfo();
        }
        this.updateStateForServer();
        timerId = setInterval(() => this.updateStateForServer('tick'), 3000);
        //TODO: use roomId to retrieve data : queue, search/access token for spotify/YT
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

    async updateStateForServer() {
        // this function periodically updates the queue from the server
        // the server should send be a json like
        // we could only send the changes and, from time to time, send the full state, but for now we should keep this simple
        if(!this.props.cookies.get('userId')) {
            return;
        }
        var newState = {
            queue: [
                {
                    name : "Song 1",
                    url : "spotify:track:2SL6oP2YAEQbqsrkOzRGO4",
                    time: "150", // time in seconds
                    score: 0
                },
                {
                    name : "Song 2",
                    url : "2g811Eo7K8U",
                    time: "150", // time in seconds
                    score: 0
                }
            ]
        }
        var url = testId + this.props.cookies.get('roomId')+ '/pending-songs';
        const response = await api.get(url, this.props.cookies.get('userId'));
        if(response.data.hasOwnProperty("failure")) {
            alert("You have been kicked or blocked!");
            clearInterval(timerId);
            this.props.history.push('/');
            return;
        }

        var currentSong = await api.get(testId + this.props.cookies.get('roomId') + '/currently-playing', this.props.cookies.get('userId'))
        var newQueue =  response.data.success.queue;
        this.setState({
            queue: newQueue,
            currentSong: {name: currentSong.data.success ? currentSong.data.success.name : ''}});
    }

    setQuery = (e) => {
        this.setState({ query: e.target.value });
    }

    handleSubmit = (e) => {
        e.preventDefault();
        this.child.current.search(this.state.query)
    }


    render() {
        return (

            <div className="container-fluid">
                <div className="row">
                    <div className="col">
                        <nav className="navbar navbar-dark bg-dark justify-content-between">
                            <a className="navbar-brand" style={{color:"white"}}>{"Your nickname is: " + this.props.cookies.get("nickname")}</a>
                            <form className="form-inline" onSubmit={this.handleSubmit}>
                                <input className="form-control mr-sm-2" type="search" placeholder="Look up song"
                                       aria-label="Search" value={this.state.query} onChange={this.setQuery} style={{ width:"300px" }}></input>
                                <button className="btn btn-outline-success my-2 my-sm-0" type="submit"><FontAwesomeIcon icon="search"/>
                                </button>
                                <span> &nbsp;</span>

                            </form>
                        </nav>
                    </div>
                </div>
                <div className="row">
                    <div className="col"><h3>
                        Playing: {this.state.currentSong.name}
                    </h3></div>
                </div>
                <div className="row">
                    <div className="col-4">

                        <SongList queue={this.state.queue} cookies={this.props.cookies}/>

                    </div>
                    <div className="col-8">

                        <ul className="list-group" style={{align:"left"}}>
                            <Search ref={this.child} cookies={this.props.cookies}/>
                        </ul>
                    </div>
                </div>
            </div>
        );
    }
    //

}


export default PeasantRoom;