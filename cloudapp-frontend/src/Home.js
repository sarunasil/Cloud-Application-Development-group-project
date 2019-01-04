import React, {Component} from 'react';
import {Input, Button} from 'semantic-ui-react'
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

    join = () => {
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