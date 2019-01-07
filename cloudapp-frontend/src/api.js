let axios = require('axios');

// api object holding post and get functions for requests
let api = {};

api.postNoCookie = (url, body) => {
    return axios.post(url, body);
}

api.post = (url, cookie, body) => {
    let headers = {
        'Authorization': cookie
    };
    return axios.post(url, body, { headers: headers });
}

api.get = (url, cookie) => {
    let headers = {
        'Authorization': cookie
    };

    return axios.get(url, { headers: headers });
}


module.exports = api;