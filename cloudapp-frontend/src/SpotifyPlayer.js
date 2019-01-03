import React, {Component} from 'react';
import SpotifyWebApi from 'spotify-web-api-node';

var spotifyApi = new SpotifyWebApi({
    clientId: '1811c9058bad498b8d829cd37564fdc6'
});

class SpotifyPlayer extends Component {

    //will receive playback tokens
    constructor(props) {
        super(props);
        spotifyApi.setAccessToken(this.props.spotifyToken);

        this.playerCheckInterval = setInterval(() => this.checkForPlayer(), 1000);
    }

    componentDidMount() {
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
                name: "Play.me Spotify Player",
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
            console.log(device_id);
            this.setState({ deviceId: device_id });
        });
    }

    componentWillUpdate(nextProps, nextState){
        console.log(nextProps);
        console.log(nextState);
        if(nextProps.songUri){
            if(nextProps.songUri === this.state.lastPlayed) return;

            const data = spotifyApi.play({
                uris:[nextProps.songUri],
                device_id: this.state.deviceId
            });

            this.setState({lastPlayed: nextProps.songUri});
        } else {
            spotifyApi.pause();
        }
    }

    resume() {
        spotifyApi.play()
    }

    pause() {
        spotifyApi.pause()
    }

    next = () => {
        spotifyApi.pause();
        this.props.next();
    }

    render(){
        return (
            <div>
                {this.props.songUri ?
                    <div>
                        <h3>Playing: {this.props.songName}</h3>
                    <button onClick={this.pause}>Pause</button>
                    <button onClick={this.resume}>Resume</button>
                    <button onClick={this.next}>Next</button>
                    </div> :
                    <div></div>}
            </div>
        )
    }
}

export default SpotifyPlayer