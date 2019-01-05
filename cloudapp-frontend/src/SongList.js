import React, {Component} from 'react';
import axios from 'axios'
import {ListGroup} from "react-bootstrap";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";

class SongList  extends Component {
    constructor(props) {
        super(props);
    }

    like = async (i) => {
        console.log('like song ' + this.props.queue[i].name);
        //TODO api call to like this song
        //no need to update state, it will update itself every 2 seconds anyway
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
        console.log(this.props.queue);
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
                    <span> </span> Votes: {song.votes}
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
                                <div></div>}
                            <button type="button" className="btn btn-info" onClick={() => this.props.like(i)}>
                                <FontAwesomeIcon icon="thumbs-up"/></button>
                        </div>
                    </div>

                </li>
        );}
}

export default SongList;