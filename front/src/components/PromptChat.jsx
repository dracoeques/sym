import React from 'react';

// import Api from '../modules/api';

import { withRouter } from './utils.jsx';

import 'bootswatch/dist/lux/bootstrap.min.css'; // Added this :boom:

import ReactMarkdown from 'react-markdown'

import Api from './api.js';
import WS from './ws.js';


class PromptChat extends React.Component {

    constructor(props){
        super(props);

        this.state = {
            ws:null,
            api:new Api(),
            id:0,
            prompt:this.props.prompt ? this.props.prompt :  "",
            system: this.props.system ? this.props.system : "",
            
            message:this.props.prompt ? this.props.prompt :  "", //user text 
            last_message:null,
            cursorIndex:0,
            sidebarHeight:props.height ? props.height : window.innerHeight,
            //messages:[],
            isLoading:false,
            nodeid2messages:{},
            node_order:[],
            last_message_ref: React.createRef(),
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

        //this.init();
    
        window.addEventListener('resize', this.handleResize);
        
        const promptInputBox = document.getElementById(`promptInputBox_${this.props.promptFlowId}`);
        promptInputBox.addEventListener('keypress', function(e){
            if (e.key === 'Enter') {
                //console.log("Enter pressed");
                this.handleWebsocketSendMessage();
            }
        }.bind(this));
        

    }

    async init(){
        const routerParams = this.props.params;
        //console.log("routerParams", routerParams);
        let promptFlowId = this.state.prompt_flow_id;
        if (routerParams.promptFlowId){
            promptFlowId = parseInt(routerParams.promptFlowId);
        }

    
        

        try {
            //const me = await this.state.api.me();
            //console.log('me:', me);

            //user is logged in, create websocket
            let base = window.location.host;
            if (base === "localhost:5173" || base === "localhost:5174"){
                base = "localhost:8000"
            } 
            let protocol = "ws";
            if (location.protocol === 'https:') {
                protocol = "wss"
            }
            const ws = new WS(
                `${protocol}://${base}/ws2`,
                this.handleWebsocketOnMessage,
                this.handleWebsocketOnOpen,
                this.handleWebsocketOnClose,
                this.handleWebsocketOnError,
            );

            this.setState({
                ws:ws,
            });

            
        } catch (error) {
            console.error('Error ininit:', error);
            //window.location.href = "/app/login";
        }
    }
 

    handleWebsocketOnMessage(event){
        
        const content = event.data;
        const obj = JSON.parse(content);
        let nodeid2messages = this.state.nodeid2messages;
        let node_order = this.state.node_order;
        let prompt_run_id = this.state.prompt_run_id;
        let last_message = this.state.last_message;
        console.log("onmessage", obj);
        if (obj.payload){
            const node_id = obj.payload.node_id
            if (!nodeid2messages[node_id]){
                nodeid2messages[node_id] = []
                node_order.push(node_id);
            }
            //if streaming, append all data
            if (obj.payload.action === "stream"){
                nodeid2messages[node_id].push(obj.payload)
            } else {
                //not streaming, just replace 
                const curlen = nodeid2messages[node_id].length;
                
                if (curlen === 0 ){
                    nodeid2messages[node_id].push(obj.payload)
                } else {
                    nodeid2messages[node_id][0] = obj.payload
                }

            }
            
            
            
            last_message = obj.payload;
            if (obj.payload.prompt_run_id){
                prompt_run_id = obj.payload.prompt_run_id;
            }
            //console.log(messages);
            this.setState({
                last_message:last_message,
                prompt_run_id:prompt_run_id,
                isLoading:false,
                node_order:node_order,
                nodeid2messages:nodeid2messages,
            }, () => {
                this.scrollToBottom();
            });
        }
        
        
    }

    handleWebsocketSendMessage(){
        const message = this.state.message;
        if (message.length === 0){
            return;
        }

        const last_message = this.state.last_message;
        let node_id = null;
        if (last_message){
            node_id = last_message.node_id;
        }

        //NOTE: more actions can be set here
        //as they get built out
        const action = "set_user_input";

        const local_node_id = `${node_id}_user`;

        const payload = {
            "action":action,
            "message":message,
            "node_type":"set_user_input",
            "prompt_flow_id":this.state.promptFlowId,
            "prompt_run_id":this.state.prompt_run_id,
            "node_id":node_id,
            "local_node_id":local_node_id,
        }
        this.state.ws.sendMessage(payload);
        console.log("sendmessage", payload);

        let node_order = this.state.node_order;
        let nodeid2messages = this.state.nodeid2messages;
        nodeid2messages[local_node_id] = []
        nodeid2messages[local_node_id].push(payload)
        node_order.push(local_node_id);

        this.setState({
            message:"",
            isLoading:true,
            node_order:node_order,
            nodeid2messages:nodeid2messages,
        });
    }

    handleWebsocketOnOpen(){        

        const wsState = this.state.ws.getState();
        if (wsState === "OPEN"){
             //send our init message
            const payload = {
                "action":"init",
                "prompt_flow_id":this.state.promptFlowId,
                
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

    scrollToBottom(){
        this.state.last_message_ref?.current?.scrollIntoView({ behavior: 'smooth' })
    }

    renderMessages(){

        const messages = this.state.node_order.map(function(node_id){
            const node_messages = this.state.nodeid2messages[node_id];
            const first_node = this.state.nodeid2messages[node_id][0];
            //console.log("message", node_messages);
            let inner_messages = [];
            for (const i in node_messages){
                const item = node_messages[i];
                inner_messages.push(item.message)
            }
            let combined_message = inner_messages.join('');

            let message_name = first_node.node_type;

            let prompt_template = (<div></div>);
            let system = (<div></div>);
            let generated_prompt = (<div></div>);
            
            if (first_node.node_type === "prompt"){
                message_name = "Response:"
                if (first_node.node_data.prompt){
                    prompt_template = (<div>
                        <h5 className='text-secondary'>Prompt Template:</h5>
                        <ReactMarkdown  children={first_node.node_data.prompt}></ReactMarkdown>
                        </div>)
                }
                if (first_node.node_data.system){
                    system = (<div >
                        <h5 className='text-secondary'>System:</h5>
                        <ReactMarkdown  children={first_node.node_data.system}></ReactMarkdown>
                        </div>)
                }
                if (first_node.node_data.generated_prompt){
                    generated_prompt = (<div >
                        <h5 className='text-secondary'>Generated Prompt:</h5>
                        <ReactMarkdown  children={first_node.node_data.generated_prompt}></ReactMarkdown>
                        </div>)
                }
            } else if (first_node.node_type === "storage"){

                if (first_node.node_data.variable_name){
                    combined_message = first_node.node_data.variable_name;
                }
                if (first_node.node_data.value){
                    combined_message += ": "+first_node.node_data.value
                }
                 
            }
            
            return (
                <div className='row message-row' key={node_id}>
                   
                    <div className='col-sm-1'>
                        {/* <img src="http://localhost:8000/static/sym-avatar-small.png" width="50" ></img> */}
                    </div>
                    
                    <div className='col-sm-10 text-light'>
                        {prompt_template}
                        {system}
                        {generated_prompt}
                        <div>
                            <h5 className='text-secondary'>{message_name}</h5>
                            <ReactMarkdown  children={combined_message}></ReactMarkdown>
                        </div>
                        <hr></hr>
                        
                      
                    </div>
                    <div className='col-sm-1'></div>
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

        const chatInputHeight = 100;
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
                   
                    <div className='col-sm-12 bg-dark nomargin nopad'>

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
                                    
                                    <textarea

                                        id={`promptInputBox_${this.props.promptFlowId}`}
                                        className="form-control dynamic-textarea"
                                        onChange={this.handleMessageInput}
                                        value={this.state.message}
                                        placeholder="Type here..."

                                        style={{
                                            color: "#a0a0a0",
                                            backgroundColor: "#fff",
                                            outline: "1px solid #ffffff",                        
                                            fontSize: "16px",
                                            boxShadow: "0 0 20px rgba(0, 0, 0, .15)",
                                            border: "0.75px solid #d8d8d8",
                                            paddingRight:75,
                                        }}
                                        
                                    ></textarea>
                        
                                    <button class="bottom-button btn btn-secondary" type="button" id="button-addon2"
                                                    
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
                                                height:69,
                                                borderLeft: "1px solid #fefefe ",
                                            }}
                                            class="image-62"/>
                                    </button>

                                        
                                       
                                    
                                </div>
                                
                                
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        )
    }

}

export default withRouter(PromptChat);