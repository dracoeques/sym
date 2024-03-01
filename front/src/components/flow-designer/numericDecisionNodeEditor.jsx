import React from 'react';

import ComboBox from '../ComboBox';

class NumericDecisionNodeEditor extends React.Component {
    constructor(props){
        super(props);
        this.state = {
            data:{
                id:props.id,
                operator: props.operator ? props.operator : "",
                threshold: props.threshold ? props.threshold : 5,
                //prompt: props.prompt ? props.prompt : "",
                system: props.system ? props.system : "You are a helpful AI assistant",
                model: props.model ? props.model : "gpt-3.5-turbo",
            },
            
        }

        //this.updatePrompt = this.updatePrompt.bind(this);
        this.updateOperator = this.updateOperator.bind(this);
        this.updateThreshold = this.updateThreshold.bind(this);
        
    }

    updateOperator(e){
        let data = this.state.data;
        data.operator = e.target.value;
        console.log("Update operator",e.target.value );
        this.props.updateNodeData(data);
    }

    updateThreshold(e){
        let data = this.state.data;
        let threshold = parseInt(e.target.value);
        data.threshold = threshold;
        this.props.updateNodeData(data);
    }

    
    getOperatorText(operator){
        switch(operator){
            case "<":
                return "Less than";
            case "<=":
                return "Less than or equal to";
            case ">=":
                return "Greater than or equal to";
            case ">":
                return "Greater than";
        }
    }


    render(){
        console.log(this.props);

        const operator_options = [
            {label:"<", value:"<"},
            {label:"<=", value:"<="},
            {label:">", value:">"},
            {label:">=", value:">="},
        ]

        let operatorText = "less than";
        let operator = "<";
        if (this.props.operator){
            operator = this.props.operator;
        } else if (this.state.operator){
            operator = this.state.operator;
        }

        operatorText = this.getOperatorText(operator);
        let threshold = this.state.data.threshold;
       

        let summary = `Go to A when input value is ${operatorText} ${threshold}, otherwise go to B`

        return (
            <div>
                <h3 className="text-light">Numeric Decision</h3>
                
                <span className='text-light'>{summary}</span>
                <hr></hr>
                <h5 className='text-light'>Operator</h5>
                
                
                
                <span style={{width:100}}>
                    <select 
                        
                        id="exampleSelect1"

                        onChange={this.updateOperator}
                        value={operator}
                    >
                        <option>{"<"}</option>
                        <option>{"<="}</option>
                        <option>{">"}</option>
                        <option>{">="}</option>
                        
                    </select>
                    <span> {operatorText}</span>
                </span>
                <hr></hr>
                <h5 className='text-light'>Threshold</h5>
                <span style={{width:100, display:'block'}}>
                    <input type='number'
                        onChange={this.updateThreshold}
                        value={threshold}
                    ></input>
                </span>
                
            </div>
        )
    }


}

export default NumericDecisionNodeEditor;