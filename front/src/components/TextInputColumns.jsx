import React from 'react';

// import Api from '../modules/api';

import { withRouter } from './utils.jsx';

import 'bootswatch/dist/lux/bootstrap.min.css'; // Added this :boom:

import ReactMarkdown from 'react-markdown'

import Api from './api.js';
import WS from './ws.js';

import TextInput from './TextInput.jsx';

class TextInputColumns extends React.Component {

    constructor(props){
        super(props);

        this.state = {
            columns:[
                {
                    "name":"3 questions",
                    "key":"single_prompt_flow",
                    "items":[
                        {
                            "id":56,
                            "key":"prompt_flow",
                            "name":"3 questions for health coaching"
                        }
                    ]
                },
                {
                    "name":"3 questions",
                    "key":"single_prompt_flow",
                    "items":[
                        {
                            "id":56,
                            "key":"prompt_flow",
                            "name":"3 questions for health coaching"
                        }
                    ]
                }
            ],
            
            
        }

    }


    renderColumns(){
        const columns = this.state.columns.map(c => {
            return (
                <p>{c.name}</p>
            )
        })
        return columns
    }
   
    
    render(){


        const columns = this.renderColumns();
        
        return (
            <div className="container-textarea">
                {columns}
            </div>
        )
    }

}

export default withRouter(TextInputColumns);