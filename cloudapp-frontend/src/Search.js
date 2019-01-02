import React, {Component} from 'react';
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import searchYouTube from "youtube-api-search";
import SpotifyWebApi from 'spotify-web-api-node';

var spotifyApi = new SpotifyWebApi({
    clientId: '1811c9058bad498b8d829cd37564fdc6'
});

class Search extends Component {

    //will receive search tokens and an add function
    constructor(props) {
        super(props);
        if(this.props.spotifyToken){
            spotifyApi.setAccessToken(this.props.spotifyToken);
        }
    }

    state = {
        query: '',
        results: []
    }

    setQuery = (e) => {
        this.setState({ query: e.target.value });
    }

    setResults = (e) => {
        this.setState({ results: e.target.value });
    }

    search = async (e) => {
        e.preventDefault();
        var entries = [];
        searchYouTube({key: "AIzaSyCIoanDddBkwWAVQRmFl62ZmVwQ184Ggls", term: this.state.query, maxResults: 6}, (videos) => {
            for(var video of videos){
                entries.push({
                    link: video.id.videoId,
                    name: video.snippet.title
                });
            }

            this.setState({results: entries});
        });

        if(spotifyApi.getAccessToken()){
            var tracks  = await spotifyApi.searchTracks(this.state.query, {limit: 6});
            for(var track of tracks.body.tracks.items){
                entries.push({
                    name: track.artists[0].name + ' - ' + track.name,
                    link: track.uri,
                    time: track.duration_ms
                });
            }
        }
    }

    addSong = (index) => {
        //TODO api call to add the song
        console.log(JSON.stringify(this.state.results[index]) + ' will be added')
    }

    renderSearch(){
        var searchResults = this.state.results;
        return searchResults.map(
            (song, i) =>

                <li style={{border:"0"}} className="list-group-item" key = {i}  >

                    { !song.link.startsWith('spotify:') &&
                    <img src={require('./youtubeLogo.png')} width="50" height="40"/>
                    }
                    {  song.link.startsWith('spotify:') &&
                    <img src={require('./spotifyLogo.png')} width="40" height="40"/>
                    }
                    <span> </span>
                    {song.name}
                    <span> </span>
                    <button type="button" className="btn btn-success" onClick={() => this.addSong(i)}><FontAwesomeIcon icon="plus-square"/></button>
                </li>


        );
    }

    render() {
        return (
            <div>
                <form className="form-inline" onSubmit={this.search}>
                    <input className="form-control mr-sm-2" type="search" placeholder="Look up song"
                           aria-label="Search" value={this.state.query} onChange={this.setQuery} style={{ width:"300px" }}></input>
                    <button className="btn btn-outline-success my-2 my-sm-0" type="submit"><FontAwesomeIcon icon="search"/>
                    </button>
                </form>
                <ul className="list-group" style={{align:"left"}}>
                    {this.renderSearch()}
                </ul>
            </div>
        );
    }
}

export default Search;