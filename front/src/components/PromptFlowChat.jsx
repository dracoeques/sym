import React from 'react';

// import Api from '../modules/api';

import { withRouter } from './utils.jsx';

import ResizableTextarea from './ResizableTextarea';
import 'bootswatch/dist/lux/bootstrap.min.css'; // Added this :boom:

import ReactMarkdown from 'react-markdown'

import Api from './api.js';
import WS from './ws.js';


//Current v2 prompt flow chat client

function LinkRenderer(props) {
    console.log({ props });
    return (
      <a href={props.href} target="_blank" rel="noreferrer">
        {props.children}
      </a>
    );
  }

class PromptFlowSimpleChat extends React.Component {

    constructor(props){
        super(props);

        this.state = {
            ws:null,
            api:new Api(),
            prompt_flow_id:props.promptFlowId ? props.promptFlowId : null,
            action: props.action ? props.action : "init",
            prompt_run_id:props.promptRunId ? props.promptRunId : null,
            message:props.prompt ? props.prompt : "", //user text 
            runFirstPrompt:props.runFirstPrompt ? props.runFirstPrompt : false, // if we recieve a prompt, should we immediately run it after init?
            finishCallback: props.finishCallback ? props.finishCallback : null,
            last_message:null,
            cursorIndex:0,
            sidebarHeight:props.height ? props.height : window.innerHeight,
            //messages:[],
            isLoading:false,
            
            
            
            runitemid2message:{}, //map from a run item to it's current message
            run_item_order:[],
            last_message_ref: React.createRef(),
            last_message_in_view: false,
            doResize: props.doResize,
        }


        //check for URL parameter for promptRun
        const prid = this.state.api.getUrlParam("prompt_run_id");
        if (prid){
            this.state.prompt_run_id=parseInt(prid)
        }

        this.handleResize = this.handleResize.bind(this);
        this.handleMessageInput = this.handleMessageInput.bind(this);
        this.handleSystemInput = this.handleSystemInput.bind(this);

        this.handleWebsocketOnMessage = this.handleWebsocketOnMessage.bind(this);
        this.handleWebsocketSendMessage = this.handleWebsocketSendMessage.bind(this);
        this.handleWebsocketOnOpen = this.handleWebsocketOnOpen.bind(this);
        this.handleWebsocketOnClose = this.handleWebsocketOnClose.bind(this);
        this.handleWebsocketOnError = this.handleWebsocketOnError.bind(this);

        this.finish = this.finish.bind(this);
    }

    componentDidMount(){
        
        this.init();
    
        window.addEventListener('resize', this.handleResize);
        
        //listen enter keypress logic
        const promptInputBox = document.getElementById(`promptInputBox_${this.props.promptFlowId}`);
        promptInputBox.addEventListener('keypress', function(e){
            if (e.key === 'Enter') {
                this.handleWebsocketSendMessage();

                //optionally listen to 2 enters pressed, if 2 are pressed in succession, submit message
                // if (this.state.message.length >= 2){
                //     const last2 = this.state.message.slice(-1);
                //     console.log("Enter pressed", last2, last2 === "\n");
                //     if (last2 === "\n"){
                //         this.handleWebsocketSendMessage();
                //     }
                // }
               
                
                
            }
        }.bind(this));

        //add an observer to see if the bottom message ref is in view
        this.observer = new IntersectionObserver(
            (entries) => {
              const [entry] = entries;
              this.setState({ last_message_in_view: entry.isIntersecting });
            },
            {
              threshold: 0.1,  // Adjust as necessary
            }
          );
        this.observer.observe(this.state.last_message_ref.current);
        

    }


    init(){

        try {
            //const me = await this.state.api.me();
            //console.log('me:', me);

            this.connectWebsocket()

            
        } catch (error) {
            console.error('Error in init:', error);
            //window.location.href = "/app/login";
        }
    }
 
    connectWebsocket(reconnect){
        //get prompt flow to connect to 
        const routerParams = this.props.params;
        //console.log("routerParams", routerParams);
        let promptFlowId = this.state.prompt_flow_id;
        if (routerParams.promptFlowId){
            promptFlowId = parseInt(routerParams.promptFlowId);
        }

        //set url host
        let base = window.location.host;
        if (base === "localhost:5173" || base === "localhost:5174"){
            base = "localhost:8000"
        } 

        //protocol ws or wss
        let protocol = "ws";
        if (location.protocol === 'https:') {
            protocol = "wss";
        }

        if (reconnect){
            //we're reconnecting, omit onOpen

            const ws = new WS(
                `${protocol}://${base}/ws-v2`,
                this.handleWebsocketOnMessage,
                null, // omit on open
                this.handleWebsocketOnClose,
                this.handleWebsocketOnError,
            );

            this.setState({
                ws:ws,
                promptFlowId:promptFlowId,
                action:"connected",
            });

        } else {

            const ws = new WS(
                `${protocol}://${base}/ws-v2`,
                this.handleWebsocketOnMessage,
                this.handleWebsocketOnOpen,
                this.handleWebsocketOnClose,
                this.handleWebsocketOnError,
            );

            this.setState({
                ws:ws,
                promptFlowId:promptFlowId,
                action:"connected",
            });

        }
    }

