import axios from "axios";

export default class WS {

    constructor(
            baseUrl,
            onMessage,
            onOpen,
            onClose,
            onError,
        ){

        //contextual base url
        const base = window.location.host;
        let url_base = window.location.host+"/ws";
        //console.log("base", base, url_base);
        
        if (base === "localhost:5173" || base === "localhost:5174"){
            url_base = "ws://localhost:8000/ws"
        } 
        //override base url if provided
        if (baseUrl){
            url_base = baseUrl;
        } 

        this.url_base = url_base;
        this.ws = new WebSocket(url_base);
        this.ws.onmessage = onMessage;

        if (onOpen){
            this.ws.onopen = onOpen;
        }

        if (onClose){
            this.ws.onclose = onClose;
        }

        if (onError){
            this.ws.onerror = onError;
        }
        
        
        //console.log("Websocket initialized",url_base);
        this.authtoken =  this.getItem("authtoken");

    }

    getItem(key){
        try {
            if(localStorage.hasOwnProperty(key)){
                return localStorage[key];
            }
        } catch (error) {
            console.error(error.message);
            return null; 
        }
    }

    setItem(key, item){
        try {
            localStorage.setItem(key, item);
            return true;
        } catch (error) {
            console.error(error.message);
            return false; 
        }
    }

    clearStorage(){
        localStorage.clear();
    }

    logout(){
        this.clearStorage();
    }

    reconnect(){
        //todo create reconnect logic
    }

    sendMessage(payload){
        //package message with authkey
        payload["authtoken"] = this.authtoken;
        // const envelope = {
        //     "authtoken":this.authtoken,
        //     "payload":payload,
        // }
        const message = JSON.stringify(payload);
        this.ws.send(message);

    }

    sendRawMessage(message){
        //send a text message directly
        this.ws.send(message);

    }

    getReadyState(){
        // 0 - connecting
        // 1 - open
        // 2 - closing
        // 3 - closed
        return this.ws.readyState;
    }

    getState(){
        //returns a string representation of websocket state
        // 0 - connecting
        // 1 - open
        // 2 - closing
        // 3 - closed
        const i = this.ws.readyState;
        switch(i){
            case 0:
                return "CONNECTING"
            case 1:
                return "OPEN"
            case 2:
                return "CLOSING"
            case 3:
                return "CLOSED"
            default:
                return `UNDEFINED STATE: ${i}`
        }
    }

}