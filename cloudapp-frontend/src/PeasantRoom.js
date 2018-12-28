import React, {Component} from 'react';

class PeasantRoom extends Component {
    constructor(props) {
        super(props);
    }


    componentDidMount(){
        //TODO: use roomId to retrieve data : queue, search/access token for spotify/YT
    }

    render() {
        return (
            <div className="PeasantRoom">
                <h1>THis is peasant room</h1>
            </div>
        );
    }
}

export default PeasantRoom;