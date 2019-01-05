import React, {Component} from 'react';
import {Input, Button} from 'semantic-ui-react'
import publicIP from "react-native-public-ip";
import axios from 'axios'


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

        const name = "spas2";
        const room = this.props.cookies.get('roomId');
        const l = testId + roomCode;
        const dataToSend = {
            ip: ip
        }
        const response = await axios.post(l, {ip});
        if(response.status === 200){
            this.props.cookies.set('UserId', response.data.userId, { path: '/', maxAge: 3600 });
            this.props.cookies.set('Nickname', response.data.nickname,  { path: '/', maxAge: 3600 });
            this.props.history.push('/' + roomCode);
        }
        // const response = await axios.post(
        //     'http://127.0.0.1:5000/' + room,

        //     {nickname: name},
        //     {IP: ip},
        //     {room_number: room}
        // );

        console.log(this.state.roomCode);
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

        this.props.history.push('master/' + response.data.success.room._id);
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