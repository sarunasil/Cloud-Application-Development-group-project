import React, {Component} from 'react';
import axios from 'axios'
import {ListGroup} from "react-bootstrap";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import api from './api.js'

const testId = 'https://cloud-app-dev-227512.appspot.com/';

class SongList  extends Component {
    constructor(props) {
        super(props);
    }

    like = async (i) => {

        const linkToSend = testId + this.props.cookies.get('roomId') + '/upvote';
        const data = {
            url : this.props.queue[i].url,
            userId : this.props.cookies.get('userId')
        };
        const response = api.post(linkToSend, this.props.cookies.get('userId'), data);
        //TODO api call to like this song
        //no need to update state, it will update itself every 2 seconds anyway
    }

    unlike = async (i) => {
        console.log('like song ' + this.props.queue[i].name);
        const linkToSend = testId + this.props.cookies.get('roomId') + '/unvote';
        const data = {
            url : this.props.queue[i].url,
            userId : this.props.cookies.get('userId')

        };
        const response = api.post(linkToSend, this.props.cookies.get('userId'), data);
        //TODO api call to like this song
        //no need to update state, it will update itself every 2 seconds anyway
    }

    removeSong = async (songNumberInQueue) => {
        const linkToSend = testId + this.props.cookies.get('roomId') + '/remove-song';
        const data = {
            name : this.props.queue[songNumberInQueue].name,
            url : this.props.queue[songNumberInQueue].url
        }

        const response = await api.post(linkToSend, this.props.cookies.get('userId'), data);
        console.log(response);
        this.setState({
            queue: this.props.queue.slice(0, songNumberInQueue).concat(
                this.props.queue.slice(songNumberInQueue+1, this.props.queue.length))
        });
    }



    render() {

        return (
            <div className = "songs">
                <ListGroup>
                    {this.renderSongList()}
                </ListGroup>
            </div>
        );
    }

    renderSongList(){
        return this.props.queue.map(
            (song, i) =>
                <li className="list-group-item" key = {i} style={{border:"0"}}>
                    { !song.url.startsWith('spotify:') &&
                    <img src={require('./youtubeLogo.png')} width="50" height="40"/>
                    }
                    {  song.url.startsWith('spotify:') &&
                    <img src={require('./spotifyLogo.png')} width="40" height="40"/>
                    }
                    <span> </span>
                    {song.name}
                    <span> </span> Votes: {song.score}
                    <span> </span> Added by: {song.nickname === "Master" ? "master" : song.nickname}
                    <span> </span>
                    <div className="float-right">
                        <div className="btn-group" role="group">
                            {this.props.play ?
                            <button type="button" className="btn btn-success" onClick={() => this.props.play(i)}>
                                <FontAwesomeIcon icon="play-circle"/></button> :
                                <div></div>}
                            {this.props.remove ?
                            <button type="button" className="btn btn-danger" onClick={() => this.props.remove(i)}>
                                <FontAwesomeIcon icon="trash-alt"/></button> :
                                song.userId === this.props.cookies.get('userName') &&
                                <button type="button" className="btn btn-danger" onClick={() => this.removeSong(i)}>
                                    <FontAwesomeIcon icon="trash-alt"/></button>}

                                <button type="button" className="btn btn-info" onClick={() => this.like(i)}>
                                    <FontAwesomeIcon icon="thumbs-up"/></button>


                                <button type="button" className="btn btn-secondary" onClick={() => this.unlike(i)}>
                                    <FontAwesomeIcon icon="thumbs-down"/></button>

                        </div>
                    </div>
                </li>
        );
    }
}

export default SongList;