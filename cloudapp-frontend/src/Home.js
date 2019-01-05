import React, {Component} from 'react';
import {Input, Button} from 'semantic-ui-react'
import publicIP from "react-native-public-ip";
import axios from 'axios'
import api from './api.js'

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
        // This ip will be needed when calling the join API
        var ip = await publicIP()
            .then(ip => {
                console.log("User IP: ", ip);
                return ip;
            })
            .catch(error => {
                console.log(error);
            });

        //TODO: api calls to join the room
        //map code to room ID
        //return ID and redirect to it

        const nickname = await api.get(testId + this.state.roomCode + "/nickname", "");
        console.log(nickname);
        if(nickname.status === 200){

            const name = "spas2";
            const l = testId + this.state.roomCode;
            const dataToSend = {
                IP: ip,
                nickname : nickname
            }
            const response = await api.post(l, "", dataToSend);
            if(response.status === 200){
                console.log(response);
                this.props.cookies.set('userName', response.data.success.room.UserId, { path: '/', maxAge: 3600 });
                this.props.cookies.set('userId', response.data.success.room.UserCookie, { path: '/', maxAge: 3600 });
                this.props.cookies.set('SpotifySearchToken', response.data.success.room.SpotifySearchToken, { path: '/', maxAge: 3600 });
                this.props.cookies.set('YoutubeSearchToken', response.data.success.room.YoutubeSearchToken, { path: '/', maxAge: 3600 });
                this.props.cookies.set('roomId', response.data.success.room._id, { path: '/', maxAge: 3600 });
                this.props.history.push('/' + response.data.success.roomId);
            }
            // const response = await axios.post(
            //     'http://127.0.0.1:5000/' + room,

            //     {nickname: name},
            //     {IP: ip},
            //     {room_number: room}
            // );

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
            this.props.cookies.set('MasterCookie', response.data.success.room.MasterCookie, { path: '/', maxAge: 3600 });
            this.props.cookies.set('userId', response.data.success.room.MasterCookie, { path: '/', maxAge: 3600 });
            this.props.cookies.set('SpotifySearchToken', response.data.success.room.SpotifySearchToken, { path: '/', maxAge: 3600 });
            this.props.cookies.set('YoutubeSearchToken', response.data.success.room.YoutubeSearchToken, { path: '/', maxAge: 3600 });
            this.props.cookies.set('roomId', response.data.success.room._id, { path: '/', maxAge: 3600 });
            this.props.history.push('master/' + response.data.success.room._id);
        }else{
            alert("Could not create room");
        }

        //this.props.history.push('master/' + response.data.success.room._id);
    }

    render() {
        return (
            <div className="Home">
                <h1>THis is home</h1>
                <Input placeholder='Enter room code' onChange={this.handleChange}/>
                <Button onClick={this.join}>Join</Button>
                <Button onClick={this.create}>Create</Button>
            </div>
        );
    }
}

export default Home;