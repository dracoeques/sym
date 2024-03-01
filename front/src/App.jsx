import React from 'react';

// import Api from '../modules/api';

import { withRouter } from './components/utils.jsx';

import 'bootswatch/dist/lux/bootstrap.min.css'; // Added this :boom:

import ReactMarkdown from 'react-markdown'



import Api from './components/api.js';
import WS from './components/ws.js';

class App extends React.Component {

    constructor(props){
        super(props);
        this.state = {
            ws:null,
            api:new Api(),
            prompt:"",
            context:"You are a helpful assistant.",
            cursorIndex:0,
            sidebarHeight:window.innerHeight,
            messages:[
                {
                    "id":0,
                    "text":"Hello there!",
                    "context":"You are a helpful assistant.",
                }
            ],
            isMetaActive:false,
            isLoading:false,
        }


        this.handleResize = this.handleResize.bind(this);
        this.handlePromptInput = this.handlePromptInput.bind(this);
        this.handleWebsocketOnMessage = this.handleWebsocketOnMessage.bind(this);
        this.handleWebsocketSendMessage = this.handleWebsocketSendMessage.bind(this);
        this.handleSystemInput = this.handleSystemInput.bind(this);
    }

    componentDidMount(){

        this.initUser();
    
        window.addEventListener('resize', this.handleResize);
        
        const promptInputBox = document.getElementById("promptInputBox");
        promptInputBox.addEventListener('keypress', function(e){
            if (e.key === 'Enter') {
                console.log("Enter pressed");
                this.handleWebsocketSendMessage();
            }
        }.bind(this));
        

    }

    async initUser(){
        try {
            const me = await this.state.api.me();
            console.log('me:', me);

            //user is logged in, create websocket
            const ws = new WS(this.handleWebsocketOnMessage);

            this.setState({
                ws:ws,
            })

            
        } catch (error) {
            console.error('Error in me:', error);
            //window.location.href = "/app/login";
        }
    }
 

    handleWebsocketOnMessage(event){
        console.log("onmessage", event);
        const content = event.data;
        const obj = JSON.parse(content);
        let messages = this.state.messages;
        messages.push(obj)
        console.log(messages);
        this.setState({
            messages:messages,
            isLoading:false,
        });
    }

    handleWebsocketSendMessage(){
        const prompt = this.state.prompt;
        if (prompt.length === 0){
            return;
        }

        const payload = {
            "prompt":prompt,
            "context":this.state.context,
        }
        this.state.ws.sendMessage(payload);
        console.log("sendmessage", payload);

        this.setState({
            prompt:"",
            isLoading:true,
        });
    }


    handleResize(){
        
        const innerHeight = window.innerHeight;
        console.log("resize",innerHeight);
        this.setState({sidebarHeight:innerHeight})
    }

    calculateTextBoxSize(){

    }

    handlePromptInput(e){
        e.preventDefault();
        const text = e.target.value;
        this.setState({prompt:text});
    }

    handleSystemInput(e){
        e.preventDefault();
        const text = e.target.value;
        this.setState({context:text});
    }

    renderMessages(){

        const messages = this.state.messages.map(function(m){
            return (
                <div className='row message-row' key={m.id}>
                    <div className='col-sm-3'></div>
                    <div className='col-sm-1'>
                        <img src="http://localhost:8000/static/sym-avatar-small.png" width="50" ></img>
                    </div>
                    <div className='col-sm-6 text-light'>
                        <h5 className='text-secondary'>Response:</h5>
                        <ReactMarkdown children={m.text}  />
                        <hr></hr>
                        <h5 className='text-secondary'>Context:</h5>
                        <p>{m.context}</p>
                        <hr></hr>
                      
                    </div>
                    <div className='col-sm-2'></div>
                </div>
                
            )
        }); 
        return (
            <ul>
                {messages}
            </ul>
        )

    }

    render(){



        const routerParams = this.props.params;
        
        //console.log(routerParams);
        //console.log(this.state.prompt);

        const chatInputHeight = 150;
        const contentHeight = this.state.sidebarHeight - chatInputHeight;

        const messages = this.renderMessages();
        let loader = (<div></div>);
        if (this.state.isLoading === true){
            loader = (
                <div className='row message-row' >
                    <div className='col-sm-2'></div>
                    <div className='col-sm-1'>
                        <img src="http://localhost:8000/static/sym-avatar-small.png" width="50" ></img>
                    </div>
                    <div className='col-sm-7 text-light'>
                        <h3>Loading...</h3>
                      
                    </div>
                    <div className='col-sm-2'></div>
                    
                </div>);

        }

        return (
            <div className='container-fluid'>
                <div className='row'>
                    <div className='col-sm-2 bg-primary nomargin'
                        style={{
                            minHeight:this.state.sidebarHeight,
                        }}
                    >
                        <h3 className="text-light">Sidebar</h3>
                        
                      
                    </div>
                    <div className='col-sm-10 bg-dark nomargin'>

                        <div
                        
                            style={{
                                height:contentHeight,
                                overflowY:"scroll",
                            }}
                        >
                            <br></br>
                            {messages}
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
                                            
                                            onChange={this.handlePromptInput}
                                            value={this.state.prompt}
                                            //onKeyUp={this.handleChatKeyDown}
                                        />
                                        <hr></hr>
                                        <input 
                                            id="systemInputBox"
                                            type="text" 
                                            className="form-control bg-primary chat-input text-light" 
                                            
                                            onChange={this.handleSystemInput}
                                            value={this.state.context}
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

export default withRouter(App);