    handleWebsocketOnMessage(event){
        
        const content = event.data;
        const obj = JSON.parse(content);
        
        console.log("onmessage", obj);

        let runitemid2message = this.state.runitemid2message;
        let run_item_order = this.state.run_item_order;
        let prompt_run_id = obj.prompt_run_id;
        let prompt_run_item_id = obj.prompt_run_item_id;
        let last_message = obj;
        
        
        if (!runitemid2message[prompt_run_item_id]){
            //new run_item, add to our logical ordering
            runitemid2message[prompt_run_item_id] = obj
            run_item_order.push(prompt_run_item_id);
        } else {
            //existing run_item, replace with new data
            runitemid2message[prompt_run_item_id] = obj
        }

        //check for finish message, if found run finish logic
        if (obj.action === "finish"){
            this.finish();
        }

        
        

        //console.log(messages);
        this.setState({
            last_message:last_message,
            prompt_run_id:prompt_run_id,
            isLoading:false,
            run_item_order:run_item_order,
            
        }, () => {
            //if we initialize with a prompt, run it immediately after init
            let runFirstPrompt = this.state.runFirstPrompt
            if (this.state.message && this.state.message.length > 0 && runFirstPrompt){
                this.handleWebsocketSendMessage();
            }

            //this.scrollToBottom(true);
        });
        
        
        
    }

    handleWebsocketSendMessage(){

        const ws_state = this.state.ws.getState();

        console.log("WS STATE: ", ws_state)
        if (ws_state === "CLOSED"){
            //TODO: see why the 
            //this.connectWebsocket(true);
        }


        const message = this.state.message;
        if (message.length === 0){
            return;
        }
        const last_message = this.state.last_message;
        console.log("last_message", last_message);
        let node_id = null;
        let prompt_run_item_id = null;
        if (last_message){
            node_id = last_message.node_id;
            prompt_run_item_id = last_message.prompt_run_item_id;
        }

        //NOTE: more actions can be set here
        //as they get built out
        const action = "set_user_input";

        const timestamp = Date.now();
        const local_run_id = `${node_id}_user_${timestamp}`;

        const payload = {
            "action":action,
            "message":message,
            "node_type":"set_user_input",
            "payload":{
                "user_response":message,
            },
            "prompt_flow_id":this.state.promptFlowId,
            "prompt_run_id":this.state.prompt_run_id,
            "prompt_run_item_id":prompt_run_item_id,
            "node_id":node_id,
            "local_run_id":local_run_id,
        }
        this.state.ws.sendMessage(payload);
        console.log("sendmessage", payload);

        let runitemid2message = this.state.runitemid2message;
        runitemid2message[local_run_id] = payload;

        let run_item_order = this.state.run_item_order;
        run_item_order.push(local_run_id);

        this.setState({
            message:"",
            isLoading:true,
            run_item_order:run_item_order,
            runitemid2message:runitemid2message,
            
        }, () => {
            this.scrollToBottom(true)
        });
    }

    handleWebsocketOnOpen(){        

        const wsState = this.state.ws.getState();
        if (wsState === "OPEN"){
                    
            const payload = {
                "action":"init",
                "prompt_flow_id":this.state.promptFlowId,
                "prompt_run_id":this.state.prompt_run_id,
                
            }
            this.state.ws.sendMessage(payload);
                
        }

       
    }

    handleWebsocketOnClose(){
        console.log("Websocket closed");
    }

    handleWebsocketOnError(e){
        console.log("Websocket Error", e);
    }

    handleResize(){

        if (this.state.doResize){
            const innerHeight = window.innerHeight;
            console.log("resize",innerHeight);
            this.setState({sidebarHeight:innerHeight})
        }
        
        
    }

    finish(){
        console.log("Finish called!!!");
        if (this.state.finishCallback){
            const obj = {
                prompt_flow_id:this.state.prompt_flow_id,
                prompt_run_id:this.state.prompt_run_id,
            }
            this.state.finishCallback(obj);
        }

    }

    handleMessageInput(e){
        e.preventDefault();
        const text = e.target.value;
        this.setState({
            message:text,
            
        });
    }

    handleSystemInput(e){
        e.preventDefault();
        const text = e.target.value;
        this.setState({context:text});
    }

    scrollToBottom(force){
        //force a scroll (after a message is sent for instance)
        if (force === true){
            this.state.last_message_ref?.current?.scrollIntoView({ behavior: 'smooth' });
        }
        //check if our message is in view, if keep scrolling
        if (this.state.last_message_in_view){
            this.state.last_message_ref?.current?.scrollIntoView({ behavior: 'smooth' });
        }

        
    }

