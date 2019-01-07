import React, {Component} from 'react';
import {Input} from 'semantic-ui-react'
import publicIP from "react-native-public-ip";
import axios from 'axios'
import api from './api.js'
import './Home.css';
import { Button } from 'react-bootstrap';


const testId = 'https://cloud-app-dev-227512.appspot.com/';
class Home extends Component {

    constructor(props) {
        super(props);
        this.state = {
            roomCode: ''
        };
    }

    handleChange = (e) => {
        this.setState({ roomCode: e.target.value });
    }

    join = async () => {
        this.props.history.push('/' + this.state.roomCode);


    }

    create = async () => {
        const response = await axios.post(testId);
        // const response = await axios.post('https://cloud-app-dev-227512.appspot.com/');
        console.log(response.data.success.room);

        console.log(response);
        if(response.status === 200){
            this.props.cookies.set('MasterCookie', response.data.success.room.MasterCookie, { path: '/', maxAge: 36000 });
            this.props.cookies.set('userId', response.data.success.room.MasterCookie, { path: '/', maxAge: 36000 });
            this.props.cookies.set('SpotifySearchToken', response.data.success.room.SpotifySearchToken, { path: '/', maxAge: 36000 });
            this.props.cookies.set('YoutubeSearchToken', response.data.success.room.YoutubeSearchToken, { path: '/', maxAge: 36000 });
            this.props.cookies.set('roomId', response.data.success.room._id, { path: '/', maxAge: 36000 });
            this.props.history.push('master/' + response.data.success.room._id);
        }else{
            alert("Could not create room");
        }

        //this.props.history.push('master/' + response.data.success.room._id);
    }

    render() {
        return (
            <div className="Home">
                <h1 className="logo">NQMe: Play your music</h1>

                <input className="search-bar" type="search" placeholder='Enter room code' onChange={this.handleChange}/>
                <div  style={{"marginTop": "10px"}}>
                    <Button style={{"marginRight": "10px"}} bsStyle="info" onClick={this.join}>Join Room</Button>
                    <Button bsStyle="success" onClick={this.create}>Create Room</Button>
                </div>
                
            </div>
        );
    }
}

export default Home;