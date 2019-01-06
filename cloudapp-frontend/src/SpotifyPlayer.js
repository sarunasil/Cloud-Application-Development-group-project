import React, {Component} from 'react';
import SpotifyWebApi from 'spotify-web-api-node';
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";

var spotifyApi = new SpotifyWebApi({
    clientId: '1811c9058bad498b8d829cd37564fdc6'
});

class SpotifyPlayer extends Component {

    //will receive playback tokens
    constructor(props) {
        super(props);
        spotifyApi.setAccessToken(this.props.spotifyToken);
        console.log("Spotify");
        console.log(this.props);
        this.playerCheckInterval = setInterval(() => this.checkForPlayer(), 1000);
        this.state={}

    }

    componentWillMount() {
        const script = document.createElement("script");
        script.src = "https://sdk.scdn.co/spotify-player.js";
        document.body.appendChild(script);

        const script2 = document.createElement("script");
        script2.innerHTML = "window.onSpotifyWebPlaybackSDKReady = () => { window.Spotify = Spotify;}";
        document.body.appendChild(script2);
    }

    checkForPlayer() {
        const token = this.props.spotifyToken;
        if (window.Spotify) {
            clearInterval(this.playerCheckInterval);

            this.player = new window.Spotify.Player({
                name: "NQ.me Spotify Player",
                getOAuthToken: cb => { cb(token); },
            });
            this.createEventHandlers();

            // finally, connect!
            this.player.connect();
        }
    }

    createEventHandlers() {
        this.player.on('initialization_error', e => { console.error(e); });
        this.player.on('authentication_error', e => { console.error(e); });
        this.player.on('account_error', e => { console.error(e); });
        this.player.on('playback_error', e => { console.error(e); });

        // Playback status updates
        this.player.on('player_state_changed', state => {
            console.log(state);
            if(!state || (state.paused && state.position === 0)) this.props.next()
        });

        // Ready
        this.player.on('ready', data => {
            let { device_id } = data;
            console.log("Device id");
            console.log(device_id);
            this.setState({ deviceId: device_id });
        });
    }

    componentWillUpdate(nextProps, nextState){
        console.log("At problem");
        console.log(nextProps);
        console.log(nextState);
        //check that we have a spotify song and that the player is ready

            if (nextProps.songUri && this.state.deviceId) {
                if (nextProps.songUri === this.state.lastPlayed) return;

                const data = spotifyApi.play({
                    uris: [nextProps.songUri],
                    device_id: this.state.deviceId
                });

                this.setState({lastPlayed: nextProps.songUri});
            } else {
                spotifyApi.pause();
            }

    }

    componentWillUnmount(){
        this.player.pause();
    }

    resume = () => {
        this.player.resume();
    }

    pause = () => {
       this.player.pause();
    }

    next = () => {
        this.player.pause();
        this.props.next();
    }

    back = async () => {
        const data = await this.player.getCurrentState();
        this.player.seek(data.position - 10000 > 0 ? data.position - 10000 : 0);
    }

    forward = async () => {
        const data = await this.player.getCurrentState();
        this.player.seek(data.position + 10000 < data.duration ? data.position + 10000 : data.duration-1);
    }


    render(){
        return (
            <div>
                {this.props.songUri ?
                    <div>
                        <h3>Playing: {this.props.songName}</h3>
                        <div className="btn-group" role="group">
                            <button onClick={this.back} className="btn btn-info"><FontAwesomeIcon icon="backward"/></button>
                            <button onClick={this.pause} className="btn btn-secondary"><FontAwesomeIcon icon="pause"/></button>
                            <button onClick={this.resume} className="btn btn-secondary"><FontAwesomeIcon icon="play"/></button>
                            <button onClick={this.forward} className="btn btn-info"><FontAwesomeIcon icon="forward"/></button>
                            <button onClick={this.next} className="btn btn-success" ><FontAwesomeIcon icon="step-forward"/></button>
                        </div>
                            </div> :
                    <div></div>}
            </div>
        )
    }
}

export default SpotifyPlayer