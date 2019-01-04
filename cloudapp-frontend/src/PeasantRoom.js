import React, {Component} from 'react';
import SpotifyWebApi from 'spotify-web-api-node';
import './App.css';
import searchYouTube from 'youtube-api-search';
import { Button, ListGroup, ListGroupItem } from 'react-bootstrap';
import publicIP from "react-native-public-ip";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import SongList from "./SongList";
import Search from "./Search";



class PeasantRoom extends Component {
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


    }

    componentDidMount(){
        // Obtains the user IP and adds it to the cookie
        this.saveIP();

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

    updateStateForServer() {
        // this function periodically updates the queue from the server
        // the server should send be a json like
        // we could only send the changes and, from time to time, send the full state, but for now we should keep this simple
        var newState = {
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
        var cnt ;
        //newState = API.get(this.roomId, emptyBody)

        this.setState(newState);

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
                            <a className="navbar-brand" style={{color:"white"}}>This is peasant</a>
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
                        <SongList queue={this.state.queue}/>
                    </div>
                    <div className="col-8">
                        <ul className="list-group" style={{align:"left"}}>
                            <Search ref={this.child} />
                        </ul>
                    </div>
                </div>
            </div>
        );
    }

}


export default PeasantRoom;