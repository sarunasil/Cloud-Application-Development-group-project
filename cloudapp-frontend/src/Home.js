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

        //TODO: What is missing: get the room code and somehow link it to the roomID?
        //map code to room ID
        //return ID and redirect to it

        //HOW THIS WORKS
        //1. Call the Generate Nickname API (needed for 2.)
        //2. Call the JOIN API (supplying nickname and IP address
        //3. SAVE the UserID and UserCookie that the Join API returns in the cookie

        // This ip will be needed when calling the join API
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
                this.props.history.push('/' + this.state.roomCode);
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