    renderMessages(){

        const messages = this.state.run_item_order.map(function(run_item_id){

            const envelope = this.state.runitemid2message[run_item_id];
            
            //console.log("envelope", envelope);
            if (envelope.action === "silent"){
                return (<span  key={run_item_id}></span>)
            }
            
            //default message
            let text_align = "left"
            let content = (<ReactMarkdown 
                style={{
                    textAlign:text_align,
                }}
                components={{ a: LinkRenderer }} 
                children={envelope.message}></ReactMarkdown>);
            
            //custom message design
            if (envelope.action === "set_user_input"){
                content = (<p 
                        
                        style={{        
                            textAlign:text_align,
                            color: "#320058",
                        }}

                    >{envelope.message}</p>);
            } else if (envelope.action === "finish"){
                //check for PDF node
                if (envelope.message.endsWith(".pdf")){
                    content = (
                        <div>
                        <a href={combined_message}>
                            <span>📁 </span><span> Client-getting-secrets.pdf</span> 
                        </a>
                        <p>* Right click the link above and select "Save Link As" to download your personal client getting secrets report!</p>
                        </div>
                    )
                }

                

            }



            


            return (
                <div 
                    className='row message-row geologica' 
                    key={run_item_id}
                      
                >
                   
                   
                    
                    <div className='col-sm-12 '>
                        
                        <div>
                            
                            {content}
                            
                        </div>
                       
                        
                      
                    </div>
                    
                </div>
                
            )
        }.bind(this)); 
        return (
            <ul
                style={{padding: "inherit"}}
            >
                {messages}
            </ul>
        )

    }

    render(){



        const routerParams = this.props.params;
        
        //console.log("routerParams", routerParams);
        //console.log(this.state.prompt);

        const chatInputHeight = 50;
        const contentHeight = this.state.sidebarHeight - chatInputHeight - 40;

        const messages = this.renderMessages();
        let loader = (<div></div>);
        if (this.state.isLoading === true){
            loader = (
                <div className='row message-row' >
                    <div className='col-sm-3'></div>
                    
                    <div className='col-sm-5 text-light'>
                        <p>Loading...</p>
                      
                    </div>
                    <div className='col-sm-4'></div>
                    
                </div>);

        }

        return (
            <div className='container-fluid'>
                <div className='row'>
                   
                    <div className='col-sm-12 '
                        style={{
                            maxWidth: 600,
                            margin: "0 auto",
                        }}
                    >

                        <div
                        
                            style={{
                                height:contentHeight,
                                overflowY:"scroll",
                                overflowX: "hidden",
                                
                            }}
                        >
                            <br></br>
                            {messages}
                            <br></br>
                            
                            {loader}
                            <br></br>
                            <div style={{ float:"left", clear: "both" }}
                                ref={this.state.last_message_ref}>
                            </div>
                        </div>
                        <div
                        
                            style={{
                                height:chatInputHeight,
                                
                            }}
                        >
                            <div className='row'>
                                
                                <div className='col-sm-12'>
                                    
                                        <div className="form-group ">


                                        
                                        
                                        <div class="input-group mb-3"

                                            style={{
                                                    height: "58px",
                                                    backgroundColor: "#fff",
                                                    border: "0.75px solid #d8d8d8",
                                                    borderRadius: "10px",
                                                    
                                                    justifyContent: "space-between",
                                                    
                                                    //overflow: "hidden",
                                                    boxShadow: "0 0 20px rgba(0, 0, 0, .15)",
                                                    flexWrap: "inherit",
    
    
                                                    
                                                }}
                                        
                                        >

                                
                                            
                                            <textarea 
                                                id={`promptInputBox_${this.props.promptFlowId}`}
                                                rows={1}
                                                onChange={this.handleMessageInput}
                                                value={this.state.message}

                                                type="text" 
                                                class="form-control " 
                                                placeholder="Type here..." 
                                                aria-label="Type here..." 
                                                aria-describedby="button-addon2"
                                                
                                                style={{
                                                    color: "#a0a0a0",
                                                    backgroundColor: "#fff",
                                                    outline: "1px solid #ffffff",                        
                                                    fontSize: "16px",
                                                    whiteSpace: "pre-line",

                                                    
                                                    //remove default textarea styling
                                                    //border: "none",
                                                    //overflow: "auto",
                                                    //outline: "none",
                                                    

                                                    //-webkit-box-shadow: "none";
                                                    //-moz-box-shadow: none;
                                                    //box-shadow: none;

                                                    resize: "none", /*remove the resize handle on the bottom right*/
                                                }}
                                                
                                                
                                            />
                                            <button class="btn btn-secondary" type="button" id="button-addon2"
                                                
                                                onClick={this.handleWebsocketSendMessage}
                                                style={{
                                                    padding: 0,
                                                }}
                                            >
                                                <img 
                                            src="https://uploads-ssl.webflow.com/64ee39d44b81a0ec6c03c3ba/64fb5f064f65e4372c4fb7ad_Screenshot%202023-09-08%20at%2010.50.21%20AM.png" 
                                            loading="lazy" 
                                            alt="" 
                                            style={{
                                                height:58,
                                                
                                                outline: "rgb(255, 255, 255) solid 1px",
                                            }}
                                            class="image-62"/></button>
                                        </div>

                                        
                                        
                                        
                                        </div>

                                        
                                       
                                    
                                </div>
                                
                                
                            </div>
                        </div>
                    </div>
                    
                </div>
            </div>
        )
    }

}

export default withRouter(PromptFlowSimpleChat);