import React from 'react';
// import 'style.css';  // assuming the CSS above is saved in 'style.css'

import PromptFlowChat from './PromptFlowChat';
import { withRouter } from './utils';


class PromptDeckBuilder extends React.Component {

    constructor(props){
        super(props);
        this.state = {
            innerHeight:window.innerHeight,

            category:"",
            subcategory:"",
        }

    }


    render(){
        return (
            <div>Hello</div>
        )
    }
}

export default withRouter(PromptDeckBuilder)
    
