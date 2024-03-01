import React from 'react';

// import Api from '../modules/api';

import { withRouter } from './utils.jsx';
import 'bootswatch/dist/lux/bootstrap.min.css'; // Added this :boom:

import Api from './api.js';
import WS from './ws.js';

import PromptDeckColumn from './PromptDeckColumn.jsx';
import PromptFlowChat from './PromptFlowChat.jsx';

class PromptDeck extends React.Component {

    constructor(props){
        super(props);

        this.state = {
            
            api:new Api(),
            innerHeight:window.innerHeight,
            
        }

        this.handleResize = this.handleResize.bind(this);
    }

    componentDidMount(){

        this.init();

        window.addEventListener('resize', this.handleResize);


    }

    handleResize(){
        
        const innerHeight = window.innerHeight;
        //console.log("resize",innerHeight);
        this.setState({innerHeight:innerHeight})
    }


    async init(){
        const routerParams = this.props.params;
        //console.log("routerParams", routerParams);
        const promptDeckId = parseInt(routerParams.promptDeckId);

        try {
            const me = await this.state.api.me();
            //console.log('me:', me);

            //user is logged in, get prompt deck data
            //TODO

            
        } catch (error) {
            console.error('Error in me:', error);
            //window.location.href = "/app/login";
        }
    }
 

    render(){



        const routerParams = this.props.params;
        
        //console.log("routerParams", routerParams);
        //console.log(this.state.prompt);

        
        const contentHeight = this.state.innerHeight;
        const controlsHeight = 500;

        let deckListHeight = 300;
        if (contentHeight > 700) {
            deckListHeight = contentHeight - controlsHeight;
        }

        
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
                    <div className='col-sm-3 bg-primary nomargin nopad'
                        style={{
                            height:contentHeight,
                        }}
                    >
                        <div className='deck-controls'> 
                            <br></br>
                            <div className='row' style={{padding:10}}>
                                <div className='col-sm-1'></div>
                                <div className='col-sm-2'>
                                    <img 
                                        width="60" 
                                        src="https://cdn.dribbble.com/users/829077/screenshots/5900353/robot2.gif"
                                        style={{
                                            borderRadius: 20,
                                        
                                        
                                        }}
                                        
                                    ></img>
                                </div>
                                <div className='col-sm-6'
                                    style={{
                                        paddingLeft:20,
                                    }}
                                >
                                    <h5 className='text-light'>Blake Allen</h5>
                                    <h6 className='text-light'>@blakedallen</h6>
                                </div>
                                <div className='col-sm-2'
                                    style={{cursor:"pointer"}}
                                >
                                <button className='btn btn-primary '
                                    style={{borderRadius: 10}}
                                >...</button>
                                </div>
                            </div>
                            <hr></hr>
                            <div className='row' style={{padding:10}}>
                                <div className='col-sm-1'></div>
                                <div className='col-sm-9'>
                                <button 
                                    className='btn btn-block btn-info' 
                                    style={{borderRadius: 20, width:"100%"}}>
                                        <h3 className="text-light"
                                            style={{marginBottom:0}}
                                        >
                                            Prompt</h3></button>
                                </div>
                                <div className='col-sm-1'></div>
                                
                            </div>
                            <div className='row' style={{padding:10}}>
                                <div className='col-sm-6'>
                                <button 
                                    className='btn btn-primary' 
                                    style={{borderRadius: 20}}>
                                        
                                        + Add column</button>

                                </div>
                                <div className='col-sm-6'>
                                <button 
                                    className='btn btn-primary' 
                                    style={{borderRadius: 20}}>
                                    
                                    <span style={{marginRight:4}}>🔍 </span> <span>Search</span></button>
                                </div>
                                <div className='col-sm-2'></div>
                                
                            </div>
                            <hr></hr>
                            <div className='row' >
                                <div className='col-sm-2'>
                                <button 
                                    className='btn btn-primary disabled' 
                                    style={{
                                            borderRadius: 20,
                                            marginLeft: 6,
                                        }}>
                                        
                                        Decks</button>
                                </div>
                                <div className='col-sm-5'>
                                
                                </div>
                                <div className='col-sm-5'>
                                <button 
                                    className='btn btn-primary' 
                                    style={{borderRadius: 20}}>
                                        
                                        + New Deck</button>
                                </div>
                                
                            </div>
                        </div> {/* controls */}
                        
                        <div className='row deck-list' 
                            style={{
                                paddingLeft: 8,
                                height:deckListHeight,
                                overflowY:"scroll",
                            }}>
                            <ul>
                                
                                <li
                                        className='btn btn-primary' 
                                        style={{
                                            borderRadius: 20, 
                                            textAlign:"left",
                                            height: 50,
                                        }}>
                                    <span style={{marginRight:4}}>🚀 </span> <span>Direct Response Copy</span>
                                    
                                </li>
                                <li>
                                    <button 
                                    className='btn btn-primary' 
                                    style={{
                                        borderRadius: 20, 
                                        textAlign:"left",
                                        height: 50,
                                    }}>
                                    
                                    <span style={{marginRight:4}}>🌋 </span> <span>Emotional Intelligence</span>
                                    </button>
                                </li>
                                <li>
                                    <button 
                                    className='btn btn-primary' 
                                    style={{
                                        borderRadius: 20, 
                                        textAlign:"left",
                                        height: 50,
                                    }}>
                                    
                                    <span style={{marginRight:4}}>🏝️ </span> <span>Travel</span>
                                    </button>
                                </li>
                                <li>
                                    <button 
                                    className='btn btn-primary' 
                                    style={{
                                        borderRadius: 20, 
                                        textAlign:"left",
                                        height: 50,
                                    }}>
                                    
                                    <span style={{marginRight:4}}>💡 </span> <span>Ideas</span>
                                    </button>
                                </li>

                                
                            </ul>
                            
                            
                        </div>

                        
                    
                        <div className='sym-footer'
                        
                        >
                        <hr></hr>
                        <img 
                            style={{
                                paddingLeft: 32,
                            }}
                            width={100}
                            src="http://localhost:8000/static/sym.png">
                        </img>
                        </div>  

                    </div>
                    
                    <div className='col-sm-9 bg-dark nomargin nopad'
                        
                            
                        >
                        
                        <div className='row'>

                        <div 
                            className='col-sm-6'
                            style={{ 
                            
                            
                            height:contentHeight-5,
                        
                        }}>

                            <PromptFlowChat 
                                
                                
                                promptFlowId={19}
                            />
                        </div>

                        <div 
                            className='col-sm-6'
                            style={{ 
                            
                            
                            height:contentHeight-5,
                        
                        }}>
                            

                            <PromptFlowChat 
                            
                                promptFlowId={31}
                            />
                        </div>

                        
                            
                        </div>
                            
                       
                            
                        
                    </div>
                </div>
            </div>
        )
    }

}

export default withRouter(PromptDeck);