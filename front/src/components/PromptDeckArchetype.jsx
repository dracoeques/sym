import React from 'react';
// import 'style.css';  // assuming the CSS above is saved in 'style.css'

import PromptTemplate from './PromptTemplate';
//import PromptFlowChat from './PromptFlowChat';
import PromptFlowSimpleChat from './PromptFlowSimpleChat';
import PromptFlowChat from './PromptFlowChat';
import FolderComponent from './FolderComponent';

import Api from './api';

import { withRouter } from './utils';

const default_columns = [
    {
        key:"prompt_flow",
        id_prompt_flow:19,
        items:[]
    },
    {
        key:"prompt_libs",
        status:"selecting",
        prompt:"",
        items:[
            {
                key:"prompt",
                id_prompt:10,
            },
            {
                key:"prompt",
                id_prompt:9,
                
            }

        ]

    },
    {

        key:"prompt_flow",
        id_prompt_flow:37,
        items:[
            {
                key:"prompt_flow",
                id_prompt_flow:31,
            }
        ]

    },
]




class PromptDeckArchetype extends React.Component {

    constructor(props){
        super(props);
        this.state = {
            api: new Api(),
            innerHeight:window.innerHeight,
            columnHeight:window.innerHeight-40,
            navheight:40,
            deckId:0,
            category:"",
            subcategory:"",
            columns:[],
        }
        this.handleResize = this.handleResize.bind(this);
    }

    componentDidMount(){
        //init data
        this.init()

        window.addEventListener('resize', this.handleResize);
        
    }

    async init(){

        const routerParams = this.props.params;
        console.log("routerParams", routerParams);
        let deckId = this.state.prompt_flow_id;
        if (routerParams.promptDeckId){

            deckId = parseInt(routerParams.promptDeckId);
        } else {
            //default deck view
            this.setState({columns :default_columns});
            return
        }

        try {
            //const me = await this.state.api.me();
            //console.log('me:', me);

            const deck = await this.state.api.loadPromptDeck(deckId);
            console.log("data", deck);

            

            this.setState({
               columns:deck.columns,
               category: deck.category,
               subcategory:deck.subcategory,
            });

            
        } catch (error) {
            console.error('Error in me:', error);
            //window.location.href = "/app/login";
        }
    }

    handleResize(){
        
        const innerHeight = window.innerHeight;
        const columnHeight = innerHeight - this.state.navheight - 40;
        console.log("resize", innerHeight);
        this.setState(
            {
                innerHeight:innerHeight,
                columnHeight:columnHeight,
        })
    }

  
    

    onRunPromptLib(prompt, columnIndex){
        console.log("onRunPrompt", prompt, columnIndex);
        let columns = this.state.columns;
        columns[columnIndex].prompt = prompt;
        columns[columnIndex].status = "running"
        this.setState({columns:columns});
    }

    

    renderPromptLibs(items, columnIndex){


        const libs = items.map(function(item){
            console.log("renderPromptLibs", item)
            return (
            <div key={item.id_prompt} >
            <PromptTemplate 
                promptLibId={item.id_prompt}
                onRunPrompt={(prompt) => this.onRunPromptLib(prompt, columnIndex)}
            />
            <br></br>
            </div>
        )}.bind(this))
        return (<div style={{
            height:this.state.columnHeight-100,
            overflowY:"scroll",
        }}>
            {libs}
        </div>)
    }

    renderPromptFlow(id_prompt_flow){
        return (<PromptFlowChat
            //doScrolling={false} //disabled until it can be debugged
            doResizing={false} //handle this at this level
            height={this.state.columnHeight-100}
            promptFlowId={id_prompt_flow}
        />)
    }

    renderPromptLibRun(prompt){
        return (
            <PromptFlowChat
                prompt={prompt}
                runFirstPrompt={false}
                doResizing={false} //handle this at this level
                height={this.state.columnHeight-100}
                promptFlowId={106} //default for libs
            />
        )
    }

    renderColumns(){

        let columnIndex = 0;

        const columns = this.state.columns.map(function(col){

            let inner = (<div></div>);
            if (col.key == "single_prompt_flow"){
                if (col.items.length === 1){
                    const flow = col.items[0]
                    inner = this.renderPromptFlow(flow.id_prompt_flow)
                } else {
                    console.log("Error, single_prompt_flow expects only one item!!! found in column: ", col.id)
                    const flow = col.items[col.items.length - 1];   
                    inner = this.renderPromptFlow(flow.id_prompt_flow)

                }
                
                
            } else if (col.key == "prompt_libs"){
                    
                if (col.status == "running"){
                    inner = this.renderPromptLibRun(col.prompt);
                } else {
                    inner = this.renderPromptLibs(col.items, columnIndex);
                }
                
            }

            columnIndex +=1;

            return (
                <div className='col-sm-4 bg-light'
                    style={{
                        // borderLeft:"1px solid #eee",
                        
                    }}
                >
                    <div 
                        className=''
                    style={{
                        height: 40,
                        width: "100%",
                        padding: 10,
                    }}>
                        <h3 className=''
                            style={{textAlign:"center"}}
                        >{col.name}</h3>
                    </div>
                    {inner}
                </div>
            )
            
        }.bind(this));
        return columns;
    }

    render(){


        return (
            <div className='bg-light'
                style={{
                    height:this.state.innerHeight,
                    
                }}
            >
                <div style={{padding:10}} className='bg-primary'>
                <ol className="breadcrumb">
                    <li className="breadcrumb-item "><a className="text-light" href="/app/flower">Flower</a></li>
                    <li className="breadcrumb-item "><a className="text-light" href="/app/flower">{this.state.category}</a></li>
                    <li className="breadcrumb-item active">{this.state.subcategory}</li>
                </ol>
                </div>
                <div className='row' style={{
                    padding:10,
                    
                    }}>
                    
                    {this.renderColumns()}
                    
                </div>
                
            </div>
        )
    }
}

export default withRouter(PromptDeckArchetype)
    
