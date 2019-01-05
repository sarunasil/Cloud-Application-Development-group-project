import React, {Component} from 'react';
import {Input, Button} from 'semantic-ui-react'
import publicIP from "react-native-public-ip";
import axios from 'axios'
import api from "./api";


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

        //Calling the generate nickname API
        var urlGenerateNickname = testId + this.props.cookies.get('roomId')+ '/nickname';
        console.log("Url ", urlGenerateNickname);
        const responseGenerateNickname = await api.get(urlGenerateNickname);
        console.log("GenerateNickname response ", responseGenerateNickname);
        if(responseGenerateNickname.status != 200) {
            alert("Could not join the room!");
            return;
        }

        var nickname = responseGenerateNickname.data.success["nickname"];
        console.log("Nickname: ", nickname);

        this.props.cookies.set('Nickname', nickname,  { path: '/', maxAge: 3600 });

        var urlJoinRoom = testId + this.props.cookies.get('roomId');
        console.log("Url ", urlJoinRoom);
        let body = {
            nickname: nickname,
            IP: ip
        };
        const responseJoinRoom = await api.postNoCookie(urlJoinRoom, body);
        console.log("JoinRoom response ", responseJoinRoom);
        if(responseJoinRoom.status === 200) {
            this.props.cookies.set('UserId', responseJoinRoom.data.success["UserId"], { path: '/', maxAge: 3600 });
            this.props.cookies.set('UserCookie', responseJoinRoom.data.success["UserCookie"],  { path: '/', maxAge: 3600 });

            console.log("Cookies set: UserId", this.props.cookies.get("UserId"));
            console.log("Cookies set: UserCookie", this.props.cookies.get("UserCookie"));

            this.props.history.push('/' +  this.props.cookies.get('roomId'));
        } else {
            alert("Could not join the room! You may have been blocked!");
            return;
        }




         /* I guess the code below was written for testing, the above code should now work
        const name = "spas2";
        const room = this.props.cookies.get('roomId');
        const l = testId + room;
        const dataToSend = {
            ip: ip
        }
        const response = await axios.post(l, {ip});
        if(response.status === 200){
            this.props.cookies.set('UserId', response.data.userId, { path: '/', maxAge: 3600 });
            this.props.cookies.set('Nickname', response.data.nickname,  { path: '/', maxAge: 3600 });
            this.props.history.push('/' + room);
        } */


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