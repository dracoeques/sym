import React from 'react';

import ComboBox from '../ComboBox';

class PersonalizeNodeEditor extends React.Component {
    constructor(props){
        super(props);
        this.state = {
            data:{
                id:props.id,
                context_str_template: props.context_str_template ? props.context : "",
            },
            
        }

        

        this.updateContext = this.updateContext.bind(this);
        
    }

    updateContext(e){
        let data = this.state.data;
        data.context = e.target.value;
        this.props.updateNodeData(data);
    }

    

    render(){
       

        
        return (
            <div>
                <h3 className="text-light">Personalization Editor</h3>
                

                <h5 className='text-light'>Context</h5>
                <textarea
                    className="form-control" 
                    rows="5"
                    value={this.props.context}
                    onChange={this.updateContext}
                ></textarea>
                <hr></hr>
                
            </div>
        )
    }


}

export default PersonalizeNodeEditor;