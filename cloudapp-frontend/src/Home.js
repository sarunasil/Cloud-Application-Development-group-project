import React, {Component} from 'react';
import {Input, Button} from 'semantic-ui-react'
import publicIP from "react-native-public-ip";
import axios from 'axios'

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

        console.log(this.state.roomCode);
        this.props.history.push('/someRandomIdToBeReplaced');
    }

    create = async () => {
        const response = await axios.post('https://cloud-app-dev-227512.appspot.com/')
        console.log(response.data.success.room);

        //TODO set whatever cookies need to be set
        // Saving the room id (the long code) and the identification cooked in the client-side cookie
        // Haven't done anything for the spotify/youtube tokes
        console.log("Master Cookie, ", response.data.success.room.MasterCookie);
        var masterCookie = response.data.success.room.MasterCookie;
        var id = response.data.success.room._id;

        this.props.cookies.set('identificationCookie', masterCookie, { path: '/', maxAge: 3600 });
        this.props.cookies.set('id', id, { path: '/', maxAge: 3600 });


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