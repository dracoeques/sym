
import React, {useRef} from 'react';

// import Api from '../modules/api';

import { withRouter } from './utils.jsx';

import 'bootswatch/dist/lux/bootstrap.min.css'; // Added this :boom:

import ReactMarkdown from 'react-markdown'

import Api from './api.js';
import WS from './ws.js';

class WebsocketTests extends React.Component {

    constructor(props){
        super(props);

        this.state = {
            status:"init",
            ws:null,
            api:new Api(),
            message:"",
            messages:[],
            message_id:0,
            last_message_ref: React.createRef(),
            sidebarHeight:window.innerHeight,

        }


        this.handleResize = this.handleResize.bind(this);
        this.handleMessageInput = this.handleMessageInput.bind(this);
        this.handleSystemInput = this.handleSystemInput.bind(this);

        this.handleWebsocketOnMessage = this.handleWebsocketOnMessage.bind(this);
        this.handleWebsocketSendMessage = this.handleWebsocketSendMessage.bind(this);
        this.handleWebsocketOnOpen = this.handleWebsocketOnOpen.bind(this);
        this.handleWebsocketOnClose = this.handleWebsocketOnClose.bind(this);
        this.handleWebsocketOnError = this.handleWebsocketOnError.bind(this);


    }

    componentDidMount(){
        const status = this.state.status;
        if (status === "init"){
            console.log("initializing")
            this.setState({
                state:"loading",
            },() => {
                this.init();
            });
        }
        

        
    
        window.addEventListener('resize', this.handleResize);
        
        const promptInputBox = document.getElementById("promptInputBox");
        promptInputBox.addEventListener('keypress', function(e){
            if (e.key === 'Enter') {
                //console.log("Enter pressed");
                this.handleWebsocketSendMessage();
            }
        }.bind(this));
        

    }

    async init(){



        try {
            
            //console.log('me:', me);
            const route = "wstest"
            //user is logged in, create websocket
            let base = window.location.host;
            if (base === "localhost:5173" || base === "localhost:5174"){
                base = "localhost:8000"
            } 
            let protocol = "ws";
            if (location.protocol === 'https:') {
                protocol = "wss"
            }
            const baseURL = `${protocol}://${base}/${route}`;
            console.log("Connecting websocket to ", baseURL)
            const ws = new WS(
                baseURL,
                this.handleWebsocketOnMessage,
                this.handleWebsocketOnOpen,
                this.handleWebsocketOnClose,
                this.handleWebsocketOnError,
            );

            this.setState({
                ws:ws,
            });

            
        } catch (error) {
            console.error('Error in init:', error);
            //window.location.href = "/app/login";
        }
    }
 

    handleWebsocketOnMessage(event){
        
        const message = event.data;
        let messages = this.state.messages;
        messages.push(message)
        console.log("onmessage", message);
        
        this.setState({
            messages:messages
        }, () => {
            this.scrollToBottom();
        });
        
        
        
    }

    handleWebsocketSendMessage(){
        
        console.log("sendRawMessage", this.state.message);
        this.state.ws.sendRawMessage(this.state.message)

        
    }

    handleWebsocketOnOpen(){        

        const wsState = this.state.ws.getState();
        if (wsState === "OPEN"){
            console.log("websocket open")
        }

       
    }

    handleWebsocketOnClose(){
        console.log("Websocket closed");
        
    }

    handleWebsocketOnError(e){
        console.log("Websocket Error", e);
    }

    handleResize(){
        
        const innerHeight = window.innerHeight;
        console.log("resize",innerHeight);
        this.setState({sidebarHeight:innerHeight})
    }

    calculateTextBoxSize(){

    }

    handleMessageInput(e){
        e.preventDefault();
        const text = e.target.value;
        this.setState({message:text});
    }

    handleSystemInput(e){
        e.preventDefault();
        const text = e.target.value;
        this.setState({context:text});
    }

    getMessageId(){
        
        //const i =  this.state.network.nodes.length+1;
        const i = `message_${Date.now()}`
        //console.log("getNodeId", nodeId);
        //console.log("currentNodes",  this.state.network.nodes);
        return i
    }

    scrollToBottom(){
        this.state.last_message_ref?.current?.scrollIntoView({ behavior: 'smooth' })
    }

    renderMessages(){
        
        let idx = 0;
        let len = this.state.messages.length;
        const messages = this.state.messages.map(function(m){
            idx += 1;
            if (idx === len){

            }
            const messageId = this.getMessageId();
            const messageIdIdx = `${messageId}_${idx}`
            return (
                <div className='row message-row' key={messageIdIdx}>
                    <div className='col-sm-1'></div>
                    <div className='col-sm-1'>
                        
                    </div>
                    
                    <div className='col-sm-6 text-light'>
                        {m}
                        <hr></hr>
                        
                      
                    </div>
                    <div className='col-sm-2'></div>
                </div>
                
            )
        }.bind(this)); 
        return (
            <ul>
                {messages}
            </ul>
        )

    }

    render(){



        const routerParams = this.props.params;
        
        //console.log("routerParams", routerParams);
        //console.log(this.state.prompt);

        const chatInputHeight = 150;
        const contentHeight = this.state.sidebarHeight - chatInputHeight;

        const messages = this.renderMessages();
        let loader = (<div></div>);
        if (this.state.isLoading === true){
            loader = (
                <div className='row message-row' >
                    <div className='col-sm-3'></div>
                    
                    <div className='col-sm-5 text-light'>
                        <h3>Loading...</h3>
                      
                    </div>
                    <div className='col-sm-4'></div>
                    
                </div>);

        }

        return (
            <div className='container-fluid'>
                <div className='row'>
                    <div className='col-sm-2 bg-primary nomargin nopad'
                        style={{
                            height:this.state.sidebarHeight,
                            overflowY: "scroll",
                        }}
                    >
                        <h3 className="text-light"></h3>
                        
                      
                    </div>
                    <div className='col-sm-10 bg-dark nomargin nopad'>

                        <div
                        
                            style={{
                                height:contentHeight,
                                overflowY:"scroll",
                                overflowX: "hidden",

                            }}
                        >
                            <br></br>
                            {messages}
                            <div style={{ float:"left", clear: "both" }}
                                ref={this.state.last_message_ref}>
                            </div>
                            <br></br>
                            {loader}
                        </div>
                        <div
                        
                            style={{
                                height:chatInputHeight,
                                
                            }}
                        >
                            <div className='row'>
                                <div className='col-sm-2'></div>
                                <div className='col-sm-8'>
                                    
                                        <div className="form-group">
                                        
                                        <input 
                                            id="promptInputBox"
                                            type="text" 
                                            className="form-control bg-primary chat-input text-light" 
                                            
                                            onChange={this.handleMessageInput}
                                            value={this.state.message}
                                            //onKeyUp={this.handleChatKeyDown}
                                        />
                                        
                                        
                                        </div>
                                    
                                </div>
                                <div className='col-sm-2'></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        )
    }

}

export default withRouter(WebsocketTests);